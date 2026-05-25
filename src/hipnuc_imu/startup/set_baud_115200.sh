#!/bin/bash
# Restore Hipnuc IMU to 115200 baud and 100 Hz HI91 output.
set -euo pipefail

PORT="${1:-/dev/hipnuc_imu}"
CURRENT_BAUD="${2:-921600}"
NEW_BAUD=115200

send_cmd() {
  local baud="$1"
  shift
  stty -F "$PORT" "$baud" raw -echo min 0 time 10
  while [[ $# -gt 0 ]]; do
    printf '%s\r\n' "$1" > "$PORT"
    sleep 0.15
    shift
  done
}

send_cmd "$CURRENT_BAUD" "LOG DISABLE" "SERIALCONFIG ${NEW_BAUD}"
send_cmd "$NEW_BAUD" "LOG HI91 ONTIME 0.01" "SAVECONFIG" "LOG ENABLE"
echo "Restored: baud=${NEW_BAUD}, HI91 100 Hz. Set hipnuc_config.yaml baud_rate: ${NEW_BAUD}."
