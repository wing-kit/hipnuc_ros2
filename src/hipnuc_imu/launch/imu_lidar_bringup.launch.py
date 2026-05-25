## Launch Hipnuc IMU, NVISTAR lidar, and optional RF2O laser odometry.
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    imu_share = get_package_share_directory('hipnuc_imu')
    lidar_share = get_package_share_directory('nvilidar_ros2')
    rf2o_share = get_package_share_directory('rf2o_laser_odometry')

    imu_params = LaunchConfiguration('imu_params_file')
    lidar_params = LaunchConfiguration('lidar_params_file')
    imu_listener = LaunchConfiguration('imu_listener')
    enable_imu = LaunchConfiguration('enable_imu')
    enable_odom = LaunchConfiguration('enable_odom')
    enable_ekf = LaunchConfiguration('enable_ekf')
    rf2o_params = LaunchConfiguration('rf2o_params_file')
    ekf_params = LaunchConfiguration('ekf_params_file')

    rf2o_params_ekf = os.path.join(rf2o_share, 'config', 'rf2o_params_ekf.yaml')

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
        DeclareLaunchArgument(
            'enable_imu',
            default_value='true',
            description='Start Hipnuc IMU publisher and imu_link TF'),
        DeclareLaunchArgument(
            'enable_odom',
            default_value='true',
            description='Start RF2O laser odometry (publishes /odom for EKF)'),
        DeclareLaunchArgument(
            'enable_ekf',
            default_value='true',
            description='Fuse /odom + /IMU_data with robot_localization EKF'),
        DeclareLaunchArgument(
            'rf2o_params_file',
            default_value=rf2o_params_ekf,
            description='RF2O parameter file (use rf2o_params.yaml if enable_ekf:=false)'),
        DeclareLaunchArgument(
            'ekf_params_file',
            default_value=os.path.join(imu_share, 'config', 'ekf.yaml'),
            description='robot_localization EKF parameter file'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(imu_share, 'launch', 'imu_spec_msg.launch.py')),
            launch_arguments={
                'config': imu_params,
                'listener': imu_listener,
            }.items(),
            condition=IfCondition(enable_imu),
        ),
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
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(imu_share, 'launch', 'ekf_localization.launch.py')),
            launch_arguments={
                'ekf_params_file': ekf_params,
            }.items(),
            condition=IfCondition(enable_ekf),
        ),
        # base_link center; lidar at center; IMU 4 cm right (-Y), imu +X aligned with base/laser +Y
        # yaw +90 deg about Z: (qx, qy, qz, qw) = (0, 0, sin(pi/4), cos(pi/4))
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_pub_imu',
            arguments=['0', '-0.04', '0.02', '0', '0', '0.7071068', '0.7071068', 'base_link', 'imu_link'],
            condition=IfCondition(enable_imu),
        ),
    ])
