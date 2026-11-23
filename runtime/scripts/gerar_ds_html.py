"""Gera a página navegável de um design system a partir do tokens.json.

Saída na pasta design-systems/<slug>/:
    design-system.html        catálogo: visão geral, fundamentos e componentes
    assets/componentes.css    componentes reutilizáveis (.btn, .btn2, .lnk, .card, .nav, .in, .selo, .h1…)
                              -> é ESTE arquivo que um site leva junto com tokens.css
    assets/catalogo.css       só o layout do catálogo (não vai para os sites)

Por padrão não sobrescreve assets/componentes.css se ele já existir, porque o agente
refina esse arquivo à mão na etapa de componentes. Use --refazer-componentes para recriar.

Exemplo:
    python gerar_ds_html.py linear
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from urllib.parse import quote_plus

from _comum import DESIGN_SYSTEMS, erro

AMOSTRA = {
    "h1": "Interfaces com identidade",
    "h2": "Uma direção visual clara",
    "h3": "Regras que a IA consegue seguir",
    "t1": "Texto corrido de exemplo para medir leitura, ritmo e altura de linha em parágrafos curtos.",
    "t2": "Texto secundário, legendas e descrições de apoio.",
    "t3": "META · 19 NOV · RÓTULO",
}

COMPONENTES_CSS = """/* ==========================================================================
   componentes.css — componentes do design system, só com tokens (tokens.css).
   Ponto de partida gerado; refine com os estados medidos na fonte (ver catálogo).
   ========================================================================== */

/* tags tipadas (mesmos nomes do wireframe do /criar-site) */
.h1, .h2, .h3 { font-family: var(--font-title); color: var(--text); }
.h1 { font-size: var(--fs-h1); font-weight: var(--fw-h1); line-height: var(--lh-h1); letter-spacing: var(--ls-h1); }
.h2 { font-size: var(--fs-h2); font-weight: var(--fw-h2); line-height: var(--lh-h2); letter-spacing: var(--ls-h2); }
.h3 { font-size: var(--fs-h3); font-weight: var(--fw-h3); line-height: var(--lh-h3); letter-spacing: var(--ls-h3); }
.t1, .t2, .t3 { font-family: var(--font-body); }
.t1 { font-size: var(--fs-t1); font-weight: var(--fw-t1); line-height: var(--lh-t1); letter-spacing: var(--ls-t1); color: var(--text); }
.t2 { font-size: var(--fs-t2); font-weight: var(--fw-t2); line-height: var(--lh-t2); letter-spacing: var(--ls-t2); color: var(--text-muted); }
.t3 { font-size: var(--fs-t3); font-weight: var(--fw-t3); line-height: var(--lh-t3); letter-spacing: var(--ls-t3); color: var(--text-muted); }

/* botões: .btn primário, .btn2 secundário, .lnk link de navegação */
.btn, .btn2, .lnk {
  display: inline-flex; align-items: center; gap: var(--space-2);
  font-family: var(--font-body); font-size: var(--fs-t1); font-weight: 500; line-height: 1;
  border: 1px solid transparent; cursor: pointer; text-decoration: none;
  transition: background-color var(--dur-base) var(--ease), color var(--dur-base) var(--ease),
              border-color var(--dur-base) var(--ease), box-shadow var(--dur-base) var(--ease),
              transform var(--dur-fast) var(--ease);
}
.btn  { padding: var(--space-3) var(--space-5); border-radius: __RAIO_BTN__; background: var(--accent); color: var(--on-accent); }
.btn2 { padding: var(--space-3) var(--space-5); border-radius: __RAIO_BTN__; background: var(--surface); color: var(--text); border-color: var(--border); }
.lnk  { padding: var(--space-2) var(--space-3); border-radius: __RAIO_BTN__; background: transparent; color: var(--text-muted); }
.btn:hover, .btn.is-hover   { filter: brightness(1.12); }
.btn2:hover, .btn2.is-hover { border-color: var(--text-muted); }
.lnk:hover, .lnk.is-hover   { color: var(--text); background: var(--surface); }
.btn:focus-visible, .btn2:focus-visible, .lnk:focus-visible, .in:focus-visible,
.btn.is-focus, .btn2.is-focus, .lnk.is-focus, .in.is-focus { outline: __FOCO__; outline-offset: 2px; }
.btn:disabled, .btn2:disabled, .is-disabled { opacity: 0.45; cursor: not-allowed; filter: none; }

/* campo */
.in {
  width: 100%; padding: var(--space-3) var(--space-4);
  font: inherit; font-size: var(--fs-t1); color: var(--text);
  background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-md);
  transition: border-color var(--dur-base) var(--ease);
}
.in::placeholder { color: var(--text-muted); }

/* selo */
.selo {
  display: inline-flex; align-items: center; padding: 2px var(--space-3);
  font-size: var(--fs-t2); color: var(--text); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius-pill);
}

/* card */
.card {
  display: flex; flex-direction: column; gap: var(--space-3);
  padding: var(--space-6); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-md);
  transition: transform var(--dur-base) var(--ease), border-color var(--dur-base) var(--ease);
}
.card:hover, .card.is-hover { border-color: var(--text-muted); }

/* nav */
.nav {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-5);
  padding: var(--space-4) var(--space-6); background: var(--bg); border-bottom: 1px solid var(--border);
}
.nav-links { display: flex; gap: var(--space-2); }
"""

CATALOGO_CSS = """/* catalogo.css — layout do catálogo (não copiar para sites) */
*, *::before, *::after { box-sizing: border-box; }
* { margin: 0; }
body { background: var(--bg); color: var(--text); font-family: var(--font-body); line-height: 1.5; -webkit-font-smoothing: antialiased; }
img { display: block; max-width: 100%; }
.cat { max-width: 1200px; margin: 0 auto; padding: 0 clamp(16px, 4vw, 40px) 96px; }
.cat-topo { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;
  padding: 20px 0; border-bottom: 1px solid var(--border); position: sticky; top: 0; background: var(--bg); z-index: 5; }
.cat-indice { display: flex; gap: 4px; flex-wrap: wrap; }
.cat-sec { padding-top: 64px; display: grid; gap: 24px; scroll-margin-top: 72px; }
.cat-rot { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; }
.cat-nota { font-size: 13px; color: var(--text-muted); max-width: 70ch; }
.cat-dupla { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; align-items: start; }
.cat-moldura { border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; }
.cat-palco { padding: 32px; border: 1px solid var(--border); border-radius: var(--radius-lg); display: grid; gap: 20px; }
.cat-linha { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.cat-grade { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }
.sw { border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; font-size: 12px; }
.sw-cor { height: 72px; }
.sw-txt { padding: 8px 10px; display: grid; gap: 2px; }
.sw-txt b { font-weight: 600; font-size: 13px; }
.sw-txt span { color: var(--text-muted); font-family: var(--font-mono); }
.tipo { display: grid; grid-template-columns: 160px 1fr; gap: 16px; padding: 16px 0; border-top: 1px solid var(--border); align-items: baseline; }
.tipo-meta { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); display: grid; gap: 2px; }
.forma { height: 96px; display: grid; place-items: center; background: var(--surface); border: 1px solid var(--border);
  font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
.esp { display: flex; align-items: center; gap: 12px; font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
.esp i { display: block; height: 12px; background: var(--accent); border-radius: 2px; }
.mov { height: 96px; display: grid; place-items: center; background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-md); font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); cursor: default; }
.mov-fast { transition: transform var(--dur-fast) var(--ease); }
.mov-base { transition: transform var(--dur-base) var(--ease); }
.mov-slow { transition: transform var(--dur-slow) var(--ease); }
.mov:hover { transform: translateY(-6px); }
.comp { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; padding: 24px 0; border-top: 1px solid var(--border); }
.estado { display: grid; gap: 8px; justify-items: start; }
.fonte-rec { border: 1px dashed var(--border); border-radius: var(--radius-sm); padding: 8px; display: grid; gap: 8px; max-width: 100%; }
.fonte-rec img { max-height: 220px; width: auto; }
.tab { width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 12px; }
.tab td, .tab th { text-align: left; padding: 6px 8px; border-top: 1px solid var(--border); vertical-align: top; }
.tab th { color: var(--text-muted); font-weight: 400; }
.ex-hero { display: grid; gap: 16px; padding: 40px; border: 1px solid var(--border); border-radius: var(--radius-lg); }
.ex-card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
"""


def e(t) -> str:
    return html.escape(str(t), quote=True)


def gerar(pasta: Path, refazer_componentes: bool) -> list[str]:
    t = json.loads((pasta / "tokens.json").read_text(encoding="utf-8"))
    (pasta / "assets").mkdir(exist_ok=True)
    c, tip, f, mv = t["cores"], t["tipografia"], t["formas"], t["movimento"]
    gerados = []

    comp = pasta / "assets" / "componentes.css"
    if refazer_componentes or not comp.exists():
        raio_btn = "var(--radius-pill)" if f.get("usa_pill") else "var(--radius-md)"
        foco = f"1px solid var(--accent)" if not t.get("anel_foco") else "1px solid " + t["anel_foco"].split(" ", 2)[-1]
        comp.write_text(COMPONENTES_CSS.replace("__RAIO_BTN__", raio_btn).replace("__FOCO__", foco), encoding="utf-8")
        gerados.append("assets/componentes.css")

    # catálogo: classes de amostra de cor/forma geradas (nada de style inline)
    din = ["", "/* amostras geradas */"]
    papeis_cor = ["bg", "surface", "text", "text-muted", "accent", "on-accent", "border"]
    papeis_cor += [k for k, v in c.items() if k not in papeis_cor and not k.startswith("_") and isinstance(v, str)]
    for k in papeis_cor:
        din.append(f".sw-{k} {{ background: var(--{k}); }}")
    din.append(".sw-linha { display: flex; gap: 8px; margin-top: 18px; }")
    din.append(".sw-linha span { width: 40px; height: 40px; border-radius: 10px; border: 1px solid var(--border); }")
    extras = []
    for grupo in ("fundos", "textos", "bordas"):
        for item in t["paleta"].get(grupo, []):
            if item["hex"] not in extras:
                extras.append(item["hex"])
    for i, hx in enumerate(extras[:16]):
        din.append(f".pal-{i} {{ background: {hx}; }}")
    for k in ("sm", "md", "lg"):
        din.append(f".r-{k} {{ border-radius: var(--radius-{k}); }}")
    din.append(".r-pill { border-radius: var(--radius-pill); }")
    for i, _ in enumerate(f["sombras"]):
        din.append(f".sh-{i} {{ box-shadow: var(--shadow-{('sm', 'md', 'lg')[i]}); border-radius: var(--radius-md); }}")
    for i, v in enumerate(f["espacos"], 1):
        din.append(f".esp-{i} {{ width: var(--space-{i}); }}")
    for i, g in enumerate(t["fundos"]["gradientes"]):
        din.append(f".grad-{i} {{ background-image: {g}; }}")
    (pasta / "assets" / "catalogo.css").write_text(CATALOGO_CSS + "\n".join(din) + "\n", encoding="utf-8")
    gerados.append("assets/catalogo.css")

    # Google Fonts: um <link> por família (uma família inexistente não derruba as outras)
    familias = []
    for nome in (tip["familias"]["titulo"], tip["familias"]["corpo"], tip["familias"]["mono"]):
        if nome:
            g = tip["fontes"].get(nome, {}).get("sugestao_google", nome)
            if g not in familias:
                familias.append(g)
    links_fontes = "\n".join(
        f'  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={quote_plus(g)}:wght@400;500;600;700&display=swap">'
        for g in familias)

    fonte = pasta / "fonte"
    recortes = {}
    cap_arq = fonte / "captura.json"
    if cap_arq.exists():
        for comp_c in json.loads(cap_arq.read_text(encoding="utf-8"))["componentes"]:
            if comp_c.get("recorte"):
                recortes.setdefault(comp_c["tipo"], []).append(("fonte/" + comp_c["recorte"], comp_c["txt"]))

    def rec(tipo, n=2):
        itens = recortes.get(tipo, [])[:n]
        if not itens:
            return '<p class="cat-nota">Sem recorte deste tipo na fonte.</p>'
        return "".join(f'<figure class="fonte-rec"><img src="{e(src)}" alt="Na fonte: {e(txt)}" loading="lazy">'
                       f'<figcaption class="cat-nota">na fonte</figcaption></figure>' for src, txt in itens)

    sw = "".join(
        f'<div class="sw"><div class="sw-cor sw-{k}"></div><div class="sw-txt"><b>--{k}</b><span>{e(c[k])}</span>'
        f'{"<span>contraste " + str(c["_contraste"].get(k + "/bg", "")) + "</span>" if k + "/bg" in c["_contraste"] else ""}'
        f"</div></div>" for k in papeis_cor)
    pal = "".join(f'<div class="sw"><div class="sw-cor pal-{i}"></div><div class="sw-txt"><span>{e(hx)}</span></div></div>'
                  for i, hx in enumerate(extras[:16]))

    tipos = "".join(
        f'<div class="tipo"><div class="tipo-meta"><b>.{p}</b><span>{e(d["familia"])}</span>'
        f'<span>{e(d["peso"])} · {d["tamanho"]:g}px · {d["altura_linha"]:g}</span>'
        f'<span>ls {d["espacamento_em"]:g}em{" · " + e(d["caixa"]) if d["caixa"] != "none" else ""}</span></div>'
        f'<p class="{p}">{e(AMOSTRA[p])}</p></div>' for p, d in tip["papeis"].items())
    avisos_fonte = "".join(
        f'<li>{e(n)} ({e(i["origem"])}) → no Google Fonts: <b>{e(i["sugestao_google"])}</b></li>'
        for n, i in tip["fontes"].items() if i["origem"] != "google")

    raios = "".join(f'<div class="forma r-{k}">--radius-{k} · {e(f.get("radius-" + k, 999))}{"px" if k != "pill" else ""}</div>'
                    for k in ("sm", "md", "lg", "pill"))
    sombras = "".join(f'<div class="forma sh-{i}">--shadow-{("sm", "md", "lg")[i]}</div>' for i in range(len(f["sombras"]))) \
        or '<p class="cat-nota">A fonte não usa sombras.</p>'
    espacos = "".join(f'<div class="esp"><i class="esp-{i}"></i>--space-{i} · {v}px</div>'
                      for i, v in enumerate(f["espacos"], 1))
    durs = mv["duracoes_ms"] or [150, 250, 400]
    movs = "".join(f'<div class="mov mov-{k}">passe o mouse · {k} · {v}ms</div>'
                   for k, v in (("fast", durs[0]), ("base", durs[len(durs) // 2]), ("slow", durs[-1])))
    grads = "".join(f'<div class="forma r-md grad-{i}"></div>' for i in range(len(t["fundos"]["gradientes"])))

    estados = "".join(
        f"<tr><td>{e(k)}</td><td>{e(v['exemplo'])}</td><td>"
        + "<br>".join(f"{e(p)}: {e(a)} → {e(b)}" for p, (a, b) in v["muda"].items()) + "</td></tr>"
        for k, v in t.get("estados", {}).items())

    if (fonte / "dobra.png").exists():
        figura_fonte = '<figure class="cat-moldura"><img src="fonte/dobra.png" alt="Primeira tela da fonte"></figure>'
    elif t["origem"].get("combinado_de"):
        partes = t["origem"]["combinado_de"]
        figura_fonte = ('<div class="cat-palco"><p class="cat-rot">combinação</p>'
                        + "".join(f'<p class="t2"><b>{e(g)}</b> ← {e(s)}</p>' for g, s in partes.items())
                        + "</div>")
    else:
        conceito = t.get("_conceito", {})
        perfil = conceito.get("motion") or mv.get("perfil") or ""
        figura_fonte = ('<div class="cat-palco grad-0"><p class="cat-rot">modelo autoral</p>'
                        f'<p class="h2">{e(t["origem"].get("titulo") or pasta.name)}</p>'
                        f'<p class="t2">Títulos em {e(tip["familias"]["titulo"])}, corpo em {e(tip["familias"]["corpo"])}.</p>'
                        + (f'<p class="t2">Movimento: {e(perfil)}.</p>' if perfil else "")
                        + '<div class="sw-linha">'
                        + "".join(f'<span class="sw-{k}" title="--{k}"></span>' for k in ("bg", "surface", "accent", "accent-2", "text") if k in c)
                        + "</div></div>")
    nota_fonte = ("A captura da fonte serve só para comparação e não deve ir para os sites: marca, textos e "
                  "imagens dela não fazem parte deste design system. ") if (fonte / "dobra.png").exists() else ""
    if t["origem"].get("combinado_de"):
        origem_txt = f'Design system combinado em {e(t["origem"]["extraido_em"])}'
    elif "autoral" in str(t["origem"].get("url", "")):
        origem_txt = f'Modelo autoral NOVYRA, definido em {e(t["origem"]["extraido_em"])} (não extraído de nenhum site)'
    else:
        origem_txt = f'Extraído de {e(t["origem"]["url"])} em {e(t["origem"]["extraido_em"])}'

    def estados_btn(cls, rot):
        return "".join(f'<div class="estado"><span class="cat-rot">{n}</span><button class="{cls} {m}" type="button"'
                       f'{" disabled" if n == "desativado" else ""}>{rot}</button></div>'
                       for n, m in (("padrão", ""), ("hover", "is-hover"), ("foco", "is-focus"), ("desativado", "")))

    paginas = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Design system · {e(pasta.name)}</title>
{links_fontes}
  <link rel="stylesheet" href="tokens.css">
  <link rel="stylesheet" href="assets/componentes.css">
  <link rel="stylesheet" href="assets/catalogo.css">
</head>
<body>
<div class="cat">
  <header class="cat-topo">
    <div>
      <p class="cat-rot">design system</p>
      <p class="h3">{e(pasta.name)}</p>
    </div>
    <nav class="cat-indice" aria-label="Seções">
      <a class="lnk" href="#visao">Visão geral</a><a class="lnk" href="#cores">Cores</a>
      <a class="lnk" href="#tipografia">Tipografia</a><a class="lnk" href="#formas">Formas</a>
      <a class="lnk" href="#movimento">Movimento</a><a class="lnk" href="#componentes">Componentes</a>
    </nav>
  </header>

  <section class="cat-sec" id="visao">
    <p class="cat-rot">1 · visão geral</p>
    <p class="cat-nota">{origem_txt}. {nota_fonte}Ao lado, uma composição feita apenas com os tokens.</p>
    <div class="cat-dupla">
      {figura_fonte}
      <div class="ex-hero">
        <span class="selo">Novo · exemplo</span>
        <h1 class="h1">{e(AMOSTRA["h1"])}</h1>
        <p class="t1">{e(AMOSTRA["t1"])}</p>
        <div class="cat-linha"><a class="btn" href="#componentes">Começar</a><a class="btn2" href="#cores">Saiba mais</a></div>
        <div class="ex-card-grid">
          <article class="card"><h3 class="h3">Card</h3><p class="t2">{e(AMOSTRA["t2"])}</p></article>
          <article class="card"><h3 class="h3">Card</h3><p class="t2">{e(AMOSTRA["t2"])}</p></article>
        </div>
      </div>
    </div>
  </section>

  <section class="cat-sec" id="cores">
    <p class="cat-rot">2 · cores (papéis)</p>
    <div class="cat-grade">{sw}</div>
    <p class="cat-nota">Paleta completa encontrada na fonte (fundos, textos e bordas, por uso):</p>
    <div class="cat-grade">{pal}</div>
  </section>

  <section class="cat-sec" id="tipografia">
    <p class="cat-rot">3 · tipografia</p>
    <div>{tipos}</div>
    {"<ul class='cat-nota'>" + avisos_fonte + "</ul>" if avisos_fonte else ""}
  </section>

  <section class="cat-sec" id="formas">
    <p class="cat-rot">4 · formas, sombras e espaçamento</p>
    <div class="cat-grade">{raios}</div>
    <div class="cat-grade">{sombras}</div>
    <div>{espacos}</div>
    {('<p class="cat-nota">Gradientes usados na fonte:</p><div class="cat-grade">' + grads + "</div>") if grads else ""}
  </section>

  <section class="cat-sec" id="movimento">
    <p class="cat-rot">5 · movimento</p>
    <div class="cat-grade">{movs}</div>
    <p class="cat-nota">Curva: {e(mv["curva"])}. Elementos animados na fonte: {mv["elementos_animados"]}.
      @keyframes: {e(", ".join(mv["keyframes"][:12]) or "nenhum legível")}.</p>
  </section>

  <section class="cat-sec" id="componentes">
    <p class="cat-rot">6 · componentes</p>
    <div class="comp"><div class="estado"><p class="h3">Botão primário</p><p class="t2">.btn</p></div>{estados_btn("btn", "Começar")}{rec("botao")}</div>
    <div class="comp"><div class="estado"><p class="h3">Botão secundário</p><p class="t2">.btn2</p></div>{estados_btn("btn2", "Saiba mais")}</div>
    <div class="comp"><div class="estado"><p class="h3">Link</p><p class="t2">.lnk</p></div>{estados_btn("lnk", "Produto")}{rec("link")}</div>
    <div class="comp"><div class="estado"><p class="h3">Campo</p><p class="t2">.in</p></div>
      <div class="estado"><span class="cat-rot">padrão</span><input class="in" placeholder="seu@email.com" aria-label="Exemplo de campo"></div>
      <div class="estado"><span class="cat-rot">foco</span><input class="in is-focus" placeholder="seu@email.com" aria-label="Exemplo de campo em foco"></div>
      {rec("campo", 1)}</div>
    <div class="comp"><div class="estado"><p class="h3">Selo</p><p class="t2">.selo</p></div>
      <div class="estado"><span class="selo">Novo</span><span class="selo">Beta</span></div>{rec("selo")}</div>
    <div class="comp"><div class="estado"><p class="h3">Card</p><p class="t2">.card</p></div>
      <article class="card"><span class="t3">{e(AMOSTRA["t3"])}</span><h3 class="h3">Título do card</h3><p class="t2">{e(AMOSTRA["t2"])}</p></article>
      <article class="card is-hover"><span class="t3">hover</span><h3 class="h3">Título do card</h3><p class="t2">{e(AMOSTRA["t2"])}</p></article>
      {rec("card")}</div>
    <div class="comp"><div class="estado"><p class="h3">Navegação</p><p class="t2">.nav</p></div>
      <header class="nav"><span class="h3">Marca</span><nav class="nav-links" aria-label="Exemplo">
        <a class="btn2" href="#visao">Início</a><a class="lnk" href="#cores">Produto</a><a class="lnk" href="#movimento">Preços</a></nav></header>
      {rec("nav", 1)}</div>
    <p class="cat-nota">Estados medidos na fonte (o que muda em hover e foco):</p>
    <table class="tab"><tr><th>componente:estado</th><th>exemplo</th><th>muda</th></tr>{estados or "<tr><td colspan='3'>nenhum medido</td></tr>"}</table>
  </section>
</div>
</body>
</html>
"""
    (pasta / "design-system.html").write_text(paginas, encoding="utf-8")
    gerados.append("design-system.html")
    return gerados


def main() -> None:
    p = argparse.ArgumentParser(description="tokens.json -> design-system.html + componentes.css")
    p.add_argument("slug")
    p.add_argument("--refazer-componentes", action="store_true")
    args = p.parse_args()
    pasta = DESIGN_SYSTEMS / args.slug
    if not (pasta / "tokens.json").exists():
        erro(f"rode antes: python extrair_tokens.py {args.slug}")
    for g in gerar(pasta, args.refazer_componentes):
        print(f"gerado: {pasta / g}")


if __name__ == "__main__":
    main()
