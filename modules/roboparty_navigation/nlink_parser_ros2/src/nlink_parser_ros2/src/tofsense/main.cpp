#include "init.h"

int main(int argc, char const *argv[])
{
  rclcpp::init(argc, argv);
  serial::Serial serial;
  NProtocolExtracter protocol_extraction;

  auto tofNode = std::make_shared<tofsense::Init>(&protocol_extraction, &serial);

  rclcpp::spin(tofNode);
  rclcpp::shutdown();
  return 0;
}
