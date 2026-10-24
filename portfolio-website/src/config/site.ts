export const site = {
  name: "Ali Fakira",
  role: "Engineering technology",
  focus: "Robotics",
  school: "Drexel University",
  program: "BSET, Engineering Technology",
  graduation: "Expected June 2029",
  description:
    "Ali Fakira studies engineering technology at Drexel. This page is his summer 2026 robotics lab work: ROS 2 models, SolidWorks, a Unity and Blender twin, and the trial notes.",
} as const;

export const nav = [
  { id: "work", label: "Work" },
  { id: "lab", label: "Lab" },
  { id: "projects", label: "Projects" },
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
