#include "bms_driver.hpp"

#include "tws_bms_driver.hpp"

std::shared_ptr<BmsDriver> BmsDriver::create_bms(const std::string& bms_type,
                                                  const std::string& socket_path) {
    if (bms_type == "TWS") {
        return std::make_shared<TwsBmsDriver>(socket_path);
    } else {
        throw std::runtime_error("BMS type not supported: " + bms_type);
    }
}
