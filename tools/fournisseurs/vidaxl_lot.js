// Recherche texte VidaXL seule, pour croiser les sources avec AliExpress.
// Écrit vidaxlNN.json (NN = ligne de la grille) dans le dossier de sortie ; planches_lot.py les fusionne.
// Usage : PWPATH=$(npm root -g)/playwright node vidaxl_lot.js DOSSIER_SORTIE "ligne|mot-clé" ...
const { chromium } = require(process.env.PWPATH);
const fs = require("fs");
const path = require("path");
const [out, ...paires] = process.argv.slice(2);

(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  for (const pair of paires) {
    const [ligne, motcle] = pair.split("|");
    const ctx = await browser.newContext({ viewport: { width: 1366, height: 1000 }, locale: "fr-FR" });
    const page = await ctx.newPage();
    let res = [];
    try {
      await page.goto("https://www.vidaxl.fr/prefix?q=" + encodeURIComponent(motcle), { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(6000);
      res = await page.$$eval("a[href*='/e/']", as => {
        const seen = new Set(), r = [];
        for (const a of as) {
          const h = a.href.split("?")[0];
          if (seen.has(h)) continue;
          const tuile = a.closest("[class*='product'], [class*='tile'], li, article") || a;
          const t = (tuile.innerText || "").replace(/\s+/g, " ").trim();
          if (!/vidaXL/i.test(t)) continue;
          seen.add(h);
          r.push({ url: h, texte: t.slice(0, 160) });
          if (r.length >= 4) break;
        }
        return r;
      });
    } catch (e) { res = [{ erreur: e.message }]; }
    await ctx.close();
    fs.writeFileSync(path.join(out, "vidaxl" + ligne + ".json"), JSON.stringify({ ligne: +ligne, motcle, vidaxl: res }, null, 1));
    console.log("ligne" + ligne, motcle, "|", res.length, "résultats VidaXL");
  }
  await browser.close();
  console.log("FIN VIDAXL");
})().catch(e => { console.error("ERR", e.message); process.exit(1); });
