// Prix de vente lus dans un vrai navigateur, pour les sites concurrents qui ne sont pas sur Shopify
// ou qui refusent les requêtes simples : données structurées (JSON-LD) + capture d'écran pour vérifier à l'œil.
// Usage : PWPATH=$(npm root -g)/playwright node prix_pages_navigateur.js DOSSIER_SORTIE "nom|url" ...
const { chromium } = require(process.env.PWPATH);
const fs = require("fs");
const path = require("path");
const [out, ...paires] = process.argv.slice(2);

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 900 }, locale: "fr-FR", timezoneId: "Europe/Paris" });
  const res = {};
  for (const pair of paires) {
    const [nom, url] = pair.split("|");
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(6000);
      const ld = await page.$$eval("script[type='application/ld+json']", ss => ss.map(s => s.textContent));
      const offres = [];
      for (const t of ld) {
        try {
          const visit = o => {
            if (!o || typeof o !== "object") return;
            if (Array.isArray(o)) return o.forEach(visit);
            if (o.price || o.lowPrice) offres.push({ prix: o.price || o.lowPrice, devise: o.priceCurrency });
            Object.values(o).forEach(visit);
          };
          visit(JSON.parse(t));
        } catch (e) { /* JSON-LD invalide */ }
      }
      await page.screenshot({ path: path.join(out, nom + ".png") });
      res[nom] = { url, titre: await page.title(), offres: offres.slice(0, 5) };
      console.log(nom, "|", JSON.stringify(offres.slice(0, 3)), "|", res[nom].titre.slice(0, 70));
    } catch (e) { res[nom] = { url, erreur: e.message }; console.log(nom, "erreur", e.message.slice(0, 100)); }
    await page.close();
  }
  fs.writeFileSync(path.join(out, "prix_pages.json"), JSON.stringify(res, null, 1));
  await browser.close();
})().catch(e => { console.error("ERR", e.message); process.exit(1); });
