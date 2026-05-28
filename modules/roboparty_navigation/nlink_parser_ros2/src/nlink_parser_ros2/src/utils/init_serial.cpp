#include "init_serial.h"

Serial_Base::Serial_Base(serial::Serial *serial, NProtocolExtracter *protocol_extraction, const std::string &node_name) : Node(node_name)
{
    serial_ = serial;
    protocol_extraction_ = protocol_extraction;
    serial_Init();
    Start();
}

void Serial_Base::serial_Init()
{
    try
    {
        std::string port = this->declare_parameter("port", "/dev/ttyCH343USB0");
        int baud_rate = this->declare_parameter("baudrate", 921600);
        auto timeout = serial::Timeout(10);

        this->serial_->setPort(port);
        this->serial_->setBaudrate(baud_rate);
        this->serial_->setTimeout(timeout);
        this->serial_->open();
        std::cout << "try to open serial port with port: " << port << baud_rate << std::endl;

        if (!this->serial_->isOpen())
        {
            std::cout << "error" << std::endl;
            exit(EXIT_FAILURE);
        }
        std::cout << "OK" << std::endl;
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
        exit(EXIT_FAILURE);
    }
}

void Serial_Base::Start()
{
    float ser_interval = 10;
    serial_timer_read_ = this->create_wall_timer(std::chrono::milliseconds(int(ser_interval)), [=]
                                                 {
                                                    auto available_bytes = this->serial_->available();
                                                    std::string str_received;

                                                    if (available_bytes)
                                                    {
                                                        this->serial_->read(str_received, available_bytes);
                                                        this->protocol_extraction_->AddNewData(str_received);
                                                    } });
}
