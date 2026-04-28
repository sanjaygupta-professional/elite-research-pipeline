import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://sanjaygupta-professional.github.io",
  base: "/elite-research-pipeline/digest",
  trailingSlash: "always",
  build: {
    format: "directory",
  },
});
