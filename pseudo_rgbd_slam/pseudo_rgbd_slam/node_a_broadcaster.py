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

        #Load dataset  
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
        
        self.publisher = self.create_publisher(Image, '/camera/rgb/image_raw', 10)
        self.timer = self.create_timer(1/30, self.timer_callback)
        self.frame_idx = 0

        self.bridge = CvBridge()

    def timer_callback(self):
        if self.frame_idx >= len(self.frame_list):
            self.get_logger().info('All frames published, stopping timer')
            self.timer.cancel()
            return
        
        current_frame = self.frame_list[self.frame_idx]
        timestamp, filepath = current_frame
        absolute_path = os.path.join(self.dataset_path, filepath)

        #read the image using OpenCV
        image = cv2.imread(absolute_path)
        if image is None:
            self.get_logger().error(f'Failed to read image at {absolute_path}')
            self.frame_idx += 1
            return

        #convert to ROS Image message
        msg = self.bridge.cv2_to_imgmsg(image, encoding = 'bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()  # ADD
        msg.header.frame_id = 'camera'

        #publish the message
        self.publisher.publish(msg)
        self.get_logger().info(f'Published frame {self.frame_idx}: {absolute_path}')
        self.frame_idx += 1

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