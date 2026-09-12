/* Japanese vocabulary flashcards (grid list). Reads a light JSON, lays out every
   word as a card. No dependencies. Same UI as the English hub.
   Front = Japanese word. Back = English meaning + reading (kana · romaji).
   - #w{id} … deep-link hook: scroll to that card, flip and highlight it.
   - Card faces are non-selectable (discourages casual copy-paste extraction). */
(function () {
  "use strict";

  var app = document.getElementById("vocab-app");
  if (!app) return;

  var src = app.getAttribute("data-src");

  function load() {
  app.innerHTML = '<p class="lead" role="status">Loading cards…</p>';
  fetch(src)
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function (data) {
      init(data.words || []);
      // Re-render on hash-only changes (in-page deep links) too.
      window.addEventListener("hashchange", function () { init(data.words || []); });
    })
    .catch(function () {
      app.innerHTML = '<p class="lead">Failed to load the data. Please try again later.</p>';
      var retry = el("button", "fc-btn", "Try again");
      retry.type = "button"; retry.addEventListener("click", load); app.appendChild(retry);
    });
  }
  load();

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function init(words) {
    var hashMatch = /^#w(\d+)$/.exec(location.hash);
    var targetId = hashMatch ? parseInt(hashMatch[1], 10) : null;

    app.innerHTML = "";

    // --- control bar ---
    var bar = el("div", "fc-bar");
    var flipAllBtn = el("button", "fc-btn", "Reveal visible cards");
    flipAllBtn.type = "button";
    flipAllBtn.setAttribute("aria-pressed", "false");
    bar.appendChild(flipAllBtn);
    bar.appendChild(el("span", "fc-bar-note", "Tap a card to flip"));
    app.appendChild(bar);

    // --- card grid ---
    var grid = el("div", "fc-grid");
    words.forEach(function (w) {
      var cell = el("button", "fc-cell");
      cell.type = "button";
      cell.id = "w" + w.id;
      cell.setAttribute("aria-label", "Show the meaning of " + w.j);

      var inner = el("div", "fc-cell-inner");

      var front = el("div", "fc-cell-face fc-cell-front");
      front.appendChild(el("span", "fc-cell-num", String(w.id)));
      var term = el("span", "fc-cell-term", w.j);
      term.lang = "ja";
      front.appendChild(term);

      var back = el("div", "fc-cell-face fc-cell-back");
      back.appendChild(el("span", "fc-cell-num", String(w.id)));
      back.appendChild(el("span", "fc-cell-meaning", w.e));
      var reading = w.k + (w.r ? "  ·  " + w.r : "");
      back.appendChild(el("span", "fc-cell-reading", reading));
      if (w.x) {
        var ex = el("span", "fc-cell-example", w.x);
        ex.lang = "ja";
        if (w.xe) ex.title = w.xe;
        back.appendChild(ex);
      }

      inner.appendChild(front);
      inner.appendChild(back);
      cell.appendChild(inner);

      cell.addEventListener("click", function () {
        cell.classList.toggle("flipped");
        var f = cell.classList.contains("flipped");
        cell.setAttribute("aria-label",
          (f ? "Hide the meaning of " : "Show the meaning of ") + w.j);
      });

      grid.appendChild(cell);
    });
    app.appendChild(grid);

    // --- flip all / reset ---
    var allFlipped = false;
    flipAllBtn.addEventListener("click", function () {
      allFlipped = !Array.from(grid.querySelectorAll(".fc-cell:not([hidden])")).every(function (cell) { return cell.classList.contains("flipped"); });
      flipAllBtn.setAttribute("aria-pressed", String(allFlipped));
      flipAllBtn.textContent = allFlipped ? "Reset visible cards" : "Reveal visible cards";
      grid.querySelectorAll(".fc-cell:not([hidden])").forEach(function (c) {
        c.classList.toggle("flipped", allFlipped);
      });
    });

    // --- deep link: scroll to, flip and highlight the target card ---
    if (targetId != null) {
      var target = document.getElementById("w" + targetId);
      if (target) {
        target.classList.add("flipped", "target");
        requestAnimationFrame(function () {
          target.scrollIntoView({ behavior: "smooth", block: "center" });
        });
      }
    }
    if (window.enhanceStudyGrid) window.enhanceStudyGrid(app);
  }
})();
