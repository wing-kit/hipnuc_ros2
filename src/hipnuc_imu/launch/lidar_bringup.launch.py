## Lidar + RF2O only (no IMU, no EKF). RF2O publishes odom->base_link TF.
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    imu_share = get_package_share_directory('hipnuc_imu')
    lidar_share = get_package_share_directory('nvilidar_ros2')
    rf2o_share = get_package_share_directory('rf2o_laser_odometry')

    lidar_params = LaunchConfiguration('lidar_params_file')
    enable_odom = LaunchConfiguration('enable_odom')
    rf2o_params = LaunchConfiguration('rf2o_params_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'lidar_params_file',
            default_value=os.path.join(lidar_share, 'params', 'nvilidar.yaml'),
            description='NVILIDAR parameter file'),
        DeclareLaunchArgument(
            'enable_odom',
            default_value='true',
            description='Start RF2O laser odometry (/odom + odom->base_link TF)'),
        DeclareLaunchArgument(
            'rf2o_params_file',
            default_value=os.path.join(rf2o_share, 'config', 'rf2o_params.yaml'),
            description='RF2O params (publish_tf: true for SLAM without EKF)'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(lidar_share, 'launch', 'nvilidar_launch.py')),
            launch_arguments={
                'params_file': lidar_params,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(rf2o_share, 'launch', 'rf2o_laser_odometry.launch.py')),
            launch_arguments={
                'params_file': rf2o_params,
            }.items(),
            condition=IfCondition(enable_odom),
        ),
    ])
