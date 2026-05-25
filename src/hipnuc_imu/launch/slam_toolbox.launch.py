"""Launch slam_toolbox async mapping (expects /scan and odom->base_link TF from bringup)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    imu_share = get_package_share_directory('hipnuc_imu')
    default_params = os.path.join(imu_share, 'config', 'slam_toolbox.yaml')

    slam_params = LaunchConfiguration('slam_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_delay = LaunchConfiguration('slam_start_delay')

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params,
            {'use_sim_time': use_sim_time},
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=default_params,
            description='slam_toolbox parameter file'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock'),
        DeclareLaunchArgument(
            'slam_start_delay',
            default_value='2.0',
            description='Seconds to wait before starting SLAM (let RF2O publish odom TF)'),
        TimerAction(
            period=slam_delay,
            actions=[slam_node],
        ),
    ])
