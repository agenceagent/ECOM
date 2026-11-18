// Recherche par image sur AliExpress (France, euros) : charge une photo, relève les premiers résultats.
// Usage : PWPATH=$(npm root -g)/playwright node recherche_image_aliexpress.js PHOTO.jpg PREFIXE_SORTIE
// Produit PREFIXE_SORTIE-resultats.json et une capture d'écran. Ensuite :
//   python3 -I planche_comparaison.py DOSSIER NOM PLANCHE.jpg   (NOM-q.jpg = photo du concurrent)
// Limites constatées le 18/11/2026 : reCAPTCHA sur la page d'accueil (on passe par une page de recherche),
// et demande de connexion après 2 ou 3 recherches d'affilée. Ne jamais tenter de contourner un captcha.
const { chromium } = require(process.env.PWPATH);
const fs = require("fs");
const [img, outPrefix] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 1000 }, locale: "fr-FR", timezoneId: "Europe/Paris" });
  await ctx.addCookies([{ name: "aep_usuc_f", value: "site=fra&c_tp=EUR&region=FR&b_locale=fr_FR", domain: ".aliexpress.com", path: "/" }]);
  const page = await ctx.newPage();
  await page.goto("https://fr.aliexpress.com/w/wholesale-produit.html?g=y", { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(6000);
  let inputs = await page.$$("input[type=file]");
  if (!inputs.length) {
    const cands = await page.$$eval("[class]", els => els.filter(e => /pic.?search|camera|image.?search|imgsearch/i.test(String(e.className))).slice(0, 8).map(e => String(e.className).slice(0, 80)));
    console.log("éléments appareil photo :", JSON.stringify(cands));
    for (const sel of ["[class*='picSearch']", "[class*='pic-search']", "[class*='camera']", "[class*='imageSearch']", "[class*='image-search']"]) {
      const el = page.locator(sel).first();
      if (await el.count()) {
        await el.click({ timeout: 5000 }).catch(() => {});
        await page.waitForTimeout(2500);
        inputs = await page.$$("input[type=file]");
        if (inputs.length) { console.log("champ fichier ouvert via", sel); break; }
      }
    }
  }
  console.log("champs fichier trouvés :", inputs.length);
  if (!inputs.length) {
    await page.screenshot({ path: outPrefix + "-accueil.png" });
    console.log((await page.innerText("body")).slice(0, 400));
    await browser.close();
    return;
  }
  await inputs[0].setInputFiles(img);
  await page.waitForURL(/image|imgsearch|imagesearch/i, { timeout: 45000 }).catch(() => {});
  await page.waitForTimeout(8000);
  console.log("url résultats :", page.url().slice(0, 140));
  const body = await page.innerText("body");
  if (/glisser|slide|captcha|inhabituel/i.test(body.slice(0, 1500))) console.log("BLOQUÉ (anti-robot)");
  await page.screenshot({ path: outPrefix + "-resultats.png" });
  const items = await page.$$eval("a[href*='/item/']", as => {
    const seen = new Set(), r = [];
    for (const a of as) {
      const m = a.href.match(/\/item\/(\d+)\.html/);
      if (!m || seen.has(m[1])) continue;
      seen.add(m[1]);
      const im = a.querySelector("img");
      const t = (a.innerText || "").replace(/\s+/g, " ").trim();
      if (t.length > 15) r.push({ url: "https://fr.aliexpress.com/item/" + m[1] + ".html", img: im ? (im.currentSrc || im.src) : null, text: t.slice(0, 220) });
      if (r.length >= 6) break;
    }
    return r;
  });
  fs.writeFileSync(outPrefix + "-resultats.json", JSON.stringify(items, null, 1));
  items.forEach((it, i) => console.log((i + 1) + ". " + it.url + " | " + it.text));
  await browser.close();
})().catch(e => { console.error("ERR", e.message); process.exit(1); });
