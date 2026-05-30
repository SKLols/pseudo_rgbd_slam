#include "rclcpp/rclcpp.hpp"
#include "message_filters/subscriber.h"
#include "message_filters/sync_policies/approximate_time.h"
#include "message_filters/synchronizer.h"
#include "sensor_msgs/msg/image.hpp"

#include "cv_bridge/cv_bridge.h"
#include "opencv2/opencv.hpp"

#include <fstream>
#include <sstream>
#include <iomanip>

class PseudoSLAM : public rclcpp::Node
{
    public:
        PseudoSLAM() : Node("node_c_slam")
        {
            RCLCPP_INFO(this->get_logger(), "Node C started");
            rgb_sub_.subscribe(this, "/camera/rgb/image_raw");
            depth_sub_.subscribe(this, "/camera/depth/image_raw");
            
            sync_ = std::make_shared<message_filters::Synchronizer<SyncPolicy>>(
                SyncPolicy(10), rgb_sub_, depth_sub_);
            sync_->registerCallback(&PseudoSLAM::callback,this);

            output_path_ = "/home/ubuntu2204/datasets/pseudo_rgbd";
            rgb_txt_.open(output_path_ + "/rgb.txt");
            depth_txt_.open(output_path_ + "/depth.txt");
            frame_count_ = 0;
        }

        void callback(
            const sensor_msgs::msg::Image::SharedPtr rgb_msg,
            const sensor_msgs::msg::Image::SharedPtr depth_msg
        )
        {
            RCLCPP_INFO(this->get_logger(), "Recieved synchronized RGB + Depth");
            double timestamp = rgb_msg->header.stamp.sec + 
                       rgb_msg->header.stamp.nanosec * 1e-9;
    
            RCLCPP_INFO(this->get_logger(), "Timestamp: %f", timestamp);
        }

    private:
        message_filters::Subscriber<sensor_msgs::msg::Image> rgb_sub_;
        message_filters::Subscriber<sensor_msgs::msg::Image> depth_sub_;

        typedef message_filters::sync_policies::ApproximateTime<
            sensor_msgs::msg::Image,
            sensor_msgs::msg::Image> SyncPolicy;

        std::shared_ptr<message_filters::Synchronizer<SyncPolicy>> sync_;

        std::string output_path_;
        std::ofstream rgb_txt_;
        std::ofstream depth_txt_;
        int frame_count_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc,argv);
    auto node = std::make_shared<PseudoSLAM>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}