"""Captura um site de referência para extrair o design system dele (etapa B).

Abre a página no Chrome (via Playwright), rola até o fim para carregar o conteúdo
preguiçoso, lê os estilos calculados de cada elemento visível, fotografa os
componentes candidatos e mede o que muda neles em hover e foco.

Saída em design-systems/<slug>/fonte/:
    captura.json        estilos, componentes, variáveis CSS, @keyframes, @font-face
    dobra.png           primeira tela (1440x900)
    pagina.png          página inteira (até 8000 px de altura)
    componentes/*.png   recorte de cada componente candidato

Exemplos:
    python capturar_site.py https://linear.app linear
    python capturar_site.py --arquivo "C:/sites/meu-site/index.html" meu-site
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from _comum import DESIGN_SYSTEMS, erro

AQUI = Path(__file__).resolve().parent
LER_ESTILO = """el => {
  const s = getComputedStyle(el);
  return {color: s.color, bg: s.backgroundColor, bgImg: s.backgroundImage, bc: s.borderTopColor,
          bw: s.borderTopWidth, bs: s.boxShadow, tf: s.transform, op: s.opacity, td: s.textDecorationLine,
          ol: s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor, fw: s.fontWeight, f: s.filter};
}"""


def ler_css_cru(css: str, dados: dict) -> None:
    """Extrai @font-face, @keyframes e variáveis do :root de um CSS em texto."""
    for bloco in re.findall(r"@font-face\s*{([^}]*)}", css):
        fam = re.search(r"font-family\s*:\s*([^;]+)", bloco)
        if fam:
            peso = re.search(r"font-weight\s*:\s*([^;]+)", bloco)
            src = re.search(r"src\s*:\s*([^;]+)", bloco)
            dados["fontes"].append({"familia": fam.group(1).strip().strip("\"'"),
                                    "peso": peso.group(1).strip() if peso else "",
                                    "src": src.group(1)[:200] if src else ""})
    for m in re.finditer(r"@(?:-webkit-)?keyframes\s+([\w-]+)\s*{", css):
        if len(dados["keyframes"]) >= 40:
            break
        dados["keyframes"].setdefault(m.group(1), css[m.start():m.start() + 800])
    for bloco in re.findall(r"(?<![\w.#-])(?::root|html)\s*{([^}]*)}", css):
        for nome, valor in re.findall(r"(--[\w-]+)\s*:\s*([^;]+)", bloco):
            dados["vars"].setdefault(nome, valor.strip())


def diferenca(antes: dict, depois: dict) -> dict:
    return {k: [antes[k], depois[k]] for k in antes if antes[k] != depois[k]}


def main() -> None:
    p = argparse.ArgumentParser(description="Captura um site de referência para extrair o design system")
    p.add_argument("url", nargs="?", help="endereço público (http/https)")
    p.add_argument("slug", help="nome curto em kebab-case para o design system")
    p.add_argument("--arquivo", help="em vez de URL, um index.html salvo no computador")
    p.add_argument("--largura", type=int, default=1440)
    p.add_argument("--altura", type=int, default=900)
    p.add_argument("--substituir", action="store_true", help="refaz a captura se já existir")
    args = p.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        erro("Playwright não instalado. Rode: pip install playwright  (usa o Chrome já instalado, não baixa navegador)")

    if args.arquivo:
        arq = Path(args.arquivo).resolve()
        if not arq.exists():
            erro(f"arquivo não encontrado: {arq}")
        url = arq.as_uri()
    elif args.url and args.url.startswith(("http://", "https://")):
        url = args.url
    else:
        erro("informe uma URL http(s) ou --arquivo")

    destino = DESIGN_SYSTEMS / args.slug / "fonte"
    if destino.exists():
        if not args.substituir:
            erro(f"já existe captura em {destino}. Use --substituir para refazer.")
        shutil.rmtree(destino)
    (destino / "componentes").mkdir(parents=True)

    coletor = (AQUI / "_coleta.js").read_text(encoding="utf-8")
    with sync_playwright() as pw:
        try:
            nav = pw.chromium.launch(channel="chrome", headless=True)
        except Exception:
            nav = pw.chromium.launch(channel="msedge", headless=True)
        pagina = nav.new_page(viewport={"width": args.largura, "height": args.altura}, device_scale_factor=1)
        try:
            pagina.goto(url, wait_until="load", timeout=60000)
        except Exception as e:
            nav.close()
            erro(f"não consegui abrir {url}: {str(e)[:200]}")
        try:
            pagina.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass  # sites com conexões abertas nunca ficam "idle"; segue assim mesmo

        # rola até o fim e volta: carrega imagens preguiçosas e dispara animações de entrada
        for _ in range(60):
            fim = pagina.evaluate("() => { scrollBy(0, innerHeight * 0.8); return innerHeight + scrollY >= document.documentElement.scrollHeight - 2; }")
            pagina.wait_for_timeout(200)
            if fim:
                break
        pagina.evaluate("() => scrollTo(0, 0)")
        pagina.wait_for_timeout(1200)
        pagina.evaluate("() => document.fonts.ready")

        pagina.screenshot(path=str(destino / "dobra.png"))
        altura = min(pagina.evaluate("() => document.documentElement.scrollHeight"), 8000)
        pagina.screenshot(path=str(destino / "pagina.png"), full_page=True,
                          clip={"x": 0, "y": 0, "width": args.largura, "height": altura})

        dados = pagina.evaluate(coletor)

        # folhas de outro domínio: o navegador não deixa o script lê-las, então baixa o texto e lê o CSS cru
        lidas = 0
        for href in dados.get("folhasExternas", [])[:20]:
            try:
                if href.startswith("file:"):
                    # o Chrome trata arquivo local como outra origem; lê direto do disco
                    from urllib.parse import unquote, urlparse
                    caminho = Path(unquote(urlparse(href).path).lstrip("/"))
                    ler_css_cru(caminho.read_text(encoding="utf-8", errors="replace"), dados)
                    lidas += 1
                    continue
                resp = pagina.request.get(href, timeout=15000)
                if not resp.ok:
                    continue
                ler_css_cru(resp.text(), dados)
                lidas += 1
            except Exception:
                pass
        dados["folhasBloqueadas"] -= lidas

        # componentes: recorte + estados (hover e foco)
        for c in dados["componentes"]:
            loc = pagina.locator(f'[data-dsx="{c["dsx"]}"]').first
            try:
                if loc.count() == 0:
                    c["aviso"] = "o site recriou este elemento depois da coleta; estados não medidos"
                    continue
                loc.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest'})")
                pagina.mouse.move(1, 1)
                pagina.wait_for_timeout(350)
                caixa = loc.bounding_box()
                if caixa and caixa["height"] <= 900:
                    arq = f'{c["tipo"]}-{c["dsx"]}.png'
                    loc.screenshot(path=str(destino / "componentes" / arq), timeout=5000)
                    c["recorte"] = f"componentes/{arq}"
                base = loc.evaluate(LER_ESTILO)
                if c["tipo"] in ("botao", "link", "card", "selo"):
                    loc.hover(timeout=3000, force=True)
                    pagina.wait_for_timeout(600)
                    c["hover"] = diferenca(base, loc.evaluate(LER_ESTILO))
                    pagina.mouse.move(1, 1)
                    pagina.wait_for_timeout(400)
                if c["tipo"] in ("botao", "campo", "link"):
                    loc.evaluate("el => el.focus({preventScroll: true})")
                    pagina.wait_for_timeout(300)
                    c["foco"] = diferenca(base, loc.evaluate(LER_ESTILO))
                    loc.evaluate("el => el.blur()")
            except Exception as e:
                c["aviso"] = f"estado não medido: {str(e)[:120]}"
        nav.close()

    (destino / "captura.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    tipos: dict[str, int] = {}
    for c in dados["componentes"]:
        tipos[c["tipo"]] = tipos.get(c["tipo"], 0) + 1
    print(f"Captura salva em: {destino}")
    print(f"  {dados['titulo']!r} | {len(dados['elementos'])} elementos | página com {dados['alturaPagina']} px")
    print(f"  componentes: {tipos or 'nenhum'}")
    print(f"  variáveis CSS no :root: {len(dados['vars'])} | @keyframes: {len(dados['keyframes'])} | @font-face: {len(dados['fontes'])}")
    if dados["folhasBloqueadas"]:
        print(f"  aviso: {dados['folhasBloqueadas']} folha(s) de estilo de outro domínio não puderam ser lidas "
              "(estilos calculados continuam válidos; só @keyframes/variáveis delas ficam de fora)")


if __name__ == "__main__":
    main()
