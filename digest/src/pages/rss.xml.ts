import type { APIRoute } from "astro";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import issues from "../data/issues.json";

// Hand-rolled RSS 2.0 feed (no @astrojs/rss dependency). Items are derived at
// build time from the current issue (index.astro) plus every archived issue in
// issues.json, reading each page's issueDate + title + description the same way
// PreviousIssues reads its metadata. Each issue is the single source of truth.

const SITE = import.meta.env.SITE ?? "https://cinnabar-intel.github.io";
const BASE = import.meta.env.BASE_URL; // e.g. "/digest/"

interface Item {
  date: string;
  title: string;
  description: string;
  link: string;
}

function readMeta(file: string) {
  const src = readFileSync(file, "utf8");
  const date = src.match(/issueDate\s*=\s*"([^"]+)"/)?.[1] ?? null;
  const description =
    src.match(/const description\s*=\s*"((?:[^"\\]|\\.)*)"/)?.[1] ?? "";
  const title = src.match(/const title\s*=\s*"((?:[^"\\]|\\.)*)"/)?.[1] ?? "";
  return { date, description, title };
}

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export const GET: APIRoute = () => {
  const root = process.cwd();
  const items: Item[] = [];

  // Current issue.
  try {
    const cur = readMeta(join(root, "src", "pages", "index.astro"));
    if (cur.date) {
      items.push({
        date: cur.date,
        title: cur.title || `The Cinnabar Dispatch · ${cur.date}`,
        description: cur.description,
        link: `${SITE}${BASE}`,
      });
    }
  } catch {
    /* index unreadable — skip */
  }

  // Archived issues.
  for (const issue of issues) {
    try {
      const m = readMeta(
        join(root, "src", "pages", "issues", `${issue.date}.astro`),
      );
      items.push({
        date: issue.date,
        title: m.title || `The Cinnabar Dispatch · ${issue.date}`,
        description: m.description,
        link: `${SITE}${BASE}issues/${issue.date}/`,
      });
    } catch {
      /* missing archive — skip */
    }
  }

  items.sort((a, b) => (a.date < b.date ? 1 : -1));

  const now = new Date().toUTCString();
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>The Cinnabar Dispatch</title>
    <link>${SITE}${BASE}</link>
    <description>Weekly futures-intelligence dispatch at the intersection of AI and organizational transformation. Possibilities with Probabilities.</description>
    <language>en</language>
    <lastBuildDate>${now}</lastBuildDate>
${items
  .map(
    (it) => `    <item>
      <title>${esc(it.title)}</title>
      <link>${it.link}</link>
      <guid isPermaLink="true">${it.link}</guid>
      <pubDate>${new Date(`${it.date}T06:00:00Z`).toUTCString()}</pubDate>
      <description>${esc(it.description)}</description>
    </item>`,
  )
  .join("\n")}
  </channel>
</rss>`;

  return new Response(body, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
};
