#include "rclcpp/rclcpp.hpp"
#include "message_filters/subscriber.h"
#include "message_filters/sync_policies/approximate_time.h"
#include "message_filters/synchronizer.h"
#include "sensor_msgs/msg/image.hpp"

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
        }

        void callback(
            const sensor_msgs::msg::Image::SharedPtr rgb_msg,
            const sensor_msgs::msg::Image::SharedPtr depth_msg
        )
        {
            RCLCPP_INFO(this->get_logger(), "Recieved synchronized RGB + Depth");
        }

    private:
        message_filters::Subscriber<sensor_msgs::msg::Image> rgb_sub_;
        message_filters::Subscriber<sensor_msgs::msg::Image> depth_sub_;

        typedef message_filters::sync_policies::ApproximateTime<
            sensor_msgs::msg::Image,
            sensor_msgs::msg::Image> SyncPolicy;

        std::shared_ptr<message_filters::Synchronizer<SyncPolicy>> sync_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc,argv);
    auto node = std::make_shared<PseudoSLAM>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}