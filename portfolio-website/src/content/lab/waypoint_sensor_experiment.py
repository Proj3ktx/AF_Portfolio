#!/usr/bin/env python3
"""Drive TurtleBot3 through coordinates while recording pose and sensor data."""

import csv
import json
import math
import os
from pathlib import Path
import time

import cv2
from cv_bridge import CvBridge
import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu, LaserScan


def clamp(value, low, high):
    return max(low, min(high, value))


def wrap_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_from_quaternion(q):
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny, cosy)


class WaypointSensorExperiment(Node):
    def __init__(self):
        super().__init__('waypoint_sensor_experiment')

        self.declare_parameter('output_dir', '/tmp/co_op_robot_experiment')
        self.declare_parameter('waypoints_flat', [-2.0, -0.5, -2.0, 1.65])
        self.declare_parameter('max_linear_speed', 0.22)
        self.declare_parameter('max_angular_speed', 1.20)
        self.declare_parameter('max_linear_accel', 0.18)
        self.declare_parameter('max_linear_jerk', 0.45)
        self.declare_parameter('max_angular_accel', 1.50)
        self.declare_parameter('max_angular_jerk', 4.00)
        self.declare_parameter('position_tolerance', 0.08)
        self.declare_parameter('heading_tolerance', 0.07)
        self.declare_parameter('obstacle_stop_distance', 0.30)
        self.declare_parameter('camera_sample_period', 1.0)
        self.declare_parameter('max_duration_sec', 150.0)

        flat = list(self.get_parameter('waypoints_flat').value)
        if len(flat) < 4 or len(flat) % 2:
            raise ValueError('waypoints_flat must contain at least two x,y pairs')
        self.waypoints = [(float(flat[i]), float(flat[i + 1])) for i in range(0, len(flat), 2)]
        self.max_linear_speed = float(self.get_parameter('max_linear_speed').value)
        self.max_angular_speed = float(self.get_parameter('max_angular_speed').value)
        self.max_linear_accel = float(self.get_parameter('max_linear_accel').value)
        self.max_linear_jerk = float(self.get_parameter('max_linear_jerk').value)
        self.max_angular_accel = float(self.get_parameter('max_angular_accel').value)
        self.max_angular_jerk = float(self.get_parameter('max_angular_jerk').value)
        self.position_tolerance = float(self.get_parameter('position_tolerance').value)
        self.heading_tolerance = float(self.get_parameter('heading_tolerance').value)
        self.obstacle_stop_distance = float(self.get_parameter('obstacle_stop_distance').value)
        self.camera_sample_period = float(self.get_parameter('camera_sample_period').value)
        self.max_duration_sec = float(self.get_parameter('max_duration_sec').value)

        self.output_dir = Path(str(self.get_parameter('output_dir').value)).expanduser()
        self.camera_dir = self.output_dir / 'camera_frames'
        self.camera_dir.mkdir(parents=True, exist_ok=True)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.camera_sample_pub = self.create_publisher(Image, '/experiment/camera_sample', 2)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 30)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.create_subscription(Imu, '/imu', self.imu_callback, 30)
        self.create_subscription(Image, '/camera/image_raw', self.camera_callback, 5)

        self.bridge = CvBridge()
        self.pose = None
        self.actual_velocity = (0.0, 0.0)
        self.latest_front_range = math.inf
        self.latest_scan_min = math.inf
        self.current_waypoint = 1
        self.state = 'WAITING_FOR_ODOM'
        self.start_wall = time.monotonic()
        self.start_ros = None
        self.last_control_wall = time.monotonic()
        self.last_camera_wall = -math.inf
        self.last_log_ros = -math.inf
        self.finished = False
        self.saved = False
        self.finish_reason = ''

        self.command_linear = 0.0
        self.command_angular = 0.0
        self.linear_accel = 0.0
        self.angular_accel = 0.0
        self.linear_jerk = 0.0
        self.angular_jerk = 0.0

        self.trajectory_rows = []
        self.lidar_rows = []
        self.imu_rows = []
        self.camera_rows = []
        self.waypoint_events = []
        self.path_length = 0.0
        self.previous_xy = None

        self.timer = self.create_timer(0.05, self.control_step)
        self.get_logger().info('Experiment ready. Waiting for odometry...')
        self.get_logger().info(f'Coordinates: {self.waypoints}')

    def ros_seconds(self, stamp=None):
        if stamp is None:
            return self.get_clock().now().nanoseconds / 1e9
        return float(stamp.sec) + float(stamp.nanosec) / 1e9

    def elapsed(self, stamp_seconds=None):
        now = self.ros_seconds() if stamp_seconds is None else stamp_seconds
        if self.start_ros is None:
            self.start_ros = now
        return max(0.0, now - self.start_ros)

    def odom_callback(self, msg):
        stamp = self.ros_seconds(msg.header.stamp)
        x = float(msg.pose.pose.position.x)
        y = float(msg.pose.pose.position.y)
        yaw = yaw_from_quaternion(msg.pose.pose.orientation)
        self.pose = (x, y, yaw)
        self.actual_velocity = (
            float(msg.twist.twist.linear.x),
            float(msg.twist.twist.angular.z),
        )

        if self.previous_xy is not None:
            self.path_length += math.hypot(x - self.previous_xy[0], y - self.previous_xy[1])
        self.previous_xy = (x, y)

        # Keep the CSV near 20 Hz even though odometry normally arrives at 30 Hz.
        elapsed = self.elapsed(stamp)
        if elapsed - self.last_log_ros >= 0.045:
            target = self.waypoints[min(self.current_waypoint, len(self.waypoints) - 1)]
            self.trajectory_rows.append([
                elapsed, x, y, yaw,
                self.actual_velocity[0], self.actual_velocity[1],
                self.command_linear, self.command_angular,
                self.linear_accel, self.angular_accel,
                self.linear_jerk, self.angular_jerk,
                self.current_waypoint, target[0], target[1], self.state,
            ])
            self.last_log_ros = elapsed

    def scan_callback(self, msg):
        ranges = np.asarray(msg.ranges, dtype=float)
        valid = np.isfinite(ranges)
        valid &= ranges >= float(msg.range_min)
        valid &= ranges <= float(msg.range_max)
        valid_values = ranges[valid]

        if valid_values.size:
            scan_min = float(np.min(valid_values))
            scan_mean = float(np.mean(valid_values))
        else:
            scan_min = math.inf
            scan_mean = math.nan

        angles = float(msg.angle_min) + np.arange(ranges.size) * float(msg.angle_increment)
        front_mask = valid & (np.abs(angles) <= math.radians(20.0))
        front_values = ranges[front_mask]
        front_min = float(np.min(front_values)) if front_values.size else math.inf

        self.latest_scan_min = scan_min
        self.latest_front_range = front_min
        self.lidar_rows.append([
            self.elapsed(self.ros_seconds(msg.header.stamp)),
            scan_min, front_min, scan_mean, int(valid_values.size),
        ])

    def imu_callback(self, msg):
        self.imu_rows.append([
            self.elapsed(self.ros_seconds(msg.header.stamp)),
            float(msg.angular_velocity.x), float(msg.angular_velocity.y), float(msg.angular_velocity.z),
            float(msg.linear_acceleration.x), float(msg.linear_acceleration.y), float(msg.linear_acceleration.z),
        ])

    def camera_callback(self, msg):
        now = time.monotonic()
        if now - self.last_camera_wall < self.camera_sample_period:
            return
        self.last_camera_wall = now
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            elapsed = self.elapsed(self.ros_seconds(msg.header.stamp))
            filename = f'camera_{len(self.camera_rows):03d}_{elapsed:07.2f}s.png'
            path = self.camera_dir / filename
            if not cv2.imwrite(str(path), frame):
                raise RuntimeError('cv2.imwrite returned false')
            self.camera_rows.append([elapsed, filename, int(msg.width), int(msg.height), msg.encoding])
            self.camera_sample_pub.publish(msg)
        except Exception as exc:
            self.get_logger().warning(f'Could not save camera frame: {exc}')

    def ramp_axis(self, desired_velocity, velocity, acceleration, max_accel, max_jerk, dt):
        required_accel = clamp((desired_velocity - velocity) / max(dt, 1e-4), -max_accel, max_accel)
        old_accel = acceleration
        accel_delta = clamp(required_accel - acceleration, -max_jerk * dt, max_jerk * dt)
        acceleration = clamp(acceleration + accel_delta, -max_accel, max_accel)
        velocity += acceleration * dt
        if (desired_velocity - velocity) * (desired_velocity - (velocity - acceleration * dt)) <= 0.0:
            velocity = desired_velocity
        jerk = (acceleration - old_accel) / max(dt, 1e-4)
        return velocity, acceleration, jerk

    def publish_smoothed_command(self, desired_linear, desired_angular, dt):
        self.command_linear, self.linear_accel, self.linear_jerk = self.ramp_axis(
            desired_linear, self.command_linear, self.linear_accel,
            self.max_linear_accel, self.max_linear_jerk, dt,
        )
        self.command_angular, self.angular_accel, self.angular_jerk = self.ramp_axis(
            desired_angular, self.command_angular, self.angular_accel,
            self.max_angular_accel, self.max_angular_jerk, dt,
        )
        # The jerk-limited acceleration can lag when the desired speed drops.
        # Enforce the absolute velocity limits after smoothing so the command
        # never exceeds the configured robot limits.
        self.command_linear = clamp(
            self.command_linear, -self.max_linear_speed, self.max_linear_speed
        )
        self.command_angular = clamp(
            self.command_angular, -self.max_angular_speed, self.max_angular_speed
        )
        cmd = Twist()
        cmd.linear.x = float(self.command_linear)
        cmd.angular.z = float(self.command_angular)
        self.cmd_pub.publish(cmd)

    def stop_now(self):
        self.command_linear = 0.0
        self.command_angular = 0.0
        self.linear_accel = 0.0
        self.angular_accel = 0.0
        self.linear_jerk = 0.0
        self.angular_jerk = 0.0
        self.cmd_pub.publish(Twist())

    def control_step(self):
        now = time.monotonic()
        dt = clamp(now - self.last_control_wall, 0.005, 0.20)
        self.last_control_wall = now

        if self.finished:
            self.stop_now()
            if not self.saved:
                self.save_results()
            return

        if now - self.start_wall > self.max_duration_sec:
            self.finish('TIMEOUT')
            return

        if self.pose is None:
            self.state = 'WAITING_FOR_ODOM'
            self.stop_now()
            return

        if self.current_waypoint >= len(self.waypoints):
            self.finish('COMPLETED')
            return

        x, y, yaw = self.pose
        tx, ty = self.waypoints[self.current_waypoint]
        dx, dy = tx - x, ty - y
        distance = math.hypot(dx, dy)
        desired_heading = math.atan2(dy, dx)
        heading_error = wrap_angle(desired_heading - yaw)

        if distance <= self.position_tolerance:
            self.waypoint_events.append({
                'waypoint_index': self.current_waypoint,
                'target_x_m': tx,
                'target_y_m': ty,
                'actual_x_m': x,
                'actual_y_m': y,
                'position_error_m': distance,
                'time_s': self.elapsed(),
            })
            self.get_logger().info(
                f'Reached waypoint {self.current_waypoint}: '
                f'position=({x:.3f}, {y:.3f}), target=({tx:.3f}, {ty:.3f})'
            )
            self.current_waypoint += 1
            self.state = 'WAYPOINT_REACHED'
            self.publish_smoothed_command(0.0, 0.0, dt)
            return

        if self.latest_front_range < self.obstacle_stop_distance:
            self.state = 'OBSTACLE_STOP'
            self.publish_smoothed_command(0.0, 0.0, dt)
            return

        if abs(heading_error) > 0.25:
            self.state = 'TURNING'
            desired_linear = 0.0
            desired_angular = clamp(2.2 * heading_error, -self.max_angular_speed, self.max_angular_speed)
        else:
            self.state = 'DRIVING'
            heading_scale = max(0.15, math.cos(heading_error))
            desired_linear = min(self.max_linear_speed, 0.75 * distance) * heading_scale
            desired_angular = clamp(2.0 * heading_error, -self.max_angular_speed, self.max_angular_speed)

        self.publish_smoothed_command(desired_linear, desired_angular, dt)

    def finish(self, reason):
        if self.finished:
            return
        self.finish_reason = reason
        self.finished = True
        self.state = reason
        self.stop_now()
        self.get_logger().info(f'Experiment finished: {reason}')

    @staticmethod
    def write_csv(path, header, rows):
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def save_results(self):
        self.stop_now()
        self.write_csv(
            self.output_dir / 'trajectory.csv',
            ['time_s', 'x_m', 'y_m', 'yaw_rad', 'actual_linear_mps', 'actual_angular_rps',
             'cmd_linear_mps', 'cmd_angular_rps', 'cmd_linear_accel_mps2',
             'cmd_angular_accel_rps2', 'cmd_linear_jerk_mps3', 'cmd_angular_jerk_rps3',
             'waypoint_index', 'target_x_m', 'target_y_m', 'state'],
            self.trajectory_rows,
        )
        self.write_csv(
            self.output_dir / 'lidar.csv',
            ['time_s', 'minimum_range_m', 'front_minimum_range_m', 'mean_valid_range_m', 'valid_points'],
            self.lidar_rows,
        )
        self.write_csv(
            self.output_dir / 'imu.csv',
            ['time_s', 'angular_x_rps', 'angular_y_rps', 'angular_z_rps',
             'linear_accel_x_mps2', 'linear_accel_y_mps2', 'linear_accel_z_mps2'],
            self.imu_rows,
        )
        self.write_csv(
            self.output_dir / 'camera_frames.csv',
            ['time_s', 'filename', 'width_px', 'height_px', 'encoding'],
            self.camera_rows,
        )
        self.write_csv(
            self.output_dir / 'waypoint_events.csv',
            ['waypoint_index', 'target_x_m', 'target_y_m', 'actual_x_m', 'actual_y_m',
             'position_error_m', 'time_s'],
            [[event[key] for key in (
                'waypoint_index', 'target_x_m', 'target_y_m', 'actual_x_m', 'actual_y_m',
                'position_error_m', 'time_s'
            )] for event in self.waypoint_events],
        )

        final_pose = self.pose if self.pose is not None else (math.nan, math.nan, math.nan)
        final_target = self.waypoints[-1]
        final_error = math.hypot(final_pose[0] - final_target[0], final_pose[1] - final_target[1])
        duration = self.trajectory_rows[-1][0] if self.trajectory_rows else 0.0
        maximum = lambda index: max(
            (abs(float(row[index])) for row in self.trajectory_rows), default=0.0
        )
        finite_scan_minima = [
            float(row[1]) for row in self.lidar_rows if math.isfinite(float(row[1]))
        ]
        finite_front_minima = [
            float(row[2]) for row in self.lidar_rows if math.isfinite(float(row[2]))
        ]
        summary = {
            'status': self.finish_reason,
            'coordinate_frame': 'odom (matches Gazebo world pose at spawn)',
            'planned_waypoints_xy_m': self.waypoints,
            'final_pose': {'x_m': final_pose[0], 'y_m': final_pose[1], 'yaw_rad': final_pose[2]},
            'final_target': {'x_m': final_target[0], 'y_m': final_target[1]},
            'final_position_error_m': final_error,
            'duration_s': duration,
            'measured_path_length_m': self.path_length,
            'trajectory_samples': len(self.trajectory_rows),
            'lidar_samples': len(self.lidar_rows),
            'imu_samples': len(self.imu_rows),
            'camera_frames_saved': len(self.camera_rows),
            'reached_waypoints': self.waypoint_events,
            'observed_motion': {
                'max_abs_commanded_linear_speed_mps': maximum(6),
                'max_abs_commanded_angular_speed_rps': maximum(7),
                'max_abs_commanded_linear_accel_mps2': maximum(8),
                'max_abs_commanded_angular_accel_rps2': maximum(9),
                'max_abs_commanded_linear_jerk_mps3': maximum(10),
                'max_abs_commanded_angular_jerk_rps3': maximum(11),
            },
            'observed_lidar': {
                'minimum_full_scan_range_m': min(finite_scan_minima, default=None),
                'minimum_front_range_m': min(finite_front_minima, default=None),
            },
            'limits': {
                'max_linear_speed_mps': self.max_linear_speed,
                'max_angular_speed_rps': self.max_angular_speed,
                'max_linear_accel_mps2': self.max_linear_accel,
                'max_linear_jerk_mps3': self.max_linear_jerk,
                'max_angular_accel_rps2': self.max_angular_accel,
                'max_angular_jerk_rps3': self.max_angular_jerk,
                'obstacle_stop_distance_m': self.obstacle_stop_distance,
            },
        }
        with (self.output_dir / 'summary.json').open('w', encoding='utf-8') as handle:
            json.dump(summary, handle, indent=2)
        (self.output_dir / 'EXPERIMENT_FINISHED').write_text(self.finish_reason + '\n', encoding='utf-8')
        self.saved = True
        self.get_logger().info(
            f'Saved {len(self.trajectory_rows)} trajectory, {len(self.lidar_rows)} LiDAR, '
            f'{len(self.imu_rows)} IMU, and {len(self.camera_rows)} camera samples to {self.output_dir}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = WaypointSensorExperiment()
    try:
        while rclpy.ok() and not node.saved:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        node.finish('INTERRUPTED')
        node.save_results()
    finally:
        node.stop_now()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
