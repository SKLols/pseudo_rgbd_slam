import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
import torch

class DepthEstimator(Node):
    def __init__(self):
        super().__init__('node_b_depth_estimator')
        self.get_logger().info('Node B started')


def main(args=None):
    rclpy.init(args=args)
    node = DepthEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()