#include "init.h"

int main(int argc, char const *argv[])
{
    rclcpp::init(argc, argv);
    serial::Serial serial;
    NProtocolExtracter protocol_extraction;

    auto iotnode = std::make_shared<iot::Init>(&protocol_extraction, &serial);

    rclcpp::spin(iotnode);
    rclcpp::shutdown();
    return 0;
}
