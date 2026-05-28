#ifndef INIT_SERIAL_H
#define INIT_SERIAL_H

#include <serial/serial.h>
#include <rclcpp/rclcpp.hpp>
#include "protocol_extracter/nprotocol_extracter.h"

class Serial_Base : public rclcpp::Node
{
public:
    explicit Serial_Base(serial::Serial *serial, NProtocolExtracter *protocol_extraction, const std::string &node_name);

    void Start();

    serial::Serial *serial_;

private:
    void serial_Init();

    NProtocolExtracter *protocol_extraction_;
    rclcpp::TimerBase::SharedPtr serial_timer_read_;
};

#endif
