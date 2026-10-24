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
    note: "ROS 2 node. Drives the TurtleBot3 through waypoints and records pose, scan, IMU, and camera samples.",
    source: turtlebot,
  },
  {
    id: "turtlebot-config",
    group: "TurtleBot3 A–B–A",
    name: "experiment.yaml",
    path: "TurtleBot3 ABA Source/config",
    lang: "yaml",
    note: "Point A to Point B and back through the clear corridor, with the speed and tolerance limits used on September 3.",
    source: turtlebotConfig,
  },
  {
    id: "turtlebot-run",
    group: "TurtleBot3 A–B–A",
    name: "run_full_experiment.sh",
    path: "TurtleBot3 ABA Source",
    lang: "bash",
    note: "Ubuntu launch for Gazebo, the rosbag, and the waypoint node. One run directory per trial.",
    source: turtlebotRun,
  },
  {
    id: "pickup",
    group: "Pick and drop lab",
    name: "mobile_pickup_experiment.py",
    path: "Drexel_ABA_Pick_Drop_Lab",
    lang: "python",
    note: "The later controller. Five waypoints, A to B, an ideal grasp, then back to A. Simulation only.",
    source: pickup,
  },
  {
    id: "kinematics",
    group: "Pick and drop lab",
    name: "robot_kinematics.py",
    path: "Drexel_ABA_Pick_Drop_Lab",
    lang: "python",
    note: "Planar arm model taken from the CAD hinge centers. Inverse kinematics for carry, hover, and pick.",
    source: kinematics,
  },
  {
    id: "pickup-config",
    group: "Pick and drop lab",
    name: "experiment.yaml",
    path: "Drexel_ABA_Pick_Drop_Lab/config",
    lang: "yaml",
    note: "Stations stay at A and B. The lesson edits only the two middle pairs.",
    source: pickupConfig,
  },
  {
    id: "open-loop",
    group: "Pick and drop lab",
    name: "open_loop_demo.py",
    path: "Drexel_ABA_Pick_Drop_Lab",
    lang: "python",
    note: "A short timed move with no pose feedback, kept separate from the waypoint controller. It refuses to run unless simulation is confirmed.",
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
    caption: "Revision B, parked envelope",
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
