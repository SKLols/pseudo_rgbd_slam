# Pseudo RGB-D SLAM

Replaces a physical depth sensor with Depth Anything V2 (neural network) to run ORB-SLAM2 RGB-D SLAM using only an RGB camera. Built as a modular 3-node ROS2 pipeline.

## Results

| Metric | Ground Truth (Real Depth) | Pseudo RGB-D (Neural Depth) |
|--------|--------------------------|------------------------------|
| Frames processed | 573 | 411 (67%) |
| Camera poses | 573 | 198 |
| Tracking loss | None | None |
| ATE RMSE | ~1-2 cm | **6.15 cm** |
| Scale correction | — | 0.615 (1.6× overestimate) |

## Architecture

    Node A (Python)         Node B (Python)          Node C (C++)
    TUM Dataset      -->    Depth Anything V2   -->   Saves RGB+Depth
    Broadcaster             Metric Estimator          to disk

    /camera/rgb/image_raw  -->  /camera/depth/image_raw  -->  /slam/trajectory

    After pipeline: rgbd_tum on saved frames --> CameraTrajectory.txt

## System Requirements

- Ubuntu 22.04 LTS (WSL2 tested)
- ROS2 Humble
- Python 3.10 (conda)
- NVIDIA GPU 2GB+ recommended (CPU works at ~2fps)
- 4GB RAM + 4GB swap minimum (set in .wslconfig for WSL2)

---

## Setup

### 1. WSL2 Memory (Windows only)

Create C:\Users\YOUR_USERNAME\.wslconfig:

    [wsl2]
    memory=4GB
    swap=4GB

Then in PowerShell: wsl --shutdown and reopen Ubuntu.

### 2. ROS2 Humble

Official guide: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html

    sudo apt install ros-humble-desktop ros-dev-tools -y
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    source ~/.bashrc

### 3. Conda Environment

    conda create -n slam_env python=3.10 -y
    conda activate slam_env
    pip install catkin-pkg "numpy==1.26.4" evo
    sudo apt install ros-humble-cv-bridge python3-colcon-common-extensions -y

### 4. ORB-SLAM2 (UCL Fork - OpenCV4 compatible)

WARNING: Deactivate conda before building

    conda deactivate
    sudo apt install cmake build-essential libeigen3-dev libboost-dev \
      libboost-filesystem-dev libblas-dev liblapack-dev libepoxy-dev \
      libopencv-dev libglew-dev mesa-utils libgl1-mesa-glx unzip -y

    git clone https://github.com/UCL/COMP0249_24-25_ORB_SLAM2.git ~/ORB_SLAM2
    cd ~/ORB_SLAM2
    export CMAKE_PREFIX_PATH=/usr/share/eigen3/cmake:$CMAKE_PREFIX_PATH
    ./Build.sh
    echo "export PATH=\$PATH:$HOME/ORB_SLAM2/Install/bin" >> ~/.bashrc
    echo "export CMAKE_PREFIX_PATH=/usr/share/eigen3/cmake:\$CMAKE_PREFIX_PATH" >> ~/.bashrc

WSL2 Notes:
- Disable Pangolin viewer: change true to false in Source/Examples/RGB-D/rgbd_tum.cc System constructor, rebuild
- To re-enable viewer with software rendering: export LIBGL_ALWAYS_SOFTWARE=1 && export DISPLAY=:0
- Add sleep before StopViewer() to keep viewer open long enough to interact

Generate binary vocabulary:

    conda activate slam_env
    cd ~/ORB_SLAM2/Install/var/lib/orbslam2/
    python3 ~/pseudo_rgbd_slam/scripts/convert_vocab.py

### 5. TUM Dataset

    mkdir -p ~/datasets/tum && cd ~/datasets/tum
    wget https://cvg.cit.tum.de/rgbd/dataset/freiburg1/rgbd_dataset_freiburg1_desk.tgz
    tar -xzf rgbd_dataset_freiburg1_desk.tgz
    mkdir -p ~/datasets/pseudo_rgbd/{rgb,depth}

Validate standalone ORB-SLAM2:

    cd ~/datasets/tum/rgbd_dataset_freiburg1_desk
    rgbd_tum TUM1.yaml . ~/ORB_SLAM2/Install/etc/orbslam2/RGB-D/associations/fr1_desk.txt

Expected: 573 frames, New map created with ~946 points, trajectory saved

### 6. Depth Anything V2 (Metric Indoor)

    conda activate slam_env
    git clone https://github.com/DepthAnything/Depth-Anything-V2.git ~/Depth-Anything-V2
    cd ~/Depth-Anything-V2/metric_depth
    pip install -r requirements.txt
    mkdir -p checkpoints && cd checkpoints
    wget "https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-Hypersim-Small/resolve/main/depth_anything_v2_metric_hypersim_vits.pth?download=true" \
      -O depth_anything_v2_metric_hypersim_vits.pth

### 7. Build This Package

    conda activate slam_env
    git clone https://github.com/SKLols/pseudo_rgbd_slam.git
    cd pseudo_rgbd_slam
    colcon build
    source install/setup.bash
    echo "source ~/pseudo_rgbd_slam/install/setup.bash" >> ~/.bashrc

IMPORTANT: In pseudo_rgbd_slam/setup.cfg add under [build_scripts]:
    executable=/home/YOUR_USERNAME/miniconda3/envs/slam_env/bin/python3

---

## Running the Pipeline

    # Single command starts all 3 nodes in correct order
    ros2 launch pseudo_rgbd_slam pipeline.launch.py

Wait for Node A to print "All frames published" (~2 minutes), then run ORB-SLAM2:

    cd ~/datasets/pseudo_rgbd

    python3 -c "
    with open('rgb.txt') as f:
        rgb_lines = [l.strip() for l in f if l.strip()]
    with open('depth.txt') as f:
        depth_lines = [l.strip() for l in f if l.strip()]
    with open('associations.txt', 'w') as f:
        for r, d in zip(rgb_lines, depth_lines):
            f.write(r + ' ' + d + '\n')
    print(f'Generated {len(rgb_lines)} associations')
    "

    rgbd_tum TUM1.yaml . associations.txt

---

## Evaluate Trajectory Accuracy (ATE)

    cd ~/datasets/pseudo_rgbd
    evo_ape tum ~/datasets/tum/rgbd_dataset_freiburg1_desk/groundtruth.txt \
        CameraTrajectory.txt --align --correct_scale --plot --verbose

---

## Visualize Results

    # Trajectory comparison plot
    python3 ~/pseudo_rgbd_slam/scripts/plot_trajectory.py

    # Live feed during pipeline
    ros2 run rviz2 rviz2
    # Add: Image(/camera/rgb/image_raw), Image(/camera/depth/image_raw), Path(/slam/trajectory)

    # Pangolin 3D viewer (after pipeline, on saved data)
    export LIBGL_ALWAYS_SOFTWARE=1
    export DISPLAY=:0
    cd ~/datasets/pseudo_rgbd
    rgbd_tum TUM1.yaml . associations.txt

---

## Performance

| Component | Hardware | FPS |
|-----------|----------|-----|
| Node A (dataset reader) | Any | 8 FPS |
| Node B (depth inference) | GPU 2GB+ | ~8 FPS |
| Node B (depth inference) | CPU only | ~2 FPS |
| ORB-SLAM2 | Any CPU | ~50 FPS capable |

Bottleneck: Node B depth inference. Pipeline designed at 8fps to match.

---

## Known Issues

| Issue | Fix |
|-------|-----|
| OpenCV 4 build errors | Use UCL fork, not original ORB-SLAM2 |
| Pangolin segfault WSL2 | export LIBGL_ALWAYS_SOFTWARE=1 before running |
| No module named torch | Fix shebang in setup.cfg to use conda Python |
| numpy/cv_bridge conflict | pip uninstall opencv-python && pip install numpy==1.26.4 |
| Eigen3 not found | export CMAKE_PREFIX_PATH=/usr/share/eigen3/cmake |
| OOM during C++ build | Set WSL2 memory=4GB swap=4GB in .wslconfig |
| Only ~67% frames synced | Increase sync queue size in node_c_slam.cpp |

---

## Repository Structure

    pseudo_rgbd_slam/
    ├── README.md
    ├── results/
    │   ├── trajectory.png
    │   └── trajectory_comparison.png
    ├── scripts/
    │   ├── convert_vocab.py        # Convert ORB vocabulary txt -> bin
    │   └── plot_trajectory.py      # Plot trajectory comparison
    ├── pseudo_rgbd_slam/           # Python ROS2 package (Node A + B)
    │   ├── launch/
    │   │   └── pipeline.launch.py
    │   └── pseudo_rgbd_slam/
    │       ├── node_a_broadcaster.py
    │       └── node_b_depth_estimator.py
    └── pseudo_rgbd_slam_cpp/       # C++ ROS2 package (Node C)
        └── src/
            └── node_c_slam.cpp

---

## Progress

- [x] Phase 1: ORB-SLAM2 standalone on TUM fr1/desk (573 frames, 573 poses)
- [x] Phase 2: Node A - RGB broadcaster (613 frames at 8fps)
- [x] Phase 3: Node B - Depth Anything V2 metric (~8fps GPU)
- [x] Phase 4: Node C - Synchronized RGB+Depth saver (C++ ROS2)
- [x] Phase 5: Launch file - single command pipeline
- [x] Phase 6: Results - 411 frames, 198 poses, ATE RMSE=6.15cm
- [x] Phase 7: Pangolin viewer working (software OpenGL on WSL2)
- [x] Phase 8: Report generated with ATE evaluation
- [ ] Phase 9: Screen recording
