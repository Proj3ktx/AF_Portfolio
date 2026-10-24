export type WorkItem = {
  title: string;
  summary: string;
};

export type Project = {
  title: string;
  dates: string;
  summary: string;
};

export type Role = {
  title: string;
  org: string;
  place: string;
  dates: string;
  summary: string;
};

export type School = {
  name: string;
  detail?: string;
  dates: string;
};

export type SkillGroup = {
  label: string;
  items: readonly string[];
};

export const work = {
  id: "work",
  index: "01",
  title: "Selected work",
  lede: "June to September 2026 at the Drexel ET robotics lab in Philadelphia. These are the pieces I worked on.",
  role: "Robotics engineering intern",
  org: "Drexel ET Robotics Lab",
  place: "Philadelphia, PA",
  dates: "June 2026 – September 2026",
  items: [
    {
      title: "ROS 2 models",
      summary:
        "URDF models I ran in ROS 2 and RViz while the robot system was being put together.",
    },
    {
      title: "Mechanical design",
      summary:
        "SolidWorks parts for a two-arm mobile robot, and a design-review CAD package that lists what still needs a check before anyone builds it.",
    },
    {
      title: "Digital twin",
      summary:
        "The same robot in Unity and Blender, so I could look at the motion without the hardware in front of me.",
    },
    {
      title: "Trials",
      summary:
        "TurtleBot3 and mobile-arm pickup runs: A-B-A, waypoints, and SLAM. I recorded the runs and wrote up what the robot did.",
    },
    {
      title: "Lab materials",
      summary:
        "Two illustrated lab worksheets, including a pickup that goes around an obstacle. I walked through them in the faculty co-op review.",
    },
  ] satisfies readonly WorkItem[],
} as const;

export const projects: readonly Project[] = [
  {
    title: "Engineering laboratory",
    dates: "2024 – present",
    summary:
      "Robotics, CAD, instrumentation, and measurement projects from class. I wrote up the results after each one.",
  },
  {
    title: "Network systems",
    dates: "2022 – 2024",
    summary:
      "Small networks: setup, who is allowed on, authentication, basic security, and fixing what broke.",
  },
];

export const roles: readonly Role[] = [
  {
    title: "Fitness coach",
    org: "Legion Fitness",
    place: "King of Prussia, PA",
    dates: "June 2024 – September 2024",
    summary: "Led group classes and coached exercise technique and participant safety.",
  },
  {
    title: "IT networking intern",
    org: "Popeyes Restaurants",
    place: "Sugar Land, TX",
    dates: "June 2023 – August 2023",
    summary:
      "Network cabling, hardware deployment, server configuration, troubleshooting, and the Excel records and technical notes that went with the work.",
  },
  {
    title: "Host, busser, and food runner",
    org: "Chili's Grill & Bar",
    place: "King of Prussia, PA",
    dates: "September 2020 – January 2021",
    summary: "Seated guests, delivered food, and kept service areas in order.",
  },
  {
    title: "Sales associate",
    org: "Nordstrom Rack",
    place: "King of Prussia, PA",
    dates: "June 2020 – September 2020",
    summary: "Assisted customers, organized merchandise, and maintained the fitting rooms.",
  },
];

export const schools: readonly School[] = [
  {
    name: "Drexel University",
    detail: "BSET, Engineering Technology",
    dates: "Expected June 2029",
  },
  {
    name: "Central Montco Technical High School",
    detail: "Networking Technology Program",
    dates: "Graduated 2024",
  },
  {
    name: "Upper Merion Area High School",
    dates: "Graduated 2024",
  },
  {
    name: "Penn Technical College",
    detail: "Dual enrollment, Networking I",
    dates: "Completed April 2022",
  },
];

export const coursework = [
  "Engineering Measurements & Instrumentation",
  "Robotics & Mechatronics",
  "Engineering Materials",
  "Physics I & II",
  "Calculus I & II",
  "Introductory Programming for Embedded Systems",
  "Engineering Design & Data Analysis",
  "Virtual Instrumentation",
] as const;

export const skillGroups: readonly SkillGroup[] = [
  {
    label: "Design",
    items: ["SolidWorks", "AutoCAD", "Blender", "Unity"],
  },
  {
    label: "Robotics",
    items: ["ROS 2", "URDF", "LabVIEW", "MATLAB"],
  },
  {
    label: "Computing",
    items: ["Python", "Excel"],
  },
  {
    label: "Practice",
    items: [
      "Engineering measurements",
      "Embedded systems",
      "Networking fundamentals",
      "Technical documentation",
      "Team collaboration",
    ],
  },
];

export const honors = [
  "Distinguished Honors, Upper Merion Area High School, 2021–2023",
  "Student of the Quarter, Networking and Automotive Technology, Central Montco Technical High School",
  "Science Olympiad, 3rd place, Seismic Detector",
  "Science Olympiad, 2nd place, Bridge Construction",
  "ILMUNC, UNICEF Best Delegate",
  "SkillsUSA State Officer. Represented SkillsUSA to audiences of 500 or more and coordinated leadership events.",
] as const;

export const activities = [
  "Model United Nations",
  "Upper Merion Wrestling",
  "Networking Program Class President",
  "Student Ambassador",
  "STEM Club",
  "Upper Merion Foundation volunteer",
] as const;
