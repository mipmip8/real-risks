/* Tradeoff sliders.
 *
 * Each slider reports where the reader sits on one screening tradeoff. The
 * fact shown on a card never changes; moving a slider swaps the framing text
 * and shifts the emphasis of the visual, then rebuilds a summary the reader
 * can print or copy and take to an appointment.
 *
 * Positions are saved per-browser in localStorage, the same as slide progress.
 */
(function () {
  "use strict";

  var root = document.querySelector(".sliders");
  if (!root) {
    return; // Not the sliders slide.
  }

  var STORAGE_KEY = "realrisks.screening.sliders.v1";
  var DEFAULT_POS = 3;

  var cards = Array.prototype.slice.call(root.querySelectorAll(".slider-card"));
  var summaryList = root.querySelector(".sliders__summary-list");
  var status = root.querySelector(".sliders__status");

  function readSaved() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      var parsed = raw ? JSON.parse(raw) : {};
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (err) {
      return {};
    }
  }

  function save(positions) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(positions));
    } catch (err) {
      /* Progress simply will not persist. */
    }
  }

  function announce(message) {
    if (!status) {
      return;
    }
    status.textContent = message;
    window.setTimeout(function () {
      if (status.textContent === message) {
        status.textContent = "";
      }
    }, 4000);
  }

  /* ---- Rendering ---- */

  function summaryFor(card, pos) {
    var parts = (card.querySelector(".slider__input")
      .getAttribute("data-summary") || "").split("|");
    return parts[pos - 1] || "";
  }

  function applyCard(card, pos) {
    card.setAttribute("data-pos", String(pos));

    var framings = card.querySelectorAll("[data-framing]");
    for (var i = 0; i < framings.length; i++) {
      var el = framings[i];
      var match = el.getAttribute("data-framing") === String(pos);
      if (match) {
        el.removeAttribute("hidden");
      } else {
        el.setAttribute("hidden", "");
      }
    }

    // Screen readers read the position as its meaning, not as a bare number.
    var input = card.querySelector(".slider__input");
    input.setAttribute("aria-valuetext", summaryFor(card, pos));
  }

  function renderSummary() {
    if (!summaryList) {
      return;
    }
    summaryList.innerHTML = "";
    cards.forEach(function (card) {
      var pos = parseInt(card.getAttribute("data-pos"), 10);
      var li = document.createElement("li");
      var label = document.createElement("strong");
      label.textContent = card.querySelector(".slider__title").textContent + ": ";
      li.appendChild(label);
      li.appendChild(document.createTextNode(summaryFor(card, pos)));
      summaryList.appendChild(li);
    });
  }

  function currentPositions() {
    var positions = {};
    cards.forEach(function (card) {
      positions[card.getAttribute("data-id")] =
        parseInt(card.getAttribute("data-pos"), 10);
    });
    return positions;
  }

  /* ---- Wiring ---- */

  var saved = readSaved();

  cards.forEach(function (card) {
    var input = card.querySelector(".slider__input");
    var id = card.getAttribute("data-id");
    var pos = parseInt(saved[id], 10);
    if (!(pos >= 1 && pos <= 5)) {
      pos = DEFAULT_POS;
    }
    input.value = String(pos);
    applyCard(card, pos);

    input.addEventListener("input", function () {
      var next = parseInt(input.value, 10);
      applyCard(card, next);
      renderSummary();
      save(currentPositions());
    });
  });

  renderSummary();

  /* ---- Actions ---- */

  function summaryText() {
    var lines = cards.map(function (card) {
      var pos = parseInt(card.getAttribute("data-pos"), 10);
      return "- " + card.querySelector(".slider__title").textContent + ": " +
        summaryFor(card, pos);
    });
    return "What matters most to me about breast cancer screening\n\n" +
      lines.join("\n") +
      "\n\nCreated with the RealRisks screening module. This is a list of " +
      "personal priorities, not medical advice.\n";
  }

  var printBtn = root.querySelector("[data-slider-print]");
  if (printBtn) {
    printBtn.addEventListener("click", function () {
      window.print();
    });
  }

  var copyBtn = root.querySelector("[data-slider-copy]");
  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var text = summaryText();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(
          function () {
            announce("Copied to your clipboard.");
          },
          function () {
            announce("Could not copy. You can select the list and copy it.");
          }
        );
      } else {
        announce("Copying is not supported here. You can select the list and copy it.");
      }
    });
  }

  var resetBtn = root.querySelector("[data-slider-reset]");
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      cards.forEach(function (card) {
        card.querySelector(".slider__input").value = String(DEFAULT_POS);
        applyCard(card, DEFAULT_POS);
      });
      renderSummary();
      save(currentPositions());
      announce("Sliders reset to the middle.");
    });
  }

  /* Arrow keys adjust a focused slider, so stop the slide-level shortcut from
   * navigating away mid-adjustment. */
  root.addEventListener("keydown", function (event) {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.stopPropagation();
    }
  });
})();
