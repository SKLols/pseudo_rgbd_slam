import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class RGBBrodcaster ( Node ):
    def __init__(self):
        super().__init__('node_a_broadcaster')
        self.get_logger().info('Node A started')

def main (args = None):
    rclpy.init(args=args)
    node = RGBBrodcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()