import launch
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return launch.LaunchDescription([
        DeclareLaunchArgument(
            'port',
            default_value='/dev/ttyACM0',
            description='Serial port name'
        ),
        DeclareLaunchArgument(
            'baudrate',
            default_value='921600',
            description='Baudrate'
        ),
        DeclareLaunchArgument(
            'is_inquire_mode',
            default_value='true',   # false or true
            description='Whether TOFSense is in query mode'
        ),
        Node(
            package='nlink_parser_ros2',
            executable='TOFSense_ros2',
            name='TOFSense_ros2',
            parameters=[
                {'port': LaunchConfiguration('port')},
                {'baudrate': LaunchConfiguration('baudrate')},
                {'is_inquire_mode': LaunchConfiguration('is_inquire_mode')},
            ]
        )
    ])
