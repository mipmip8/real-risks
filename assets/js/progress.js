/* Progress tracking for the RealRisks Screening module.
 *
 * A slide counts as complete once it has been visited. Progress lives in
 * localStorage only, so it is per-browser and survives no sign-in — which is
 * all a static site can do without a backend.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "realrisks.screening.visited.v1";

  function read() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (err) {
      // Private browsing or disabled storage: fall back to no progress.
      return [];
    }
  }

  function write(ids) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
    } catch (err) {
      /* Nothing we can do; progress simply will not persist. */
    }
  }

  function markVisited(id) {
    var ids = read();
    if (ids.indexOf(id) === -1) {
      ids.push(id);
      write(ids);
    }
  }

  /* ---- Slide pages: record the visit ---- */

  var body = document.body;

  function str(name, fallback) {
    return body.getAttribute("data-i18n-" + name) || fallback;
  }

  var slideId = body.getAttribute("data-slide-id");
  if (slideId) {
    markVisited(slideId);
  }

  /* ---- Any page: render the accomplishments bar ---- */

  function renderProgress() {
    var visited = read();
    var total = parseInt(body.getAttribute("data-total-slides") || "0", 10);
    var done = 0;
    var i;

    // Only count ids that still exist in the module.
    var all = (body.getAttribute("data-all-slide-ids") || "")
      .split(",")
      .filter(Boolean);
    for (i = 0; i < all.length; i++) {
      if (visited.indexOf(all[i]) !== -1) {
        done++;
      }
    }

    var fill = document.querySelector(".progress-fill");
    var count = document.querySelector(".progress-count");
    if (fill && total > 0) {
      var pct = Math.round((done / total) * 100);
      fill.style.width = pct + "%";
      var track = fill.parentNode;
      track.setAttribute("role", "progressbar");
      track.setAttribute("aria-valuenow", String(done));
      track.setAttribute("aria-valuemin", "0");
      track.setAttribute("aria-valuemax", String(total));
      track.setAttribute(
        "aria-valuetext",
        str("progress", "{done} of {total} slides completed")
          .replace("{done}", String(done))
          .replace("{total}", String(total))
      );
    }
    if (count) {
      count.textContent = done + " / " + total;
    }

    // Tick a checkbox once every slide it covers has been visited. A menu
    // entry may stand for several slides, and a chapter for all of its own.
    var checks = document.querySelectorAll("[data-check-all]");
    for (i = 0; i < checks.length; i++) {
      var el = checks[i];
      var members = el.getAttribute("data-check-all").split(",").filter(Boolean);
      var complete =
        members.length > 0 &&
        members.every(function (id) {
          return visited.indexOf(id) !== -1;
        });
      el.classList.toggle("is-done", complete);
      el.setAttribute(
        "aria-label",
        complete ? str("completed", "Completed") : str("not-completed", "Not completed yet")
      );
    }
  }

  renderProgress();

  /* ---- Reset ---- */

  var reset = document.querySelector(".reset-progress");
  if (reset) {
    reset.addEventListener("click", function () {
      var message = reset.getAttribute("data-confirm") ||
        "Reset your progress through this module?";
      if (!window.confirm(message)) {
        return;
      }
      write([]);
      renderProgress();
    });
  }

  /* ---- Home page accordion ---- */

  var headers = document.querySelectorAll(".chapter__header");
  Array.prototype.forEach.call(headers, function (header) {
    header.addEventListener("click", function () {
      var chapter = header.closest(".chapter");
      var open = chapter.getAttribute("data-open") === "true";
      chapter.setAttribute("data-open", open ? "false" : "true");
      header.setAttribute("aria-expanded", open ? "false" : "true");
    });
  });

  /* ---- Left/right arrow keys move between slides ---- */

  document.addEventListener("keydown", function (event) {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
      return;
    }
    var tag = (event.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select") {
      return;
    }
    var selector =
      event.key === "ArrowRight"
        ? 'a[rel="next"]'
        : event.key === "ArrowLeft"
          ? 'a[rel="prev"]'
          : null;
    if (!selector) {
      return;
    }
    var link = document.querySelector(selector);
    if (link && link.getAttribute("aria-disabled") !== "true") {
      window.location.href = link.href;
    }
  });
})();
