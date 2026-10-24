export const site = {
  name: "Ali Fakira",
  role: "Engineering technology",
  focus: "Robotics",
  school: "Drexel University",
  program: "BSET, Engineering Technology",
  graduation: "Expected June 2029",
  description:
    "Portfolio of Ali Fakira, a Drexel engineering technology student. Robotics models, mechanical design, digital twins, and recorded robot trials.",
} as const;

export const nav = [
  { id: "work", label: "Work" },
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
