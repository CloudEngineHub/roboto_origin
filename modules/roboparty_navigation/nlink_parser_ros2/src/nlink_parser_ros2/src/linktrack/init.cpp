#include "init.h"

#define ARRAY_ASSIGN(DEST, SRC)                                        \
    for (size_t _CNT = 0; _CNT < sizeof(SRC) / sizeof(SRC[0]); ++_CNT) \
    {                                                                  \
        DEST[_CNT] = SRC[_CNT];                                        \
    }

namespace linktrack
{
    anchorframe0 g_msg_anchorframe0;
    tagframe0 g_msg_tagframe0;
    nodeframe0 g_msg_nodeframe0;
    nodeframe1 g_msg_nodeframe1;
    nodeframe2 g_msg_nodeframe2;
    nodeframe3 g_msg_nodeframe3;
    nodeframe4 g_msg_nodeframe4;
    nodeframe5 g_msg_nodeframe5;
    nodeframe6 g_msg_nodeframe6;
    nodeframe7 g_msg_nodeframe7;

    Init::Init(NProtocolExtracter *protocol_extraction, serial::Serial *serial) : Nutils(serial, protocol_extraction, "linktrack_ros2")
    {
        initPubliser();
        initDataTransmission();
        initAnchorFrame0(protocol_extraction);
        initTagFrame0(protocol_extraction);
        initNodeFrame0(protocol_extraction);
        initNodeFrame1(protocol_extraction);
        initNodeFrame2(protocol_extraction);
        initNodeFrame3(protocol_extraction);
        initNodeFrame4(protocol_extraction);
        initNodeFrame5(protocol_extraction);
        initNodeFrame6(protocol_extraction);
        initNodeFrame7(protocol_extraction);

        RCLCPP_INFO(this->get_logger(), "LinkTrack init OK");
    }

    void Init::initPubliser(void)
    {
        rclcpp::QoS qos(rclcpp::KeepLast(200));
        pub_anchor_frame0_ = this->create_publisher<anchorframe0>("nlink_linktrack_anchorframe0", qos);
        pub_tag_frame0_ = this->create_publisher<tagframe0>("nlink_linktrack_tagframe0", qos);
        pub_node_frame0_ = this->create_publisher<nodeframe0>("nlink_linktrack_nodeframe0", qos);
        pub_node_frame1_ = this->create_publisher<nodeframe1>("nlink_linktrack_nodeframe1", qos);
        pub_node_frame2_ = this->create_publisher<nodeframe2>("nlink_linktrack_nodeframe2", qos);
        pub_node_frame3_ = this->create_publisher<nodeframe3>("nlink_linktrack_nodeframe3", qos);
        pub_node_frame4_ = this->create_publisher<nodeframe4>("nlink_linktrack_nodeframe4", qos);
        pub_node_frame5_ = this->create_publisher<nodeframe5>("nlink_linktrack_nodeframe5", qos);
        pub_node_frame6_ = this->create_publisher<nodeframe6>("nlink_linktrack_nodeframe6", qos);
        pub_node_frame7_ = this->create_publisher<nodeframe7>("nlink_linktrack_nodeframe7", qos);
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

    void Init::initAnchorFrame0(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolAnchorFrame0;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            auto data = nlt_anchorframe0_.result;
                                            g_msg_anchorframe0.role = data.role;
                                            g_msg_anchorframe0.id = data.id;
                                            g_msg_anchorframe0.voltage = data.voltage;
                                            g_msg_anchorframe0.local_time = data.local_time;
                                            g_msg_anchorframe0.system_time = data.system_time;
                                            auto &msg_nodes = g_msg_anchorframe0.nodes;
                                            msg_nodes.clear();
                                            decltype(g_msg_anchorframe0.nodes)::value_type msg_node;
                                            for (size_t i = 0, icount = data.valid_node_count; i < icount; ++i)
                                            {
                                                auto node = data.nodes[i];
                                                msg_node.role = node->role;
                                                msg_node.id = node->id;
                                                ARRAY_ASSIGN(msg_node.pos_3d, node->pos_3d)
                                                ARRAY_ASSIGN(msg_node.dis_arr, node->dis_arr)
                                                msg_nodes.push_back(msg_node);
                                            }

                                            pub_anchor_frame0_->publish(g_msg_anchorframe0); });
    }

    void Init::initTagFrame0(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolTagFrame0;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_tagframe0.result;
                                            auto &msg_data = g_msg_tagframe0;

                                            msg_data.role = data.role;
                                            msg_data.id = data.id;
                                            msg_data.local_time = data.local_time;
                                            msg_data.system_time = data.system_time;
                                            msg_data.voltage = data.voltage;
                                            ARRAY_ASSIGN(msg_data.pos_3d, data.pos_3d)
                                            ARRAY_ASSIGN(msg_data.eop_3d, data.eop_3d)
                                            ARRAY_ASSIGN(msg_data.vel_3d, data.vel_3d)
                                            ARRAY_ASSIGN(msg_data.dis_arr, data.dis_arr)
                                            ARRAY_ASSIGN(msg_data.imu_gyro_3d, data.imu_gyro_3d)
                                            ARRAY_ASSIGN(msg_data.imu_acc_3d, data.imu_acc_3d)
                                            ARRAY_ASSIGN(msg_data.angle_3d, data.angle_3d)
                                            ARRAY_ASSIGN(msg_data.quaternion, data.quaternion)

                                            pub_tag_frame0_->publish(msg_data); });
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

    void Init::initNodeFrame1(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame1;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe1.result;
                                            auto &msg_data = g_msg_nodeframe1;
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
                                                ARRAY_ASSIGN(msg_node.pos_3d, node->pos_3d)
                                            }

                                            pub_node_frame1_->publish(msg_data); });
    }

    void Init::initNodeFrame2(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame2;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe2.result;
                                            auto &msg_data = g_msg_nodeframe2;
                                            auto &msg_nodes = msg_data.nodes;

                                            msg_data.role = data.role;
                                            msg_data.id = data.id;
                                            msg_data.local_time = data.local_time;
                                            msg_data.system_time = data.system_time;
                                            msg_data.voltage = data.voltage;
                                            ARRAY_ASSIGN(msg_data.pos_3d, data.pos_3d)
                                            ARRAY_ASSIGN(msg_data.eop_3d, data.eop_3d)
                                            ARRAY_ASSIGN(msg_data.vel_3d, data.vel_3d)
                                            ARRAY_ASSIGN(msg_data.imu_gyro_3d, data.imu_gyro_3d)
                                            ARRAY_ASSIGN(msg_data.imu_acc_3d, data.imu_acc_3d)
                                            ARRAY_ASSIGN(msg_data.angle_3d, data.angle_3d)
                                            ARRAY_ASSIGN(msg_data.quaternion, data.quaternion)

                                            msg_nodes.resize(data.valid_node_count);
                                            for (size_t i = 0; i < data.valid_node_count; ++i) 
                                            {
                                                auto &msg_node = msg_nodes[i];
                                                auto node = data.nodes[i];
                                                msg_node.id = node->id;
                                                msg_node.role = node->role;
                                                msg_node.dis = node->dis;
                                                msg_node.fp_rssi = node->fp_rssi;
                                                msg_node.rx_rssi = node->rx_rssi;
                                            }
                                            
                                            msg_data.header.stamp = this->now();

                                            pub_node_frame2_->publish(msg_data); });
    }

    void Init::initNodeFrame3(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame3;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe3.result;
                                            auto &msg_data = g_msg_nodeframe3;
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
                                                msg_node.fp_rssi = node->fp_rssi;
                                                msg_node.rx_rssi = node->rx_rssi;
                                            }

                                            pub_node_frame3_->publish(msg_data); });
    }

    void Init::initNodeFrame4(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame4;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe4.result;
                                            auto &msg_data = g_msg_nodeframe4;
                                            msg_data.role = data.role;
                                            msg_data.id = data.id;
                                            msg_data.local_time = data.local_time;
                                            msg_data.system_time = data.system_time;
                                            msg_data.voltage = data.voltage;
                                            msg_data.tags.resize(data.tag_count);
                                            for (int i = 0; i < data.tag_count; ++i)
                                            {
                                                auto &msg_tag = msg_data.tags[i];
                                                auto tag = data.tags[i];
                                                msg_tag.id = tag->id;
                                                msg_tag.voltage = tag->voltage;
                                                msg_tag.anchors.resize(tag->anchor_count);
                                                for (int j = 0; j < tag->anchor_count; ++j)
                                                {
                                                    auto &msg_anchor = msg_tag.anchors[j];
                                                    auto anchor = tag->anchors[j];
                                                    msg_anchor.id = anchor->id;
                                                    msg_anchor.dis = anchor->dis;
                                                }
                                            }

                                            pub_node_frame4_->publish(msg_data); });
    }

    void Init::initNodeFrame5(NProtocolExtracter *protocol_extraction)
    {
        auto protocol = new NLT_ProtocolNodeFrame5;
        protocol_extraction->AddProtocol(protocol);
        protocol->SetHandleDataCallback([=]
                                        {
                                            const auto &data = g_nlt_nodeframe5.result;
                                            auto &msg_data = g_msg_nodeframe5;
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
                                                msg_node.fp_rssi = node->fp_rssi;
                                                msg_node.rx_rssi = node->rx_rssi;
                                            }

                                            pub_node_frame5_->publish(msg_data); });
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

} // namespace linktrack end