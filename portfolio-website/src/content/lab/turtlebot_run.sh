#!/usr/bin/env bash
set -eo pipefail

# This script is intended to run inside Ubuntu/WSL, not PowerShell.
source /usr/share/gazebo/setup.sh
source /opt/ros/humble/setup.bash
source "$HOME/turtlebot3_ws/install/setup.bash"
source "$HOME/co_op_experiment_ws/install/setup.bash"
set -u

export TURTLEBOT3_MODEL=waffle_pi
export RCUTILS_COLORIZED_OUTPUT=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$HOME/co_op_experiment_ws/src/co_op_robot_experiment/config/experiment.yaml"
RESULTS_ROOT="${1:-$SCRIPT_DIR/results}"
RUN_DIR="$RESULTS_ROOT/run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_DIR"

GAZEBO_PID=""
BAG_PID=""

cleanup() {
  set +e
  if [[ -n "$BAG_PID" ]] && kill -0 "$BAG_PID" 2>/dev/null; then
    kill -INT -- "-$BAG_PID"
    wait "$BAG_PID"
  fi
  if [[ -n "$GAZEBO_PID" ]] && kill -0 "$GAZEBO_PID" 2>/dev/null; then
    kill -INT -- "-$GAZEBO_PID"
    wait "$GAZEBO_PID"
  fi
}
trap cleanup EXIT INT TERM

wait_for_topic() {
  local topic="$1"
  local timeout_s="$2"
  local start
  start="$(date +%s)"
  until ros2 topic type "$topic" >/dev/null 2>&1; do
    if (( $(date +%s) - start >= timeout_s )); then
      echo "Timed out waiting for $topic" >&2
      return 1
    fi
    sleep 1
  done
  echo "Ready: $topic ($(ros2 topic type "$topic"))"
}

echo "Run directory: $RUN_DIR"
if pgrep -x gzserver >/dev/null 2>&1 || pgrep -x gzclient >/dev/null 2>&1; then
  echo "Gazebo is already running. Close the existing simulation before starting a recorded run." >&2
  exit 2
fi
echo "Starting Gazebo at x=-2.0 m, y=-0.5 m..."
setsid ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py \
  x_pose:=-2.0 y_pose:=-0.5 >"$RUN_DIR/gazebo.log" 2>&1 &
GAZEBO_PID=$!

wait_for_topic /odom 45
wait_for_topic /scan 45
wait_for_topic /imu 45
wait_for_topic /camera/image_raw 45

echo "Starting rosbag recorder..."
setsid ros2 bag record \
  --compression-mode file --compression-format zstd \
  -o "$RUN_DIR/rosbag" \
  /odom /cmd_vel /scan /imu /joint_states /tf /tf_static \
  /camera/camera_info /experiment/camera_sample \
  >"$RUN_DIR/rosbag.log" 2>&1 &
BAG_PID=$!
sleep 2

echo "Running waypoint and sensor experiment..."
ros2 run co_op_robot_experiment run_experiment \
  --ros-args --params-file "$CONFIG" -p output_dir:="$RUN_DIR" \
  2>&1 | tee "$RUN_DIR/controller.log"

kill -INT "$BAG_PID"
wait "$BAG_PID" || true
BAG_PID=""

echo "Creating plots..."
ros2 run co_op_robot_experiment plot_results --run-dir "$RUN_DIR" \
  2>&1 | tee "$RUN_DIR/plot.log"

basename "$RUN_DIR" > "$RESULTS_ROOT/LATEST_RUN.txt"
echo "Experiment complete: $RUN_DIR"
