#ifndef NUTILS_H
#define NUTILS_H
#include <rclcpp/rclcpp.hpp>

#include "init_serial.h"

class Nutils : public Serial_Base
{
public:
    Nutils(serial::Serial *serial, NProtocolExtracter *protocol_extraction, const std::string &node_name);

    void TopicAdvertisedTip(const char *topic);

private:
};

#endif // NUTILS_H
