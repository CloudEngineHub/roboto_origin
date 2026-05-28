#ifndef IOTINIT_H
#define IOTINIT_H

#include <rclcpp/rclcpp.hpp>
#include <iostream>
#include <serial/serial.h>

#include "../utils/nutils.h"
#include "../utils/init_serial.h"
#include "../utils/nlink_protocol.h"
#include "../utils/nlink_unpack/nlink_utils.h"
#include "../utils/protocol_extracter/nprotocol_extracter.h"
#include "../utils/nlink_unpack/nlink_iot_frame0.h"

#include <nlink_message/msg/iot_frame0.hpp>

namespace iot
{
    class Init : public Nutils
    {
    public:
        explicit Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial);

    private:
        void initFrame0(NProtocolExtracter *protocol_extraction);

        rclcpp::Publisher<nlink_message::msg::IotFrame0>::SharedPtr pub_iot_frame0_;
    };
} // namespace iot end

#endif
