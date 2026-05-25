#!/bin/bash
# Install udev rule for Hipnuc CP210x IMU (creates /dev/hipnuc_imu symlink)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo cp "${SCRIPT_DIR}/99-hipnuc_imu_usb.rules" /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "Done. Replug USB or wait a moment, then check: ls -l /dev/hipnuc_imu /dev/ttyUSB0"
