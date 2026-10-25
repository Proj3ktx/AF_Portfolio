import kinematics from "./lab/robot_kinematics.py?raw";
import openLoop from "./lab/open_loop_demo.py?raw";
import pickup from "./lab/mobile_pickup_experiment.py?raw";
import pickupConfig from "./lab/pickup_experiment.yaml?raw";
import turtlebot from "./lab/waypoint_sensor_experiment.py?raw";
import turtlebotConfig from "./lab/turtlebot_experiment.yaml?raw";
import turtlebotRun from "./lab/turtlebot_run.sh?raw";

export type LabFile = {
  id: string;
  group: string;
  name: string;
  path: string;
  lang: "python" | "yaml" | "bash";
  note: string;
  source: string;
};

export const labFiles: readonly LabFile[] = [
  {
    id: "waypoint",
    group: "TurtleBot3 A–B–A",
    name: "waypoint_sensor_experiment.py",
    path: "TurtleBot3 ABA Source/ros2_ws/src/co_op_robot_experiment",
    lang: "python",
    note: "Python ROS 2 node for the simulated TurtleBot3. Follows waypoints using odometry feedback and records pose, LiDAR, IMU, and camera data.",
    source: turtlebot,
  },
  {
    id: "turtlebot-config",
    group: "TurtleBot3 A–B–A",
    name: "experiment.yaml",
    path: "TurtleBot3 ABA Source/config",
    lang: "yaml",
    note: "The A–B–A route through a clear corridor, with the speed limits and position tolerances used in the September 3 simulation.",
    source: turtlebotConfig,
  },
  {
    id: "turtlebot-run",
    group: "TurtleBot3 A–B–A",
    name: "run_full_experiment.sh",
    path: "TurtleBot3 ABA Source",
    lang: "bash",
    note: "Launch script for Gazebo, rosbag recording, and the waypoint controller on Ubuntu. Saves each trial in its own run directory.",
    source: turtlebotRun,
  },
  {
    id: "pickup",
    group: "Pick and drop lab",
    name: "mobile_pickup_experiment.py",
    path: "Drexel_ABA_Pick_Drop_Lab",
    lang: "python",
    note: "Simulation controller for the single-arm pickup lab. Follows a five-waypoint route, checks the pickup position, and returns the object to A using a simplified grasp model.",
    source: pickup,
  },
  {
    id: "kinematics",
    group: "Pick and drop lab",
    name: "robot_kinematics.py",
    path: "Drexel_ABA_Pick_Drop_Lab",
    lang: "python",
    note: "Planar arm model based on joint centers in the supplied single-arm CAD. Uses inverse kinematics to calculate carry, hover, and pickup poses.",
    source: kinematics,
  },
  {
    id: "pickup-config",
    group: "Pick and drop lab",
    name: "experiment.yaml",
    path: "Drexel_ABA_Pick_Drop_Lab/config",
    lang: "yaml",
    note: "Configuration for the pickup lab. Students change the two intermediate waypoint pairs to test a detour while keeping the pickup and drop-off stations fixed.",
    source: pickupConfig,
  },
  {
    id: "open-loop",
    group: "Pick and drop lab",
    name: "open_loop_demo.py",
    path: "Drexel_ABA_Pick_Drop_Lab",
    lang: "python",
    note: "A short timed-motion demo without pose feedback, separate from the waypoint controller. It requires explicit simulation confirmation before running.",
    source: openLoop,
  },
];

export const labGroups = [...new Set(labFiles.map((file) => file.group))];

export const deliverables = [
  "Co-op review presentation",
  "ROS 2 and TurtleBot3 worksheet",
  "A–B–A pick and drop handout",
  "TurtleBot3 A–B–A report",
  "Mobile robot pickup and SLAM report",
  "CAD handoff note",
] as const;

export const cadViews = [
  {
    src: "lab/robot-isometric.png",
    alt: "Isometric CAD view of the Revision B two-arm mobile robot, with a mecanum base, pedestal, sensor head, and two arms.",
    caption: "Two-arm robot CAD overview",
  },
  {
    src: "lab/sensor-head.png",
    alt: "CAD detail of the sensor head: LiDAR on the lid, a camera on the front, and both arm bases.",
    caption: "Sensor head and arm bases",
  },
  {
    src: "lab/mecanum-wheel.png",
    alt: "CAD detail of one mecanum wheel module, with the roller star and the motor behind it.",
    caption: "Mecanum wheel module",
  },
] as const;

export const cadModules = [
  "Chassis plate",
  "Four drive modules",
  "Lower frame and equipment",
  "Body shell, lid, and service covers",
  "Pedestal and shoulder deck",
  "Camera head and LiDAR lid",
  "Left and right arms",
  "Upper wiring and controllers",
] as const;
