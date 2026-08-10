// Single source of truth for cross-property URLs.
//
// The digest (this Astro app) and the knowledge system (MkDocs) are served from
// the same GitHub Pages origin: the knowledge system lives at the site root and
// the digest under /digest/. On a domain change, edit ORIGIN here and the live
// components (Masthead, Methodology) follow automatically. Archived issue pages
// under src/pages/issues/ are static snapshots and carry their own literal URLs.
export const ORIGIN = "https://cinnabar-intel.github.io";

export const KS_HOME_URL = `${ORIGIN}/`;
export const KS_FRAMEWORK_URL = `${ORIGIN}/design/05-signal-scoring-framework/`;
export const KS_ARCHIVE_URL = `${ORIGIN}/baseline/zone2-futures-intelligence/06-weak-signal-watch/`;
