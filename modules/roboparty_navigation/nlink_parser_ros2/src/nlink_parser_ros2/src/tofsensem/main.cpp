#include "init.h"

int main(int argc, char const *argv[])
{
  rclcpp::init(argc, argv);
  serial::Serial serial;
  NProtocolExtracter protocol_extraction;

  auto tofmNode = std::make_shared<tofsensem::Init>(&protocol_extraction, &serial);

  rclcpp::spin(tofmNode);
  rclcpp::shutdown();
  return 0;
}
