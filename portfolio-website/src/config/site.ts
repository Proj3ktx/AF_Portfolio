export const site = {
  name: "Ali Fakira",
  role: "Engineering technology",
  focus: "Robotics",
  school: "Drexel University",
  program: "BSET, Engineering Technology",
  graduation: "Expected June 2029",
  description:
    "Ali Fakira is an Engineering Technology student at Drexel University with experience in robotics simulation, Python and ROS 2, and mechanical CAD design. Explore his projects and summer 2026 co-op work.",
} as const;

export const nav = [
  { id: "work", label: "Work" },
  { id: "lab", label: "Lab files" },
  { id: "lab-source", label: "Code" },
  { id: "projects", label: "Coursework" },
  { id: "experience", label: "Experience" },
  { id: "education", label: "Education" },
] as const;

export function href(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  if (!path || path === "/") return `${base}/`;

  const hashAt = path.indexOf("#");
  const hash = hashAt >= 0 ? path.slice(hashAt) : "";
  const pathname = hashAt >= 0 ? path.slice(0, hashAt) : path;

  if (!pathname || pathname === "/") return `${base}/${hash}`;
  return `${base}${pathname.startsWith("/") ? pathname : `/${pathname}`}${hash}`;
}
