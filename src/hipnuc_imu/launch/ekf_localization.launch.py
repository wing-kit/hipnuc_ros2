import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    imu_share = get_package_share_directory('hipnuc_imu')
    default_ekf_params = os.path.join(imu_share, 'config', 'ekf.yaml')

    ekf_params = LaunchConfiguration('ekf_params_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'ekf_params_file',
            default_value=default_ekf_params,
            description='robot_localization EKF parameter file'),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_params],
        ),
    ])
