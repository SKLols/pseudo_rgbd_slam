import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class RGBBrodcaster ( Node ):
    def __init__(self):
        super().__init__('node_a_broadcaster')
        self.dataset_path = '/home/ubuntu2204/datasets/tum/rgbd_dataset_freiburg1_desk'
        self.get_logger().info(f'Path_exists: {os.path.exists(self.dataset_path)}')        
        self.get_logger().info(f'Dataset_path:{self.dataset_path}')

        #Load frames
        self.frame_list = self._load_rgb_list()

        #verify count
        self.get_logger().info(f'Loaded{len(self.frame_list)} frames')

        #print first and last frames to verify order 
        if self.frame_list:
            self.get_logger().info(f'First frame: {self.frame_list[0]}')   
            self.get_logger().info(f'Last frame: {self.frame_list[-1]}')
        
        self.get_logger().info('Node A started')

    def _load_rgb_list(self):
        rgb_txt = os.path.join(self.dataset_path, 'rgb.txt')

        #verify the file exists
        if not os.path.exists(rgb_txt):
            self.get_logger().error(f'File {rgb_txt} does not exist')
            return []
        
        entries = []
        with open(rgb_txt, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                parts = line.split()
                timestamp = parts[0]
                filepath = parts[1]
                entries.append((timestamp, filepath))
        return entries


def main (args = None):
    rclpy.init(args=args)
    node = RGBBrodcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()