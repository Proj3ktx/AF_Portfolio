import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const roots = process.argv.slice(2);
if (roots.length === 0) {
  console.error("Usage: node scripts/guard-public-content.mjs <dir> [dir...]");
  process.exit(1);
}

const blockedExt = new Set([
  ".pdf",
  ".doc",
  ".docx",
  ".heic",
  ".mov",
  ".mp4",
  ".zip",
  ".csv",
]);
const blockedName = /(resume|curriculum|passport|social-security|\bssn\b|bank-statement)/i;
const email = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i;
const phone = /(?:\+?1[\s.-])?(?:\(\d{3}\)|\d{3})[\s.-]\d{3}[\s.-]\d{4}/;
const mailto = /mailto:/i;
const textExt = new Set([
  ".astro",
  ".css",
  ".html",
  ".js",
  ".json",
  ".mjs",
  ".svg",
  ".ts",
  ".txt",
]);

const findings = [];

async function walk(dir) {
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch (error) {
    if (error && error.code === "ENOENT") return;
    throw error;
  }

  for (const entry of entries) {
    if (entry.name === ".local-backup" || entry.name === "node_modules") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await walk(full);
      continue;
    }

    const rel = path.relative(process.cwd(), full);
    const ext = path.extname(entry.name).toLowerCase();
    if (blockedExt.has(ext) || blockedName.test(entry.name)) {
      findings.push(`${rel}: blocked file`);
    }
    if (!textExt.has(ext)) continue;

    const text = await readFile(full, "utf8");
    if (email.test(text)) findings.push(`${rel}: email address`);
    if (phone.test(text)) findings.push(`${rel}: phone number`);
    if (mailto.test(text)) findings.push(`${rel}: mailto link`);
  }
}

for (const root of roots) {
  await walk(path.resolve(root));
}

if (findings.length > 0) {
  console.error("Public build blocked. Remove personal data before publishing:");
  for (const finding of findings) console.error(`  ${finding}`);
  process.exit(1);
}

console.log(`Public content check passed (${roots.join(", ")}).`);
