"""Funções compartilhadas pelos scripts do NOVYRA.

RAIZ é a pasta do runtime (no computador do usuário: ~/Novyra ou NOVYRA_HOME).
Os sites vão para RAIZ/sites, ou para NOVYRA_SITES se essa variável existir.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITES = Path(os.environ["NOVYRA_SITES"]).expanduser() if os.environ.get("NOVYRA_SITES") else RAIZ / "sites"
TEMPLATES = RAIZ / "templates"
DESIGN_SYSTEMS = RAIZ / "design-systems"

# Nomes usados na v0.1.x (antes da troca por nomes neutros). Continuam aceitos.
APELIDOS = {
    "lusion-immersive-3d": "immersive-3d",
    "takamo-cinematic-sci-fi": "cinematic-sci-fi",
    "databahn-futuristic-tech": "futuristic-tech",
    "lusion-3d-immersive": "immersive-3d-studio",
    "databahn-tech-product": "tech-product",
}


def resolver(slug: str | None) -> str | None:
    """Traduz um nome antigo de template ou design system para o atual."""
    return APELIDOS.get(slug, slug) if slug else slug

# Windows: garantir saída UTF-8 no terminal
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def erro(msg: str, codigo: int = 1) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(codigo)


def caixa(texto: str) -> tuple[int, int, int, int]:
    """Converte 'x,y,largura,altura' em tupla (x0, y0, x1, y1)."""
    try:
        x, y, w, h = (int(float(v)) for v in texto.split(","))
    except ValueError:
        erro(f"caixa inválida '{texto}'. Use x,y,largura,altura")
    return x, y, x + w, y + h


def achar_navegadores() -> list[str]:
    """Lista navegadores Chromium disponíveis para captura headless, na ordem de preferência.

    Chrome vem antes do Edge: em máquinas corporativas o Edge headless costuma ser
    bloqueado por política e sair sem gerar a imagem.
    """
    candidatos = [
        os.environ.get("NAVEGADOR", ""),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for nome in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        candidatos.append(shutil.which(nome) or "")
    achados: list[str] = []
    for c in candidatos:
        if c and Path(c).exists() and c not in achados:
            achados.append(c)
    if not achados:
        erro("Chrome/Edge não encontrado. Defina a variável NAVEGADOR com o caminho do executável.")
    return achados


def carregar_env() -> None:
    """Lê .env da raiz do projeto e da pasta do usuário (sem dependências)."""
    for arq in (RAIZ / ".env", Path.home() / ".env"):
        if not arq.exists():
            continue
        for linha in arq.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))
