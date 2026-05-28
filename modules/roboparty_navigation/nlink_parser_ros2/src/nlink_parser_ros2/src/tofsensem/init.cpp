#include "init.h"

class ProtocolFrame0 : public NLinkProtocolVLength
{
public:
    ProtocolFrame0()
        : NLinkProtocolVLength(
              true, g_ntsm_frame0.fixed_part_size,
              {g_ntsm_frame0.frame_header, g_ntsm_frame0.function_mark}) {}

protected:
    bool UpdateLength(const uint8_t *data, size_t available_bytes) override
    {
        if (available_bytes < g_ntsm_frame0.fixed_part_size)
            return false;
        return set_length(tofm_frame0_size(data));
    }
    void UnpackFrameData(const uint8_t *data) override
    {
        g_ntsm_frame0.UnpackData(data, length());
    }
};

namespace tofsensem
{
    nlink_message::msg::TofsenseMFrame0 g_mgs_tofmframe0;

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

    Init::Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial) : Nutils(serial, protocol_extraction, "TOFSensem_ros2")
    {
        protocol_extraction_ = protocol_extraction;
        is_inquire_mode_ = this->declare_parameter("is_inquire_mode", false);
        if (is_inquire_mode_)
        {
            publisher_cascade_ = this->create_publisher<nlink_message::msg::TofsenseMCascade>("nlink_tofsensem_cacade", 50);
        }
        else
        {
            publisher_ = this->create_publisher<nlink_message::msg::TofsenseMFrame0>("nlink_tofsensem_frame0", 50);
        }

        InitFrame0();

        RCLCPP_INFO(this->get_logger(), "TOFSenseM init OK");
    }

    void Init::InitFrame0()
    {
        static auto protocol_farme0_ = new ProtocolFrame0;
        this->protocol_extraction_->AddProtocol(protocol_farme0_);
        protocol_farme0_->SetHandleDataCallback([=]
                                                {
                                                    const auto &data = g_ntsm_frame0;

                                                    g_mgs_tofmframe0.id = data.id;
                                                    g_mgs_tofmframe0.system_time = data.system_time;
                                                    g_mgs_tofmframe0.pixels.resize(data.pixel_count);
                                                    for (int i = 0; i < data.pixel_count; ++i)
                                                    {
                                                        const auto &src_pixel = data.pixels[i];
                                                        auto &pixel = g_mgs_tofmframe0.pixels[i];
                                                        pixel.dis = src_pixel.dis;
                                                        pixel.dis_status = src_pixel.dis_status;
                                                        pixel.signal_strength = src_pixel.signal_strength;
                                                    }

                                                    if (is_inquire_mode_)
                                                    {
                                                        frame0_map_[data.id] = g_mgs_tofmframe0;
                                                    }
                                                    else
                                                    {
                                                        publisher_->publish(g_mgs_tofmframe0);
                                                    } });
        if (is_inquire_mode_)
        {
            timer_scan_ = this->create_wall_timer(std::chrono::milliseconds(int(timer_scan_interval_)), [=]
                                                    { 
                                                    if (node_index_ >= 8)
                                                    {
                                                        if (!frame0_map_.empty())
                                                        {
                                                            nlink_message::msg::TofsenseMCascade msg_cascade;
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

} // namespace tofsensem
