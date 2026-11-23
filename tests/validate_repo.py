"""Valida a estrutura do repositório NOVYRA (roda no CI e localmente).

Confere: arquivos obrigatórios, frontmatter das skills, openai.yaml do Codex, manifestos do
plugin com a mesma versão de VERSION, design systems completos, templates, sintaxe dos
scripts Python, links e imagens do README, e que nada de terceiros/privado foi publicado.

    python tests/validate_repo.py
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = ("novyra", "criar-site", "wireframe", "extrair-ds", "combinar-ds")
OBRIGATORIOS = [
    "README.md", "README.en.md", "LICENSE", "NOTICE", "VERSION", "CHANGELOG.md", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "SECURITY.md", "SUPPORT.md", ".gitignore", ".gitattributes", ".editorconfig",
    "install.sh", "install.ps1", "uninstall.sh", "uninstall.ps1", "scripts/install_novyra.py",
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".github/workflows/ci.yml",
    ".github/workflows/release.yml", ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/pull_request_template.md",
    "runtime/requirements.txt", "runtime/scripts/_comum.py", "runtime/scripts/gerar_painel.py",
    "runtime/scripts/novo_site.py", "runtime/templates/site-base/index.html",
]
# Termos que não podem ir a público. Os genéricos ficam aqui; nomes privados de quem mantém o
# projeto vão na variável NOVYRA_PROIBIDOS (regex), definida só na máquina dela.
PROIBIDOS = re.compile(r"(?i)" + "|".join(filter(None, [
    r"00_referencia", r"BEGIN [A-Z ]*PRIVATE KEY", r"sk-or-v1-[0-9a-f]{8}",
    os.environ.get("NOVYRA_PROIBIDOS", ""),
])))
erros: list[str] = []


def falha(msg: str) -> None:
    erros.append(msg)


def frontmatter(txt: str) -> dict[str, str]:
    if not txt.startswith("---"):
        return {}
    bloco = txt[3:txt.index("\n---", 3)]
    campos, chave = {}, None
    for linha in bloco.splitlines():
        m = re.match(r"^([a-z-]+):\s*(.*)$", linha)
        if m:
            chave = m.group(1)
            campos[chave] = m.group(2).strip()
        elif chave and linha.startswith("  "):
            campos[chave] = (campos[chave] + " " + linha.strip()).strip()
    return campos


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for rel in OBRIGATORIOS:
        if not (RAIZ / rel).exists():
            falha(f"falta {rel}")

    versao = (RAIZ / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", versao):
        falha(f"VERSION inválida: {versao}")
    for man in ("plugin.json", "marketplace.json"):
        d = json.loads((RAIZ / ".claude-plugin" / man).read_text(encoding="utf-8"))
        v = d.get("version") or d["plugins"][0].get("version")
        if v != versao:
            falha(f".claude-plugin/{man} tem versão {v}, VERSION tem {versao}")
    if f"## [{versao}]" not in (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8"):
        falha(f"CHANGELOG.md não tem a seção ## [{versao}]")

    for nome in SKILLS:
        sk = RAIZ / "skills" / nome / "SKILL.md"
        if not sk.exists():
            falha(f"falta skills/{nome}/SKILL.md")
            continue
        fm = frontmatter(sk.read_text(encoding="utf-8"))
        if fm.get("name") != nome:
            falha(f"skills/{nome}: name no frontmatter é {fm.get('name')!r}")
        if len(fm.get("description", "")) < 40:
            falha(f"skills/{nome}: description curta demais")
        yml = RAIZ / "skills" / nome / "agents" / "openai.yaml"
        if not yml.exists():
            falha(f"falta skills/{nome}/agents/openai.yaml")
        else:
            y = yml.read_text(encoding="utf-8")
            for k in ("interface:", "display_name:", "short_description:", "policy:", "allow_implicit_invocation:"):
                if k not in y:
                    falha(f"skills/{nome}/agents/openai.yaml sem {k}")
        txt = sk.read_text(encoding="utf-8")
        if nome != "wireframe" and "{{RAIZ}}" not in txt:
            falha(f"skills/{nome}: não usa {{{{RAIZ}}}} para achar o runtime")

    for ds in sorted((RAIZ / "runtime" / "design-systems").iterdir()):
        if not ds.is_dir():
            continue
        for arq in ("tokens.json", "tokens.css", "DS.md", "design-system.html", "assets/componentes.css"):
            if not (ds / arq).exists():
                falha(f"design system {ds.name} sem {arq}")
        if (ds / "fonte").exists():
            falha(f"design system {ds.name} tem pasta fonte/ (material de terceiros)")
        t = json.loads((ds / "tokens.json").read_text(encoding="utf-8"))
        for k in ("origem", "cores", "tipografia", "formas", "movimento", "fundos"):
            if k not in t:
                falha(f"design system {ds.name}: tokens.json sem {k}")
        if t.get("cores", {}).get("_contraste", {}).get("text/bg", 0) < 4.5:
            falha(f"design system {ds.name}: contraste texto/fundo abaixo de 4.5")

    for tpl in sorted((RAIZ / "runtime" / "templates").iterdir()):
        if tpl.is_dir() and not (tpl / "index.html").exists():
            falha(f"template {tpl.name} sem index.html")

    for py in list((RAIZ / "runtime" / "scripts").glob("*.py")) + list((RAIZ / "scripts").glob("*.py")) \
            + list((RAIZ / "tests").glob("*.py")):
        try:
            ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            falha(f"sintaxe em {py.relative_to(RAIZ)}: {exc}")

    for ps1 in RAIZ.glob("*.ps1"):
        dados = ps1.read_bytes()
        if dados.startswith(b"\xef\xbb\xbf"):
            falha(f"{ps1.name} tem BOM (quebra o irm | iex)")

    for readme in ("README.md", "README.en.md"):
        arq = RAIZ / readme
        if not arq.exists():
            continue
        txt = arq.read_text(encoding="utf-8")
        for alvo in re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)", txt) + re.findall(r'src="(?!https?://)([^"]+)"', txt):
            if not (RAIZ / alvo.split("#")[0]).exists():
                falha(f"{readme}: link quebrado {alvo}")
        for trecho in ("install.sh", "install.ps1", "/criar-site", "$criar-site", "NOVYRA Studio"):
            if trecho not in txt:
                falha(f"{readme} não menciona {trecho}")

    ignorar = {".git", "tests"}
    for arq in RAIZ.rglob("*"):
        if arq.is_dir() or ignorar & set(arq.relative_to(RAIZ).parts) or arq.suffix in (".png", ".jpg", ".webp"):
            continue
        if arq.name in ("CHANGELOG.md",):
            continue
        try:
            txt = arq.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        m = PROIBIDOS.search(txt)
        if m:
            falha(f"{arq.relative_to(RAIZ)} cita {m.group(0)!r} (privado ou de terceiros)")

    if erros:
        print("Falhou:")
        for e in erros:
            print(f"  - {e}")
        return 1
    print(f"OK: repositório NOVYRA {versao} válido ({len(SKILLS)} skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
