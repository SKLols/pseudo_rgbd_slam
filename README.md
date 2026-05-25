# Pseudo RGB-D SLAM

Replaces a physical depth sensor with Depth Anything V2 (neural network) to run ORB-SLAM2 RGB-D SLAM using only an RGB camera.

## Architecture

    Node A (Python)    →    Node B (Python)    →    Node C (C++)
    TUM Dataset             Depth Anything V2        ORB-SLAM2
    Broadcaster             Metric Estimator         RGB-D SLAM

    /camera/rgb/image_raw → /camera/depth/image_raw → /slam/camera_pose

## System Requirements

- Ubuntu 22.04 LTS (tested on WSL2)
- ROS2 Humble
- Python 3.10 (conda)
- NVIDIA GPU 2GB+ (optional, CPU works at ~2fps)

---

## Setup

### 1. ROS2 Humble
Follow official guide: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html

    sudo apt install ros-humble-desktop ros-dev-tools -y
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

### 2. Conda Environment

    conda create -n slam_env python=3.10 -y
    conda activate slam_env
    pip install catkin-pkg "numpy==1.26.4"
    sudo apt install ros-humble-cv-bridge python3-colcon-common-extensions -y

### 3. ORB-SLAM2

WARNING: Deactivate conda before building ORB-SLAM2

    conda deactivate
    sudo apt install cmake build-essential libeigen3-dev libboost-dev libboost-filesystem-dev libblas-dev liblapack-dev libepoxy-dev libopencv-dev libglew-dev mesa-utils libgl1-mesa-glx unzip -y
    git clone https://github.com/UCL/COMP0249_24-25_ORB_SLAM2.git ~/ORB_SLAM2
    cd ~/ORB_SLAM2
    export CMAKE_PREFIX_PATH=/usr/share/eigen3/cmake:$CMAKE_PREFIX_PATH
    ./Build.sh
    echo "export PATH=\$PATH:$HOME/ORB_SLAM2/Install/bin" >> ~/.bashrc
    echo "export CMAKE_PREFIX_PATH=/usr/share/eigen3/cmake:\$CMAKE_PREFIX_PATH" >> ~/.bashrc

WSL2 Note: Pangolin viewer causes segfault. Disable it by changing true to false
in Source/Examples/RGB-D/rgbd_tum.cc System constructor, then rebuild.

Generate binary vocabulary:

    conda activate slam_env
    cd ~/ORB_SLAM2/Install/var/lib/orbslam2/
    python3 ~/pseudo_rgbd_slam/scripts/convert_vocab.py

### 4. TUM Dataset

    mkdir -p ~/datasets/tum && cd ~/datasets/tum
    wget https://cvg.cit.tum.de/rgbd/dataset/freiburg1/rgbd_dataset_freiburg1_desk.tgz
    tar -xzf rgbd_dataset_freiburg1_desk.tgz

Validate ORB-SLAM2 works standalone:

    cd ~/datasets/tum/rgbd_dataset_freiburg1_desk
    rgbd_tum TUM1.yaml . ~/ORB_SLAM2/Install/etc/orbslam2/RGB-D/associations/fr1_desk.txt

### 5. Depth Anything V2

    git clone https://github.com/DepthAnything/Depth-Anything-V2.git ~/Depth-Anything-V2
    cd ~/Depth-Anything-V2/metric_depth
    pip install -r requirements.txt
    mkdir -p checkpoints && cd checkpoints
    wget "https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-Hypersim-Small/resolve/main/depth_anything_v2_metric_hypersim_vits.pth?download=true" -O depth_anything_v2_metric_hypersim_vits.pth

### 6. Build This Package

    conda activate slam_env
    git clone https://github.com/SKLols/pseudo_rgbd_slam.git
    cd pseudo_rgbd_slam
    colcon build
    source install/setup.bash
    echo "source ~/pseudo_rgbd_slam/install/setup.bash" >> ~/.bashrc

NOTE: In pseudo_rgbd_slam/setup.cfg add under [build_scripts]:
executable=/home/YOUR_USERNAME/miniconda3/envs/slam_env/bin/python3

---

## Running

    # Terminal 1 - Node B first (model takes ~5s to load)
    ros2 run pseudo_rgbd_slam node_b_depth_estimator

    # Terminal 2 - After Node B prints "Model loaded successfully"
    ros2 run pseudo_rgbd_slam node_a_broadcaster

    # Terminal 3 - Verify
    ros2 topic list
    ros2 topic hz /camera/depth/image_raw

---

## Known Issues

| Issue | Fix |
|-------|-----|
| OpenCV 4 build errors | Use UCL fork, not original ORB-SLAM2 |
| Pangolin segfault on WSL2 | Disable viewer in source, recompile |
| No module named torch | Fix shebang in setup.cfg to use conda Python |
| numpy/cv_bridge conflict | pip uninstall opencv-python and pip install numpy==1.26.4 |
| Eigen3 not found by cmake | export CMAKE_PREFIX_PATH=/usr/share/eigen3/cmake |

---

## Progress

- [x] Phase 1: ORB-SLAM2 standalone on TUM fr1/desk
- [x] Phase 2: Node A - RGB broadcaster (613 frames, 30fps)
- [x] Phase 3: Node B - Depth Anything V2 (~8fps GPU)
- [ ] Phase 4: Node C - ORB-SLAM2 C++ ROS2 node
- [ ] Phase 5: Launch file + full pipeline
- [ ] Phase 6: Report + screen recording
