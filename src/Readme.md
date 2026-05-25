# ROS 2 串口例程

本文件說明如何在 ROS 2 **Humble** 下讀取超核電子 IMU 與 GNSS 資料。工作空間提供 C++ 節點；執行對應的 launch 後，可在終端機或話題上查看輸出。

* **測試環境**：Ubuntu 22.04（建議）
* **ROS 版本**：ROS 2 Humble
* **測試裝置**：超核電子 IMU / GNSS 系列（本機範例：HI13S3-USB-000）

## 工作空間套件

| 套件 | 說明 |
|------|------|
| `hipnuc_imu` | USB 串口 IMU → `sensor_msgs/Imu` |
| `hipnuc_gnss` | GNSS / INS 串口 → `Imu` + `NavSatFix` |
| `hipnuc_imu_can` | CAN 介面 IMU（選用） |
| `nvilidar_ros2` | NVISTAR 2D 雷達（選用） |
| `rf2o_laser_odometry` | 雷射掃描 2D 里程計（選用） |
| `slam_toolbox`（系統套件） | 2D SLAM 建圖（選用，`hipnuc_imu` 提供 launch/config） |

## 安裝 USB-UART 驅動

Ubuntu 內建 CP210x 驅動，一般無需另外安裝。將模組以 USB 連上主機後，通常會出現 `/dev/ttyUSB*`（CP210x）。

**檢查裝置是否被辨識：**

1. 終端機執行 `ls /dev`，記下既有串口裝置。
2. 插入 USB 後再執行 `ls /dev`，應多出例如 `ttyUSB0`：

```shell
linux@ubuntu:~$ ls /dev
.....
ttyUSB0    .....
```

3. 建議將使用者加入 `dialout` 群組（登出後再登入生效）：

```shell
sudo usermod -aG dialout $USER
```

4. 若仍無讀寫權限，可暫時放寬（重插 USB 後可能需重做）：

```shell
sudo chmod 666 /dev/ttyUSB0
```

### 固定裝置名稱（建議）

HI13 USB 模組可安裝 udev 規則，建立穩定符號連結 `/dev/hipnuc_imu`：

```shell
/home/wingkit/hipnuc_ws/src/hipnuc_imu/startup/install_udev.sh
ls -l /dev/hipnuc_imu
```

## 編譯 hipnuc_ws 工作空間

```shell
source /opt/ros/humble/setup.bash
cd ~/hipnuc_ws
colcon build
source install/setup.bash
```

僅編譯 IMU 相關套件：

```shell
colcon build --packages-select hipnuc_lib_package hipnuc_imu
```

編譯成功範例：

```shell
Starting >>> hipnuc_imu
Finished <<< hipnuc_imu [0.44s]
Summary: 2 packages finished [0.61s]
```

## 修改串口鮑率與裝置路徑

1. 支援鮑率包含 **115200**、**460800**、**921600**。預設為 **115200**。
2. 編輯 `hipnuc_imu/config/hipnuc_config.yaml`（或 GNSS 的 `hipnuc_gnss/config/hipnuc_config.yaml`），修改後請重新 `colcon build`。

**IMU 設定範例（`hipnuc_imu/config/hipnuc_config.yaml`）：**

```yaml
IMU_publisher:
    ros__parameters:
        serial_port: "/dev/hipnuc_imu"
        baud_rate: 115200
        frame_id: "imu_link"
        imu_switch: true
        imu_topic: "/IMU_data"
        euler_switch: false
        euler_topic: "/euler_data"
        magnetic_switch: false
        magnetic_topic: "/magnetic_data"
```

> `imu_switch` 須為 `true` 才會發布 IMU 話題。

**GNSS 設定範例（`hipnuc_gnss/config/hipnuc_config.yaml`）：**

```yaml
INS_publisher:
    ros__parameters:
        serial_port: "/dev/ttyUSB0"
        baud_rate: 115200
        frame_id: "gnss_link"
        imu_topic: "/rawimu_data"
        nav_topic: "/NavSatFix_data"
```

### 提高輸出頻率（選用）

出廠預設約 **100 Hz**（115200）。若要更高頻率，需提高模組鮑率並設定輸出週期，例如：

```shell
# 執行後請將 yaml 中 baud_rate 改為 921600，再 colcon build
src/hipnuc_imu/startup/set_baud_921600.sh

# 還原 115200 / 100 Hz
src/hipnuc_imu/startup/set_baud_115200.sh
```

亦可使用超核官方 GUI 或《指令與編程手冊》中的 `SERIALCONFIG`、`LOG HI91 ONTIME` 等 ASCII 指令。

## 顯示資料

資料輸出方式：

1. `sensor_msgs/Imu`
2. `sensor_msgs/NavSatFix`（GNSS 套件）

### 輸出標準 Imu.msg

```shell
source /opt/ros/humble/setup.bash
source ~/hipnuc_ws/install/setup.bash
ros2 launch hipnuc_imu imu_spec_msg.launch.py
```

若找不到 launch 檔，請確認已 `source install/setup.bash`。

關閉終端機列印、僅啟動發布節點：

```shell
ros2 launch hipnuc_imu imu_spec_msg.launch.py listener:=false
```

成功後 listener 會週期性列印 IMU 內容，例如：

```text
header:
  frame_id: imu_link
orientation:
  x: -0.095125280320644379
  ...
linear_acceleration:
  x: 8.110355603694916482
  ...
```

另開終端機查看話題頻率（注意大小寫；IMU 須使用 **Best Effort**，見下方 [QoS：Best Effort](#qosbest-effort)）：

```shell
ros2 topic hz /IMU_data --qos-profile sensor_data
```

```shell
average rate: 100.032
  min: 0.008s max: 0.012s std dev: 0.00058s window: 102
```

### 輸出標準 NavSatFix.msg

```shell
source ~/hipnuc_ws/install/setup.bash
ros2 launch hipnuc_gnss nav_spec_msg.launch.py
```

成功後可看到類似：

```text
frame_id: gnss_link
latitude: 40.20336080
longitude: 116.24086010
altitude: 66.30100000
```

查看話題頻率：

```shell
ros2 topic hz /NavSatFix_data
```

### 同時啟動 IMU 與 NVISTAR 雷達

需已編譯 `nvilidar_ros2`，且雷達 udev 規則已安裝（`/dev/nvilidar`）：

```shell
ros2 launch hipnuc_imu imu_lidar_bringup.launch.py
```

可選：`imu_listener:=true` 開啟 IMU 示範列印。

查看雷達掃描（須 **Best Effort**）：

```shell
ros2 topic hz /scan --qos-profile sensor_data
```

### 雷射里程計（RF2O）+ IMU 融合（EKF）

`imu_lidar_bringup.launch.py` 預設啟動：

| 節點 | 輸入 | 輸出 |
|------|------|------|
| `rf2o_laser_odometry` | `/scan` | `/odom`（雷射里程，不發 TF） |
| `ekf_filter_node` | `/odom` + `/IMU_data` | `/odometry/filtered`、TF `odom`→`base_link` |

需已安裝：`sudo apt install ros-humble-robot-localization`

參數檔：

- EKF：`hipnuc_imu/config/ekf.yaml`（**100 Hz IMU + 10 Hz 雷射** 建議值，見檔頭註解）
- RF2O（EKF 模式）：`rf2o_laser_odometry/config/rf2o_params_ekf.yaml`（`publish_tf: false`）

**建議融合分工（2D）**

| 量 | 率 | 來源 | 說明 |
|----|-----|------|------|
| x, y | 10 Hz | RF2O | 平面位置主來源 |
| vx, vy | 10 Hz | RF2O twist | 介於兩次 scan 之間由 EKF 預測 |
| yaw | 100 Hz + 10 Hz | IMU AHRS + RF2O | IMU 為主；不融合 **vyaw**（靜止陀螺易飄） |
| 9-DOF 加速度 | — | 不進 EKF | `two_d_mode` 下不用 accel 推位置 |

**量測協方差（愈小愈信任）**：IMU `orientation_covariance[8]=0.006`；RF2O `pose[0,7]=0.01`、`pose[35]=0.12`。

**快速調參**

| 現象 | 調整 |
|------|------|
| 靜止航向飄 | 勿開 vyaw；RF2O `pose[35]` 加大；yaw `process_noise` 勿 > 0.1 |
| 轉彎與牆不符 | RF2O `pose[35]` 減小（如 `0.06`） |
| 位置跳 | RF2O `pose[0,7]` 加大 |
| 輸出延遲 | 保持 `frequency:100`、`predict_to_current_time:true` |

僅啟動 EKF：

```shell
ros2 launch hipnuc_imu ekf_localization.launch.py
```

僅 RF2O（自帶 TF，不融合 IMU）：

```shell
ros2 launch rf2o_laser_odometry rf2o_laser_odometry.launch.py
```

關閉 EKF、僅用 RF2O 發布 TF：

```shell
ros2 launch hipnuc_imu imu_lidar_bringup.launch.py enable_ekf:=false \
  rf2o_params_file:=$(ros2 pkg prefix rf2o_laser_odometry)/share/rf2o_laser_odometry/config/rf2o_params.yaml
```

關閉里程計（僅 IMU + 雷達）：

```shell
ros2 launch hipnuc_imu imu_lidar_bringup.launch.py enable_odom:=false enable_ekf:=false
```

查看融合里程計：

```shell
ros2 topic echo /odometry/filtered --once
ros2 topic hz /odometry/filtered
```

### RViz：2D 里程 + IMU 三維姿態

RF2O / EKF 輸出為 **平面**（x, y, yaw）。**完整 3D 姿態**來自 `/IMU_data` 的 `orientation`（四元數），可在 RViz 顯示：

| 顯示 | 內容 |
|------|------|
| **Imu** | `/IMU_data`：三軸姿態 + 角速度/加速度箭頭 |
| **TF** | `imu_link` 相對 `base_link` 的 3D 座標軸 |
| **Odometry** | `/odometry/filtered`：僅 2D 軌跡 |

一鍵啟動 bringup + RViz：

```shell
ros2 launch hipnuc_imu imu_lidar_bringup_view.launch.py
```

已在跑 bringup 時，另開終端：

```shell
rviz2 -d $(ros2 pkg prefix hipnuc_imu)/share/hipnuc_imu/config/imu_lidar.rviz
```

手動添加顯示時，**Imu**（`/IMU_data`）與 **LaserScan**（`/scan`）的 Topic → **Reliability** 均須選 **Best Effort**（詳見 [QoS：Best Effort](#qosbest-effort)）。**Fixed Frame** 設 `base_link` 或 `odom`；視角用 **Orbit** 可旋轉查看 3D。

查看原始四元數：

```shell
ros2 topic echo /IMU_data --field orientation --qos-profile sensor_data
```

### SLAM（slam_toolbox）

需已安裝：

```shell
sudo apt install ros-humble-slam-toolbox
```

**TF 鏈**（建圖時）：

```text
map → odom → base_link → laser_frame
              └→ imu_link
```

- `odom`→`base_link`：EKF（`/odometry/filtered`）
- `map`→`odom`：slam_toolbox（閉環修正）
- 輸入：`/scan`（Best Effort）、既有里程 TF

**一鍵啟動**（感測 + RF2O + EKF + SLAM）：

```shell
ros2 launch hipnuc_imu imu_lidar_slam.launch.py
```

**不含 IMU**（僅雷達 + RF2O 里程 + SLAM，RF2O 發布 `odom`→`base_link` TF）：

```shell
ros2 launch hipnuc_imu lidar_slam.launch.py
```

**不含 IMU + RViz**：

```shell
ros2 launch hipnuc_imu lidar_slam_view.launch.py
```

亦可沿用 bringup 關閉 IMU/EKF（需手動再開 SLAM）：

```shell
ros2 launch hipnuc_imu imu_lidar_bringup.launch.py enable_imu:=false enable_ekf:=false
# 另開終端
ros2 launch hipnuc_imu slam_toolbox.launch.py
```

**含 RViz 地圖（含 IMU）**（Fixed Frame = `map`）：

```shell
ros2 launch hipnuc_imu imu_lidar_slam_view.launch.py
```

僅啟動 SLAM（需另開終端已跑 `imu_lidar_bringup.launch.py`）：

```shell
ros2 launch hipnuc_imu slam_toolbox.launch.py
```

參數檔：`hipnuc_imu/config/slam_toolbox.yaml`（`base_link`、`/scan`、`max_laser_range: 30` 等，可依環境調整）。

儲存地圖：

```shell
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: 'my_map'}}"
```

查看地圖話題：

```shell
ros2 topic hz /map
```

> 建圖時請**緩慢移動**機器人，讓 RF2O/EKF 與 SLAM 同步；若 `/map` 空白，先確認 `ros2 run tf2_tools view_frames` 中 `map`→`odom`→`base_link`→`laser_frame` 完整。

**日誌出現 `Message Filter dropping message ... queue is full`**：slam_toolbox 在處理 `/scan` 前無法及時取得 `odom`→`base_link`（或 `base_link`→`laser_frame`）TF，掃描會被全部丟棄、無法建圖。本 repo 已在 `slam_toolbox.yaml` 調高 `transform_timeout`、`scan_queue_size`，並將 `transform_publish_period` 設為 `0.1`（避免過頻發 TF 拖慢掃描處理）；SLAM 節點預設延遲 2 秒啟動。請重新 `colcon build` 後再跑 `lidar_slam_view.launch.py`。

### QoS：Best Effort

本工作空間的 **IMU** 與 **雷達** 感測話題均以 `SensorDataQoS` 發布，對應 **Reliability = Best Effort**（適合高頻、可丟帧的感測資料）。

| 話題 | 訊息類型 | 發布端 QoS |
|------|----------|------------|
| `/IMU_data` | `sensor_msgs/Imu` | Best Effort |
| `/scan` | `sensor_msgs/LaserScan` | Best Effort |

`ros2 topic echo` / `ros2 topic hz` 預設常為 **Reliable**，與上述話題不相容時會**收不到資料**，或節點日誌出現 `RELIABILITY_QOS_POLICY` 警告。訂閱時請加上：

```shell
# 等同於 --qos-reliability best_effort
ros2 topic echo /IMU_data --qos-profile sensor_data
ros2 topic echo /scan --qos-profile sensor_data
ros2 topic hz /IMU_data --qos-profile sensor_data
ros2 topic hz /scan --qos-profile sensor_data
```

**RViz2**：在 **Imu**（`/IMU_data`）與 **LaserScan**（`/scan`）顯示的 Topic 設定中，將 **Reliability Policy** 設為 **Best Effort**（勿用預設 Reliable）。本 repo 的 `imu_lidar.rviz` 已預設 Best Effort。

**節點訂閱**：`rf2o_laser_odometry` 已對齊 `/scan` 的 Best Effort；`robot_localization` 的 EKF 訂閱 `/IMU_data` 時由套件內部處理，一般無需手動設定。

> **Odometry**（`/odom`、`/odometry/filtered`）多為 **Reliable**，與感測話題不同；在 RViz 的 Odometry 顯示可維持 Reliable。

## 常見問題

| 現象 | 處理方式 |
|------|----------|
| 找不到 `/dev/ttyUSB0` | 檢查 USB 連線、`lsusb` 是否出現 CP210x |
| 無法開啟串口 | 加入 `dialout` 或使用 `chmod` / udev 規則 |
| 無 `/IMU_data` 資料 | 確認 `imu_switch: true`、鮑率與模組一致 |
| launch 找不到套件 | `source /opt/ros/humble/setup.bash` 與 `install/setup.bash` |
| `/scan` 有資料但無 `/odom` | 確認 `enable_odom:=true`；先確認能 `ros2 topic hz /scan --qos-profile sensor_data` |
| 收不到 `/IMU_data` 或 `/scan` | 訂閱須 **Best Effort**：`--qos-profile sensor_data`（見 [QoS：Best Effort](#qosbest-effort)） |
| QoS 不相容警告 | RViz / `ros2 topic` 對 `/IMU_data`、`/scan` 均改為 **Best Effort**，勿用 Reliable |
| SLAM 無 `/map` 或 TF 斷裂 | `lidar_slam` 不需 EKF；確認 RF2O 發布 `odom`→`base_link`；`ros2 topic hz /scan --qos-profile sensor_data`；若日誌為 queue full，見上文 SLAM 故障排除 |
| RViz 看不到雷射/地圖 | `lidar_slam.rviz` 固定座標為 `odom`；`/scan` 須 **Best Effort**；有 `/map` 後可改 Fixed Frame 為 `map` |
