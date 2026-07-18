/* Multiple-choice quiz + reveal panels. No dependencies. */
(function () {
  "use strict";

  // --- multiple-choice quiz -------------------------------------------
  document.querySelectorAll("[data-quiz]").forEach(function (quiz) {
    var answer = parseInt(quiz.getAttribute("data-answer"), 10);
    var choices = quiz.querySelectorAll(".choice");
    var verdict = quiz.querySelector(".verdict");
    var panel = quiz.querySelector(".answer-panel");
    var done = false;

    choices.forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (done) return;
        done = true;
        var picked = parseInt(btn.getAttribute("data-index"), 10);
        choices.forEach(function (b) {
          b.disabled = true;
          var i = parseInt(b.getAttribute("data-index"), 10);
          if (i === answer) {
            b.classList.add("correct");
          } else if (i === picked) {
            b.classList.add("wrong");
          } else {
            b.classList.add("dim");
          }
        });
        if (verdict) {
          if (picked === answer) {
            verdict.textContent = "✅ Correct!";
            verdict.classList.add("ok");
          } else {
            verdict.textContent = "❌ Not quite — the answer is \"" +
              choices[answer].querySelector(".label").textContent + "\"";
            verdict.classList.add("ng");
          }
        }
        if (panel) panel.classList.add("open");
      });
    });
  });

  // --- reveal buttons --------------------------------------------------
  document.querySelectorAll("[data-reveal]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = document.getElementById(btn.getAttribute("data-reveal"));
      if (target) target.classList.add("open");
      btn.style.display = "none";
    });
  });

})();
