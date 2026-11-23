"""Transforma a captura de um site (capturar_site.py) em tokens de design system.

Lê design-systems/<slug>/fonte/captura.json e grava, na pasta do design system:
    tokens.json   valores + de onde vieram (pesos, amostras), para o agente revisar
    tokens.css    os mesmos valores como custom properties no :root

Os papéis (fundo, superfície, texto, acento...) são palpites por frequência e área.
Revise-os no tokens.json e rode de novo com --sem-recalcular para só regerar o CSS.

Exemplos:
    python extrair_tokens.py linear
    python extrair_tokens.py linear --sem-recalcular      # após editar tokens.json à mão
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from _comum import DESIGN_SYSTEMS, erro

# Fontes comerciais/do sistema -> equivalente no Google Fonts (sugestão; o agente confirma olhando)
EQUIVALENTES = {
    "inter variable": "Inter", "inter display": "Inter", "sf pro": "Inter", "sf pro display": "Inter",
    "sf pro text": "Inter", "-apple-system": "Inter", "system-ui": "Inter", "helvetica neue": "Inter",
    "helvetica": "Inter", "arial": "Inter", "segoe ui": "Inter", "graphik": "Inter", "circular": "DM Sans",
    "gt walsheim": "DM Sans", "suisse intl": "Inter Tight", "neue haas grotesk": "Inter Tight",
    "berkeley mono": "JetBrains Mono", "sf mono": "JetBrains Mono", "menlo": "JetBrains Mono",
    "consolas": "JetBrains Mono", "monaco": "JetBrains Mono", "söhne": "Inter", "sohne": "Inter",
    "tiempos": "Source Serif 4", "georgia": "Source Serif 4", "times new roman": "Source Serif 4",
}


# ---------------------------------------------------------------- cor
def hexa(c) -> str:
    r, g, b = c[:3]
    s = f"#{r:02x}{g:02x}{b:02x}"
    return s if len(c) < 4 or c[3] >= 0.995 else f"rgba({r}, {g}, {b}, {c[3]})"


def lab(c):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in c[:3])
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta(a, b) -> float:
    return math.dist(lab(a), lab(b))


def croma(c) -> float:
    _, a, b = lab(c)
    return math.hypot(a, b)


def luminancia(c) -> float:
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def agrupar(pesos: dict, limite: float = 5.0) -> list[dict]:
    """Junta cores quase iguais (ΔE < limite), mantendo a mais usada como representante."""
    grupos: list[dict] = []
    for c, p in sorted(pesos.items(), key=lambda kv: -kv[1]):
        c = list(c)
        for g in grupos:
            if abs(g["cor"][3] - c[3]) < 0.1 and delta(g["cor"], c) < limite:
                g["peso"] += p
                break
        else:
            grupos.append({"cor": c, "peso": p})
    total = sum(g["peso"] for g in grupos) or 1
    for g in grupos:
        g["pct"] = round(100 * g["peso"] / total, 1)
        g["hex"] = hexa(g["cor"])
    return grupos


# ---------------------------------------------------------------- tipografia
def familia(ff: str) -> str:
    return (ff or "").split(",")[0].strip().strip("\"'")


def px(valor: str, base: float = 16) -> float | None:
    if not valor or valor == "normal":
        return None
    m = re.match(r"(-?[\d.]+)(px|em|rem)?", valor)
    if not m:
        return None
    v = float(m.group(1))
    return v * base if m.group(2) in ("em", "rem") else v


def normalizar(nome: str) -> str:
    """'sohne-var' -> 'Sohne', 'SourceCodePro' -> 'Source Code Pro', 'Inter Variable' -> 'Inter Variable'."""
    n = re.sub(r"[-_ ]?(var|vf|variable|webfont|web)$", "", nome.strip(), flags=re.I)
    n = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", n)
    n = re.sub(r"[-_]+", " ", n).strip()
    return " ".join(p if p.isupper() else p.capitalize() for p in n.split())


def equivalente(nome: str) -> str:
    for chave in (nome.lower(), normalizar(nome).lower()):
        if chave in EQUIVALENTES:
            return EQUIVALENTES[chave]
    return normalizar(nome)


# ---------------------------------------------------------------- extração
def extrair(cap: dict) -> dict:
    els = cap["elementos"]
    area_pagina = cap["viewport"][0] * max(cap["alturaPagina"], 1)

    fundos, translucidos, textos, bordas = Counter(), Counter(), Counter(), Counter()
    for e in els:
        s = e["s"]
        if s["bg"]:
            alvo = fundos if s["bg"][3] >= 0.9 else translucidos
            alvo[tuple(s["bg"])] += min(e["w"] * e["h"], area_pagina)
        if e["txt"] and s["color"]:
            textos[tuple(s["color"])] += len(e["txt"])
        if s["bc"] and s["bw"]:
            bordas[tuple(s["bc"])] += 1

    g_fundos, g_textos, g_bordas = agrupar(fundos), agrupar(textos), agrupar(bordas)
    bg = list(cap["fundoPagina"])

    # superfície: fundo mais usado que não é o da página
    sup = next((g["cor"] for g in g_fundos if delta(g["cor"], bg) >= 3), None)
    if sup is None:
        claro = luminancia(bg) > 0.5
        sup = [max(0, min(255, v + (-8 if claro else 10))) for v in bg[:3]] + [1]

    # texto e texto secundário
    # texto principal: entre as cores de texto bem usadas (>= 10%), a de maior contraste com o fundo;
    # a mais frequente costuma ser a dos parágrafos secundários, não a dos títulos
    usadas = [g for g in g_textos if g["pct"] >= 10 and contraste(g["cor"], bg) >= 3] or \
             [g for g in g_textos if contraste(g["cor"], bg) >= 3]
    texto = max(usadas, key=lambda g: contraste(g["cor"], bg))["cor"] if usadas else \
        ([20, 20, 20, 1] if luminancia(bg) > 0.5 else [240, 240, 240, 1])
    muted = next((g["cor"] for g in g_textos
                  if delta(g["cor"], texto) > 8 and 2.5 <= contraste(g["cor"], bg) < contraste(texto, bg)), None)
    if muted is None:
        muted = [round(t * 0.62 + b * 0.38) for t, b in zip(texto[:3], bg[:3])] + [1]

    # acento: a cor mais saturada usada em botões, links ou com peso relevante
    cands: Counter = Counter()
    for c in cap["componentes"]:
        for k in ("bg", "color", "bc"):
            if c["s"].get(k):
                cands[tuple(c["s"][k])] += 3
    for g in g_textos[:12] + g_fundos[:12] + g_bordas[:8]:
        cands[tuple(g["cor"])] += 1
    # a cor do anel de foco costuma ser a cor da marca
    for c in cap["componentes"]:
        ol = (c.get("foco") or {}).get("ol")
        m = re.search(r"rgba?\((\d+), (\d+), (\d+)", ol[1]) if ol else None
        if m:
            cands[(int(m.group(1)), int(m.group(2)), int(m.group(3)), 1.0)] += 4
    saturadas = sorted((c for c in cands if croma(c) >= 18), key=lambda c: (-croma(c) * cands[c]))
    monocromatico = not saturadas
    acento = list(saturadas[0]) if saturadas else list(texto)
    sobre_acento = max(([255, 255, 255, 1], [0, 0, 0, 1], bg), key=lambda c: contraste(c, acento))
    borda = g_bordas[0]["cor"] if g_bordas else [round(t * 0.15 + b * 0.85) for t, b in zip(texto[:3], bg[:3])] + [1]

    # --- tipografia
    grupos = defaultdict(int)
    amostra = {}
    for e in els:
        if not e["txt"]:
            continue
        s = e["s"]
        fs = round(s["fs"] * 2) / 2
        lh = px(s["lh"])
        chave = (familia(s["ff"]), str(s["fw"]), fs, round(lh / fs, 2) if lh else 1.2,
                 round((px(s["ls"]) or 0) / fs, 3), s["tt"])
        grupos[chave] += len(e["txt"])
        amostra.setdefault(chave, (e["tag"], e["txt"][:50]))
    fam_titulo = Counter()
    fam_corpo = Counter()
    for k, p in grupos.items():
        (fam_titulo if k[2] >= 22 else fam_corpo)[k[0]] += p
    sem_mono = lambda cnt: [f for f, _ in cnt.most_common() if not re.search(r"mono|code", f, re.I)]
    titulo = (sem_mono(fam_titulo) or [None])[0]
    corpo_f = (sem_mono(fam_corpo) or [titulo])[0]
    titulo = titulo or corpo_f
    mono = next((f for f in list(fam_corpo) + list(fam_titulo) if re.search(r"mono|code", f, re.I)), None)

    # papéis de texto usam a família do corpo (evita pegar um bloco de código como .t2)
    por_tamanho = defaultdict(int)
    for k, p in grupos.items():
        if k[2] >= 22 or k[0] == corpo_f:
            por_tamanho[k[2]] += p

    def dominante(fs):
        cands = [k for k in grupos if k[2] == fs and (fs >= 22 or k[0] == corpo_f)] or [k for k in grupos if k[2] == fs]
        k = max(cands, key=lambda k: grupos[k])
        tag, txt = amostra[k]
        return {"familia": k[0], "peso": k[1], "tamanho": fs, "altura_linha": k[3],
                "espacamento_em": k[4], "caixa": k[5], "exemplo": txt, "tag": tag}

    tamanhos = sorted((fs for fs, p in por_tamanho.items() if p >= 8), reverse=True)
    papeis = {}
    corpo = [fs for fs in tamanhos if 14 <= fs <= 20]
    t1 = max(corpo, key=lambda fs: por_tamanho[fs]) if corpo else (tamanhos[-1] if tamanhos else 16)
    restante = [fs for fs in tamanhos if fs > t1 * 1.2]
    for nome, fator, minimo in (("h1", 1, 0), ("h2", 0.85, 20), ("h3", 0.9, 17)):
        teto = papeis[list(papeis)[-1]]["tamanho"] * fator if papeis else math.inf
        fs = next((f for f in restante if f < teto and f >= minimo and (nome == "h1" or f < teto)), None)
        if fs:
            papeis[nome] = dominante(fs)
    papeis["t1"] = dominante(t1)
    menores = [fs for fs in tamanhos if 12 <= fs < t1]
    if menores:
        papeis["t2"] = dominante(max(menores, key=lambda fs: por_tamanho[fs]))
    minimos = [fs for fs in tamanhos if 10 <= fs < papeis.get("t2", papeis["t1"])["tamanho"]]
    if minimos:
        papeis["t3"] = dominante(min(minimos))

    google = " ".join(cap.get("linksFontes", []))
    fontes_info = {}
    for f in {titulo, corpo_f, mono} - {None}:
        origem = "google" if f.replace(" ", "+") in google else (
            "propria" if any(ff["familia"] == f for ff in cap.get("fontes", [])) else "sistema/desconhecida")
        fontes_info[f] = {"origem": origem, "sugestao_google": f if origem == "google" else equivalente(f)}

    # --- formas
    raios = Counter()
    for e in els:
        v = px(e["s"]["br"].split(" ")[0]) if e["s"]["br"] else None
        if e["s"]["br"] and "%" in e["s"]["br"]:
            raios["pill"] += 1
        elif v:
            raios["pill" if v >= 999 else round(v)] += 1

    def raio(lo, hi, padrao):
        cs = [(r, n) for r, n in raios.items() if r != "pill" and lo <= r <= hi]
        return max(cs, key=lambda x: x[1])[0] if cs else padrao

    sombras = Counter(e["s"]["bs"] for e in els if e["s"]["bs"])

    def borrao(s):
        nums = [float(n) for n in re.findall(r"(-?[\d.]+)px", s)]
        return max(nums) if nums else 0

    top_sombras = sorted([s for s, _ in sombras.most_common(6)], key=borrao)[:3]

    espacos = Counter()
    for e in els:
        for v in e["s"]["pad"] + ([e["s"]["gap"]] if e["s"]["gap"] else []):
            if v and 2 <= v <= 160:
                # grade: múltiplos de 2 até 8px, de 4 acima disso (some com 7px, 11px etc.)
                espacos[round(v / 2) * 2 if v < 8 else round(v / 4) * 4] += 1
    escala = sorted(v for v, _ in espacos.most_common(8))

    # --- movimento
    duracoes, curvas = Counter(), Counter()
    for e in els:
        tr = e["s"]["tr"]
        if not tr:
            continue
        for parte in re.split(r",(?![^(]*\))", tr):
            m = re.search(r"([\d.]+)(m?s)", parte)
            if m:
                ms = float(m.group(1)) * (1 if m.group(2) == "ms" else 1000)
                if 0 < ms <= 2000:
                    duracoes[round(ms)] += 1
            c = re.search(r"(cubic-bezier\([^)]*\)|ease-in-out|ease-in|ease-out|linear|ease)", parte)
            if c:
                curvas[c.group(1)] += 1
    durs = sorted(d for d, _ in duracoes.most_common(4))
    animados = Counter(e["s"]["an"] for e in els if e["s"]["an"])

    gradientes = Counter(e["s"]["bgImg"] for e in els if e["s"]["bgImg"] and "gradient" in e["s"]["bgImg"])
    vidros = [e["s"]["bf"] for e in els if e["s"]["bf"]]

    # --- estados medidos nos componentes
    estados = {}
    for c in cap["componentes"]:
        for est in ("hover", "foco"):
            if c.get(est) and (c["tipo"], est) not in estados:
                estados[(c["tipo"], est)] = {"exemplo": c["txt"][:30], "muda": c[est]}
    anel_foco = next((v["muda"]["ol"][1] for (t, e), v in estados.items() if e == "foco" and "ol" in v["muda"]), None)

    return {
        "origem": {"url": cap["url"], "titulo": cap["titulo"], "extraido_em": date.today().isoformat()},
        "cores": {
            "bg": hexa(bg), "surface": hexa(sup), "text": hexa(texto), "text-muted": hexa(muted),
            "accent": hexa(acento), "on-accent": hexa(sobre_acento), "border": hexa(borda),
            "_monocromatico": monocromatico,
            "_contraste": {"text/bg": contraste(texto, bg), "text-muted/bg": contraste(muted, bg),
                           "on-accent/accent": contraste(sobre_acento, acento)},
        },
        "paleta": {"fundos": [{k: g[k] for k in ("hex", "pct")} for g in g_fundos[:8]],
                   "textos": [{k: g[k] for k in ("hex", "pct")} for g in g_textos[:6]],
                   "bordas": [{k: g[k] for k in ("hex", "pct")} for g in g_bordas[:4]],
                   "translucidos": [hexa(list(c)) for c, _ in translucidos.most_common(5)]},
        "tipografia": {"familias": {"titulo": titulo, "corpo": corpo_f, "mono": mono},
                       "fontes": fontes_info, "papeis": papeis},
        "formas": {"radius-sm": raio(2, 6, 4), "radius-md": raio(7, 14, 10), "radius-lg": raio(15, 40, 20),
                   "usa_pill": raios["pill"] > 0, "sombras": top_sombras, "espacos": escala},
        "movimento": {"duracoes_ms": durs, "curva": curvas.most_common(1)[0][0] if curvas else "ease",
                      "keyframes": list(cap.get("keyframes", {}))[:20],
                      "elementos_animados": sum(animados.values())},
        "fundos": {"gradientes": [g for g, _ in gradientes.most_common(5)], "vidro": vidros[:3]},
        "estados": {f"{t}:{e}": v for (t, e), v in estados.items()},
        "anel_foco": anel_foco,
        "variaveis_originais": dict(list(cap.get("vars", {}).items())[:80]),
    }


# ---------------------------------------------------------------- CSS
def pilha(nome: str | None, tipo: str) -> str:
    resto = {"serif": "Georgia, serif", "mono": "ui-monospace, monospace"}.get(tipo, "system-ui, sans-serif")
    return f'"{nome}", {resto}' if nome else resto


def gerar_css(t: dict) -> str:
    c, tip, f, mv = t["cores"], t["tipografia"], t["formas"], t["movimento"]
    fam = tip["familias"]
    sug = lambda n: tip["fontes"].get(n, {}).get("sugestao_google", n) if n else None
    linhas = [
        "/* Tokens extraídos de " + t["origem"]["url"] + " em " + t["origem"]["extraido_em"] + ".",
        "   Gerado por extrair_tokens.py. Ajuste em tokens.json e rode de novo com --sem-recalcular. */",
        ":root {",
        "  /* cores */",
    ]
    base = ("bg", "surface", "text", "text-muted", "accent", "on-accent", "border")
    for k in base:
        linhas.append(f"  --{k}: {c[k]};")
    # cores extras adicionadas à mão no tokens.json (ex.: accent-depth, highlight-blue)
    for k, v in c.items():
        if k not in base and not k.startswith("_") and isinstance(v, str):
            linhas.append(f"  --{k}: {v};")
    linhas += ["", "  /* tipografia */",
               f"  --font-title: {pilha(sug(fam['titulo']), 'sans')};",
               f"  --font-body: {pilha(sug(fam['corpo']), 'sans')};",
               f"  --font-mono: {pilha(sug(fam['mono']), 'mono')};"]
    for papel, d in tip["papeis"].items():
        linhas.append(f"  --fs-{papel}: {d['tamanho']:g}px; --fw-{papel}: {d['peso']}; "
                      f"--lh-{papel}: {d['altura_linha']:g}; --ls-{papel}: {d['espacamento_em']:g}em;")
    linhas += ["", "  /* formas */",
               f"  --radius-sm: {f['radius-sm']}px;", f"  --radius-md: {f['radius-md']}px;",
               f"  --radius-lg: {f['radius-lg']}px;", "  --radius-pill: 999px;"]
    for nome, s in zip(("sm", "md", "lg"), f["sombras"] or []):
        linhas.append(f"  --shadow-{nome}: {s};")
    if not f["sombras"]:
        linhas.append("  --shadow-md: none;")
    for i, v in enumerate(f["espacos"], 1):
        linhas.append(f"  --space-{i}: {v}px;")
    d = mv["duracoes_ms"] or [150, 250, 400]
    linhas += ["", "  /* movimento */",
               f"  --dur-fast: {d[0]}ms;", f"  --dur-base: {d[len(d) // 2]}ms;", f"  --dur-slow: {d[-1]}ms;",
               f"  --ease: {mv['curva']};"]
    if t.get("anel_foco"):
        linhas.append(f"  --focus-ring: {t['anel_foco'].replace('solid ', '', 1)};")
    linhas.append("}")
    return "\n".join(linhas) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description="Captura de site -> tokens.json + tokens.css")
    p.add_argument("slug")
    p.add_argument("--sem-recalcular", action="store_true", help="só regera tokens.css a partir do tokens.json")
    args = p.parse_args()

    pasta = DESIGN_SYSTEMS / args.slug
    arq_tokens = pasta / "tokens.json"
    if args.sem_recalcular:
        if not arq_tokens.exists():
            erro(f"não existe {arq_tokens}")
        tokens = json.loads(arq_tokens.read_text(encoding="utf-8"))
        # papéis podem ter sido editados à mão: recalcula o contraste
        c = tokens["cores"]
        def cor(v):
            if v.startswith("#"):
                return [int(v[i:i + 2], 16) for i in (1, 3, 5)] + [1]
            n = re.findall(r"[\d.]+", v)
            return [int(float(x)) for x in n[:3]] + [1]
        c["_contraste"] = {"text/bg": contraste(cor(c["text"]), cor(c["bg"])),
                           "text-muted/bg": contraste(cor(c["text-muted"]), cor(c["bg"])),
                           "on-accent/accent": contraste(cor(c["on-accent"]), cor(c["accent"]))}
        arq_tokens.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        cap = pasta / "fonte" / "captura.json"
        if not cap.exists():
            erro(f"rode antes: python capturar_site.py <url> {args.slug}")
        tokens = extrair(json.loads(cap.read_text(encoding="utf-8")))
        arq_tokens.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
    (pasta / "tokens.css").write_text(gerar_css(tokens), encoding="utf-8")

    c, tip = tokens["cores"], tokens["tipografia"]
    print(f"Tokens gravados em: {pasta}")
    print(f"  cores: fundo {c['bg']} | superfície {c['surface']} | texto {c['text']} | secundário {c['text-muted']} "
          f"| acento {c['accent']}{' (monocromático)' if c['_monocromatico'] else ''} | borda {c['border']}")
    print(f"  contraste: {c['_contraste']}")
    for papel, f in tip["papeis"].items():
        print(f"  {papel}: {f['familia']} {f['peso']} {f['tamanho']:g}px  ex.: {f['exemplo']!r}")
    for nome, info in tip["fontes"].items():
        if info["origem"] != "google":
            print(f"  fonte '{nome}' ({info['origem']}): sugestão no Google Fonts = {info['sugestao_google']} (confirmar)")
    for k, v in c["_contraste"].items():
        if v < 4.5:
            print(f"  ATENÇÃO: contraste {k} = {v} (< 4.5, abaixo do recomendado para texto)")


if __name__ == "__main__":
    main()
