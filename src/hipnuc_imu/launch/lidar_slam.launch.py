"""Lidar + RF2O odom + slam_toolbox (no IMU, no EKF)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    imu_share = get_package_share_directory('hipnuc_imu')

    slam_params = LaunchConfiguration('slam_params_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=os.path.join(imu_share, 'config', 'slam_toolbox.yaml'),
            description='slam_toolbox parameter file'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(imu_share, 'launch', 'lidar_bringup.launch.py')),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(imu_share, 'launch', 'slam_toolbox.launch.py')),
            launch_arguments={
                'slam_params_file': slam_params,
            }.items(),
        ),
    ])
