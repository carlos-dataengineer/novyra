"""Cria a pasta de um novo site em sites/<slug> a partir do template.

Exemplo:
    python novo_site.py painel-vendas --imagem "C:/mocks/painel.png"
    python novo_site.py landing-cafe            # sem imagem (modo brief)
    python novo_site.py landing-cafe --ds linear   # já nasce com o design system 'linear'
"""
from __future__ import annotations

import argparse
import re
import shutil
from datetime import date
from pathlib import Path

import json
from urllib.parse import quote_plus

from _comum import DESIGN_SYSTEMS, SITES, TEMPLATES, erro, resolver

ESTADO = """# Estado do site: {slug}

Criado em: {hoje}
Entrada: {entrada}

| Etapa | Status | Observação |
|-------|--------|------------|
| 1. Wireframe + plano | pendente | |
| 2. Fundo completo | pendente | |
| 3. Estrutura, componentes e fontes | pendente | |
| 4. Assets restantes | pendente | |
| 5. Revisão final | pendente | |

## Decisões e aproximações
- (registre aqui fontes aproximadas, cores ajustadas, assets que ficaram como placeholder)
"""


def aplicar_ds(destino: Path, slug: str) -> None:
    """Leva o design system para o site: tokens no :root, componentes no fim do CSS,
    <link> do Google Fonts no index.html e DS.md como referência. Nada de fonte/ (material de terceiros)."""
    ds = DESIGN_SYSTEMS / slug
    css_arq = destino / "assets" / "styles.css"
    if not css_arq.exists():
        aplicar_ds_por_link(destino, slug, ds)
        return
    css = css_arq.read_text(encoding="utf-8")
    tokens = (ds / "tokens.css").read_text(encoding="utf-8")
    raiz_ds = tokens[tokens.index(":root"):]
    ini = css.index(":root")
    fim = css.index("}", ini) + 1
    css = css[:ini] + raiz_ds.strip() + css[fim:]
    comp = ds / "assets" / "componentes.css"
    if comp.exists():
        css += f"\n/* ---- componentes do design system '{slug}' (design-systems/{slug}) ---- */\n"
        css += comp.read_text(encoding="utf-8")
    css_arq.write_text(css, encoding="utf-8")

    tj = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
    tip = tj["tipografia"]
    familias = []
    for nome in tip["familias"].values():
        if nome:
            g = tip["fontes"].get(nome, {}).get("sugestao_google", nome)
            if g not in familias:
                familias.append(g)
    links = "\n".join(
        f'  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={quote_plus(g)}:wght@400;500;600;700&display=swap">'
        for g in familias)
    html_arq = destino / "index.html"
    html = html_arq.read_text(encoding="utf-8")
    marcador = "  <!-- Etapa 3: adicionar aqui o <link> do Google Fonts escolhido -->"
    html = html.replace(marcador, f"  <!-- fontes do design system '{slug}' -->\n{links}") if marcador in html \
        else html.replace('  <link rel="stylesheet" href="assets/styles.css">',
                          f'{links}\n  <link rel="stylesheet" href="assets/styles.css">')
    html_arq.write_text(html, encoding="utf-8")
    if (ds / "DS.md").exists():
        shutil.copy2(ds / "DS.md", destino / "DS.md")


def aplicar_ds_por_link(destino: Path, slug: str, ds: Path) -> None:
    """Templates de arquivo único (CSS dentro do HTML): copia tokens.css e componentes.css
    para assets/ e liga os dois no <head>. Os tokens do DS ficam disponíveis como variáveis;
    a etapa 3 do /criar-site troca as variáveis próprias do template pelas do DS."""
    pasta = destino / "assets"
    pasta.mkdir(exist_ok=True)
    links = []
    for nome in ("tokens.css", "assets/componentes.css"):
        arq = ds / nome
        if arq.exists():
            shutil.copy2(arq, pasta / f"ds-{arq.name}")
            links.append(f'  <link rel="stylesheet" href="assets/ds-{arq.name}">')
    html_arq = destino / "index.html"
    html = html_arq.read_text(encoding="utf-8")
    bloco = f"  <!-- design system '{slug}' -->" + chr(10) + chr(10).join(links) + chr(10)
    html = html.replace("</head>", bloco + "</head>", 1)
    html_arq.write_text(html, encoding="utf-8")
    if (ds / "DS.md").exists():
        shutil.copy2(ds / "DS.md", destino / "DS.md")


def main() -> None:
    p = argparse.ArgumentParser(description="Cria um novo site a partir do template")
    p.add_argument("slug", help="nome curto em kebab-case, ex.: painel-vendas")
    p.add_argument("--imagem", help="mock de referência (png/jpg/webp)")
    p.add_argument("--template", default="site-base")
    p.add_argument("--ds", help="design system de design-systems a aplicar (tokens, componentes, fontes, DS.md)")
    args = p.parse_args()
    args.ds, args.template = resolver(args.ds), resolver(args.template)
    if args.ds and not (DESIGN_SYSTEMS / args.ds / "tokens.css").exists():
        erro(f"design system não encontrado: {DESIGN_SYSTEMS / args.ds} (rode /extrair-ds antes)")

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        erro("slug deve ser kebab-case: letras minúsculas, números e hífens")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.template):
        erro("template deve ser o nome de uma pasta de templates (kebab-case, sem caminhos)")
    destino = SITES / args.slug
    if destino.exists():
        erro(f"já existe: {destino}")
    origem = TEMPLATES / args.template
    if not origem.is_dir() or not origem.resolve().is_relative_to(TEMPLATES.resolve()):
        disponiveis = ", ".join(sorted(d.name for d in TEMPLATES.iterdir() if d.is_dir()))
        erro(f"template não encontrado: {args.template}. Disponíveis: {disponiveis}")

    shutil.copytree(origem, destino)
    entrada = "brief (sem imagem)"
    if args.imagem:
        img = Path(args.imagem)
        if not img.exists():
            shutil.rmtree(destino)
            erro(f"imagem não encontrada: {img}")
        shutil.copy2(img, destino / f"reference{img.suffix.lower()}")
        entrada = f"imagem `{img.name}`"
    if args.ds:
        aplicar_ds(destino, args.ds)
        entrada += f" + design system `{args.ds}`"
    (destino / "ESTADO.md").write_text(
        ESTADO.format(slug=args.slug, hoje=date.today().isoformat(), entrada=entrada),
        encoding="utf-8",
    )
    print(f"Site criado em: {destino}")


if __name__ == "__main__":
    main()
