// Audio Brief — cloned-voice TLDR player for MkDocs Material category pages.
// Mirrors digest/src/components/AudioBrief.astro behavior. Each .audio-brief
// element on the page is wired independently. Uses document$.subscribe (the
// MkDocs Material instant-loading hook) so handlers re-bind on SPA navigation.

document$.subscribe(function () {
  document.querySelectorAll("[data-audio-brief]").forEach(function (root) {
    if (root.dataset.audioBriefBound === "1") return;
    root.dataset.audioBriefBound = "1";

    var audio = root.querySelector("[data-audio-element]");
    var playBtn = root.querySelector("[data-audio-play]");
    var icon = root.querySelector("[data-audio-icon]");
    var timeEl = root.querySelector("[data-audio-time]");
    var progressEl = root.querySelector("[data-audio-progress]");
    if (!audio || !playBtn || !icon || !timeEl || !progressEl) return;

    function formatTime(seconds) {
      if (!isFinite(seconds) || seconds < 0) return "0:00";
      var m = Math.floor(seconds / 60);
      var s = Math.floor(seconds % 60);
      return m + ":" + (s < 10 ? "0" : "") + s;
    }

    audio.addEventListener("loadedmetadata", function () {
      timeEl.textContent = formatTime(audio.duration);
    });

    audio.addEventListener("timeupdate", function () {
      if (audio.duration > 0) {
        var pct = (audio.currentTime / audio.duration) * 100;
        progressEl.style.width = pct + "%";
      }
    });

    audio.addEventListener("ended", function () {
      icon.textContent = "▶";
      playBtn.setAttribute("aria-label", "Play audio brief");
      progressEl.style.width = "0%";
      timeEl.textContent = formatTime(audio.duration);
    });

    audio.addEventListener("play", function () {
      icon.textContent = "❚❚";
      playBtn.setAttribute("aria-label", "Pause audio brief");
    });

    audio.addEventListener("pause", function () {
      if (!audio.ended) {
        icon.textContent = "▶";
        playBtn.setAttribute("aria-label", "Play audio brief");
      }
    });

    playBtn.addEventListener("click", function () {
      if (audio.paused) {
        audio.play().catch(function () { /* noop */ });
      } else {
        audio.pause();
      }
    });
  });
});
