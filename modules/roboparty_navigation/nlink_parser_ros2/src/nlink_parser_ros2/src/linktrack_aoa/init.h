#ifndef LINKTRACKAOAINIT_H
#define LINKTRACKAOAINIT_H

#include <rclcpp/rclcpp.hpp>
#include <iostream>
#include <serial/serial.h>
#include <std_msgs/msg/string.hpp>

#include "../linktrack/protocols.h"
#include "../utils/nutils.h"
#include "../utils/init_serial.h"
#include "../utils/nlink_protocol.h"
#include "../utils/nlink_unpack/nlink_utils.h"
#include "../utils/protocol_extracter/nprotocol_extracter.h"
#include "../utils/nlink_unpack/nlink_linktrack_aoa_nodeframe0.h"

#include <nlink_message/msg/linktrack_aoa_nodeframe0.hpp>
#include <nlink_message/msg/linktrack_nodeframe0.hpp>
#include <nlink_message/msg/linktrack_nodeframe6.hpp>
#include <nlink_message/msg/linktrack_nodeframe7.hpp>

using aoanodeframe0 = nlink_message::msg::LinktrackAoaNodeframe0;
using nodeframe0 = nlink_message::msg::LinktrackNodeframe0;
using nodeframe6 = nlink_message::msg::LinktrackNodeframe6;
using nodeframe7 = nlink_message::msg::LinktrackNodeframe7;

namespace linktrack_aoa
{
    class Init : public Nutils
    {
    public:
        explicit Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial);

    private:
        void initDataTransmission(void);
        void initAoaNodeFrame0(NProtocolExtracter *protocol_extraction);
        void initNodeFrame0(NProtocolExtracter *protocol_extraction);
        void initNodeFrame6(NProtocolExtracter *protocol_extraction);
        void initNodeFrame7(NProtocolExtracter *protocol_extraction);

        rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_dt_;

        rclcpp::Publisher<aoanodeframe0>::SharedPtr pub_aoa_node_frame0_;
        rclcpp::Publisher<nodeframe0>::SharedPtr pub_node_frame0_;
        rclcpp::Publisher<nodeframe6>::SharedPtr pub_node_frame6_;
        rclcpp::Publisher<nodeframe7>::SharedPtr pub_node_frame7_;
    };
} // namespace linktrack_aoa end

#endif
