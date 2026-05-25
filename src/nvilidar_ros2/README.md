# NVILIDAR ROS2 Driver

nvilidar_ros2_driver is a new ros package, which is designed to gradually become the standard driver package for nvilidar devices in the ros2 environment.

## How to install ROS2

[install](https://index.ros.org/doc/ros2/Installation)

## How to Create a ROS2 workspace
[Create a workspace](https://index.ros.org/doc/ros2/Tutorials/Colcon-Tutorial/#create-a-workspace)

## Clone or Download nvilidar_ros2

1. Clone nvilidar_ros2_driver package for github : 

   `git clone https://github.com/nvilidar/nvilidar_ros2.git`

   or 

   `git clone https://gitee.com/nvilidar/nvilidar_ros2.git`

   or get the source in the website: [nvistar](https://www.nvistar.com)

2. copy the file to the "src" dir

3. Build nvilidar_ros2_driver package :

   ```
   cd nvilidar_ros2_ws
   colcon build --symlink-install
   ```
   Note: install colcon [see](https://index.ros.org/doc/ros2/Tutorials/Colcon-Tutorial/#install-colcon)

4. Package environment setup :

   `source ./install/setup.bash`

    Note: Add permanent workspace environment variables.
    It's convenientif the ROS2 environment variables are automatically added to your bash session every time a new shell is launched:
    ```
    $echo "source ~/nvilidar_ros2_ws/install/setup.bash" >> ~/.bashrc
    $source ~/.bashrc
    ```
5. Confirmation
    To confirm that your package path has been set, printenv the `grep -i ROS` variable.
    ```
    $ printenv | grep -i ROS
    ```

6. Create serial port Alias [optional] 
    ```
	$chmod 0777 nvilidar_ros2/startup/*
	$sudo sh nvilidar_ros2/startup/initenv.sh
    ```
   Note: After completing the previous operation, replug the LiDAR again.
	
## Configure LiDAR [paramters](params/nvilidar.yaml)
```
nvilidar_ros2_node:
  ros__parameters:
    serialport_name: "/dev/nvilidar"
    serialport_baud: 921600
    ip_addr: "192.168.1.200"
    lidar_udp_port: 8100
    config_udp_port: 8200
    frame_id: "laser_frame"
    resolution_fixed: true
    auto_reconnect: false
    reversion: false
    inverted: false
    angle_min: -180.0
    angle_max: 180.0
    range_min: 0.0
    range_max: 64.0
    aim_speed: 10.0
    sampling_rate: 10
    sensitive: false
    tailing_level: 6
    angle_offset: 0.0
    apd_change_flag: false
    apd_value: 500
    single_channel: false
    ignore_array_string: ""
```

## Run nvilidar_ros2

##### Run nvilidar_ros2 using launch file

The command format is : 

 `ros2 launch nvilidar_ros2 [launch file].py`

1. Connect LiDAR uint(s).
   ```
   ros2 launch nvilidar_ros2 nvilidar_launch.py 
   ```
2. RVIZ 
   ```
   ros2 launch nvilidar_ros2 nvilidar_launch_view.py 
   ```
3. echo scan topic
   ```
   ros2 run nvilidar_ros2 nvilidar_ros2_client
   ```
   or
   ```
   ros2 topic echo /scan
   ```

## nvilidar_ros2 Parameter

   |  value   |  information  |
   |  :----:    | :----:  |
   | serialport_baud  | if use serialport,the lidar's serialport |
   | serialport_name  | if use serialport,the lidar's port name |
   | ip_addr  | if use udp socket,the lidar's ip addr,default:192.168.1.200 |
   | lidar_udp_port  | if use udp socket,the lidar's udp port,default:8100 |
   | config_tcp_port  | if use udp socket,config the net converter's para,default:8200 |
   | frame_id  | it is useful in ros,sdk don't use it |
   | resolution_fixed  | Rotate one circle fixed number of points,it is 'true' in ros,default |
   | auto_reconnect  | lidar auto connect,if it is disconnet in case |
   | reversion  | lidar's point revert|
   | inverted  | lidar's point invert|
   | angle_max  | lidar angle max value,max:180.0°|
   | angle_max  | lidar angle min value,min:-180.0°|
   | range_max  | lidar's max measure distance,default:64.0 meters|
   | range_min  | lidar's min measure distance,default:0.0 meters|
   | aim_speed  | lidar's run speed,default:10.0 Hz|
   | sampling_rate  | lidar's sampling rate,default:10.0 K points in 1 second|
   | sensitive  | lidar's data with sensitive,default:false|
   | tailing_level  | lidar's tailing level,The smaller the value, the stronger the filtering,default:6|
   | angle_offset  | angle offset,default:0.0|
   | adp_change_flag  | change apd value,don't change it if nessesary,default:false|
   | adp_value  | change apd value,if the 'apd_change_flag' is true,it is valid,default:500|
   | single_channel  | it is default false,don't change it|
   | ignore_array_string  | if you want to filter some point's you can change it,it is anti-clockwise for the lidar.eg. you can set the value "30,60,90,120",you can remove the 30°~60° and 90°~120° points in the view|








