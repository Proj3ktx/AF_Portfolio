# Ali Fakira portfolio

Static portfolio site. Astro and TypeScript. No personal documents are part of the build.

Needs Node.js 22.23 or newer. Node 24 is a safe choice.

```bash
npm install
npm run dev
```

The dev server is http://127.0.0.1:3000.

```bash
npm run build
npm run preview
```

`npm run build` refuses to finish if an email address, phone number, résumé file, or photo/video of a private type is inside `src/`, `public/`, or the finished `dist/` folder.

Photos, the résumé, and the old site copy are in `.local-backup/`. That folder is gitignored. Leave it there.

GitHub Pages builds with `GITHUB_PAGES=true`, which sets the site base to `/AF_Portfolio`. The workflow is `.github/workflows/pages.yml` in the parent repository.
