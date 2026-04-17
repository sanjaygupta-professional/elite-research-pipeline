// Mermaid initialization for MkDocs Material
//
// Problem: pymdownx.superfences produces <pre class="mermaid"><code>...</code></pre>
// with HTML-escaped content. Mermaid v10 needs raw text inside <div class="mermaid">
// and can hit a "getBBox on null" error when the container isn't laid out yet.
//
// Fix: unwrap <pre><code> into <div>, set raw text (auto-decoded by textContent),
// then run mermaid inside requestAnimationFrame so layout is complete.

document$.subscribe(function () {
  if (typeof mermaid === "undefined") {
    console.warn("[mermaid-init] mermaid global not defined");
    return;
  }

  mermaid.initialize({
    startOnLoad: false,
    theme: "default",
    securityLevel: "loose",
    fontFamily: "Roboto, sans-serif"
  });

  // Step 1: convert <pre class="mermaid"><code>…</code></pre> → <div class="mermaid">raw</div>
  document.querySelectorAll("pre.mermaid").forEach(function (pre) {
    if (pre.dataset.mermaidConverted) return;
    const code = pre.querySelector("code");
    const raw = code ? code.textContent : pre.textContent;
    const div = document.createElement("div");
    div.className = "mermaid";
    div.dataset.mermaidConverted = "1";
    div.textContent = raw;
    pre.replaceWith(div);
  });

  // Step 2: defer render until after the next layout frame to avoid getBBox-on-null
  const divs = document.querySelectorAll("div.mermaid:not([data-mermaid-rendered])");
  if (divs.length === 0) return;

  requestAnimationFrame(function () {
    mermaid.run({ nodes: divs })
      .then(function () {
        divs.forEach(function (d) { d.dataset.mermaidRendered = "1"; });
      })
      .catch(function (err) {
        console.error("[mermaid-init] render failed:", err);
      });
  });
});
