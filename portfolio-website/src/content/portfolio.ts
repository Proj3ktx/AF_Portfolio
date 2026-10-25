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
  lede: "During my summer 2026 co-op at Drexel’s Engineering Technology Robotics Lab, I worked on CAD models, ROS 2 simulations, robot experiments, testing, troubleshooting, and documenting my progress.",
  role: "Robotics engineering intern",
  org: "Drexel ET Robotics Lab",
  place: "Philadelphia, PA",
  dates: "June 2026 – September 2026",
} as const;

export const projects: readonly Project[] = [
  {
    title: "Engineering laboratory",
    dates: "2024 – present",
    summary:
      "My coursework has included robotics, CAD, instrumentation, and engineering measurements. These projects gave me practice collecting data, analyzing results, and explaining my work in technical reports.",
  },
  {
    title: "Network systems",
    dates: "2022 – 2024",
    summary:
      "I configured small networks and worked on access controls, authentication, basic cybersecurity, and troubleshooting through my technical school program.",
  },
];

export const roles: readonly Role[] = [
  {
    title: "Fitness coach",
    org: "Legion Fitness",
    place: "King of Prussia, PA",
    dates: "June 2024 – September 2024",
    summary: "I led group fitness classes and coached proper exercise technique and safety. Teaching others pushed me to explain things clearly and keep improving my own understanding.",
  },
  {
    title: "IT networking intern",
    org: "Popeyes Restaurants",
    place: "Sugar Land, TX",
    dates: "June 2023 – August 2023",
    summary:
      "I assisted with network cabling, hardware deployment, server configuration, and troubleshooting. I also maintained technical documentation and Excel records to keep track of the work.",
  },
  {
    title: "Host, busser, and food runner",
    org: "Chili's Grill & Bar",
    place: "King of Prussia, PA",
    dates: "September 2020 – January 2021",
    summary: "I seated guests, delivered food, and helped keep service running smoothly during busy shifts.",
  },
  {
    title: "Sales associate",
    org: "Nordstrom Rack",
    place: "King of Prussia, PA",
    dates: "June 2020 – September 2020",
    summary: "I helped customers, organized merchandise, and maintained the fitting rooms while working with the sales team.",
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
    label: "Robotics and simulation",
    items: ["ROS 2", "URDF", "Gazebo", "RViz"],
  },
  {
    label: "Programming and analysis",
    items: ["Python", "MATLAB", "LabVIEW", "Excel"],
  },
  {
    label: "Technical work",
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
