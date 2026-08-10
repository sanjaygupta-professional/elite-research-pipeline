import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://cinnabar-intel.github.io",
  base: "/digest",
  trailingSlash: "always",
  build: {
    format: "directory",
  },
});
