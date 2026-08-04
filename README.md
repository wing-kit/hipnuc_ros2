# hipnuc_ros2 手動操作指南

ROS 2 Humble workspace：Hipnuc IMU + NVISTAR VP300 LiDAR + RF2O + EKF + SLAM Toolbox
（詳細技術說明見 `src/Readme.md`；呢份係日常操作速查）

---

## 0. 硬件

| 裝置 | 裝置檔 | udev symlink |
|------|--------|--------------|
| Hipnuc IMU（CP210x USB-UART） | `/dev/ttyUSB0` | `/dev/hipnuc_imu` |
| NVISTAR VP300 LiDAR | `/dev/ttyACM0/1` | `/dev/nvilidar` |

檢查裝置：

```bash
ls -l /dev/hipnuc_imu /dev/nvilidar
```

---

## 1. 每次開新終端都要 source

```bash
source /opt/ros/humble/setup.bash
source ~/hipnuc_ros2/install/setup.bash
```

可以加入 `~/.bashrc` 自動化：

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/hipnuc_ros2/install/setup.bash" >> ~/.bashrc
```

---

## 2. Build（改咗 code 或 config 先需要做）

```bash
source /opt/ros/humble/setup.bash
cd ~/hipnuc_ros2
colcon build
source install/setup.bash
```

> ⚠️ 如果係由 Hermes agent 嘅終端 build，要先將 venv 剔出 PATH：
> `export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v 'hermes-agent/venv' | paste -sd:)`
> 再 `rm -rf build install log` 清 cache 先 build。（自己開嘅普通終端冇呢個問題）

---

## 3. 运行模式

### 3.1 淨係 IMU（終端會打印數據）

```bash
ros2 launch hipnuc_imu imu_spec_msg.launch.py
```

唔想打印、淨係發布 topic：

```bash
ros2 launch hipnuc_imu imu_spec_msg.launch.py listener:=false
```

### 3.2 IMU + LiDAR + RF2O + EKF（bringup，冇地圖）

```bash
ros2 launch hipnuc_imu imu_lidar_bringup.launch.py
```

帶 RViz：

```bash
ros2 launch hipnuc_imu imu_lidar_bringup_view.launch.py
```

### 3.3 SLAM 建圖（IMU + LiDAR + RF2O + EKF + slam_toolbox）⭐

```bash
ros2 launch hipnuc_imu imu_lidar_slam.launch.py
```

帶 RViz（Fixed Frame = `map`）：

```bash
ros2 launch hipnuc_imu imu_lidar_slam_view.launch.py
```

唔使 IMU、淨係雷達 + RF2O + SLAM：

```bash
ros2 launch hipnuc_imu lidar_slam_view.launch.py
```

### 3.4 儲存地圖（SLAM 行緊嘅時候，另開終端）

```bash
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: 'my_map'}}"
```

會喺當前目錄產生 `my_map.yaml` + `my_map.pgm`。

---

## 4. 檢查數據（另開終端，記住 source）

⚠️ `/IMU_data` 同 `/scan` 係 **Best Effort** QoS，要加 `--qos-reliability best_effort`，否則收唔到：

```bash
# IMU 四元數
ros2 topic echo /IMU_data --once --qos-reliability best_effort

# 雷達掃描
ros2 topic echo /scan --once --qos-reliability best_effort

# EKF 融合里程計（Reliable，唔使加旗）
ros2 topic hz /odometry/filtered

# 地圖
ros2 topic echo /map --once --no-arr

# TF 鏈檢查：map → odom → base_link → laser_frame / imu_link
ros2 run tf2_ros tf2_echo map base_link
```

RViz 手動加 display 時：`Imu` 同 `LaserScan` 嘅 **Reliability Policy** 要揀 **Best Effort**。

---

## 5. 收工 / 清場

launch 前面個終端撳 `Ctrl+C` 就會停晒。

如果有殘留節點（例如再開新 launch 時報串口開唔到），一鑊熟清場：

```bash
pkill -f 'ros2 launch'; sleep 1
pkill -9 -f nvilidar_ros2_node; pkill -9 -f async_slam_toolbox
pkill -9 -f rf2o_laser_odometry; pkill -9 -f robot_localization
pkill -9 -f 'hipnuc_imu/lib/hipnuc_imu/talker'
pkill -9 -f static_transform_publisher
```

一鑊熟冧巴快版（連 launch、node、static TF 全部清晒）：

```bash
pkill -9 -f 'ros2 launch|nvilidar_ros2_node|async_slam_toolbox|rf2o_laser_odometry|robot_localization|hipnuc_imu/talker|static_transform_publisher'
```

檢查有冇殘留：

```bash
pgrep -af 'ros2|talker|nvilidar|ekf_node|slam_toolbox|rf2o|static_transform' | grep -v pgrep
```

> ℹ️ 見到 `ros2-daemon`（`ros2cli.daemon.daemonize`）唔使驚，係 `ros2` CLI 嘅背景 daemon，唔霸串口。想停都可以用 `ros2 daemon stop`。

---

## 6. 疑難排解

| 現象 | 處理 |
|------|------|
| `Failed to get Lidar Device Info` / `Lidar Data Invalid` | 有舊 node 霸住個串口 → 先清場（第 5 節）；如果反覆 kill/重開後 LiDAR 仲係唔醒 → USB reset（下面） |
| `/dev/nvilidar` 或 `/dev/hipnuc_imu` 唔見咗 | `lsusb` 睇裝置在唔在；重插 USB；udev 規則已裝好唔使再裝 |
| 收唔到 `/IMU_data` / `/scan` | 加 `--qos-reliability best_effort`（第 4 節） |
| SLAM 冇 `/map`、log 話 `queue is full` | 確認 RF2O/EKF 有出 `odom→base_link` TF：`ros2 run tf2_ros tf2_echo odom base_link` |
| `colcon build` 報 `No module named 'catkin_pkg'` | Hermes venv Python 問題，見第 2 節 ⚠️ |
| LiDAR 完全冇反應 | USB reset：`echo 0 \| sudo tee /sys/bus/usb/devices/3-3.2/authorized; sleep 2; echo 1 \| sudo tee /sys/bus/usb/devices/3-3.2/authorized`（裝置路徑可用 `lsusb` + `udevadm info` 搵） |

**USB reset 點搵路徑：**

```bash
for f in /sys/bus/usb/devices/*/idProduct; do d=$(dirname $f)
  [ "$(cat $d/idVendor 2>/dev/null)" = "2e3c" ] && echo "lidar at $d"
done
```

---

## 7. 一頁速查

```bash
source /opt/ros/humble/setup.bash
source ~/hipnuc_ros2/install/setup.bash

# 最常用：SLAM + RViz
ros2 launch hipnuc_imu imu_lidar_slam_view.launch.py

# 儲地圖（另開終端）
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: 'my_map'}}"

# Ctrl+C 收工
```
