// Coletor executado DENTRO da página pelo capturar_site.py (Playwright).
// Lê os estilos calculados dos elementos visíveis e marca candidatos a componente.
// Não altera a página, exceto pelo atributo data-dsx nos candidatos (para o Python achá-los).
// Retorna um objeto JSON simples.
() => {
  const LIMITE = 6000;
  const W = window.innerWidth;

  // --- cor: qualquer formato (rgb, oklch, lab, nome) -> [r,g,b,a] via canvas 1x1
  const cv = document.createElement("canvas");
  cv.width = cv.height = 1;
  const cx = cv.getContext("2d", { willReadFrequently: true });
  const cache = new Map();
  const cor = (c) => {
    if (!c || c === "transparent" || c === "rgba(0, 0, 0, 0)") return null;
    if (cache.has(c)) return cache.get(c);
    let v = null;
    try {
      cx.clearRect(0, 0, 1, 1);
      cx.fillStyle = "#000";
      cx.fillStyle = c;
      cx.fillRect(0, 0, 1, 1);
      const d = cx.getImageData(0, 0, 1, 1).data;
      v = d[3] === 0 ? null : [d[0], d[1], d[2], +(d[3] / 255).toFixed(2)];
    } catch (e) { v = null; }
    cache.set(c, v);
    return v;
  };

  const textoProprio = (el) => {
    let t = "";
    for (const n of el.childNodes) if (n.nodeType === 3) t += n.textContent;
    return t.replace(/\s+/g, " ").trim();
  };

  const visivel = (el, r, s) =>
    r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none" && +s.opacity > 0.05;

  const estilos = (s) => ({
    color: cor(s.color),
    bg: cor(s.backgroundColor),
    bgImg: s.backgroundImage !== "none" ? s.backgroundImage.slice(0, 400) : null,
    ff: s.fontFamily,
    fw: s.fontWeight,
    fs: parseFloat(s.fontSize),
    lh: s.lineHeight,
    ls: s.letterSpacing,
    tt: s.textTransform,
    br: s.borderRadius,
    bs: s.boxShadow !== "none" ? s.boxShadow : null,
    bw: parseFloat(s.borderTopWidth) || 0,
    bc: parseFloat(s.borderTopWidth) ? cor(s.borderTopColor) : null,
    pad: [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft].map(parseFloat),
    gap: s.gap && s.gap !== "normal" ? parseFloat(s.gap) : null,
    tr: s.transition && !/^all 0s ease 0s$/.test(s.transition) ? s.transition.slice(0, 200) : null,
    an: s.animationName !== "none" ? s.animationName : null,
    bf: s.backdropFilter && s.backdropFilter !== "none" ? s.backdropFilter : null,
    ts: s.textShadow !== "none" ? s.textShadow : null,
    op: +s.opacity,
  });

  // --- elementos visíveis com algo a dizer (texto, fundo, borda, sombra, imagem de fundo)
  const els = [];
  const todos = document.body.querySelectorAll("*");
  for (const el of todos) {
    if (els.length >= LIMITE) break;
    if (["SCRIPT", "STYLE", "NOSCRIPT", "META", "LINK", "BR", "PATH", "G", "DEFS"].includes(el.tagName)) continue;
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    if (!visivel(el, r, s)) continue;
    const st = estilos(s);
    const txt = textoProprio(el);
    if (!txt && !st.bg && !st.bw && !st.bs && !st.bgImg && !st.an && !st.bf) continue;
    els.push({
      tag: el.tagName.toLowerCase(),
      txt: txt.slice(0, 80),
      x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY),
      w: Math.round(r.width), h: Math.round(r.height),
      s: st,
    });
  }

  // --- candidatos a componente
  const marcar = [];
  let id = 0;
  const assinatura = (st) => JSON.stringify([st.bg, st.color, st.br, st.bw, st.bc, st.bs, st.fs, st.fw]);
  const vistos = {};
  const add = (tipo, el, max) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    if (!visivel(el, r, s)) return;
    const st = estilos(s);
    const sig = tipo + assinatura(st);
    vistos[tipo] = vistos[tipo] || 0;
    if (marcar.some((m) => m.sig === sig) || vistos[tipo] >= max) return;
    vistos[tipo]++;
    const dsx = "c" + id++;
    el.setAttribute("data-dsx", dsx);
    marcar.push({
      tipo, dsx, sig, tag: el.tagName.toLowerCase(),
      txt: (el.innerText || el.value || el.placeholder || "").replace(/\s+/g, " ").trim().slice(0, 60),
      x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY),
      w: Math.round(r.width), h: Math.round(r.height), s: st,
    });
  };
  const temFundoOuBorda = (s) => cor(s.backgroundColor) || parseFloat(s.borderTopWidth) > 0;

  document.querySelectorAll("header, nav, [role=navigation]").forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.top + scrollY < 200 && r.width > W * 0.5) add("nav", el, 2);
  });
  document.querySelectorAll("button, [role=button], input[type=submit], a").forEach((el) => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    const t = (el.innerText || "").trim();
    if (!t || t.length > 40 || r.height < 24 || r.height > 80) return;
    if (temFundoOuBorda(s) && parseFloat(s.paddingLeft) >= 8) add("botao", el, 6);
    else if (el.tagName === "A") add("link", el, 4);
  });
  document.querySelectorAll("input:not([type=hidden]):not([type=submit]):not([type=checkbox]):not([type=radio]), textarea, select")
    .forEach((el) => add("campo", el, 3));
  for (const el of todos) {
    if (vistos.card >= 6 && vistos.selo >= 4) break;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (r.width === 0) continue;
    const pai = el.parentElement ? getComputedStyle(el.parentElement) : null;
    const fundoProprio = cor(s.backgroundColor) && (!pai || s.backgroundColor !== pai.backgroundColor);
    const destaque = fundoProprio || parseFloat(s.borderTopWidth) > 0 || s.boxShadow !== "none";
    if (!destaque || parseFloat(s.borderRadius) <= 0) continue;
    const t = (el.innerText || "").trim();
    if (r.width >= 160 && r.width <= 720 && r.height >= 100 && r.height <= 900 && t.length > 10) add("card", el, 6);
    else if (r.height <= 32 && r.width <= 220 && t && t.length <= 24 && fundoProprio) add("selo", el, 4);
  }

  // --- CSS: variáveis do :root, @keyframes, @font-face (folhas de outro domínio podem bloquear a leitura)
  const vars = {}, keyframes = {}, fontes = [];
  let folhasBloqueadas = 0;
  const folhasExternas = [];
  const lerRegras = (regras) => {
    for (const r of regras) {
      if (r.cssRules && !(r instanceof CSSKeyframesRule)) { try { lerRegras(r.cssRules); } catch (e) {} }
      if (r instanceof CSSStyleRule && /(^|,)\s*(:root|html)\s*(,|$)/.test(r.selectorText)) {
        for (const p of r.style) if (p.startsWith("--")) vars[p] = r.style.getPropertyValue(p).trim();
      } else if (r instanceof CSSKeyframesRule) {
        if (Object.keys(keyframes).length < 40) keyframes[r.name] = r.cssText.slice(0, 800);
      } else if (r instanceof CSSFontFaceRule) {
        fontes.push({ familia: r.style.getPropertyValue("font-family").replace(/["']/g, "").trim(),
                      peso: r.style.getPropertyValue("font-weight"),
                      src: r.style.getPropertyValue("src").slice(0, 200) });
      }
    }
  };
  for (const f of document.styleSheets) {
    try { lerRegras(f.cssRules); } catch (e) { folhasBloqueadas++; if (f.href) folhasExternas.push(f.href); }
  }
  const linksFontes = [...document.querySelectorAll("link[href*='fonts.googleapis'], link[href*='use.typekit'], link[href*='fonts.bunny']")]
    .map((l) => l.href);

  const raiz = getComputedStyle(document.documentElement), corpo = getComputedStyle(document.body);
  return {
    url: location.href,
    titulo: document.title,
    viewport: [W, window.innerHeight],
    alturaPagina: document.documentElement.scrollHeight,
    fundoPagina: cor(corpo.backgroundColor) || cor(raiz.backgroundColor) || [255, 255, 255, 1],
    elementos: els,
    componentes: marcar.map(({ sig, ...m }) => m),
    vars, keyframes, fontes, linksFontes, folhasBloqueadas, folhasExternas,
  };
}
