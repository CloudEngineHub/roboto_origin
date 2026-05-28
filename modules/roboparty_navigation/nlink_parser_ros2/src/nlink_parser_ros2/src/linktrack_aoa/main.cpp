#include "init.h"

int main(int argc, char const *argv[])
{
    rclcpp::init(argc, argv);
    serial::Serial serial;
    NProtocolExtracter protocol_extraction;

    auto linktrackaoanode = std::make_shared<linktrack_aoa::Init>(&protocol_extraction, &serial);

    rclcpp::spin(linktrackaoanode);
    rclcpp::shutdown();
    return 0;
}
