/* Interactive MRI walk-through.
 *
 * The page ships a plain ordered list of the steps and a hidden step-by-step
 * version. This script swaps them, so a reader without JavaScript gets the
 * whole thing as prose rather than buttons that do nothing.
 *
 * Each step reveals its explanation on click, then offers the next one. The
 * scene's data-step drives the illustration from CSS; no state lives here
 * beyond the current index.
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

  if (!game || !steps.length) {
    return;
  }

  // Enhance: hide the prose version, show the interactive one.
  staticList.hidden = true;
  game.hidden = false;

  var current = 0; // 0 = not started

  function show(el, visible) {
    el.hidden = !visible;
  }

  function paint() {
    game.setAttribute("data-step", String(current));
    dots.forEach(function (dot, i) {
      dot.classList.toggle("is-done", i + 1 <= current);
      dot.classList.toggle("is-current", i + 1 === current);
    });
  }

  function goTo(index, moveFocus) {
    current = index;
    show(intro, index === 0);
    steps.forEach(function (step, i) {
      show(step, i + 1 === index);
      // A step re-entered after a restart should ask again, not show its answer.
      var result = step.querySelector(".wt-step__result");
      var action = step.querySelector(".wt-step__action");
      if (i + 1 !== index) {
        result.hidden = true;
        action.removeAttribute("data-answered");
        action.textContent = action.getAttribute("data-action-label");
      }
    });
    show(done, index > steps.length);
    show(restartBtn, index > 0);
    paint();

    if (moveFocus) {
      var target = index === 0
        ? startBtn
        : index > steps.length
          ? restartBtn
          : steps[index - 1].querySelector(".wt-step__action");
      if (target) {
        target.focus();
      }
    }
  }

  startBtn.addEventListener("click", function () {
    goTo(1, true);
  });

  restartBtn.addEventListener("click", function () {
    goTo(0, true);
  });

  steps.forEach(function (step, i) {
    var action = step.querySelector(".wt-step__action");
    var result = step.querySelector(".wt-step__result");

    action.addEventListener("click", function () {
      if (action.getAttribute("data-answered")) {
        // Second press moves on; the first revealed the explanation.
        goTo(i + 2, true);
        return;
      }
      result.hidden = false;
      action.setAttribute("data-answered", "true");
      action.textContent = action.getAttribute("data-next-label");
      // Advancing the scene on reveal lets the illustration react immediately.
      current = i + 1;
      paint();
      action.focus();
    });
  });

  goTo(0, false);
})();
