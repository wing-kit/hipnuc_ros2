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

另開終端機查看話題頻率（注意大小寫）：

```shell
ros2 topic hz /IMU_data
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

## 常見問題

| 現象 | 處理方式 |
|------|----------|
| 找不到 `/dev/ttyUSB0` | 檢查 USB 連線、`lsusb` 是否出現 CP210x |
| 無法開啟串口 | 加入 `dialout` 或使用 `chmod` / udev 規則 |
| 無 `/IMU_data` 資料 | 確認 `imu_switch: true`、鮑率與模組一致 |
| launch 找不到套件 | `source /opt/ros/humble/setup.bash` 與 `install/setup.bash` |
