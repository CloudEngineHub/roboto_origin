cmake_minimum_required(VERSION 3.8)
project(nlink_message)


# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

set(msg_files
  "msg/IotFrame0.msg"
  "msg/IotFrame0Node.msg"
  "msg/LinktrackAoaNode0.msg"
  "msg/LinktrackAoaNodeframe0.msg"
  "msg/LinktrackAnchorframe0.msg"
  "msg/LinktrackNode0.msg"
  "msg/LinktrackNode1.msg"
  "msg/LinktrackNode2.msg"
  "msg/LinktrackNode4Anchor.msg"
  "msg/LinktrackNode4Tag.msg"
  "msg/LinktrackNode5.msg"
  "msg/LinktrackNode6.msg"
  "msg/LinktrackNode7.msg"
  "msg/LinktrackNodeframe0.msg"
  "msg/LinktrackNodeframe1.msg"
  "msg/LinktrackNodeframe2.msg"
  "msg/LinktrackNodeframe3.msg"
  "msg/LinktrackNodeframe4.msg"
  "msg/LinktrackNodeframe5.msg"
  "msg/LinktrackNodeframe6.msg"
  "msg/LinktrackNodeframe7.msg"
  "msg/LinktrackTag.msg"
  "msg/LinktrackTagframe0.msg"
  "msg/TofsenseCascade.msg"
  "msg/TofsenseFrame0.msg"
  "msg/TofsenseMCascade.msg"
  "msg/TofsenseMFrame0.msg"
  "msg/TofsenseMFrame0Pixel.msg"
)
rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  DEPENDENCIES builtin_interfaces std_msgs
)

ament_package()
