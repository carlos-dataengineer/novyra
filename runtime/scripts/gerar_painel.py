"""Gera o NOVYRA Studio: a página-ferramenta que o instalador cria e abre.

Ela reúne, num único HTML sem dependências locais:
  - o montador de comandos (imagem/briefing + template + design system -> comando pronto
    para Claude Code ou Codex, com botão de copiar);
  - a galeria dos templates (prévia ao vivo) e dos design systems (cores, fontes, catálogo);
  - os sites já criados e em que etapa cada um está;
  - as skills, os scripts e os atalhos de teclado.

A página é autocontida (templates entram como srcdoc), então serve tanto para abrir no
navegador quanto para publicar como artefato no Claude.

Exemplo:
    python gerar_painel.py                 # grava <RAIZ>/novyra.html
    python gerar_painel.py --saida x.html  # outro destino
    python gerar_painel.py --artefato      # sem links para arquivos locais (para publicar)
"""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path

from _comum import DESIGN_SYSTEMS, RAIZ, SITES, TEMPLATES

TEMPLATE_INFO = {
    "site-base": ("Base limpa", "Estrutura mínima para recriar qualquer mock pixel a pixel. É o padrão do /criar-site."),
    "immersive-3d-studio": ("Immersive 3D Studio", "Portfólio ou landing com objeto protagonista, palco escuro e narrativa."),
    "cinematic-sci-fi": ("Cinematic Sci-Fi", "Universo sci-fi, atmosfera espacial e conteúdo editorial."),
    "tech-product": ("Tech Product", "Produto B2B de IA/tecnologia com dados e módulos claros."),
    "studio-3d-light": ("Studio 3D Light", "Estúdio em página clara com palco 3D emoldurado e botões em pílula."),
    "retro-glitch": ("Retro Glitch", "Janelas de sistema antigo, verde neon, sombras duras e glitch."),
    "bio-data-mono": ("Bio Data Mono", "Natureza como dados: preto monocromático, grade, mira e módulos."),
}

SKILLS = [
    ("criar-site", "Imagem ou briefing vira site HTML + CSS em 5 etapas com aprovação.",
     'imagem="C:/mocks/tela.png" slug=meu-site', "imagem, brief, slug, ds, template"),
    ("wireframe", "Planta tipada da tela (ASCII ou SVG). É a etapa 1 do criar-site.",
     'formato=svg imagem="C:/mocks/tela.png"', "formato, imagem, brief, saida"),
    ("extrair-ds", "Extrai o design system de um site público: tokens, componentes e catálogo vivo.",
     "url=https://exemplo.com slug=referencia", "url, slug"),
    ("combinar-ds", "Combina design systems: cores de um, tipografia de outro, formas de um terceiro.",
     "nome=minha-marca base=novyra-future-lab tipografia=cinematic-sci-fi", "nome, base, cores, tipografia, formas, movimento, fundos"),
    ("novyra", "Abre este painel (no Claude, como artefato) e lista sites, templates e design systems.",
     "", "—"),
]

SCRIPTS = [
    ("novo_site.py", "cria sites/<slug> a partir de um template (--imagem, --ds, --template)"),
    ("recortar.py", "grade de coordenadas e recortes da imagem de referência"),
    ("amostrar_cores.py", "cores exatas de pontos e paleta de regiões"),
    ("capturar_tela.py", "captura do site no Chrome headless (--igual-referencia)"),
    ("comparar.py", "lado a lado + mapa de diferenças + nota de similaridade"),
    ("validar_site.py", "checa assets, caminhos, CSS/JS inline e CDNs proibidos"),
    ("capturar_site.py", "captura DOM e estilos calculados de uma URL (Playwright)"),
    ("extrair_tokens.py", "transforma a captura em tokens.json + tokens.css"),
    ("gerar_ds_html.py", "gera o catálogo navegável de um design system"),
    ("combinar_ds.py", "recombina grupos de tokens de vários design systems"),
    ("gerar_imagem.py", "opcional e pago: gera ícones/imagens via OpenRouter"),
    ("gerar_painel.py", "gera este painel"),
]

ETAPAS = [
    ("1", "Wireframe + plano", "Planta tipada, inventário de assets, fontes e seções."),
    ("2", "Fundo", "Cores, gradientes e camadas de fundo medidos na referência."),
    ("3", "Componentes + fontes", "Estrutura, tipografia e componentes com tokens."),
    ("4", "Assets", "Ícones, imagens e recortes; nada de placeholder esquecido."),
    ("5", "Revisão final", "Captura, comparação por pixels, validação e responsivo."),
]

ESTADO_RE = re.compile(r"^\|\s*(\d)\.\s*[^|]+\|\s*([^|]+?)\s*\|", re.M)
ESTADO_LINHA_RE = re.compile(r"^\|\s*(\d)\.\s*[^|]+\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|", re.M)
FEITO = ("aprovad", "feit", "conclu", "ok")

# Cada etapa do /criar-site vista como um agente do pipeline (painel "Pipeline")
AGENTES = [
    {"n": 1, "nome": "Agente de Planta", "etapa": "Wireframe + plano", "acao": "Mapeando regiões", "icone": "◫", "cor": "#3ddc97",
     "faz": "Lê a referência, desenha o wireframe tipado e decide a técnica de cada região.",
     "scripts": ["/wireframe"]},
    {"n": 2, "nome": "Agente de Atmosfera", "etapa": "Fundo completo", "acao": "Medindo o fundo", "icone": "◐", "cor": "#f5d90a",
     "faz": "Amostra cores e gradientes, monta as camadas de fundo e compara com a referência.",
     "scripts": ["amostrar_cores.py", "recortar.py", "comparar.py"]},
    {"n": 3, "nome": "Agente de Interface", "etapa": "Componentes + fontes", "acao": "Compondo a interface", "icone": "▦", "cor": "#20d9f5",
     "faz": "Constrói estrutura, tipografia e componentes com os tokens e compara região por região.",
     "scripts": ["capturar_tela.py", "comparar.py --caixa"]},
    {"n": 4, "nome": "Agente de Assets", "etapa": "Assets", "acao": "Encaixando assets", "icone": "◈", "cor": "#d946ef",
     "faz": "Recorta ou gera ícones, fotos e avatares e associa cada um à sua região.",
     "scripts": ["recortar.py", "gerar_imagem.py"]},
    {"n": 5, "nome": "Agente de Revisão", "etapa": "Revisão final", "acao": "Validando a entrega", "icone": "✓", "cor": "#ff8a5c",
     "faz": "Captura no tamanho da referência, mede a semelhança, valida o site e checa o celular.",
     "scripts": ["capturar_tela.py", "comparar.py", "validar_site.py"]},
]


def artefatos(pasta: Path) -> dict[int, list[tuple[str, bool]]]:
    """O que existe de fato na pasta do site, por etapa (para o painel não inventar progresso)."""
    cap = pasta / "_capturas"
    capturas = sorted(p.name for p in cap.glob("*.png")) if cap.exists() else []
    html_txt = (pasta / "index.html").read_text(encoding="utf-8", errors="ignore") if (pasta / "index.html").exists() else ""
    secoes = len(re.findall(r"<(section|header|footer|nav|article)\b", html_txt))
    crops = [p for p in (pasta / "assets" / "crops").glob("*") if p.is_file() and p.name != ".gitkeep"] \
        if (pasta / "assets" / "crops").exists() else []
    ref = next(iter(pasta.glob("reference.*")), None)
    return {
        1: [("referência " + (ref.name if ref else "(modo briefing)"), bool(ref)),
            ("wireframe.txt / .svg", (pasta / "wireframe.txt").exists() or (pasta / "wireframe.svg").exists()),
            ("plano no ESTADO.md", (pasta / "ESTADO.md").exists())],
        2: [("camadas de fundo no CSS", "/* 3. Fundo" in (pasta / "assets" / "styles.css").read_text(encoding="utf-8", errors="ignore")
             and ".bg" in (pasta / "assets" / "styles.css").read_text(encoding="utf-8", errors="ignore")
             if (pasta / "assets" / "styles.css").exists() else False),
            ("captura da etapa 2", any("etapa2" in c for c in capturas))],
        3: [(f"{secoes} regiões no index.html", secoes >= 3),
            ("captura da etapa 3", any("etapa3" in c for c in capturas)),
            ("design system (DS.md)", (pasta / "DS.md").exists())],
        4: [(f"{len(crops)} recorte(s) em assets/crops", bool(crops))],
        5: [("comparação lado a lado", any(c.endswith(".lado.png") for c in capturas)),
            ("captura final", any(c.startswith("final") for c in capturas))],
    }


def e(t) -> str:
    return html.escape(str(t), quote=True)


def versao() -> str:
    for arq in (RAIZ / "VERSION", RAIZ.parent / "VERSION"):
        if arq.exists():
            return arq.read_text(encoding="utf-8").strip()
    return "dev"


def html_template(pasta: Path) -> str:
    """HTML do template com o CSS externo embutido, para a prévia funcionar em srcdoc."""
    doc = (pasta / "index.html").read_text(encoding="utf-8")
    css = pasta / "assets" / "styles.css"
    if css.exists():
        doc = re.sub(r'<link[^>]+href="assets/styles\.css"[^>]*>',
                     lambda _m: "<style>" + css.read_text(encoding="utf-8") + "</style>", doc)
    return doc


def coletar_templates() -> list[dict]:
    itens = []
    if not TEMPLATES.exists():
        return itens
    for pasta in sorted(d for d in TEMPLATES.iterdir() if (d / "index.html").exists()):
        nome, desc = TEMPLATE_INFO.get(pasta.name, (pasta.name, "Template adicionado por você."))
        itens.append({"slug": pasta.name, "nome": nome, "desc": desc, "srcdoc": html_template(pasta),
                      "arquivo": (pasta / "index.html").as_posix()})
    itens.sort(key=lambda t: (t["slug"] != "site-base", t["slug"]))
    return itens


def coletar_ds() -> list[dict]:
    itens = []
    if not DESIGN_SYSTEMS.exists():
        return itens
    for pasta in sorted(d for d in DESIGN_SYSTEMS.iterdir() if (d / "tokens.json").exists()):
        try:
            t = json.loads((pasta / "tokens.json").read_text(encoding="utf-8"))
            c, fam = t["cores"], t["tipografia"]["familias"]
        except (KeyError, ValueError):
            continue
        cores = [(k, v) for k, v in c.items() if not k.startswith("_") and isinstance(v, str)]
        desc = ""
        if (pasta / "DS.md").exists():
            linhas = [l.strip() for l in (pasta / "DS.md").read_text(encoding="utf-8").splitlines()]
            desc = next((l for l in linhas[1:] if l and not l.startswith(("#", "|", "*", "-", ">"))), "")
        origem = t.get("origem", {})
        autoral = "autoral" in str(origem.get("url", ""))
        itens.append({"slug": pasta.name, "titulo": origem.get("titulo") or pasta.name, "desc": desc,
                      "cores": cores, "titulo_fonte": fam.get("titulo"), "corpo_fonte": fam.get("corpo"),
                      "tipo": "autoral" if autoral else ("combinado" if origem.get("combinado_de") else "extraído"),
                      "catalogo": (pasta / "design-system.html").as_posix()
                      if (pasta / "design-system.html").exists() else ""})
    itens.sort(key=lambda d: (d["tipo"] != "autoral", d["slug"] != "novyra-future-lab", d["slug"]))
    return itens


def coletar_referencias() -> dict:
    arq = RAIZ / "referencias" / "futuristas.json"
    if not arq.exists():
        return {"referencias": [], "fontes": []}
    try:
        return json.loads(arq.read_text(encoding="utf-8"))
    except ValueError:
        return {"referencias": [], "fontes": []}


def coletar_sites() -> list[dict]:
    itens = []
    if not SITES.exists():
        return itens
    for pasta in sorted(d for d in SITES.iterdir() if d.is_dir() and not d.name.startswith(".")):
        estado = pasta / "ESTADO.md"
        feitas, total = 0, 5
        linhas: dict[int, tuple[str, str]] = {}
        if estado.exists():
            txt = estado.read_text(encoding="utf-8")
            status = ESTADO_RE.findall(txt)
            total = len(status) or 5
            feitas = sum(1 for _n, s in status if s.lower().startswith(FEITO))
            linhas = {int(n): (s.strip(), o.strip()) for n, s, o in ESTADO_LINHA_RE.findall(txt)}
        arts = artefatos(pasta)
        etapas, ativa = [], None
        for ag in AGENTES:
            st, obs = linhas.get(ag["n"], ("pendente", ""))
            feito = st.lower().startswith(FEITO)
            if not feito and ativa is None:
                ativa = ag["n"]
            etapas.append({"n": ag["n"], "status": "feito" if feito else ("ativo" if ativa == ag["n"] else "fila"),
                           "obs": obs, "artefatos": arts.get(ag["n"], [])})
        ref = next((p for p in pasta.glob("reference.*")), None)
        itens.append({"slug": pasta.name, "feitas": feitas, "total": total, "etapas": etapas,
                      "arquivo": (pasta / "index.html").as_posix(), "ref": ref.name if ref else "",
                      "quando": datetime.fromtimestamp(pasta.stat().st_mtime).strftime("%d/%m/%Y")})
    itens.sort(key=lambda s: s["quando"], reverse=True)
    return itens


CSS = """
:root{--bg:#080b16;--surface:#11172a;--surface2:#1a2340;--text:#e5e7f0;--muted:#a7b0c4;--accent:#8757ff;
--accent2:#20d9f5;--border:rgba(135,87,255,.25);--ok:#3ddc97;--radius:18px;--shadow:0 24px 80px -24px rgba(135,87,255,.55);
--font-title:"Space Grotesk",system-ui,sans-serif;--font-body:"Inter",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
:root[data-theme="light"]{--bg:#f5f6fb;--surface:#ffffff;--surface2:#eceffa;--text:#12152a;--muted:#525a78;--accent:#6a3df0;
--accent2:#0a8fa6;--border:rgba(106,61,240,.22);--shadow:0 18px 50px -24px rgba(106,61,240,.35)}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 var(--font-body);
background-image:radial-gradient(60% 40% at 50% -5%,rgba(135,87,255,.35),transparent 70%),radial-gradient(40% 30% at 100% 10%,rgba(32,217,245,.12),transparent 70%);background-attachment:fixed}
a{color:var(--accent2)}code,kbd,pre{font-family:var(--mono)}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:10;backdrop-filter:blur(18px);background:color-mix(in srgb,var(--bg) 72%,transparent);border-bottom:1px solid var(--border)}
header.top .wrap{display:flex;align-items:center;gap:18px;height:64px}
.logo{font:700 20px var(--font-title);letter-spacing:.18em;display:flex;align-items:center;gap:10px}
.logo i{width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 0 24px rgba(135,87,255,.7)}
nav.tabs{display:flex;gap:4px;margin-left:auto;flex-wrap:wrap}
nav.tabs button{background:none;border:1px solid transparent;color:var(--muted);font:500 14px var(--font-body);padding:8px 14px;border-radius:999px;cursor:pointer}
nav.tabs button[aria-selected="true"]{color:var(--text);border-color:var(--border);background:var(--surface)}
nav.tabs button kbd{font-size:11px;opacity:.55;margin-left:6px}
.icon-btn{background:var(--surface);border:1px solid var(--border);color:var(--text);border-radius:999px;width:38px;height:38px;cursor:pointer}
.hero{padding:64px 0 28px}
.eyebrow{font:500 12px var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--accent2)}
h1{font:600 clamp(36px,6vw,64px)/1.02 var(--font-title);letter-spacing:-.03em;margin:10px 0 14px}
h1 span{background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}
h2{font:600 28px/1.15 var(--font-title);letter-spacing:-.02em;margin:0 0 6px}
h3{font:600 18px var(--font-title);margin:0 0 4px}
.lead{color:var(--muted);max-width:720px;font-size:17px}
.stats{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:10px 16px;font-size:13px;color:var(--muted)}
.stat b{display:block;font:600 22px var(--font-title);color:var(--text)}
section.panel{display:none;padding:12px 0 64px}section.panel.on{display:block}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:22px}
.grid{display:grid;gap:18px}.g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}.g3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.builder{display:grid;grid-template-columns:1.1fr .9fr;gap:18px}
@media(max-width:860px){.builder{grid-template-columns:1fr}header.top .wrap{height:auto;flex-wrap:wrap;padding-top:10px;padding-bottom:10px}}
label{display:block;font-size:13px;color:var(--muted);margin:14px 0 6px}
input,select,textarea{width:100%;background:var(--surface2);color:var(--text);border:1px solid var(--border);border-radius:12px;padding:11px 12px;font:14px var(--font-body)}
textarea{min-height:84px;resize:vertical}
input:focus,select:focus,textarea:focus,button:focus-visible{outline:2px solid var(--accent2);outline-offset:2px}
.seg{display:inline-flex;background:var(--surface2);border:1px solid var(--border);border-radius:999px;padding:3px}
.seg button{background:none;border:0;color:var(--muted);padding:7px 14px;border-radius:999px;cursor:pointer;font:500 13px var(--font-body)}
.seg button[aria-pressed="true"]{background:var(--accent);color:#fff}
.cmd{position:relative;background:#05070c;color:#dfe6ff;border:1px solid var(--border);border-radius:14px;padding:18px 18px 18px 18px;font:14px/1.6 var(--mono);white-space:pre-wrap;word-break:break-word;min-height:76px}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--accent);color:#fff;border:0;border-radius:999px;padding:10px 18px;font:600 14px var(--font-body);cursor:pointer;box-shadow:var(--shadow);text-decoration:none}
.btn2{display:inline-flex;align-items:center;gap:8px;background:var(--surface2);color:var(--text);border:1px solid var(--border);border-radius:999px;padding:8px 14px;font:500 13px var(--font-body);cursor:pointer;text-decoration:none}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:14px}
.flow{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:18px}
@media(max-width:860px){.flow{grid-template-columns:1fr 1fr}}
.step{background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:14px}
.step b{font:600 24px var(--font-title);color:var(--accent2)}.step p{margin:4px 0 0;font-size:13px;color:var(--muted)}
.prev{height:220px;border-radius:14px;overflow:hidden;border:1px solid var(--border);background:#000;position:relative}
.prev iframe{width:1440px;height:900px;border:0;transform:scale(.25);transform-origin:0 0;pointer-events:none}
.sw{display:flex;height:56px;border-radius:12px;overflow:hidden;border:1px solid var(--border);margin:12px 0}
.sw span{flex:1}
.tag{display:inline-block;font:500 11px var(--mono);letter-spacing:.08em;text-transform:uppercase;padding:3px 8px;border-radius:999px;border:1px solid var(--border);color:var(--muted)}
.muted{color:var(--muted)}.small{font-size:13px}
.bar{height:6px;background:var(--surface2);border-radius:999px;overflow:hidden;margin:10px 0}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2))}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--border);vertical-align:top}th{color:var(--muted);font-weight:500}
kbd{background:var(--surface2);border:1px solid var(--border);border-bottom-width:2px;border-radius:6px;padding:1px 7px;font-size:12px}
.empty{border:1px dashed var(--border);border-radius:var(--radius);padding:28px;text-align:center;color:var(--muted)}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(30px);opacity:0;background:var(--accent);color:#fff;padding:10px 18px;border-radius:999px;transition:.25s;font-weight:600;z-index:20}
.toast.on{opacity:1;transform:translateX(-50%) translateY(0)}
.search{max-width:320px}
footer{border-top:1px solid var(--border);padding:22px 0;color:var(--muted);font-size:13px}
/* pipeline de agentes */
.pipe-cab{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-bottom:18px}
.pipe-cab select{width:auto;min-width:240px}
.pipe-palco{position:relative;padding:64px 22px;border-radius:24px;border:1px solid var(--border);overflow:hidden;
background:radial-gradient(1px 1px at 20% 30%,rgba(32,217,245,.6),transparent),radial-gradient(1px 1px at 70% 80%,rgba(135,87,255,.6),transparent),
radial-gradient(1px 1px at 85% 20%,rgba(255,255,255,.4),transparent),radial-gradient(1px 1px at 40% 90%,rgba(32,217,245,.4),transparent),
linear-gradient(rgba(135,87,255,.06) 1px,transparent 1px) 0 0/32px 32px,linear-gradient(90deg,rgba(135,87,255,.06) 1px,transparent 1px) 0 0/32px 32px,#060913}
.pipe-fios{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible}
.pipe-fios path{fill:none;stroke-width:2.5;stroke-linecap:round}
.pipe-fios path.brilho{stroke-width:9;opacity:.28;filter:blur(5px)}
.pipe-fios path.base{opacity:.95}
.pipe-fios path.base.apagado{opacity:.28}.pipe-fios path.brilho.apagado{opacity:.08}
.pipe-fios path.fluxo{stroke:#fff;stroke-width:2;stroke-dasharray:1.5 18;opacity:.85;animation:fluxo 1.2s linear infinite}
@keyframes fluxo{to{stroke-dashoffset:-20}}
.pipe-trilho{position:relative;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:28px;align-items:start}
.agente{--cor:#8757ff;position:relative;border-radius:16px;padding:14px;background:linear-gradient(180deg,color-mix(in srgb,var(--cor) 16%,#0c1120),#0a0e1a 70%);
border:1px solid color-mix(in srgb,var(--cor) 70%,transparent);box-shadow:0 0 0 1px color-mix(in srgb,var(--cor) 25%,transparent),0 0 28px -6px color-mix(in srgb,var(--cor) 55%,transparent);
display:grid;gap:10px;min-height:340px;align-content:start;transition:transform .25s}
.agente:hover{transform:translateY(-3px)}
.agente.fila{filter:saturate(.35);opacity:.72}
.ag-topo{display:flex;align-items:center;gap:10px}
.ag-ico{width:34px;height:34px;flex:none;border-radius:10px;display:grid;place-items:center;font-size:17px;color:var(--cor);border:1px solid color-mix(in srgb,var(--cor) 60%,transparent);background:color-mix(in srgb,var(--cor) 14%,transparent)}
.ag-nome{font:600 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;line-height:1.3}
.ag-st{font-size:12px;color:var(--cor)}
.ag-caixa{border:1px solid color-mix(in srgb,var(--cor) 35%,transparent);border-radius:10px;padding:9px 10px;background:rgba(0,0,0,.25)}
.ag-acao{display:flex;justify-content:space-between;font:500 11px var(--mono);letter-spacing:.06em;text-transform:uppercase}
.ag-barra{height:5px;border-radius:9px;background:rgba(255,255,255,.08);margin-top:8px;overflow:hidden}
.ag-barra i{display:block;height:100%;background:linear-gradient(90deg,color-mix(in srgb,var(--cor) 60%,#fff 0%),var(--cor));box-shadow:0 0 12px var(--cor)}
.agente.ativo .ag-barra i{background-size:200% 100%;background-image:linear-gradient(90deg,var(--cor),#fff,var(--cor));animation:corre 1.6s linear infinite}
@keyframes corre{to{background-position:-200% 0}}
.ag-faz{font-size:12.5px;color:var(--muted);line-height:1.5}
.ag-lista{list-style:none;padding:0;margin:0;display:grid;gap:5px;font-size:12px}
.ag-lista li{display:flex;gap:7px;align-items:flex-start}
.ag-lista b{color:var(--cor);font-weight:600}.ag-lista .nao{color:var(--muted)}
.ag-obs{font-size:11.5px;color:var(--text);opacity:.85;border-left:2px solid var(--cor);padding-left:8px}
.ag-chips{display:flex;flex-wrap:wrap;gap:5px}
.ag-chips span{font:11px var(--mono);padding:3px 7px;border-radius:7px;background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--muted)}
.pipe-status{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-top:14px;font-size:13px;color:var(--muted)}
.pipe-status .ponto{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ok);box-shadow:0 0 10px var(--ok);margin-right:8px}
@media(max-width:1100px){.pipe-trilho{grid-template-columns:repeat(2,minmax(0,1fr))}.pipe-fios{display:none}}
@media(max-width:620px){.pipe-trilho{grid-template-columns:1fr}.pipe-palco{padding:22px 14px}.agente{min-height:0}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important;animation:none!important}}
"""

JS = r"""
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const toast=t=>{const el=$('#toast');el.textContent=t;el.classList.add('on');setTimeout(()=>el.classList.remove('on'),1600)};
const copy=t=>{(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(()=>toast('Copiado!')).catch(()=>{const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');toast('Copiado!')}catch(e){toast('Copie manualmente')}a.remove()})};
function tab(id){$$('nav.tabs button').forEach(b=>b.setAttribute('aria-selected',b.dataset.tab===id));$$('section.panel').forEach(s=>s.classList.toggle('on',s.id===id));try{localStorage.setItem('novyra-tab',id)}catch(e){}}
$$('nav.tabs button').forEach(b=>b.onclick=()=>tab(b.dataset.tab));
let agente='claude';
$$('#agente button').forEach(b=>b.onclick=()=>{agente=b.dataset.a;$$('#agente button').forEach(x=>x.setAttribute('aria-pressed',x===b));montar()});
let modo='imagem';
$$('#modo button').forEach(b=>b.onclick=()=>{modo=b.dataset.m;$$('#modo button').forEach(x=>x.setAttribute('aria-pressed',x===b));$('#f-imagem').hidden=modo!=='imagem';$('#f-brief').hidden=modo!=='brief';montar()});
const slugify=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40);
function montar(){
  const p=agente==='claude'?'/':'$';const slug=slugify($('#slug').value)||'meu-site';
  let a=[`${p}criar-site`];
  if(modo==='imagem'){const im=$('#imagem').value.trim().replace(/^"|"$/g,'').replace(/\\/g,'/');a.push(`imagem="${im||'C:/caminho/da/tela.png'}"`)}
  else{const br=$('#brief').value.trim().replace(/"/g,"'");a.push(`brief="${br||'Landing futurista com hero, 3 recursos e CTA'}"`)}
  a.push(`slug=${slug}`);
  const ds=$('#ds').value;if(ds)a.push(`ds=${ds}`);
  const tp=$('#tpl').value;if(tp&&tp!=='site-base')a.push(`template=${tp}`);
  $('#cmd').textContent=a.join(' ');
  $('#cmd-hint').textContent=agente==='claude'?'Cole no Claude Code (terminal, app ou IDE). O agente para e pede sua aprovação a cada etapa.':'Cole no Codex (CLI ou IDE). Se a skill não aparecer, abra uma conversa nova.';
}
['#slug','#imagem','#brief','#ds','#tpl'].forEach(s=>$(s).addEventListener('input',montar));
$('#copiar').onclick=()=>copy($('#cmd').textContent);
$$('[data-copy]').forEach(b=>b.onclick=()=>copy(b.dataset.copy));
$$('[data-usar-ds]').forEach(b=>b.onclick=()=>{$('#ds').value=b.dataset.usarDs;tab('criar');montar();toast('Design system escolhido')});
$$('[data-usar-tpl]').forEach(b=>b.onclick=()=>{$('#tpl').value=b.dataset.usarTpl;tab('criar');montar();toast('Template escolhido')});
$$('[data-filtro]').forEach(inp=>inp.addEventListener('input',()=>{const q=inp.value.toLowerCase();$$(inp.dataset.filtro).forEach(c=>c.hidden=!c.textContent.toLowerCase().includes(q))}));
function tema(t){document.documentElement.dataset.theme=t;try{localStorage.setItem('novyra-tema',t)}catch(e){}}
$('#tema').onclick=()=>tema(document.documentElement.dataset.theme==='light'?'dark':'light');
// ---- pipeline de agentes ----
const PIPE=JSON.parse(($('#pipe-dados')||{}).textContent||'{"agentes":[],"sites":[]}');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ROTULO={feito:'Aprovado',ativo:'Em andamento',fila:'Na fila'};
function pipeline(slug){
  const site=PIPE.sites.find(s=>s.slug===slug)||PIPE.sites[0];const trilho=$('#pipe-trilho');if(!trilho)return;
  if(!site){trilho.innerHTML='<div class="empty" style="grid-column:1/-1">Nenhum site ainda. Crie o primeiro na aba <b>Criar</b>: cada etapa vira um agente aqui.</div>';$('#pipe-st').textContent='Sem sites';$('#pipe-fios').innerHTML='';return}
  $('#pipe-site').value=site.slug;
  trilho.innerHTML=PIPE.agentes.map((ag,i)=>{const et=site.etapas[i]||{status:'fila',artefatos:[],obs:''};
    const pct=et.status==='feito'?100:et.status==='ativo'?55:0;
    const arts=et.artefatos.map(([t,ok])=>`<li><b class="${ok?'':'nao'}">${ok?'✓':'○'}</b><span class="${ok?'':'nao'}">${esc(t)}</span></li>`).join('');
    return `<article class="agente ${et.status}" style="--cor:${ag.cor}" data-i="${i}">
      <div class="ag-topo"><span class="ag-ico" aria-hidden="true">${esc(ag.icone)}</span><div><div class="ag-nome">${esc(ag.nome)}</div><div class="ag-st">${ROTULO[et.status]} · etapa ${ag.n}</div></div></div>
      <div class="ag-caixa"><div class="ag-acao"><span>${esc(et.status==='feito'?ag.etapa:ag.acao)}</span><span>${pct}%</span></div><div class="ag-barra"><i style="width:${pct}%"></i></div></div>
      <p class="ag-faz">${esc(ag.faz)}</p>
      <ul class="ag-lista">${arts}</ul>
      ${et.obs?`<p class="ag-obs">${esc(et.obs)}</p>`:''}
      <div class="ag-chips">${ag.scripts.map(s=>`<span>${esc(s)}</span>`).join('')}</div></article>`}).join('');
  const ativo=site.etapas.find(e=>e.status==='ativo');const feitas=site.etapas.filter(e=>e.status==='feito').length;
  $('#pipe-st').innerHTML=`<span class="ponto"></span>${ativo?esc(PIPE.agentes[ativo.n-1].nome)+' trabalhando na etapa '+ativo.n:'Pipeline concluído'} · ${feitas} de 5 etapas aprovadas`;
  const cmd=`/criar-site slug=${site.slug}`;$('#pipe-cmd').dataset.copy=cmd;$('#pipe-cmd').textContent=ativo?'Continuar: '+cmd:'Reabrir: '+cmd;
  requestAnimationFrame(fios);
}
function fios(){
  const svg=$('#pipe-fios'),palco=$('#pipe-palco');if(!svg||!palco||!palco.offsetParent)return;
  const P=palco.getBoundingClientRect();const cards=$$('#pipe-trilho .agente');const site=PIPE.sites.find(s=>s.slug===$('#pipe-site').value);
  let defs='',linhas='';
  for(let i=0;i<cards.length-1;i++){
    const a=cards[i].getBoundingClientRect(),b=cards[i+1].getBoundingClientRect();
    if(Math.abs(a.top-b.top)>20)continue;
    const cima=i%2===0,r=14;
    const x1=a.left-P.left+a.width*.72,x2=b.left-P.left+b.width*.28;
    const yA=cima?a.top-P.top:a.bottom-P.top,yB=cima?b.top-P.top:b.bottom-P.top;
    const yM=cima?Math.min(yA,yB)-34:Math.max(yA,yB)+34,s=cima?-1:1;
    const d=`M${x1},${yA} L${x1},${yM-s*r} Q${x1},${yM} ${x1+r},${yM} L${x2-r},${yM} Q${x2},${yM} ${x2},${yM-s*r} L${x2},${yB}`;
    const c1=PIPE.agentes[i].cor,c2=PIPE.agentes[i+1].cor;
    defs+=`<linearGradient id="g${i}" gradientUnits="userSpaceOnUse" x1="${x1}" y1="0" x2="${x2}" y2="0"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient>`;
    const viva=site&&site.etapas[i+1]&&site.etapas[i+1].status!=='fila';
    const k=viva?'':' apagado';
    linhas+=`<path class="brilho${k}" d="${d}" stroke="url(#g${i})"/><path class="base${k}" d="${d}" stroke="url(#g${i})"/>`;
    if(viva)linhas+=`<path class="fluxo" d="${d}"/>`;
    linhas+=`<circle cx="${x1}" cy="${yA}" r="3" fill="${c1}"/><circle cx="${x2}" cy="${yB}" r="3.5" fill="${c2}"/>`;
  }
  svg.innerHTML=`<defs>${defs}</defs>${linhas}`;
}
if($('#pipe-site')){$('#pipe-site').addEventListener('change',e=>pipeline(e.target.value));addEventListener('resize',()=>requestAnimationFrame(fios));pipeline(PIPE.sites[0]&&PIPE.sites[0].slug)}
$$('[data-pipe]').forEach(b=>b.onclick=()=>{tab('pipeline');pipeline(b.dataset.pipe)});
$$('nav.tabs button').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.tab==='pipeline')requestAnimationFrame(fios)}));
const ordem=['criar','templates','ds','sites','pipeline','refs','guia'];
document.addEventListener('keydown',ev=>{
  const tag=(ev.target.tagName||'').toLowerCase();const digitando=['input','textarea','select'].includes(tag);
  if(ev.key==='Escape'&&digitando){ev.target.blur();return}
  if(digitando||ev.ctrlKey||ev.metaKey||ev.altKey)return;
  if(/^[1-7]$/.test(ev.key)){tab(ordem[+ev.key-1]);if(ev.key==='5')requestAnimationFrame(fios);ev.preventDefault()}
  else if(ev.key==='c'){copy($('#cmd').textContent);ev.preventDefault()}
  else if(ev.key==='t'){$('#tema').click();ev.preventDefault()}
  else if(ev.key==='a'){($$('#agente button').find(b=>b.getAttribute('aria-pressed')!=='true')||{}).click?.();ev.preventDefault()}
  else if(ev.key==='/'){const f=$('section.panel.on [data-filtro]')||$('#slug');f.focus();ev.preventDefault()}
  else if(ev.key==='?'){tab('guia');location.hash='#atalhos';ev.preventDefault()}
});
try{const t=localStorage.getItem('novyra-tema');if(t)tema(t);const s=localStorage.getItem('novyra-tab');if(s&&$('#'+s)){tab(s);requestAnimationFrame(fios)}}catch(e){}
function encaixar(){$$('.prev').forEach(p=>{const f=p.querySelector('iframe');const k=p.clientWidth/1440;if(!k)return;f.style.transform=`scale(${k})`;p.style.height=Math.round(900*k)+'px'})}
addEventListener('resize',encaixar);$$('nav.tabs button').forEach(b=>b.addEventListener('click',()=>requestAnimationFrame(encaixar)));document.addEventListener('keydown',()=>requestAnimationFrame(encaixar));
montar();encaixar();
"""


def gerar(artefato: bool) -> str:
    templates, dss, sites = coletar_templates(), coletar_ds(), coletar_sites()
    refs = coletar_referencias()
    v = versao()

    def abrir(arq: str, rotulo: str) -> str:
        if artefato or not arq:
            return ""
        return f'<a class="btn2" href="{e(Path(arq).as_uri())}" target="_blank" rel="noopener">{rotulo}</a>'

    opt_ds = '<option value="">Nenhum (cores medidas da imagem)</option>' + "".join(
        f'<option value="{e(d["slug"])}">{e(d["titulo"])} · {e(d["tipo"])}</option>' for d in dss)
    opt_tpl = "".join(f'<option value="{e(t["slug"])}">{e(t["nome"])}</option>' for t in templates)
    fluxo = "".join(f'<div class="step"><b>{n}</b><h3>{e(t)}</h3><p>{e(d)}</p></div>' for n, t, d in ETAPAS)

    cards_tpl = "".join(f"""
      <article class="card tpl"><div class="prev"><iframe scrolling="no" title="Prévia {e(t['nome'])}" loading="lazy" sandbox="" srcdoc="{e(t['srcdoc'])}"></iframe></div>
        <h3 style="margin-top:14px">{e(t['nome'])}</h3><p class="muted small">{e(t['desc'])}</p>
        <div class="row"><span class="tag">{e(t['slug'])}</span><button class="btn2" data-usar-tpl="{e(t['slug'])}">Usar no montador</button>{abrir(t['arquivo'], 'Abrir')}</div></article>"""
        for t in templates)

    cards_ds = "".join(f"""
      <article class="card dsc"><div class="row" style="margin:0;justify-content:space-between"><h3>{e(d['titulo'])}</h3><span class="tag">{e(d['tipo'])}</span></div>
        <div class="sw">{''.join(f'<span title="--{e(k)}: {e(val)}" style="background:{e(val)}"></span>' for k, val in d['cores'][:9])}</div>
        <p class="muted small">{e(d['desc'])}</p>
        <p class="small">Títulos <b>{e(d['titulo_fonte'] or '—')}</b> · Corpo <b>{e(d['corpo_fonte'] or '—')}</b></p>
        <div class="row"><span class="tag">{e(d['slug'])}</span><button class="btn2" data-usar-ds="{e(d['slug'])}">Usar no montador</button>{abrir(d['catalogo'], 'Catálogo')}</div></article>"""
        for d in dss) or '<div class="empty">Nenhum design system ainda. Rode <code>/extrair-ds</code>.</div>'

    def card_ref(r: dict) -> str:
        url, fonte = r.get("url", ""), r.get("fonte", "")
        cmd_ds = f"/extrair-ds url={url} slug={r.get('slug_sugerido', r['id'])}" if url else ""
        cmd_site = (f'/criar-site brief="Site autoral na direção {r["nome"]}: ' + "; ".join(r.get("padroes", [])[:3])
                    + f'" slug=meu-{r["id"]} ds={r.get("modelo", "")} template={r.get("template", "site-base")}')
        botoes = (f'<button class="btn2" data-copy="{e(cmd_ds)}">Copiar /extrair-ds</button>' if cmd_ds else "")
        botoes += f'<button class="btn2" data-copy="{e(cmd_site)}">Criar nesta direção</button>'
        botoes += f'<button class="btn2" data-usar-ds="{e(r.get("modelo", ""))}">Usar o modelo</button>'
        links = " · ".join(x for x in (
            f'<a href="{e(url)}" target="_blank" rel="noopener">site</a>' if url else "",
            f'<a href="{e(fonte)}" target="_blank" rel="noopener">ficha</a>' if fonte else "") if x)
        obs = f'<p class="small muted">⚠ {e(r["observacao"])}</p>' if r.get("observacao") else ""
        return (f'<article class="card ref"><div class="row" style="margin:0;justify-content:space-between"><h3>{e(r["nome"])}</h3>'
                f'<span class="tag">{e(r.get("categoria", ""))}</span></div>'
                f'<p class="small muted">{e(r.get("autoria", ""))} · {links}</p>'
                f'<p class="small">{e(" · ".join(r.get("padroes", [])))}</p>'
                f'<p class="small">Modelo NOVYRA: <code>{e(r.get("modelo", ""))}</code> · template <code>{e(r.get("template", ""))}</code></p>'
                f'{obs}<div class="row">{botoes}</div></article>')

    cards_refs = "".join(card_ref(r) for r in refs.get("referencias", [])) or \
        '<div class="empty">Sem catálogo de referências.</div>'
    fontes_refs = " · ".join(f'<a href="{e(f["url"])}" target="_blank" rel="noopener">{e(f["nome"])}</a>'
                             for f in refs.get("fontes", []))

    if sites:
        cards_sites = "".join(f"""
      <article class="card site"><div class="row" style="margin:0;justify-content:space-between"><h3>{e(s['slug'])}</h3><span class="tag">{e(s['quando'])}</span></div>
        <div class="bar"><i style="width:{int(100 * s['feitas'] / max(s['total'], 1))}%"></i></div>
        <p class="muted small">{s['feitas']} de {s['total']} etapas aprovadas{(' · referência ' + e(s['ref'])) if s['ref'] else ' · modo briefing'}</p>
        <div class="row"><button class="btn2" data-copy="/criar-site slug={e(s['slug'])}">Continuar (Claude)</button><button class="btn2" data-copy="$criar-site slug={e(s['slug'])}">Continuar (Codex)</button><button class="btn2" data-pipe="{e(s['slug'])}">Ver pipeline</button>{abrir(s['arquivo'], 'Abrir site')}</div></article>"""
            for s in sites)
    else:
        cards_sites = '<div class="empty">Nenhum site criado ainda. Use a aba <b>Criar</b> para montar o primeiro comando.</div>'

    linhas_skills = "".join(
        f"<tr><td><code>/{e(n)}</code><br><code class='muted'>${e(n)}</code></td><td>{e(d)}</td><td><code>{e(p)}</code></td>"
        f"<td><button class='btn2' data-copy='/{e(n)} {e(ex)}'>Copiar</button></td></tr>"
        for n, d, ex, p in SKILLS)
    linhas_scripts = "".join(f"<tr><td><code>{e(n)}</code></td><td>{e(d)}</td></tr>" for n, d in SCRIPTS)
    pipe_json = json.dumps({"agentes": AGENTES, "sites": [{"slug": s["slug"], "etapas": s["etapas"]} for s in sites]},
                           ensure_ascii=False).replace("</", "<\\/")
    opt_pipe = "".join(f'<option value="{e(s["slug"])}">{e(s["slug"])}</option>' for s in sites)
    raiz_txt = "" if artefato else f'<p class="small muted local-path">Instalado em <code>{e(RAIZ.as_posix())}</code> · sites em <code>{e(SITES.as_posix())}</code></p>'

    return f"""<!doctype html>
<html lang="pt-BR" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NOVYRA Studio</title>
<meta name="description" content="NOVYRA Studio: monte comandos, veja templates, design systems e seus sites.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><div class="logo"><i></i>NOVYRA</div>
<nav class="tabs" aria-label="Seções"><button data-tab="criar" aria-selected="true">Criar<kbd>1</kbd></button><button data-tab="templates" aria-selected="false">Templates<kbd>2</kbd></button><button data-tab="ds" aria-selected="false">Design systems<kbd>3</kbd></button><button data-tab="sites" aria-selected="false">Meus sites<kbd>4</kbd></button><button data-tab="pipeline" aria-selected="false">Pipeline<kbd>5</kbd></button><button data-tab="refs" aria-selected="false">Referências<kbd>6</kbd></button><button data-tab="guia" aria-selected="false">Guia<kbd>7</kbd></button></nav>
<button class="icon-btn" id="tema" title="Alternar tema (t)" aria-label="Alternar tema">◐</button></div></header>
<main class="wrap">
<div class="hero"><div class="eyebrow">Imagem → site · v{e(v)}</div><h1>Crie além dos <span>limites</span>.</h1>
<p class="lead">Transforme um print, um mock ou uma ideia em um site HTML + CSS fiel, em 5 etapas com a sua aprovação. Funciona no Claude Code e no Codex.</p>
<div class="stats"><div class="stat"><b>{len(templates)}</b>templates</div><div class="stat"><b>{len(dss)}</b>design systems</div><div class="stat"><b>{len(sites)}</b>sites criados</div><div class="stat"><b>5</b>skills</div></div></div>

<section class="panel on" id="criar"><div class="builder">
<div class="card"><h2>Montador de comando</h2><p class="muted small">Preencha, copie e cole no seu agente. Atalho: <kbd>c</kbd> copia.</p>
<div class="row"><div class="seg" id="agente" role="group" aria-label="Agente"><button data-a="claude" aria-pressed="true">Claude Code</button><button data-a="codex" aria-pressed="false">Codex</button></div>
<div class="seg" id="modo" role="group" aria-label="Entrada"><button data-m="imagem" aria-pressed="true">Tenho uma imagem</button><button data-m="brief" aria-pressed="false">Só uma ideia</button></div></div>
<div id="f-imagem"><label for="imagem">Caminho da imagem (png, jpg, webp)</label><input id="imagem" placeholder="C:/Users/voce/Desktop/tela.png"></div>
<div id="f-brief" hidden><label for="brief">Descreva o site</label><textarea id="brief" placeholder="Landing de uma plataforma de IA com hero imersivo, 3 recursos, depoimentos e CTA"></textarea></div>
<label for="slug">Nome do site (vira a pasta)</label><input id="slug" placeholder="meu-site">
<label for="tpl">Template</label><select id="tpl">{opt_tpl}</select>
<label for="ds">Design system</label><select id="ds">{opt_ds}</select></div>
<div class="card"><h2>Seu comando</h2><div class="cmd" id="cmd" aria-live="polite"></div><p class="small muted" id="cmd-hint"></p>
<div class="row"><button class="btn" id="copiar">Copiar comando</button></div>
<h3 style="margin-top:22px">O que acontece depois</h3><div class="flow" style="grid-template-columns:1fr">{fluxo}</div></div></div></section>

<section class="panel" id="templates"><div class="row" style="justify-content:space-between;margin-bottom:16px"><div><h2>Templates</h2><p class="muted small">Pontos de partida. A prévia é ao vivo.</p></div><input class="search" data-filtro="#templates .tpl" placeholder="Filtrar ( / )"></div>
<div class="grid g2">{cards_tpl}</div></section>

<section class="panel" id="ds"><div class="row" style="justify-content:space-between;margin-bottom:16px"><div><h2>Design systems</h2><p class="muted small">Autorais, extraídos com <code>/extrair-ds</code> ou combinados com <code>/combinar-ds</code>.</p></div><input class="search" data-filtro="#ds .dsc" placeholder="Filtrar ( / )"></div>
<div class="grid g3">{cards_ds}</div></section>

<section class="panel" id="sites"><div class="row" style="justify-content:space-between;margin-bottom:16px"><div><h2>Meus sites</h2><p class="muted small">Atualize esta lista com <code>/novyra</code> ou <code>$novyra</code>.</p></div><input class="search" data-filtro="#sites .site" placeholder="Filtrar ( / )"></div>
<div class="grid g2">{cards_sites}</div>{raiz_txt}</section>

<section class="panel" id="pipeline"><div class="pipe-cab"><div><h2>Pipeline de agentes</h2><p class="muted small">Cada etapa do <code>/criar-site</code> é um agente. O status vem do <code>ESTADO.md</code> e os itens marcados vêm dos arquivos que existem de fato na pasta do site.</p></div>
<label class="small muted">Site<select id="pipe-site" aria-label="Escolher site">{opt_pipe}</select></label></div>
<div class="pipe-palco" id="pipe-palco"><svg class="pipe-fios" id="pipe-fios" aria-hidden="true"></svg><div class="pipe-trilho" id="pipe-trilho"></div></div>
<div class="pipe-status"><span id="pipe-st"></span><button class="btn2" id="pipe-cmd" data-copy="">Continuar</button></div>
<script type="application/json" id="pipe-dados">{pipe_json}</script></section>

<section class="panel" id="refs"><div class="row" style="justify-content:space-between;margin-bottom:16px"><div><h2>Referências futuristas</h2><p class="muted small">{e(refs.get("aviso", ""))}</p><p class="small">Fontes: {fontes_refs}</p></div><input class="search" data-filtro="#refs .ref" placeholder="Filtrar ( / )"></div>
<div class="grid g2">{cards_refs}</div></section>

<section class="panel" id="guia"><div class="grid" style="gap:22px">
<div class="card"><h2>As 5 etapas</h2><p class="muted">Cada etapa termina com uma captura e o seu "aprovado". Nada avança sem você.</p><div class="flow">{fluxo}</div></div>
<div class="card"><h2>Skills</h2><p class="muted small">No Claude Code use <code>/nome</code>; no Codex use <code>$nome</code>.</p><div style="overflow-x:auto"><table><thead><tr><th>Skill</th><th>O que faz</th><th>Parâmetros</th><th></th></tr></thead><tbody>{linhas_skills}</tbody></table></div></div>
<div class="card" id="atalhos"><h2>Atalhos deste painel</h2><table><tbody>
<tr><td><kbd>1</kbd>–<kbd>7</kbd></td><td>Troca de aba</td></tr><tr><td><kbd>c</kbd></td><td>Copia o comando montado</td></tr>
<tr><td><kbd>a</kbd></td><td>Alterna Claude Code / Codex</td></tr><tr><td><kbd>/</kbd></td><td>Foca o filtro da aba</td></tr>
<tr><td><kbd>t</kbd></td><td>Tema claro / escuro</td></tr><tr><td><kbd>?</kbd></td><td>Abre estes atalhos</td></tr><tr><td><kbd>Esc</kbd></td><td>Sai do campo de texto</td></tr></tbody></table>
<h3 style="margin-top:18px">Durante a criação</h3><table><tbody>
<tr><td><code>aprovado</code></td><td>Libera a próxima etapa</td></tr><tr><td><code>ajusta o hero: ...</code></td><td>Pede correção na etapa atual</td></tr>
<tr><td><code>volta para a etapa 2</code></td><td>Refaz a partir de uma etapa</td></tr><tr><td><code>/criar-site slug=x</code></td><td>Retoma um site pelo ESTADO.md</td></tr></tbody></table></div>
<div class="card"><h2>Scripts de medição</h2><p class="muted small">Ficam em <code>scripts/</code>. As skills chamam por você; também rodam à mão com <code>python -X utf8</code>.</p><div style="overflow-x:auto"><table><tbody>{linhas_scripts}</tbody></table></div></div>
</div></section>
</main>
<footer><div class="wrap">NOVYRA v{e(v)} · gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} · MIT · <a href="https://github.com/carlos-dataengineer/novyra" target="_blank" rel="noopener">github.com/carlos-dataengineer/novyra</a></div></footer>
<div class="toast" id="toast" role="status"></div>
<script>{JS}</script></body></html>
"""


def main() -> None:
    p = argparse.ArgumentParser(description="Gera o NOVYRA Studio (painel da ferramenta)")
    p.add_argument("--saida", help="arquivo de saída (padrão: <RAIZ>/novyra.html)")
    p.add_argument("--artefato", action="store_true", help="sem links para arquivos locais (para publicar)")
    args = p.parse_args()
    saida = Path(args.saida) if args.saida else RAIZ / ("novyra-artefato.html" if args.artefato else "novyra.html")
    saida.write_text(gerar(args.artefato), encoding="utf-8")
    print(f"Painel gerado em: {saida}")


if __name__ == "__main__":
    main()
