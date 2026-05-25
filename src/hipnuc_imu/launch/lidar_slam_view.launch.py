"""Lidar + RF2O + slam_toolbox + RViz (no IMU)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    imu_share = get_package_share_directory('hipnuc_imu')
    rviz_config = os.path.join(imu_share, 'config', 'lidar_slam.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'rviz_config',
            default_value=rviz_config,
            description='RViz config for lidar-only SLAM'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(imu_share, 'launch', 'lidar_slam.launch.py')),
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', LaunchConfiguration('rviz_config')],
        ),
    ])
