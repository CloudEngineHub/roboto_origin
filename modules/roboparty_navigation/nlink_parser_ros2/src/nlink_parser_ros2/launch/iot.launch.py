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
        Node(
            package='nlink_parser_ros2',
            executable='iot',
            name='iot',
            parameters=[
                {'port': LaunchConfiguration('port')},
                {'baudrate': LaunchConfiguration('baudrate')},
            ]
        )
    ])
