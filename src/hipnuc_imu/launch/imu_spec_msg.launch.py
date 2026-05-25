## Launch Hipnuc IMU publisher (optional demo listener).
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    default_config = os.path.join(
        get_package_share_directory('hipnuc_imu'),
        'config',
        'hipnuc_config.yaml',
    )

    config = LaunchConfiguration('config')
    listener = LaunchConfiguration('listener')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config',
            default_value=default_config,
            description='Path to hipnuc IMU parameter file'),
        DeclareLaunchArgument(
            'listener',
            default_value='true',
            description='Start demo listener that prints IMU messages'),
        Node(
            package='hipnuc_imu',
            executable='talker',
            name='IMU_publisher',
            parameters=[config],
            output='screen',
        ),
        Node(
            package='hipnuc_imu',
            executable='listener',
            output='screen',
            condition=IfCondition(listener),
        ),
    ])
