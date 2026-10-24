import { defineConfig } from "astro/config";

const onGithubPages = process.env.GITHUB_PAGES === "true";

export default defineConfig({
  site: "https://proj3ktx.github.io",
  base: onGithubPages ? "/AF_Portfolio" : "/",
  output: "static",
  compressHTML: true,
  devToolbar: {
    enabled: false,
  },
});
