#include "init.h"

class NLTAoa_ProtocolNodeFrame0 : public NLinkProtocolVLength
{
public:
    NLTAoa_ProtocolNodeFrame0() : NLinkProtocolVLength(
                                      true, g_nltaoa_nodeframe0.fixed_part_size, {g_nltaoa_nodeframe0.frame_header, g_nltaoa_nodeframe0.function_mark})
    {
    }
    void UnpackFrameData(const uint8_t *data) override
    {
        g_nltaoa_nodeframe0.UnpackData(data, length());
    }
};

namespace linktrack_aoa
{
    aoanodeframe0 g_msg_aoa_nodeframe0;
    nodeframe0 g_msg_nodeframe0;
    nodeframe6 g_msg_nodeframe6;
    nodeframe7 g_msg_nodeframe7;

    Init::Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial) : Nutils(serial, protocol_extraction, "linktrack_aoa_ros2")
    {
        rclcpp::QoS qos(rclcpp::KeepLast(200));
        pub_aoa_node_frame0_ = this->create_publisher<aoanodeframe0>("nlink_linktrack_aoa_nodeframe0", qos);
        pub_node_frame0_ = this->create_publisher<nodeframe0>("nlink_linktrack_nodeframe0", qos);
        pub_node_frame6_ = this->create_publisher<nodeframe6>("nlink_linktrack_nodeframe6", qos);
        pub_node_frame7_ = this->create_publisher<nodeframe7>("nlink_linktrack_nodeframe7", qos);

        initDataTransmission();
        initAoaNodeFrame0(protocol_extraction);
        initNodeFrame0(protocol_extraction);
        initNodeFrame6(protocol_extraction);
        initNodeFrame7(protocol_extraction);

        RCLCPP_INFO(this->get_logger(), "LinkTrack-AOA init OK");
    }

    void Init::initDataTransmission(void)
    {
        auto DT_callback = [this](const std_msgs::msg::String::SharedPtr msg) -> void
        {
            if (serial_)
            {
                serial_->write(msg->data);
            }
        };
        sub_dt_ = this->create_subscription<std_msgs::msg::String>("nlink_linktrack_data_transmission", 1000, DT_callback);
    }

    void Init::initAoaNodeFrame0(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLTAoa_ProtocolNodeFrame0;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nltaoa_nodeframe0.result;
                                            auto &msg_data = g_msg_aoa_nodeframe0;
                                            auto &msg_nodes = msg_data.nodes;

                                            msg_data.role = data.role;
                                            msg_data.id = data.id;
                                            msg_data.local_time = data.local_time;
                                            msg_data.system_time = data.system_time;
                                            msg_data.voltage = data.voltage;

                                            msg_nodes.resize(data.valid_node_count);
                                            for (size_t i = 0; i < data.valid_node_count; ++i)
                                            {
                                                auto &msg_node = msg_nodes[i];
                                                auto node = data.nodes[i];
                                                msg_node.id = node->id;
                                                msg_node.role = node->role;
                                                msg_node.dis = node->dis;
                                                msg_node.angle = node->angle;
                                                msg_node.fp_rssi = node->fp_rssi;
                                                msg_node.rx_rssi = node->rx_rssi;
                                            } 
                                            pub_aoa_node_frame0_->publish(msg_data); });
    }

    void Init::initNodeFrame0(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame0;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe0.result;
                                            auto &msg_data = g_msg_nodeframe0;
                                            auto &msg_nodes = msg_data.nodes;

                                            msg_data.role = data.role;
                                            msg_data.id = data.id;

                                            msg_nodes.resize(data.valid_node_count);
                                            for (size_t i = 0; i < data.valid_node_count; ++i) 
                                            {
                                                auto &msg_node = msg_nodes[i];
                                                auto node = data.nodes[i];
                                                msg_node.id = node->id;
                                                msg_node.role = node->role;
                                                msg_node.data.resize(node->data_length);
                                                memcpy(msg_node.data.data(), node->data, node->data_length);
                                            }

                                            pub_node_frame0_->publish(msg_data); });
    }

    void Init::initNodeFrame6(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame6;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe6.result;
                                            auto &msg_data = g_msg_nodeframe6;
                                            auto &msg_nodes = msg_data.nodes;

                                            msg_data.role = data.role;
                                            msg_data.id = data.id;

                                            msg_nodes.resize(data.valid_node_count);
                                            for (size_t i = 0; i < data.valid_node_count; ++i) 
                                            {
                                                auto &msg_node = msg_nodes[i];
                                                auto node = data.nodes[i];
                                                msg_node.id = node->id;
                                                msg_node.role = node->role;
                                                msg_node.data.resize(node->data_length);
                                                memcpy(msg_node.data.data(), node->data, node->data_length);
                                            }

                                            pub_node_frame6_->publish(msg_data); });
    }

    void Init::initNodeFrame7(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame7;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe7.result;
                                            auto &msg_data = g_msg_nodeframe7;
                                            auto &msg_nodes = msg_data.nodes;

                                            msg_data.role = data.role;
                                            msg_data.id = data.id;
                                            msg_data.local_time = data.local_time;
                                            msg_data.system_time = data.system_time;
                                            msg_data.voltage = data.voltage;

                                            msg_nodes.resize(data.valid_node_count);
                                            for (size_t i = 0; i < data.valid_node_count; ++i) 
                                            {
                                                auto &msg_node = msg_nodes[i];
                                                auto node = data.nodes[i];
                                                msg_node.id = node->id;
                                                msg_node.role = node->role;
                                                msg_node.dis = node->dis;
                                                msg_node.angle0 = node->angle0;
                                                msg_node.angle1 = node->angle1;
                                                msg_node.fp_rssi = node->fp_rssi;
                                                msg_node.rx_rssi = node->rx_rssi;
                                            }

                                            pub_node_frame7_->publish(msg_data); });
    }

} // namespace linktrack_aoa end