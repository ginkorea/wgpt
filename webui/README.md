# WebUI (Base Directory) — README

## Purpose

This folder contains the React + Vite front end for the chat UI. During development it runs with Vite’s dev server and proxies API calls to your backend. In production it builds a single-file HTML bundle that the backend can serve directly. &#x20;

---

## How the WebUI talks to the backend

* **Dev proxy**
  When you run the dev server, requests to `/v1` and `/props` are proxied to `http://127.0.0.1:8081` so you can point the UI at your running llama-server without CORS pain. COEP/COOP headers are also set for features that need them.&#x20;

* **Preview server**
  `vite preview` serves the built app on port `8080` and keeps the same proxy rules and headers as dev. Useful to test the production build locally.&#x20;

* **Production artifact**
  The build produces a self-contained `index.html` and also writes a gzipped `index.html.gz` after scrubbing gzip headers for reproducible builds. The build will throw if the compressed bundle exceeds **2 MiB** to keep the frontend lightweight.  &#x20;

> If you need to increase the cap, change `MAX_BUNDLE_SIZE` in `vite.config.ts`.&#x20;

---

## What files in this folder do

* **`vite.config.ts`**
  Vite config for React, single-file output, bundle size guard, dev/preview proxies, and security headers. Also injects a small “don’t edit this build” banner into the generated HTML then gzips it for serving.   &#x20;

* **`tailwind.config.js`**
  Tailwind setup with `src/**/*.{js,ts,jsx,tsx}` and `index.html` content scanning, plus the `daisyui` plugin with a wide set of themes available.&#x20;

* **`postcss.config.js`**
  PostCSS config enabling Tailwind via `@tailwindcss/postcss`.&#x20;

* **TypeScript project files**

  * `tsconfig.json` uses project references to split app vs node configs.&#x20;
  * `tsconfig.app.json` configures the browser build (ES2021 + DOM libs, JSX, bundler resolution, strict flags). &#x20;
  * `tsconfig.node.json` configures the Node side for tooling (targets ES2022 and includes only `vite.config.ts`).&#x20;

* **Formatting/ignore**
  `.prettierignore` excludes common folders and generated files from formatting. &#x20;

* **Dependencies snapshot**
  `package-lock.json` shows core UI deps like React, Tailwind, DaisyUI, Markdown/KaTeX, PDF.js, Vite, and the single-file plugin. (You normally do not edit this by hand.) &#x20;

---

## Styling pipeline

* Tailwind is wired through PostCSS and the DaisyUI plugin. Add your component classes in `src/**` and they will be included at build time based on the `content` globs. &#x20;

* Global styles live in `src/index.scss` where Tailwind and DaisyUI are imported, and Markdown styling helpers are defined. (Look there when changing chat bubble or table styles.) &#x20;

---

## Dev vs. Build commands

* **Install**

  ```bash
  npm install
  ```

* **Run dev server**

  ```bash
  npm run dev
  ```

  The UI runs with hot reload and proxies API calls to `127.0.0.1:8081`.&#x20;

* **Build production bundle**

  ```bash
  npm run build
  ```

  Produces a single `index.html` plus `index.html.gz` in `dist/`. The gzipped file is size-checked.&#x20;

* **Preview the production build**

  ```bash
  npm run preview
  ```

  Serves on port `8080` with the same proxy and headers to mimic how the backend will see it.&#x20;

---

## Where to edit backend endpoints from the UI side

* During **dev/preview**, change the proxy targets in `vite.config.ts` if your backend is not on `127.0.0.1:8081`. Update the `/v1` and `/props` proxy entries. &#x20;

* In **app code**, API requests hit `/v1/chat/completions` and `/props`. The UI fetches `/props` to learn server capabilities. If you serve the UI from the same host/port as the backend, the relative paths will just work without proxy. &#x20;

---

## Typical edit points

* **Add UI components / logic** → edit files under `src/` (see the separate `src/` README).
* **Change styling defaults** → `src/index.scss` and `tailwind.config.js`. &#x20;
* **Adjust build behavior** → `vite.config.ts` for gzip, size budget, headers, proxies. &#x20;

---

## Troubleshooting

* **Bundle too large error**
  You will see a thrown error if `index.html.gz` exceeds the allowed size. Reduce dependencies or raise the limit in `vite.config.ts`.&#x20;

* **CORS or cross-origin isolation issues**
  Make sure the dev server sets COEP/COOP headers and that the backend cooperates when you deploy. These headers are defined in the Vite config for dev/preview. &#x20;

---

## Tech stack at a glance

React 18, Vite 6, TypeScript 5, Tailwind 4 with DaisyUI, PDF.js for PDF handling, KaTeX/remark/rehype for Markdown and math, Dexie for IndexedDB, and the Vite single-file plugin. See `package-lock.json` for exact versions.&#x20;

