#ifndef TOFSENSEMINIT_H
#define TOFSENSEMINIT_H

#include <rclcpp/rclcpp.hpp>
#include <iostream>
#include <serial/serial.h>

#include <map>

#include "../utils/nutils.h"
#include "../utils/init_serial.h"
#include "../utils/nlink_protocol.h"
#include "../utils/nlink_unpack/nlink_utils.h"
#include "../utils/nlink_unpack/nlink_tofsensem_frame0.h"
#include "../utils/protocol_extracter/nprotocol_extracter.h"

#include <nlink_message/msg/tofsense_m_frame0.hpp>
#include <nlink_message/msg/tofsense_m_cascade.hpp>

namespace tofsensem
{
    class Init : public Nutils
    {
    public:
        explicit Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial);

    private:
        void InitFrame0();

        uint8_t node_index_ = 0;
        bool is_inquire_mode_;
        const float timer_scan_interval_ = 10;

        NProtocolExtracter *protocol_extraction_;
        rclcpp::TimerBase::SharedPtr timer_scan_;

        rclcpp::Publisher<nlink_message::msg::TofsenseMFrame0>::SharedPtr publisher_;
        rclcpp::Publisher<nlink_message::msg::TofsenseMCascade>::SharedPtr publisher_cascade_;

        std::map<int, nlink_message::msg::TofsenseMFrame0> frame0_map_;
    };

} // namespace tofsmense

#endif
