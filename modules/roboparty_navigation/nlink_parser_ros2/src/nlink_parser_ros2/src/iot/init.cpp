#include "init.h"

class NLT_ProtocolIotFrame0 : public NLinkProtocolVLength
{
public:
    NLT_ProtocolIotFrame0() : NLinkProtocolVLength(
                                  true, g_iot_frame0.fixed_part_size, {g_iot_frame0.frame_header, g_iot_frame0.function_mark})
    {
    }
    void UnpackFrameData(const uint8_t *data) override
    {
        g_iot_frame0.UnpackData(data, length());
    }
};
namespace iot
{
    nlink_message::msg::IotFrame0 g_msg_iotframe0;

    Init::Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial) : Nutils(serial, protocol_extraction, "linktrack_aoa_ros2")
    {
        rclcpp::QoS qos(rclcpp::KeepLast(200));
        pub_iot_frame0_ = this->create_publisher<nlink_message::msg::IotFrame0>("nlink_iot_frame0", qos);
        initFrame0(protocol_extraction);
    }
    void Init::initFrame0(NProtocolExtracter *protocol_extraction)
    {
        static auto protocol = new NLT_ProtocolIotFrame0;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_iot_frame0;
                                            g_msg_iotframe0.uid = data.uid;
                                            g_msg_iotframe0.system_time = data.system_time;
                                            g_msg_iotframe0.io_status = *(const uint8_t *)&(data.io_status);
                                            g_msg_iotframe0.nodes.resize(data.node_count);
                                            for (int i = 0; i < data.node_count; ++i) 
                                            {
                                                auto &dst = g_msg_iotframe0.nodes[i];
                                                const auto &src = data.nodes[i];
                                                dst.uid = src.uid;
                                                dst.dis = src.dis;
                                                dst.aoa_angle_horizontal = src.aoa_angle_horizontal;
                                                dst.aoa_angle_vertical = src.aoa_angle_vertical;
                                                dst.fp_rssi = src.fp_rssi;
                                                dst.rx_rssi = src.rx_rssi;
                                                dst.user_data.clear();
                                                dst.user_data.insert(dst.user_data.begin(), src.user_data,
                                                                    src.user_data + src.user_data_len);
                                            }

                                            pub_iot_frame0_->publish(g_msg_iotframe0); });
    }
} // namespace iot end