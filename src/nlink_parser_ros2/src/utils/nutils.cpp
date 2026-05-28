#include "nutils.h"

Nutils::Nutils(serial::Serial *serial, NProtocolExtracter *protocol_extraction, const std::string &node_name) : Serial_Base(serial, protocol_extraction, node_name)
{
}
void Nutils::TopicAdvertisedTip(const char *topic)
{
  RCLCPP_INFO(this->get_logger(), "%s has been advertised,use 'rostopic "
                                  "echo /%s' to view the data",
              topic, topic);
}
