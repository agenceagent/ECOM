/* Simulateur « budget pub → ventes → résultat », réutilisable dans toutes les leçons.

   Usage :
   <div class="simu wide" id="simu-1"
        data-titre="Ton test Google Ads"
        data-prix="449" data-cout="220" data-frais="3" data-urssaf="12.3" data-retours="5"
        data-budget="1000" data-cpc="1.2" data-conv="1"></div>

   Toutes les valeurs data-* sont optionnelles (valeurs par défaut ci-dessous).
   Les calculs sont dans window.SimuPub.compute(), testable à part. */
(function () {
  "use strict";

  var DEFAULTS = { prix: 449, cout: 220, frais: 3, urssaf: 12.3, retours: 5, budget: 1000, cpc: 1.2, conv: 1 };
  var ROAS_CIBLE_MIN = 15; // conversions en 30 jours, Aide Google Ads « À propos du ROAS cible »

  function compute(v) {
    var variablePct = (v.frais + v.urssaf + v.retours) / 100;
    var fraisVar = v.prix * variablePct;
    var marge = v.prix - v.cout - fraisVar;
    var clics = v.cpc > 0 ? v.budget / v.cpc : 0;
    var ventes = clics * (v.conv / 100);
    var ca = ventes * v.prix;
    var resultat = ventes * marge - v.budget;
    return {
      fraisPaiement: v.prix * v.frais / 100,
      cotisations: v.prix * v.urssaf / 100,
      provision: v.prix * v.retours / 100,
      marge: marge,
      cpaMax: marge,
      roasRentab: marge > 0 ? v.prix / marge : Infinity,
      clics: clics,
      ventes: ventes,
      ca: ca,
      cpaAttendu: ventes > 0 ? v.budget / ventes : Infinity,
      roasAttendu: v.budget > 0 ? ca / v.budget : 0,
      resultat: resultat,
      convRentab: marge > 0 ? (v.cpc / marge) * 100 : Infinity
    };
  }

  var nf0 = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
  var nf1 = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  var nf2 = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function eur(n) { return isFinite(n) ? nf2.format(n) + " €" : "—"; }
  function eur0(n) { return isFinite(n) ? (n > 0 ? "+" : "") + nf0.format(n) + " €" : "—"; }

  var FIELDS = [
    { group: "Le produit", items: [
      { k: "prix", label: "Prix de vente", hint: "payé par le client", unit: "€", step: "1" },
      { k: "cout", label: "Coût produit livré", hint: "produit + livraison + taxes", unit: "€", step: "1" },
      { k: "frais", label: "Frais de paiement", hint: "carte, en % du prix", unit: "%", step: "0.1" },
      { k: "urssaf", label: "Cotisations URSSAF", hint: "micro, vente de marchandises", unit: "%", step: "0.1" },
      { k: "retours", label: "Provision retours et SAV", hint: "ton hypothèse", unit: "%", step: "0.5" }
    ] },
    { group: "Le test publicitaire", items: [
      { k: "budget", label: "Budget pub", hint: "sur la période de test", unit: "€", step: "50" },
      { k: "cpc", label: "CPC moyen", hint: "coût d'un clic", unit: "€", step: "0.05" },
      { k: "conv", label: "Taux de conversion", hint: "clics qui achètent", unit: "%", step: "0.1" }
    ] }
  ];

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function parse(raw) {
    var n = Number(String(raw).replace(/\s/g, "").replace(",", "."));
    return isFinite(n) && n >= 0 ? n : 0;
  }

  function build(root) {
    var id = root.id || "simu";
    var start = {};
    Object.keys(DEFAULTS).forEach(function (k) {
      var d = root.getAttribute("data-" + k);
      start[k] = d != null ? parse(d) : DEFAULTS[k];
    });

    root.appendChild(el("h3", "simu-title", root.getAttribute("data-titre") || "Simulateur de test publicitaire"));
    root.appendChild(el("p", "simu-sub", "Exemple prérempli. Remplace les valeurs par celles de ton produit : tout se recalcule."));

    var grid = el("div", "simu-grid");
    var form = el("form");
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    var inputs = {};

    FIELDS.forEach(function (g) {
      var fs = el("fieldset");
      fs.appendChild(el("legend", null, g.group));
      g.items.forEach(function (f) {
        var row = el("div", "field");
        var lab = el("label", null, f.label);
        lab.setAttribute("for", id + "-" + f.k);
        lab.appendChild(el("small", null, f.hint));
        var wrap = el("div", "input");
        var inp = el("input");
        inp.id = id + "-" + f.k;
        inp.type = "number";
        inp.min = "0";
        inp.step = f.step;
        inp.inputMode = "decimal";
        inp.value = String(start[f.k]);
        inp.addEventListener("input", render);
        inputs[f.k] = inp;
        wrap.appendChild(inp);
        wrap.appendChild(el("span", "unit", f.unit));
        row.appendChild(lab);
        row.appendChild(wrap);
        fs.appendChild(row);
      });
      form.appendChild(fs);
    });
    var reset = el("button", "reset", "Revenir à l'exemple");
    reset.type = "button";
    reset.addEventListener("click", function () {
      Object.keys(inputs).forEach(function (k) { inputs[k].value = String(start[k]); });
      render();
    });
    form.appendChild(reset);

    var res = el("div", "results");
    res.setAttribute("aria-live", "polite");

    var ticket = el("div", "ticket");
    var kpis = el("div", "kpis");
    var verdict = el("div", "verdict");
    var verdictText = el("p", "verdict-text");

    res.appendChild(ticket);
    res.appendChild(verdict);
    res.appendChild(kpis);
    res.appendChild(verdictText);

    grid.appendChild(form);
    grid.appendChild(res);
    root.appendChild(grid);

    function row(label, value, cls) {
      var r = el("div", "t-row" + (cls ? " " + cls : ""));
      r.appendChild(el("span", null, label));
      r.appendChild(el("span", null, value));
      return r;
    }

    function kpi(label, value) {
      var k = el("div", "kpi");
      k.appendChild(el("div", "k", label));
      k.appendChild(el("div", "v", value));
      return k;
    }

    function render() {
      var v = {};
      Object.keys(inputs).forEach(function (k) { v[k] = parse(inputs[k].value); });
      var r = compute(v);

      ticket.textContent = "";
      ticket.appendChild(el("div", "t-head", "Ticket d'une commande"));
      ticket.appendChild(row("Prix de vente", eur(v.prix)));
      ticket.appendChild(row("− Coût produit livré", eur(v.cout), "minus"));
      ticket.appendChild(row("− Frais de paiement", eur(r.fraisPaiement), "minus"));
      ticket.appendChild(row("− Cotisations URSSAF", eur(r.cotisations), "minus"));
      ticket.appendChild(row("− Provision retours", eur(r.provision), "minus"));
      var tot = el("div", "t-total " + (r.marge > 0 ? "pos" : "neg"));
      tot.appendChild(el("span", null, "= Marge par commande"));
      tot.appendChild(el("span", null, eur(r.marge)));
      ticket.appendChild(tot);

      kpis.textContent = "";
      kpis.appendChild(kpi("CPA max", eur(r.cpaMax)));
      kpis.appendChild(kpi("ROAS de rentabilité", isFinite(r.roasRentab) ? "×" + nf2.format(r.roasRentab) + " (" + nf0.format(r.roasRentab * 100) + " %)" : "—"));
      kpis.appendChild(kpi("Clics achetés", nf0.format(r.clics)));
      kpis.appendChild(kpi("Ventes attendues", nf1.format(r.ventes)));
      kpis.appendChild(kpi("Taux de conversion de rentabilité", isFinite(r.convRentab) ? nf2.format(r.convRentab) + " %" : "—"));
      kpis.appendChild(kpi("ROAS attendu", "×" + nf2.format(r.roasAttendu)));

      verdict.textContent = "";
      var pill, msg;
      if (r.marge <= 0) {
        pill = el("span", "pill loss", "Produit non viable");
        msg = "Ce produit perd de l'argent avant même la publicité : baisse le coût ou monte le prix.";
      } else if (r.resultat > 0.5) {
        pill = el("span", "pill gain", "Test rentable " + eur0(r.resultat));
        msg = "Avec ces hypothèses, le test rapporte plus qu'il ne coûte. Vérifie que le taux de conversion et le CPC sont réalistes.";
      } else if (r.resultat < -0.5) {
        pill = el("span", "pill loss", "Test en perte " + eur0(r.resultat));
        msg = "Il faudrait au moins " + (isFinite(r.convRentab) ? nf2.format(r.convRentab) + " %" : "—") + " de taux de conversion avec ce CPC pour ne pas perdre d'argent.";
      } else {
        pill = el("span", "pill warn", "À l'équilibre");
        msg = "Le test ne gagne ni ne perd : tu achètes surtout des données.";
      }
      verdict.appendChild(pill);
      var data = el("span", "pill " + (r.ventes >= ROAS_CIBLE_MIN ? "gain" : "warn"),
        nf1.format(r.ventes) + " / " + ROAS_CIBLE_MIN + " ventes en 30 j requises pour le ROAS cible");
      verdict.appendChild(data);
      verdictText.textContent = msg;
    }

    render();
  }

  window.SimuPub = { compute: compute };

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll(".simu"), build);
  }
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  }
})();
