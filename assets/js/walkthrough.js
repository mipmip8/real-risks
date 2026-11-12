/* Interactive MRI walk-through.
 *
 * The page ships a plain ordered list of the steps and a hidden interactive
 * version. This script swaps them, so a reader without JavaScript gets the
 * whole thing as prose rather than controls that do nothing.
 *
 * Each step asks the reader to act on the scene — click the necklace, the
 * table, the machine — and only then explains what happened and offers the
 * next step.
 *
 * Two indices, deliberately separate:
 *   current  which step card is on screen (0 = intro, steps.length + 1 = done)
 *   revealed whether the reader has acted on that step yet
 * The illustration is driven by how many steps are actually complete, so the
 * picture changes *because* of the click rather than ahead of it. Going back
 * rewinds both the card and the picture, so a step can be replayed.
 */
(function () {
  "use strict";

  var root = document.querySelector(".walkthrough");
  if (!root) {
    return; // Not the walk-through slide.
  }

  var staticList = root.querySelector(".walkthrough__static");
  var game = root.querySelector(".walkthrough__game");
  var intro = root.querySelector(".wt-intro");
  var startBtn = root.querySelector(".wt-start");
  var restartBtn = root.querySelector(".wt-restart");
  var done = root.querySelector(".wt-done");
  var steps = Array.prototype.slice.call(root.querySelectorAll(".wt-step"));
  var dots = Array.prototype.slice.call(root.querySelectorAll(".wt-dot"));
  var hotspots = Array.prototype.slice.call(root.querySelectorAll(".wt-hotspot"));

  if (!game || !steps.length) {
    return;
  }

  staticList.hidden = true;
  game.hidden = false;

  var current = 0;
  var revealed = false;

  function completed() {
    // Steps finished so far — what the illustration should show.
    if (current === 0) {
      return 0;
    }
    if (current > steps.length) {
      return steps.length;
    }
    return revealed ? current : current - 1;
  }

  function paint() {
    var scene = completed();
    game.setAttribute("data-step", String(scene));
    // The room follows the step being asked; the state inside it follows the
    // steps already finished.
    game.setAttribute("data-current", String(current));
    dots.forEach(function (dot, i) {
      dot.classList.toggle("is-done", i + 1 <= scene);
      dot.classList.toggle("is-current", i + 1 === current && !revealed);
    });
    // Only the live step's hotspot is reachable, so a stale target cannot be
    // tabbed to or clicked out of turn.
    hotspots.forEach(function (spot) {
      var mine = parseInt(spot.getAttribute("data-for"), 10) === current;
      spot.hidden = !(mine && !revealed);
    });
  }

  function goTo(index, moveFocus, startRevealed) {
    current = index;
    revealed = Boolean(startRevealed);
    intro.hidden = index !== 0;

    steps.forEach(function (step, i) {
      var showing = i + 1 === index;
      step.hidden = !showing;
      step.querySelector(".wt-step__result").hidden = !(showing && revealed);
      step.querySelector(".wt-next").hidden = !(showing && revealed);
    });

    done.hidden = index <= steps.length;
    restartBtn.hidden = index === 0;
    paint();

    if (moveFocus) {
      var target;
      if (index === 0) {
        target = startBtn;
      } else if (index > steps.length) {
        target = done.querySelector(".wt-back");
      } else if (revealed) {
        target = steps[index - 1].querySelector(".wt-next");
      } else {
        target = hotspots[index - 1];
      }
      if (target) {
        target.focus();
      }
    }
  }

  function reveal(index) {
    revealed = true;
    var step = steps[index - 1];
    step.querySelector(".wt-step__result").hidden = false;
    var next = step.querySelector(".wt-next");
    next.hidden = false;
    paint();
    next.focus();
  }

  startBtn.addEventListener("click", function () {
    goTo(1, true);
  });

  restartBtn.addEventListener("click", function () {
    goTo(0, true);
  });

  hotspots.forEach(function (spot) {
    spot.addEventListener("click", function () {
      reveal(parseInt(spot.getAttribute("data-for"), 10));
    });
  });

  steps.forEach(function (step, i) {
    step.querySelector(".wt-next").addEventListener("click", function () {
      goTo(i + 2, true);
    });
    step.querySelector(".wt-back").addEventListener("click", function () {
      // Always one step back, shown as already done so it can be reread.
      // Going forward again re-asks the step, so it stays replayable.
      goTo(i, true, i > 0);
    });
  });

  done.querySelector(".wt-back").addEventListener("click", function () {
    goTo(steps.length, true, true);
  });

  goTo(0, false);
})();
