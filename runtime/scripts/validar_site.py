"""Confere se um site segue as regras do projeto.

Regras:
  - entrypoint chamado exatamente index.html, carregando assets/styles.css
  - nada de <style>, style="..." ou <script> inline
  - todo arquivo referenciado (src/href/url()) existe, usa caminho relativo
    e fica dentro da pasta do site (nada de ../ para fora)
  - nenhum package.json / node_modules / framework via CDN
  - classes usadas no HTML existem no CSS (aviso)

Exemplo:
    python validar_site.py ../sites/painel-vendas
Sai com código 1 se houver erro (útil antes de publicar).
"""
from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

from _comum import erro

CDN_PROIBIDO = ("tailwind", "bootstrap", "react", "vue", "jquery", "unpkg.com", "jsdelivr")
EXTERNO_OK = ("fonts.googleapis.com", "fonts.gstatic.com")


class Leitor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.classes: set[str] = set()
        self.problemas: list[str] = []
        self._em_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "style" in a:
            self.problemas.append(f'style="…" inline em <{tag}>')
        if tag == "style":
            self.problemas.append("bloco <style> inline")
        if tag == "script":
            if not a.get("src"):
                self._em_script = True
            else:
                self.refs.append(("script", a["src"]))
        for k in ("src", "href", "poster"):
            if a.get(k) and tag != "script":
                self.refs.append((tag, a[k]))
        if a.get("srcset"):
            for parte in a["srcset"].split(","):
                self.refs.append((tag, parte.strip().split(" ")[0]))
        for c in (a.get("class") or "").split():
            self.classes.add(c)

    def handle_data(self, data):
        if self._em_script and data.strip():
            self.problemas.append("bloco <script> inline")

    def handle_endtag(self, tag):
        if tag == "script":
            self._em_script = False


def checar_ref(site: Path, ref: str, erros: list[str], avisos: list[str]) -> None:
    if ref.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
        return
    if ref.startswith(("http://", "https://", "//")):
        if any(c in ref for c in CDN_PROIBIDO):
            erros.append(f"framework/CDN proibido: {ref}")
        elif not any(c in ref for c in EXTERNO_OK):
            avisos.append(f"recurso externo (site não funciona offline): {ref}")
        return
    if ref.startswith("/") or re.match(r"^[a-zA-Z]:", ref):
        erros.append(f"caminho absoluto (use relativo): {ref}")
        return
    alvo = (site / ref.split("?")[0].split("#")[0]).resolve()
    if not dentro(site, alvo):
        erros.append(f"caminho sai da pasta do site: {ref}")
    elif not alvo.exists():
        erros.append(f"arquivo referenciado não existe: {ref}")


def dentro(site: Path, alvo: Path) -> bool:
    """True se alvo está dentro da pasta do site (bloqueia ../ e links para fora)."""
    return alvo.is_relative_to(site.resolve())


def main() -> None:
    p = argparse.ArgumentParser(description="Valida as regras de um site")
    p.add_argument("site")
    args = p.parse_args()
    site = Path(args.site)
    if not site.is_dir():
        erro(f"pasta não encontrada: {site}")

    erros: list[str] = []
    avisos: list[str] = []
    html_p = site / "index.html"
    if not html_p.exists():
        erro("index.html não encontrado (o entrypoint deve se chamar exatamente index.html)")
    html = html_p.read_text(encoding="utf-8")
    leitor = Leitor()
    leitor.feed(html)
    erros += leitor.problemas

    if not any(r == "assets/styles.css" for _, r in leitor.refs):
        erros.append('index.html não carrega "assets/styles.css"')
    for _, r in leitor.refs:
        checar_ref(site, r, erros, avisos)

    css_total = ""
    for css in sorted((site / "assets").rglob("*.css")):
        txt = css.read_text(encoding="utf-8")
        css_total += txt
        for url in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", txt):
            if url.startswith(("data:", "#")):
                continue
            if url.startswith(("http://", "https://", "//")):
                if not any(c in url for c in EXTERNO_OK):
                    avisos.append(f"{css.name}: url() externo: {url}")
                continue
            alvo = (css.parent / url.split("?")[0].split("#")[0]).resolve()
            if not dentro(site, alvo):
                erros.append(f"{css.name}: url() sai da pasta do site: {url}")
            elif not alvo.exists():
                erros.append(f"{css.name}: url() não existe: {url}")
        for imp in re.findall(r"@import\s+(?:url\()?\s*['\"]?([^'\")\s;]+)", txt):
            if imp.startswith(("http://", "https://", "//")) and not any(c in imp for c in EXTERNO_OK):
                erros.append(f"{css.name}: @import externo não permitido: {imp}")
        linhas = txt.count("\n")
        if linhas > 1500:
            avisos.append(f"{css.name} tem {linhas} linhas: considere dividir por região")

    for proibido in ("package.json", "node_modules"):
        if (site / proibido).exists():
            erros.append(f"{proibido} não é permitido (projeto sem build)")

    sem_css = sorted(c for c in leitor.classes
                     if not re.search(r"\." + re.escape(c) + r"(?![\w-])", css_total))
    if sem_css:
        avisos.append("classes sem regra no CSS: " + ", ".join(sem_css[:20]))

    for a in avisos:
        print(f"AVISO  {a}")
    for e in erros:
        print(f"ERRO   {e}")
    if erros:
        print(f"\n{len(erros)} erro(s), {len(avisos)} aviso(s).")
        raise SystemExit(1)
    print(f"\nOK: site válido ({len(avisos)} aviso(s)).")


if __name__ == "__main__":
    main()
