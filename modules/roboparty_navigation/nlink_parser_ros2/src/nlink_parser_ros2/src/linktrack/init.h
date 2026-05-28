#ifndef LINKTRACKINIT_H
#define LINKTRACKINIT_H

#include <rclcpp/rclcpp.hpp>
#include <iostream>
#include <serial/serial.h>
#include <std_msgs/msg/string.hpp>

#include "protocols.h"

#include "../utils/nutils.h"
#include "../utils/init_serial.h"
#include "../utils/nlink_protocol.h"
#include "../utils/nlink_unpack/nlink_utils.h"
#include "../utils/protocol_extracter/nprotocol_extracter.h"

#include <nlink_message/msg/linktrack_anchorframe0.hpp>
#include <nlink_message/msg/linktrack_nodeframe0.hpp>
#include <nlink_message/msg/linktrack_nodeframe1.hpp>
#include <nlink_message/msg/linktrack_nodeframe2.hpp>
#include <nlink_message/msg/linktrack_nodeframe3.hpp>
#include <nlink_message/msg/linktrack_nodeframe4.hpp>
#include <nlink_message/msg/linktrack_nodeframe5.hpp>
#include <nlink_message/msg/linktrack_nodeframe6.hpp>
#include <nlink_message/msg/linktrack_nodeframe7.hpp>
#include <nlink_message/msg/linktrack_tagframe0.hpp>

using anchorframe0 = nlink_message::msg::LinktrackAnchorframe0;
using tagframe0 = nlink_message::msg::LinktrackTagframe0;
using nodeframe0 = nlink_message::msg::LinktrackNodeframe0;
using nodeframe1 = nlink_message::msg::LinktrackNodeframe1;
using nodeframe2 = nlink_message::msg::LinktrackNodeframe2;
using nodeframe3 = nlink_message::msg::LinktrackNodeframe3;
using nodeframe4 = nlink_message::msg::LinktrackNodeframe4;
using nodeframe5 = nlink_message::msg::LinktrackNodeframe5;
using nodeframe6 = nlink_message::msg::LinktrackNodeframe6;
using nodeframe7 = nlink_message::msg::LinktrackNodeframe7;

class NProtocolExtracter;
namespace linktrack
{
    class Init : public Nutils
    {
    public:
        explicit Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial);

    private:
        void initPubliser(void);
        void initDataTransmission(void);
        void initAnchorFrame0(NProtocolExtracter *protocol_extraction);
        void initTagFrame0(NProtocolExtracter *protocol_extraction);
        void initNodeFrame0(NProtocolExtracter *protocol_extraction);
        void initNodeFrame1(NProtocolExtracter *protocol_extraction);
        void initNodeFrame2(NProtocolExtracter *protocol_extraction);
        void initNodeFrame3(NProtocolExtracter *protocol_extraction);
        void initNodeFrame4(NProtocolExtracter *protocol_extraction);
        void initNodeFrame5(NProtocolExtracter *protocol_extraction);
        void initNodeFrame6(NProtocolExtracter *protocol_extraction);
        void initNodeFrame7(NProtocolExtracter *protocol_extraction);

        rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_dt_;

        rclcpp::Publisher<anchorframe0>::SharedPtr pub_anchor_frame0_;
        rclcpp::Publisher<tagframe0>::SharedPtr pub_tag_frame0_;
        rclcpp::Publisher<nodeframe0>::SharedPtr pub_node_frame0_;
        rclcpp::Publisher<nodeframe1>::SharedPtr pub_node_frame1_;
        rclcpp::Publisher<nodeframe2>::SharedPtr pub_node_frame2_;
        rclcpp::Publisher<nodeframe3>::SharedPtr pub_node_frame3_;
        rclcpp::Publisher<nodeframe4>::SharedPtr pub_node_frame4_;
        rclcpp::Publisher<nodeframe5>::SharedPtr pub_node_frame5_;
        rclcpp::Publisher<nodeframe6>::SharedPtr pub_node_frame6_;
        rclcpp::Publisher<nodeframe7>::SharedPtr pub_node_frame7_;
    };
} // namespace linktrack end

#endif
