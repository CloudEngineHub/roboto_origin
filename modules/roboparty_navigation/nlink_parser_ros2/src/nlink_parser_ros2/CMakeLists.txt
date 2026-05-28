cmake_minimum_required(VERSION 3.8)
project(nlink_parser_ros2)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(serial REQUIRED)
find_package(nlink_message REQUIRED)
find_package(std_msgs REQUIRED)


###########
## Build ##
###########
include(GNUInstallDirs)

include_directories(
  include
  ${serial_INCLUDE_DIRS}
  src/utils
)

set(nutils "nutils")
add_library(${nutils}
  src/utils/protocol_extracter/nprotocol_base.cpp
  src/utils/protocol_extracter/nprotocol_extracter.cpp
  src/utils/nlink_unpack/nlink_utils.c
  src/utils/nlink_unpack/nlink_linktrack_anchorframe0.c
  src/utils/nlink_unpack/nlink_linktrack_tagframe0.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe0.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe1.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe2.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe3.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe4.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe5.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe6.c
  src/utils/nlink_unpack/nlink_linktrack_nodeframe7.c
  src/utils/nlink_unpack/nlink_tofsense_frame0.c
  src/utils/nlink_unpack/nlink_tofsensem_frame0.c
  src/utils/nlink_unpack/nlink_linktrack_aoa_nodeframe0.c
  src/utils/nlink_unpack/nlink_iot_frame0.c
  src/utils/init_serial.cpp
  src/utils/nlink_protocol.cpp
  src/utils/nutils.cpp
)

target_link_libraries(${nutils}
  rclcpp::rclcpp
)
ament_target_dependencies(${nutils}
  "rclcpp"
  "serial"
  "nlink_message"
  "std_msgs"
)

set(TOFSENSE_NAME "tofsense")
add_executable(${TOFSENSE_NAME} 
  src/tofsense/main.cpp
  src/tofsense/init.cpp
)
target_link_libraries(${TOFSENSE_NAME}
  ${nutils}
)
ament_target_dependencies(${TOFSENSE_NAME}
  "rclcpp"
  "serial"
  "nlink_message"
)

set(TOFSENSEM_NAME "tofsensem")
add_executable(${TOFSENSEM_NAME} 
  src/tofsensem/main.cpp
  src/tofsensem/init.cpp
)
target_link_libraries(${TOFSENSEM_NAME}
  ${nutils}
)
ament_target_dependencies(${TOFSENSEM_NAME}
  "rclcpp"
  "serial"
  "nlink_message"
)

set(LINKTRACK "linktrack")
add_executable(${LINKTRACK} 
  src/linktrack/main.cpp
  src/linktrack/init.cpp
  src/linktrack/protocols.cpp
)
target_link_libraries(${LINKTRACK}
  ${nutils}
)
ament_target_dependencies(${LINKTRACK}
  "rclcpp"
  "serial"
  "nlink_message"
)

set(LINKTRACK_AOA "linktrack_aoa")
add_executable(${LINKTRACK_AOA} 
  src/linktrack_aoa/main.cpp
  src/linktrack_aoa/init.cpp
  src/linktrack/protocols.cpp
)
target_link_libraries(${LINKTRACK_AOA}
  ${nutils}
)
ament_target_dependencies(${LINKTRACK_AOA}
  "rclcpp"
  "serial"
  "nlink_message"
)

set(IOT "iot")
add_executable(${IOT} 
  src/iot/main.cpp
  src/iot/init.cpp
)
target_link_libraries(${IOT}
  ${nutils}
)
ament_target_dependencies(${IOT}
  "rclcpp"
  "serial"
  "nlink_message"
)


# 添加launch文件
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

install(TARGETS 
  ${TOFSENSE_NAME}
  ${TOFSENSEM_NAME}
  ${LINKTRACK}
  ${LINKTRACK_AOA}
  ${IOT}
  DESTINATION lib/${PROJECT_NAME})

ament_package()
