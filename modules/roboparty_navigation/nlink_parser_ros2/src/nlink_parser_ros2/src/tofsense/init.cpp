#include "init.h"

class NTS_ProtocolFrame0 : public NLinkProtocol
{
public:
    NTS_ProtocolFrame0() : NLinkProtocol(true, g_nts_frame0.fixed_part_size,
                                         {g_nts_frame0.frame_header, g_nts_frame0.function_mark})
    {
    }

protected:
    void UnpackFrameData(const uint8_t *data) override
    {
        g_nts_frame0.UnpackData(data, length());
    }
};

namespace tofsense
{
    nlink_message::msg::TofsenseFrame0 g_mgs_frame0;

#pragma pack(push, 1)
    struct
    {
        char header[2]{0x57, 0x10};
        uint8_t reserved0[2]{0xff, 0xff};
        uint8_t id{};
        uint8_t reserved1[2]{0xff, 0xff};
        uint8_t checkSum{};
    } g_command_read;
#pragma pack(pop)

    Init::Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial) : Nutils(serial, protocol_extraction, "TOFSense_ros2")
    {
        protocol_extraction_ = protocol_extraction;
        is_inquire_mode_ = this->declare_parameter("is_inquire_mode", false);
        if (is_inquire_mode_)
        {
            publisher_cascade_ = this->create_publisher<nlink_message::msg::TofsenseCascade>("nlink_tofsense_cacade", 50);
        }
        else
        {
            publisher_ = this->create_publisher<nlink_message::msg::TofsenseFrame0>("nlink_tofsense_frame0", 50);
        }
        InitFrame0();

        RCLCPP_INFO(this->get_logger(), "TOFSense init OK");
    }

    void Init::InitFrame0(void)
    {
        static auto protocol_farme0_ = new NTS_ProtocolFrame0;
        this->protocol_extraction_->AddProtocol(protocol_farme0_);
        protocol_farme0_->SetHandleDataCallback([=]
                                                {
                                                    const auto &data = g_nts_frame0.result;

                                                    g_mgs_frame0.id = data.id;
                                                    g_mgs_frame0.system_time = data.system_time;
                                                    g_mgs_frame0.dis = data.dis;
                                                    g_mgs_frame0.dis_status = data.dis_status;
                                                    g_mgs_frame0.signal_strength = data.signal_strength;
                                                    g_mgs_frame0.range_precision = data.range_precision; 
                                                    
                                                    if (is_inquire_mode_)
                                                    {
                                                        frame0_map_[data.id] = g_mgs_frame0;
                                                    }
                                                    else
                                                    {
                                                        publisher_->publish(g_mgs_frame0);
                                                    } });
        if (is_inquire_mode_)
        {
            timer_scan_ = this->create_wall_timer(std::chrono::milliseconds(int(timer_scan_interval_)), [=]
                                                { 
                                                    if (node_index_ >= 8)
                                                    {
                                                        if (!frame0_map_.empty())
                                                        {
                                                            nlink_message::msg::TofsenseCascade msg_cascade;
                                                            for (const auto &msg : frame0_map_)
                                                            {
                                                                msg_cascade.nodes.push_back(msg.second);
                                                            }
                                                            publisher_cascade_->publish(msg_cascade);
                                                        }
                                                        node_index_ = 0; 
                                                        frame0_map_.clear();
                                                    }
                                                    else
                                                    {
                                                        g_command_read.id = node_index_;
                                                        auto data = reinterpret_cast<uint8_t *>(&g_command_read);
                                                        NLink_UpdateCheckSum(data, sizeof(g_command_read));
                                                        if (serial_)
                                                        {
                                                            serial_->write(data, sizeof(g_command_read));
                                                        }
                                                        ++node_index_;
                                                    } });
        }
    }

} // namespace tofsense
