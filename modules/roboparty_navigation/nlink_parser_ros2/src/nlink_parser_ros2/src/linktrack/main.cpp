#include "init.h"

int main(int argc, char const *argv[])
{
    rclcpp::init(argc, argv);
    serial::Serial serial;
    NProtocolExtracter protocol_extraction;

    auto linktracknode = std::make_shared<linktrack::Init>(&protocol_extraction, &serial);

    rclcpp::spin(linktracknode);
    rclcpp::shutdown();
    return 0;
}
