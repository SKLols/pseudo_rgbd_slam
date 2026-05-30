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

#include "nav_msgs/msg/path.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"

class PseudoSLAM : public rclcpp::Node
{
    public:
        PseudoSLAM() : Node("node_c_slam")
        {
            RCLCPP_INFO(this->get_logger(), "Node C started");
            rgb_sub_.subscribe(this, "/camera/rgb/image_raw");
            depth_sub_.subscribe(this, "/camera/depth/image_raw");
            
            sync_ = std::make_shared<message_filters::Synchronizer<SyncPolicy>>(
                SyncPolicy(50), rgb_sub_, depth_sub_);
            sync_->registerCallback(&PseudoSLAM::callback,this);

            output_path_ = "/home/ubuntu2204/datasets/pseudo_rgbd";
            rgb_txt_.open(output_path_ + "/rgb.txt", std::ios::trunc);
            depth_txt_.open(output_path_ + "/depth.txt", std::ios::trunc);
            frame_count_ = 0;

            path_pub_ = this->create_publisher<nav_msgs::msg::Path>("/slam/trajectory", 10);
            path_.header.frame_id = "map";
        }

        ~PseudoSLAM()
        {
            rgb_txt_.close();
            depth_txt_.close();
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

            // Convert to cv::Mat
            cv_bridge::CvImagePtr rgb_cv = cv_bridge::toCvCopy(rgb_msg, "bgr8");
            cv_bridge::CvImagePtr depth_cv = cv_bridge::toCvCopy(depth_msg, "32FC1");

            // Create filename from timestamp
            std::ostringstream ss;
            ss << std::fixed << std::setprecision(6) << timestamp;
            std::string ts_str = ss.str();

            // Save images
            std::string rgb_path = output_path_ + "/rgb/" + ts_str + ".png";
            std::string depth_path = output_path_ + "/depth/" + ts_str + ".png";
    
            cv::imwrite(rgb_path, rgb_cv->image);
            cv::Mat depth_16bit;
            depth_cv->image.convertTo(depth_16bit, CV_16U, 5000.0);
            cv::imwrite(depth_path, depth_16bit);

            // Write to txt files
            rgb_txt_ << ts_str << " rgb/" << ts_str << ".png\n";
            rgb_txt_.flush();
            depth_txt_ << ts_str << " depth/" << ts_str << ".png\n";
            depth_txt_.flush();
    
            frame_count_++;
            RCLCPP_INFO(this->get_logger(), "Saved frame %d: %s", frame_count_, ts_str.c_str());

            geometry_msgs::msg::PoseStamped pose;
            pose.header.stamp = rgb_msg->header.stamp;
            pose.header.frame_id = "map";
            pose.pose.position.x = timestamp; // placeholder
            path_.poses.push_back(pose);
            path_.header.stamp = rgb_msg->header.stamp;
            path_pub_->publish(path_);
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

        rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr path_pub_;
        nav_msgs::msg::Path path_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc,argv);
    auto node = std::make_shared<PseudoSLAM>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}