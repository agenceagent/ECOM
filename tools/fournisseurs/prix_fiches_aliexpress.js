// Relève le prix affiché et les options (tailles, modèles) de fiches AliExpress, quand la recherche
// par image n'a pas donné de prix ou a donné le prix d'une autre taille.
// Une capture d'écran par fiche pour vérifier à l'œil. Pause entre deux fiches ; en cas de demande
// de connexion ou de captcha, on s'arrête (on ne contourne jamais ces protections).
// Constaté le 19/11/2026 : reCAPTCHA dès la première fiche après une série de recherches par image ;
// relever ces prix à la main dans un navigateur connecté.
// Usage : PWPATH=$(npm root -g)/playwright node prix_fiches_aliexpress.js DOSSIER_SORTIE "nom|url" ...
const { chromium } = require(process.env.PWPATH);
const fs = require("fs");
const path = require("path");
const [out, ...paires] = process.argv.slice(2);
const dormir = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 1000 }, locale: "fr-FR", timezoneId: "Europe/Paris" });
  await ctx.addCookies([{ name: "aep_usuc_f", value: "site=fra&c_tp=EUR&region=FR&b_locale=fr_FR", domain: ".aliexpress.com", path: "/" }]);
  const resultats = {};
  for (const [k, pair] of paires.entries()) {
    const [nom, url] = pair.split("|");
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(9000);
      const texte = (await page.innerText("body")).replace(/\s+/g, " ");
      // Le reCAPTCHA s'affiche dans une fenêtre à part (iframe) : son texte n'est pas dans la page
      const robot = page.frames().some(f => /recaptcha|captcha|punish/i.test(f.url())) ||
        /check if you are a robot|captcha|slide to verify|Se connecter \/ S'inscrire.{0,40}Désolé/i.test(texte.slice(0, 600));
      if (robot) {
        resultats[nom] = { url, bloque: texte.slice(0, 160) };
        console.log(nom, "bloqué : arrêt.");
        await page.close();
        break;
      }
      const titre = await page.title();
      const prix = await page.$$eval("[class*='price--current'], [class*='product-price-current'], [class*='price-default--current']",
        els => els.map(e => e.innerText.replace(/\s+/g, " ").trim()).filter(Boolean).slice(0, 3));
      const options = await page.$$eval("[class*='sku-item--title'], [class*='sku-property-text'], [class*='sku-item--property'] [title], [data-sku-col] [title]",
        els => els.map(e => (e.getAttribute("title") || e.innerText || "").replace(/\s+/g, " ").trim()).filter(Boolean).slice(0, 20));
      await page.screenshot({ path: path.join(out, nom + ".png") });
      resultats[nom] = { url, titre, prix, options, debut: texte.slice(0, 400) };
      console.log(nom, "|", prix.join(" / "), "|", options.join(" ; ").slice(0, 200));
    } catch (e) { resultats[nom] = { url, erreur: e.message }; console.log(nom, "erreur", e.message); }
    await page.close();
    if (k < paires.length - 1) await dormir(30000);
  }
  fs.writeFileSync(path.join(out, "prix_fiches.json"), JSON.stringify(resultats, null, 1));
  await browser.close();
  console.log("FIN FICHES");
})().catch(e => { console.error("ERR", e.message); process.exit(1); });
