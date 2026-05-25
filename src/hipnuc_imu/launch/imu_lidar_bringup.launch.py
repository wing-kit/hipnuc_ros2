## Launch Hipnuc IMU and NVISTAR lidar together.
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    imu_share = get_package_share_directory('hipnuc_imu')
    lidar_share = get_package_share_directory('nvilidar_ros2')

    imu_params = LaunchConfiguration('imu_params_file')
    lidar_params = LaunchConfiguration('lidar_params_file')
    imu_listener = LaunchConfiguration('imu_listener')

    return LaunchDescription([
        DeclareLaunchArgument(
            'imu_params_file',
            default_value=os.path.join(imu_share, 'config', 'hipnuc_config.yaml'),
            description='Hipnuc IMU parameter file'),
        DeclareLaunchArgument(
            'lidar_params_file',
            default_value=os.path.join(lidar_share, 'params', 'nvilidar.yaml'),
            description='NVILIDAR parameter file'),
        DeclareLaunchArgument(
            'imu_listener',
            default_value='false',
            description='Start demo IMU listener (prints to screen)'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(imu_share, 'launch', 'imu_spec_msg.launch.py')),
            launch_arguments={
                'config': imu_params,
                'listener': imu_listener,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(lidar_share, 'launch', 'nvilidar_launch.py')),
            launch_arguments={
                'params_file': lidar_params,
            }.items(),
        ),
        # base_link -> imu_link (adjust mount offset if needed)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_pub_imu',
            arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'imu_link'],
        ),
    ])
