import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ubuntu2204/pseudo_rgbd_slam/install/pseudo_rgbd_slam'
