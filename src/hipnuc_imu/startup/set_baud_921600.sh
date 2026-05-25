#!/bin/bash
# Configure Hipnuc IMU: 921600 baud + 500 Hz HI91 output (saved to flash).
set -euo pipefail

PORT="${1:-/dev/hipnuc_imu}"
OLD_BAUD="${2:-115200}"
NEW_BAUD=921600
# 0.002 s = 500 Hz (within HI91 @ 921600 capability per manual)
OUTPUT_PERIOD=0.002

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

if [[ ! -e "$PORT" ]]; then
  echo "Error: $PORT not found." >&2
  exit 1
fi

echo "Stopping output and setting baud on ${PORT}..."
send_cmd "$OLD_BAUD" "LOG DISABLE" "SERIALCONFIG ${NEW_BAUD}"

echo "Configuring ${OUTPUT_PERIOD}s HI91 period at ${NEW_BAUD}..."
send_cmd "$NEW_BAUD" \
  "LOG HI91 ONTIME ${OUTPUT_PERIOD}" \
  "SAVECONFIG" \
  "LOG ENABLE"

echo "Done. Module: baud=${NEW_BAUD}, HI91 period=${OUTPUT_PERIOD}s (~500 Hz)."
echo "Use hipnuc_config.yaml with baud_rate: ${NEW_BAUD}"
