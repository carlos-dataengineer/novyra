"""Tira screenshot de um index.html no tamanho exato (Playwright, se instalado; senão Chrome/Edge headless).

Exemplo:
    python capturar_tela.py ../sites/painel-vendas --largura 1440 --altura 900
    python capturar_tela.py ../sites/painel-vendas --igual-referencia
Saída padrão: <site>/_capturas/captura-<largura>x<altura>.png
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from _comum import achar_navegadores, erro


def referencia(site: Path) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        r = site / f"reference{ext}"
        if r.exists():
            return r
    return None


def capturar_playwright(html: Path, saida: Path, largura: int, altura: int, espera_ms: int) -> bool:
    """Viewport exato (o Chrome pela linha de comando não desce de ~500 px de largura)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as pw:
            nav = None
            for canal in ("chrome", "msedge", None):
                try:
                    nav = pw.chromium.launch(channel=canal) if canal else pw.chromium.launch()
                    break
                except Exception:  # noqa: BLE001
                    continue
            if nav is None:
                return False
            pg = nav.new_page(viewport={"width": largura, "height": altura}, device_scale_factor=1)
            pg.goto(html.resolve().as_uri())
            pg.wait_for_timeout(min(espera_ms, 5000))
            pg.screenshot(path=str(saida))
            nav.close()
    except Exception:  # noqa: BLE001
        return False
    if saida.exists():
        print(f"Captura salva em: {saida} (playwright)")
        return True
    return False


def capturar(html: Path, saida: Path, largura: int, altura: int, espera_ms: int) -> None:
    saida = saida.resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    if saida.exists():
        saida.unlink()
    if capturar_playwright(html, saida, largura, altura, espera_ms):
        return
    falhas = []
    for navegador in achar_navegadores():
        # perfil temporário; o navegador pode segurar arquivos ao sair, então ignorar falha na limpeza
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as perfil:
            cmd = [
                navegador,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--user-data-dir={perfil}",
                f"--window-size={largura},{altura}",
                f"--virtual-time-budget={espera_ms}",
                f"--screenshot={saida}",
                html.resolve().as_uri(),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if saida.exists():
            print(f"Captura salva em: {saida} ({Path(navegador).stem})")
            return
        falhas.append(f"{Path(navegador).stem}: {(r.stderr or 'saiu sem gerar imagem').strip()[-300:]}")
    erro("captura falhou em todos os navegadores.\n" + "\n".join(falhas))


def main() -> None:
    p = argparse.ArgumentParser(description="Screenshot headless de um site")
    p.add_argument("site", help="pasta do site ou caminho do index.html")
    p.add_argument("--largura", type=int, default=1440)
    p.add_argument("--altura", type=int, default=900)
    p.add_argument("--igual-referencia", action="store_true",
                   help="usa o tamanho da reference.* do site")
    p.add_argument("--espera", type=int, default=3000, help="ms para fontes/imagens carregarem")
    p.add_argument("--saida")
    args = p.parse_args()

    alvo = Path(args.site)
    html = alvo / "index.html" if alvo.is_dir() else alvo
    if not html.exists():
        erro(f"index.html não encontrado em {alvo}")
    site = html.parent
    largura, altura = args.largura, args.altura
    if args.igual_referencia:
        ref = referencia(site)
        if not ref:
            erro("site sem reference.*")
        from PIL import Image
        with Image.open(ref) as im:
            largura, altura = im.size
    saida = Path(args.saida) if args.saida else site / "_capturas" / f"captura-{largura}x{altura}.png"
    capturar(html, saida, largura, altura, args.espera)


if __name__ == "__main__":
    main()
