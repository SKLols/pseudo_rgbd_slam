#include "rclcpp/rclcpp.hpp"

class PseudoSLAM : public rclcpp::Node
{
    public:
        PseudoSLAM() : Node("node_c_slam")
        {
            RCLCPP_INFO(this->get_logger(), "Node C started");
        }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc,argv);
    auto node = std::make_shared<PseudoSLAM>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}