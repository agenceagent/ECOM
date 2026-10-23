/* Quiz à correction immédiate, réutilisable dans toutes les leçons.

   Usage :
   <section class="quiz" id="quiz-lecon-1" data-title="Quiz">
     <script type="application/json">
       { "questions": [
         { "type": "choice", "q": "…", "options": ["…", "…"], "answer": 1, "explain": "…" },
         { "type": "number", "q": "…", "answer": 4, "tolerance": 0.05, "unit": "×", "explain": "…" }
       ] }
     </script>
   </section>

   - "answer" d'une question "choice" = index de la bonne option (0 = première).
   - Une question "number" accepte la virgule ou le point, et ignore espaces, % et €.
   - Seule la première réponse compte (pratique de rappel) ; la bonne réponse s'affiche ensuite.
   - Le dernier score est gardé dans le navigateur, si le stockage local est disponible. */
(function () {
  "use strict";

  var LETTERS = ["A", "B", "C", "D", "E", "F"];

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function parseNum(raw) {
    if (raw == null) return NaN;
    var s = String(raw).replace(/[\s  %€×x]/gi, "").replace(",", ".");
    if (s === "") return NaN;
    return Number(s);
  }

  function fmt(n) {
    return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 }).format(n);
  }

  function store(key, value) {
    try {
      if (value === undefined) return window.localStorage.getItem(key);
      window.localStorage.setItem(key, value);
    } catch (e) { return null; }
    return null;
  }

  function setFeedback(box, ok, explain, extra) {
    box.hidden = false;
    box.className = "feedback " + (ok ? "right" : "wrong");
    box.textContent = "";
    var head = el("b", null, ok ? "Juste. " : "Pas tout à fait. ");
    box.appendChild(head);
    if (extra) box.appendChild(document.createTextNode(extra + " "));
    box.appendChild(document.createTextNode(explain || ""));
  }

  function buildQuiz(root) {
    var dataNode = root.querySelector('script[type="application/json"]');
    if (!dataNode) return;
    var data;
    try { data = JSON.parse(dataNode.textContent); } catch (e) { return; }
    var questions = data.questions || [];
    var answered = 0;
    var correct = 0;
    var key = "quiz:" + (root.id || location.pathname);

    var scoreBox = el("p", "score");
    scoreBox.setAttribute("aria-live", "polite");

    function updateScore() {
      scoreBox.textContent = "";
      if (answered < questions.length) {
        scoreBox.appendChild(document.createTextNode(answered + " / " + questions.length + " questions répondues"));
      } else {
        scoreBox.appendChild(document.createTextNode("Score : " + correct + " / " + questions.length));
        store(key, JSON.stringify({ score: correct, total: questions.length, date: new Date().toISOString().slice(0, 10) }));
      }
      var prev = store(key);
      if (prev && answered === 0) {
        try {
          var p = JSON.parse(prev);
          var span = el("span", "prev", "Dernier score enregistré dans ce navigateur : " + p.score + " / " + p.total + " (" + p.date + ")");
          scoreBox.appendChild(span);
        } catch (e) { /* ignore */ }
      }
    }

    function record(ok) {
      answered += 1;
      if (ok) correct += 1;
      updateScore();
    }

    questions.forEach(function (item, i) {
      var q = el("div", "q");
      q.appendChild(el("p", "q-num", "Question " + (i + 1) + " sur " + questions.length));
      var text = el("p", "q-text", item.q);
      text.id = (root.id || "quiz") + "-q" + i;
      q.appendChild(text);
      var fb = el("p", "feedback");
      fb.hidden = true;
      fb.setAttribute("aria-live", "polite");

      if (item.type === "number") {
        var row = el("div", "numrow");
        var input = el("input");
        input.type = "text";
        input.inputMode = "decimal";
        input.id = text.id + "-input";
        input.setAttribute("aria-labelledby", text.id);
        input.autocomplete = "off";
        var unit = item.unit ? el("span", "muted", item.unit) : null;
        var btn = el("button", "btn", "Vérifier");
        btn.type = "button";
        function check() {
          var v = parseNum(input.value);
          if (isNaN(v)) {
            fb.hidden = false;
            fb.className = "feedback wrong";
            fb.textContent = "Entre un nombre (par exemple 2,5).";
            return;
          }
          var tol = item.tolerance != null ? item.tolerance : 0.01;
          var ok = Math.abs(v - item.answer) <= tol * Math.max(1, Math.abs(item.answer));
          input.disabled = true;
          btn.disabled = true;
          setFeedback(fb, ok, item.explain, ok ? null : "La réponse attendue est " + fmt(item.answer) + (item.unit ? " " + item.unit : "") + ".");
          record(ok);
        }
        btn.addEventListener("click", check);
        input.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); check(); } });
        row.appendChild(input);
        if (unit) row.appendChild(unit);
        row.appendChild(btn);
        q.appendChild(row);
      } else {
        var opts = el("div", "opts");
        opts.setAttribute("role", "group");
        opts.setAttribute("aria-labelledby", text.id);
        var buttons = [];
        item.options.forEach(function (label, j) {
          var b = el("button", "opt");
          b.type = "button";
          b.appendChild(el("span", "letter", LETTERS[j]));
          b.appendChild(el("span", null, label));
          b.addEventListener("click", function () {
            var ok = j === item.answer;
            buttons.forEach(function (bb, k) {
              bb.disabled = true;
              if (k === item.answer) bb.classList.add("right");
            });
            if (!ok) b.classList.add("wrong");
            setFeedback(fb, ok, item.explain, ok ? null : "La bonne réponse est " + LETTERS[item.answer] + ".");
            record(ok);
          });
          buttons.push(b);
          opts.appendChild(b);
        });
        q.appendChild(opts);
      }
      q.appendChild(fb);
      root.appendChild(q);
    });

    root.appendChild(scoreBox);
    updateScore();
  }

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll(".quiz"), buildQuiz);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
