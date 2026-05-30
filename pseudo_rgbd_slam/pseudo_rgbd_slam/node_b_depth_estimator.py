import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
import torch

import sys
sys.path.insert(0, '/home/ubuntu2204/Depth-Anything-V2/metric_depth')
from depth_anything_v2.dpt import DepthAnythingV2

class DepthEstimator(Node):
    def __init__(self):
        super().__init__('node_b_depth_estimator')
        self.get_logger().info('Node B started')

        #Initialize depth estimation model
        #Set device to GPU if available, otherwise CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.get_logger().info(f'Using device: {self.device}')

        #Model Configuration
        model_configs = {
            'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
            'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
            'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]}
        }

        encoder = 'vits' # or 'vits', 'vitb'
        dataset = 'hypersim' # 'hypersim' for indoor model, 'vkitti' for outdoor model
        max_depth = 20 # 20 for indoor model, 80 for outdoor model

        self.model = DepthAnythingV2(**{**model_configs[encoder], 'max_depth': max_depth})
        self.model.load_state_dict(torch.load('/home/ubuntu2204/Depth-Anything-V2/metric_depth/checkpoints/depth_anything_v2_metric_hypersim_vits.pth', map_location='cpu'))
        self.model = self.model.to(self.device)
        self.model.eval()
        self.get_logger().info('Model loaded successfully')

        #Subscriber
        self.subscription = self.create_subscription(Image, '/camera/rgb/image_raw', self.image_callback, 10)

        self.bridge = CvBridge()

        #Publisher for depth images
        self.depth_publisher = self.create_publisher(Image, '/camera/depth/image_raw', 10)

    def image_callback(self, msg):
        #Convert ROS2 Image message to OpenCV image
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        #Run inference
        depth = self.model.infer_image(cv_image)

        #Convert depth map to ROS Image message and publish
        depth_msg = self.bridge.cv2_to_imgmsg(depth, encoding='32FC1')
        depth_msg.header.stamp = msg.header.stamp  # ADD - copy from RGB
        depth_msg.header.frame_id = 'camera'
        self.depth_publisher.publish(depth_msg)
        self.get_logger().info(f'Depth range: {depth.min():.2f}m - {depth.max():.2f}m')
    
def main(args=None):
    rclpy.init(args=args)
    node = DepthEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()