// Recherche fournisseurs en lot : pour chaque produit de lot.json,
// 1) photo, titre et prix de la page concurrente (fiche Shopify .json, sinon balise og:image),
// 2) recherche par image AliExpress (France, euros), 6 premiers résultats,
// 3) si demandé, recherche texte VidaXL (4 premiers résultats).
// Pause entre deux recherches AliExpress ; en cas de blocage (captcha, connexion), une seule
// nouvelle tentative après une longue pause, puis arrêt. On ne contourne jamais un captcha.
// Usage : PWPATH=$(npm root -g)/playwright node lot_recherche.js lot.json DOSSIER_SORTIE [ligne_de_depart]
const { chromium } = require(process.env.PWPATH);
const fs = require("fs");
const path = require("path");
const [lotFile, out, depart] = process.argv.slice(2);
const PAUSE = 60000, PAUSE_BLOCAGE = 300000;
const dormir = ms => new Promise(r => setTimeout(r, ms));
const propre = u => u.split("?")[0];

async function concurrent(ctx, url, dest) {
  const r = { url: propre(url) };
  try {
    const j = await ctx.request.get(propre(url) + ".json", { timeout: 30000 });
    if (j.ok()) {
      const p = (await j.json()).product;
      r.titre = p.title; r.prix = Math.min(...p.variants.map(v => parseFloat(v.price)));
      r.image = p.images[0] && p.images[0].src;
    }
  } catch (e) { /* pas Shopify : on tente la page */ }
  if (!r.image) {
    try {
      const h = await (await ctx.request.get(url, { timeout: 30000 })).text();
      r.image = (h.match(/property="og:image"\s+content="([^"]+)"/) || h.match(/content="([^"]+)"\s+property="og:image"/) || [])[1];
      r.titre = r.titre || (h.match(/property="og:title"\s+content="([^"]+)"/) || [])[1];
      const pm = h.match(/product:price:amount"\s+content="([\d.,]+)"/); if (pm) r.prix = parseFloat(pm[1].replace(",", "."));
    } catch (e) { r.erreur = e.message; }
  }
  if (r.image) {
    const src = r.image.startsWith("//") ? "https:" + r.image : r.image;
    const img = await ctx.request.get(src, { timeout: 30000 });
    fs.writeFileSync(dest, await img.body());
    r.fichier = dest;
  }
  return r;
}

async function rechercheImage(browser, img) {
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 1000 }, locale: "fr-FR", timezoneId: "Europe/Paris" });
  await ctx.addCookies([{ name: "aep_usuc_f", value: "site=fra&c_tp=EUR&region=FR&b_locale=fr_FR", domain: ".aliexpress.com", path: "/" }]);
  const page = await ctx.newPage();
  try {
    await page.goto("https://fr.aliexpress.com/w/wholesale-produit.html?g=y", { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(6000);
    let inputs = await page.$$("input[type=file]");
    if (!inputs.length) {
      const cam = page.locator("[class*='picSearch']").first();
      if (await cam.count()) { await cam.click({ timeout: 5000 }).catch(() => {}); await page.waitForTimeout(2500); }
      inputs = await page.$$("input[type=file]");
    }
    if (!inputs.length) return { bloque: "pas de champ image (" + (await page.innerText("body")).slice(0, 80).replace(/\s+/g, " ") + ")" };
    await inputs[0].setInputFiles(img);
    await page.waitForURL(/isNewImageSearch|imagesearch/i, { timeout: 45000 }).catch(() => {});
    await page.waitForTimeout(8000);
    const items = await page.$$eval("a[href*='/item/']", as => {
      const seen = new Set(), r = [];
      for (const a of as) {
        const m = a.href.match(/\/item\/(\d+)\.html/);
        if (!m || seen.has(m[1])) continue;
        seen.add(m[1]);
        const im = a.querySelector("img");
        const t = (a.innerText || "").replace(/\s+/g, " ").trim();
        if (t.length > 15) r.push({ url: "https://fr.aliexpress.com/item/" + m[1] + ".html", img: im ? (im.currentSrc || im.src) : null, texte: t.slice(0, 240) });
        if (r.length >= 6) break;
      }
      return r;
    });
    if (!items.length) return { bloque: (await page.innerText("body")).slice(0, 120).replace(/\s+/g, " ") };
    items.forEach(it => { const m = it.texte.match(/(\d[\d\s]*,\d{2})\s?€/); it.prix = m ? parseFloat(m[1].replace(/\s/g, "").replace(",", ".")) : null; });
    return { resultats: items };
  } finally { await ctx.close(); }
}

async function rechercheVidaxl(browser, motcle) {
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 1000 }, locale: "fr-FR" });
  const page = await ctx.newPage();
  try {
    await page.goto("https://www.vidaxl.fr/prefix?q=" + encodeURIComponent(motcle), { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(7000);
    return await page.$$eval("a[href*='/e/']", as => {
      const seen = new Set(), r = [];
      for (const a of as) {
        const h = a.href.split("?")[0];
        if (seen.has(h)) continue;
        const tuile = a.closest("[class*='product'], [class*='tile'], li, article") || a;
        const t = (tuile.innerText || "").replace(/\s+/g, " ").trim();
        const im = tuile.querySelector("img");
        const m = t.match(/(\d[\d\s]*,\d{2})\s?€/) || t.match(/(\d+)\s(\d{2})\s?€/);
        if (!/vidaXL/i.test(t)) continue;
        seen.add(h);
        r.push({ url: h, img: im ? (im.currentSrc || im.src) : null, texte: t.slice(0, 160),
                 prix: m ? parseFloat((m[2] ? m[1] + "." + m[2] : m[1].replace(/\s/g, "").replace(",", "."))) : null });
        if (r.length >= 4) break;
      }
      return r;
    });
  } catch (e) { return [{ erreur: e.message }]; } finally { await ctx.close(); }
}

(async () => {
  const lot = JSON.parse(fs.readFileSync(lotFile, "utf8")).produits.filter(p => !depart || p.ligne >= 0);
  const debut = depart ? lot.findIndex(p => String(p.ligne) === String(depart)) : 0;
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const req = await browser.newContext();
  for (const p of lot.slice(Math.max(0, debut))) {
    const nom = "ligne" + p.ligne;
    const fiche = path.join(out, nom + ".json");
    if (fs.existsSync(fiche) && JSON.parse(fs.readFileSync(fiche)).aliexpress) { console.log(nom, "déjà fait"); continue; }
    const r = { ligne: p.ligne, produit: p.produit };
    r.concurrent = await concurrent(req, p.concurrent, path.join(out, nom + "-concurrent.img"));
    if (r.concurrent.fichier) {
      let a = await rechercheImage(browser, r.concurrent.fichier);
      if (a.bloque) { console.log(nom, "bloqué :", a.bloque, "- pause longue puis 2e essai"); await dormir(PAUSE_BLOCAGE); a = await rechercheImage(browser, r.concurrent.fichier); }
      r.aliexpress = a;
      if (a.bloque) { fs.writeFileSync(fiche, JSON.stringify(r, null, 1)); console.log(nom, "toujours bloqué : arrêt du lot."); break; }
    } else r.aliexpress = { bloque: "pas de photo concurrente" };
    if (p.vidaxl) r.vidaxl = await rechercheVidaxl(browser, p.vidaxl);
    fs.writeFileSync(fiche, JSON.stringify(r, null, 1));
    console.log(nom, p.produit, "| concurrent", r.concurrent.prix, "€ |", (r.aliexpress.resultats || []).length, "résultats AliExpress |", (r.vidaxl || []).length, "VidaXL");
    await dormir(PAUSE);
  }
  await browser.close();
  console.log("FIN DU LOT");
})().catch(e => { console.error("ERR", e.message); process.exit(1); });
