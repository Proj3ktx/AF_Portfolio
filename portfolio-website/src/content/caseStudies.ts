export type CaseStudy = {
  id: string;
  category: string;
  title: string;
  overview: string;
  tools: readonly string[];
  goal: string;
  contributions: readonly string[];
  outcome: string;
  lesson: string;
  image?: {
    src: string;
    alt: string;
    caption: string;
    width: number;
    height: number;
  };
};

export const caseStudies: readonly CaseStudy[] = [
  {
    id: "two-arm-cad",
    category: "Mechanical design",
    title: "Two-arm mobile robot CAD",
    overview:
      "I developed and refined the layout for a two-arm mobile robot, then prepared the CAD files for engineering review. The work pushed me to think about how the structure, equipment, and service access fit together.",
    tools: ["CAD design", "SolidWorks and STEP", "18 modules"],
    goal:
      "My goal was to develop a detailed design that the engineering team could review and adjust before fabrication.",
    contributions: [
      "I worked on the base, body, upper structure, arm layout, and sensor supports, including space for equipment and access for assembly and maintenance.",
      "I refined support and retention details, cable passages, removable covers, and static clearances. I combined custom geometry with existing arm and sensor references.",
      "I organized the handoff into 18 modules and documented the reference sources, fit checks, and questions that still needed answers.",
    ],
    outcome:
      "The Revision B handoff includes SolidWorks assembly and part files, STEP exports, and review notes. It is a design-review model. Wheel sizing was not an exact measurement, and the mounting interfaces, structural loads, materials, and full-motion clearances still need final verification before fabrication.",
    lesson:
      "A model has to do more than look good. I had to account for component space, sensor placement, clearances, and how someone would reach a part later. I also learned to make the remaining questions clear enough for another person to continue the work.",
  },
  {
    id: "turtlebot-experiment",
    category: "Python and ROS 2 simulation",
    title: "TurtleBot3 A–B–A experiment",
    overview:
      "I used Python and ROS 2 to run a TurtleBot3 from point A to point B and back in Gazebo. I recorded its motion and sensor data so I could check what happened during the run.",
    tools: ["Python", "ROS 2", "Gazebo", "Sensor data"],
    goal:
      "I wanted a repeatable experiment that connected the robot’s movement with data a student could inspect and explain.",
    contributions: [
      "I worked on waypoint control using odometry feedback, which tracks the robot’s estimated position. I configured speed, acceleration, and jerk limits to smooth the motion commands.",
      "I recorded position, LiDAR, IMU, and sampled camera data, with a separate output folder for each run.",
      "I used Python plots, waypoint logs, CSV files, and a ROS bag recording to compare the planned route with the recorded motion.",
    ],
    outcome:
      "The recorded run completed the A–B–A route and produced motion data, sensor records, and plots for review. The figure below comes from that simulation run; it is not a physical-robot measurement.",
    lesson:
      "Getting the robot to finish was only part of the work. Saving the commands and recorded motion made it easier to understand the result and check whether the experiment behaved as intended.",
    image: {
      src: "lab/turtlebot-path.png",
      alt: "Plot of the simulated TurtleBot3 traveling from A at minus two meters to B at two meters and back, comparing the planned route with recorded motion.",
      caption:
        "Recorded TurtleBot3 route from September 3, 2026. X and Y positions are in meters. Source: the Gazebo experiment’s saved motion data.",
      width: 1620,
      height: 1260,
    },
  },
  {
    id: "pickup-simulation",
    category: "Robot integration and testing",
    title: "Single-arm mobile pickup simulation",
    overview:
      "I worked from a supplied single-arm CAD model to put together a Gazebo experiment where a mobile robot travels to a block, picks it up, and brings it back. This is separate from the two-arm CAD design.",
    tools: ["Python", "URDF and SDF", "ROS 2", "Cartographer"],
    goal:
      "I wanted students to see how navigation, arm movement, sensor data, and testing fit into one task.",
    contributions: [
      "I worked on the robot descriptions and Python task sequence to coordinate the waypoint route, arm poses, pickup, return, and placement.",
      "I recorded motion, joint positions, sensor data, and contact events so the results could be checked after each run.",
      "I compared a clear route, a blocked route, and a manually edited detour. Cartographer built a map alongside the experiment; the waypoint controller used odometry independently of that map.",
    ],
    outcome:
      "The baseline completed. With the route blocked, the robot stopped and timed out before pickup. After the intermediate waypoints were changed, the detour completed. The simulation uses simplified base motion and grasp attachment, so these results do not establish physical-robot performance.",
    lesson:
      "A failed run can still be useful evidence. Comparing the cases helped me understand why stopping for an obstacle and finding a route around it are different problems. It also taught me to test one change at a time instead of changing everything at once.",
    image: {
      src: "lab/pickup-sequence.png",
      alt: "Two frames from the single-arm Gazebo simulation showing the gripper closing around a red block and lifting it from a yellow stand.",
      caption:
        "Recorded pickup sequence from September 9, 2026. The simulation checks alignment and contact before using a simplified grasp attachment.",
      width: 2040,
      height: 680,
    },
  },
  {
    id: "student-labs",
    category: "Technical communication",
    title: "Student labs and co-op documentation",
    overview:
      "I turned the robotics work into illustrated student labs, experiment reports, and a faculty review presentation. I wanted someone else to be able to follow the process and understand the results.",
    tools: ["2 worksheets", "2 experiment reports", "Faculty presentation"],
    goal:
      "I wanted to continue the Drexel ROS and TurtleBot learning series with clear instructions and a way for students to check their work.",
    contributions: [
      "I created two illustrated worksheets covering ROS 2 and TurtleBot3 setup and the simulated A–B–A pick-and-drop task.",
      "I connected the instructions to code references, screenshots, questions, checks, and troubleshooting steps.",
      "I brought the design work and recorded experiment evidence into reports, a presentation with presenter notes, and a CAD handoff package.",
    ],
    outcome:
      "The review package includes both worksheets, two experiment reports, a 20-slide presentation, and the supporting code and CAD references. The instructions were checked in the existing lab environment; a fresh student-computer setup still needs a trial.",
    lesson:
      "Explaining the steps made me look more closely at what the programs were actually doing. I had to think about what another student would need to know and how they could recognize when something went wrong.",
  },
];

export const coOpReflection =
  "This co-op helped me understand how CAD, sensors, programming, and simulation work together in a robotics project. I learned to break large problems into smaller steps and revise the design based on what the tests showed. I want to keep building those skills through robotics, automation, and hands-on engineering work.";
