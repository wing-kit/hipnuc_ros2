#include <cstdio>
#include <vector>
#include <iostream>
#include <string>
#include <signal.h>
#include <pthread.h>

#include <sys/time.h>

#include "rclcpp/clock.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp/time_source.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include <cmath>
#include <memory>

#include "nvilidar_process.h"

//版本号 
#define ROS2Verision "1.0.3"

//参数相关 宏定义 
#define READ_PARAM(TYPE, NAME, VAR, VALUE) VAR = VALUE; \
       	node->declare_parameter<TYPE>(NAME, VAR); \
       	node->get_parameter(NAME, VAR);

//主入口函数 
int main(int argc,char *argv[])
{
    rclcpp::init(argc,argv);    //初始化 

    auto node = rclcpp::Node::make_shared("nvilidar_ros2_node");

    RCLCPP_INFO(node->get_logger(), "[NVILIDAR INFO] Current ROS2 Driver Version: %s\n", ((std::string)ROS2Verision).c_str());  //版本号输出 

    //para 
    Nvilidar_UserConfigTypeDef cfg;

    //获取参数 
    READ_PARAM(std::string, "serialport_name", (cfg.serialport_name), "dev/nvilidar");
    READ_PARAM(int, "serialport_baud", (cfg.serialport_baud), 921600);
    READ_PARAM(std::string, "ip_addr", (cfg.ip_addr), "192.168.1.200");
    READ_PARAM(int, "lidar_udp_port", (cfg.lidar_udp_port), 8100);
    READ_PARAM(int, "config_tcp_port", (cfg.config_tcp_port), 8200);
    READ_PARAM(std::string, "frame_id", (cfg.frame_id), "laser_frame");
    READ_PARAM(bool, "resolution_fixed", (cfg.resolution_fixed), true);
    READ_PARAM(bool, "auto_reconnect", (cfg.auto_reconnect), false);
    READ_PARAM(bool, "reversion", (cfg.reversion), false);
    READ_PARAM(bool, "inverted", (cfg.inverted), false);
    READ_PARAM(double, "angle_max", (cfg.angle_max), 180.0);
    READ_PARAM(double, "angle_min", (cfg.angle_min), -180.0);
    READ_PARAM(double, "range_max", (cfg.range_max), 64.0);
    READ_PARAM(double, "range_min", (cfg.range_min), 0.0);
    READ_PARAM(double, "aim_speed", (cfg.aim_speed), 10.0);
    READ_PARAM(int, "sampling_rate", (cfg.sampling_rate), 10);
    READ_PARAM(bool, "sensitive", (cfg.sensitive), false);
    READ_PARAM(int, "tailing_level", (cfg.tailing_level), 6);
    READ_PARAM(double, "angle_offset", (cfg.angle_offset), 0.0);
    READ_PARAM(bool, "apd_change_flag", (cfg.apd_change_flag), false);
    READ_PARAM(int,  "apd_value", (cfg.apd_value), 500);
    READ_PARAM(bool, "single_channel", (cfg.single_channel), false);
    READ_PARAM(std::string, "ignore_array_string", (cfg.ignore_array_string), "");
    std::string connection_type;
    READ_PARAM(std::string, "connection_type", connection_type, "serial");

    std::unique_ptr<nvilidar::LidarProcess> laser;
    if (connection_type == "udp" || connection_type == "network" || connection_type == "socket") {
        RCLCPP_INFO(node->get_logger(), "[NVILIDAR INFO] Connection: UDP %s:%d",
            cfg.ip_addr.c_str(), cfg.lidar_udp_port);
        laser = std::make_unique<nvilidar::LidarProcess>(
            USE_SOCKET, cfg.ip_addr, static_cast<uint32_t>(cfg.lidar_udp_port));
    } else {
        RCLCPP_INFO(node->get_logger(), "[NVILIDAR INFO] Connection: serial %s @ %d",
            cfg.serialport_name.c_str(), cfg.serialport_baud);
        laser = std::make_unique<nvilidar::LidarProcess>(
            USE_SERIALPORT, cfg.serialport_name, static_cast<uint32_t>(cfg.serialport_baud));
    }

    //根据配置 重新加载参数 
    laser->LidarReloadPara(cfg); 

    //初始化 
    bool ret = laser->LidarInitialialize();
    if (ret) 
    {
        //启动雷达 
        ret = laser->LidarTurnOn();
        if (!ret) 
        {
            RCLCPP_ERROR(node->get_logger(),"Failed to start Scan!!!");
        }
    } 
    else 
    {
        RCLCPP_ERROR(node->get_logger(),"Error initializing NVILIDAR Comms and Status!!!");
    }

    auto laser_pub = node->create_publisher<sensor_msgs::msg::LaserScan>("scan", rclcpp::SensorDataQoS());

    rclcpp::WallRate loop_rate(50);

    //循环读取雷达数据 
    while (ret && rclcpp::ok())
    {
        LidarScan scan;

        //get lidar data
        try
        {
            /* code */
            if(laser->LidarSamplingProcess(scan))
            {
            	if(scan.points.size() > 0)
            	{
					auto scan_msg = std::make_shared<sensor_msgs::msg::LaserScan>();

					scan_msg->header.stamp.sec = RCL_NS_TO_S(scan.stamp);
					scan_msg->header.stamp.nanosec =  scan.stamp - RCL_S_TO_NS(scan_msg->header.stamp.sec);
					scan_msg->header.frame_id = cfg.frame_id;
					scan_msg->angle_min = scan.config.min_angle;
					scan_msg->angle_max = scan.config.max_angle;
					scan_msg->angle_increment = scan.config.angle_increment;
					scan_msg->scan_time = scan.config.scan_time;
					scan_msg->time_increment = scan.config.time_increment;
					scan_msg->range_min = scan.config.min_range;
					scan_msg->range_max = scan.config.max_range;

					size_t size = (scan.config.max_angle - scan.config.min_angle)/ scan.config.angle_increment + 1;
					scan_msg->ranges.resize(size);
					scan_msg->intensities.resize(size);

					for(size_t i=0; i < scan.points.size(); i++) 
					{
						int index = std::ceil((scan.points[i].angle - scan.config.min_angle)/scan.config.angle_increment);
						if(index >=0 && index < size) 
						{
							scan_msg->ranges[index] = scan.points[i].range;
							scan_msg->intensities[index] = scan.points[i].intensity;
						}
					}

					laser_pub->publish(*scan_msg);
                }
                else 
                {
                	RCLCPP_WARN(node->get_logger(), "Lidar Data Invalid!");
                }
            }
            else 
            {
                RCLCPP_ERROR(node->get_logger(), "Failed to get Lidar Data!");
                break;
            }

            rclcpp::spin_some(node);
        }
        catch(const rclcpp::exceptions::RCLError &e)
        {
            //RCLCPP_ERROR(node->get_logger(),"unexpectedly failed with %s",e.what());
        }
        
        loop_rate.sleep();
    }

    laser->LidarTurnOff();
    RCLCPP_INFO(node->get_logger(), "[NVILIDAR INFO] Now NVILIDAR is stopping .......");
    laser->LidarCloseHandle();
    rclcpp::shutdown();

    return 0;
}
