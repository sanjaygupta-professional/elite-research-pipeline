// Mermaid initialization for MkDocs Material
// Material uses document$ (RxJS) which fires on every SPA page navigation.
// Without this, Mermaid only runs on first hard load and misses navigated pages.
document$.subscribe(function () {
  mermaid.initialize({
    startOnLoad: false,
    theme: "default",
    securityLevel: "loose",
    fontFamily: "Roboto, sans-serif"
  });
  const nodes = document.querySelectorAll("code.mermaid");
  if (nodes.length > 0) {
    mermaid.run({ nodes: nodes });
  }
});
