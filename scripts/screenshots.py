"""Gera as capturas de tela do README em docs/images/.

Instala o runtime numa pasta temporária, cria sites de exemplo, gera o NOVYRA Studio e
fotografa cada aba, um catálogo de design system e os templates. Com --demo, copia um site
pronto (pasta com index.html e reference.*) para aparecer no painel e gera as imagens da demo.

Requer: pip install playwright pillow  (usa o Chrome instalado; ou: python -m playwright install chromium)
Uso:    python scripts/screenshots.py [--demo caminho/do/site]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images"
EXEMPLOS = {  # slug -> etapas aprovadas (só para mostrar o painel com progresso)
    "landing-plataforma-ia": 5,
    "portfolio-estudio-3d": 3,
    "evento-sci-fi": 1,
}


def py(*args: str, cwd: Path | None = None) -> None:
    subprocess.run([sys.executable, "-X", "utf8", *args], check=True, cwd=cwd, capture_output=True)


def marcar_etapas(site: Path, n: int) -> None:
    estado = site / "ESTADO.md"
    linhas = estado.read_text(encoding="utf-8").splitlines()
    feitas = 0
    for i, l in enumerate(linhas):
        if l.startswith("| ") and "| pendente |" in l and feitas < n:
            linhas[i] = l.replace("| pendente |", "| aprovado |")
            feitas += 1
    estado.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def abrir_navegador(pw):
    for canal in ("chrome", "msedge", None):
        try:
            return pw.chromium.launch(channel=canal, headless=True) if canal else pw.chromium.launch(headless=True)
        except Exception:  # noqa: BLE001
            continue
    raise SystemExit("Nenhum Chromium disponível. Instale o Chrome ou rode: python -m playwright install chromium")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", help="pasta de um site pronto para incluir no painel")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        user = Path(tmp)
        raiz = user / "Novyra"
        py(str(ROOT / "scripts" / "install_novyra.py"), "--home", str(raiz), "--user-home", str(user),
           "--skip-deps", "--no-open", "--skip-claude", "--skip-codex")
        s = raiz / "scripts"
        combos = {"landing-plataforma-ia": ("tech-product", "novyra-future-lab"),
                  "portfolio-estudio-3d": ("immersive-3d-studio", "immersive-3d"),
                  "evento-sci-fi": ("cinematic-sci-fi", "cinematic-sci-fi")}
        for slug, n in EXEMPLOS.items():
            tpl, ds = combos[slug]
            py(str(s / "novo_site.py"), slug, "--template", tpl, "--ds", ds)
            marcar_etapas(raiz / "sites" / slug, n)
        if a.demo:
            demo = Path(a.demo)
            shutil.copytree(demo, raiz / "sites" / demo.name)
        py(str(s / "gerar_painel.py"))
        painel = (raiz / "novyra.html").as_uri()

        with sync_playwright() as pw:
            nav = abrir_navegador(pw)
            pg = nav.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            pg.goto(painel)
            pg.wait_for_timeout(1500)  # fontes
            # o caminho local (com o nome do usuário da máquina) não aparece nas imagens públicas
            pg.evaluate("document.querySelectorAll('.local-path').forEach(p => p.remove())")

            # aba Criar com um comando preenchido
            pg.fill("#imagem", "C:/Users/voce/Desktop/landing-ia.png")
            pg.fill("#slug", "landing-plataforma-ia")
            pg.select_option("#tpl", "tech-product")
            pg.select_option("#ds", "novyra-future-lab")
            pg.wait_for_timeout(200)
            pg.screenshot(path=str(OUT / "studio-criar.png"))
            pg.click("#agente button[data-a='codex']")
            pg.wait_for_timeout(150)
            pg.locator(".builder").screenshot(path=str(OUT / "studio-codex.png"))
            pg.click("#agente button[data-a='claude']")

            for tecla, nome in (("2", "studio-templates"), ("3", "studio-design-systems"), ("4", "studio-sites"), ("6", "studio-referencias")):
                pg.locator("body").click(position={"x": 5, "y": 300})
                pg.keyboard.press(tecla)
                pg.wait_for_timeout(700)
                pg.evaluate("window.scrollTo(0, 330)")
                pg.wait_for_timeout(300)
                pg.screenshot(path=str(OUT / f"{nome}.png"))

            # pipeline de agentes: um site no meio do caminho e a demo concluída
            pg.locator("body").click(position={"x": 5, "y": 300})
            pg.keyboard.press("5")
            pg.wait_for_timeout(400)
            for slug, nome in (("portfolio-estudio-3d", "studio-pipeline"), (Path(a.demo).name if a.demo else "", "studio-pipeline-demo")):
                if not slug:
                    continue
                pg.select_option("#pipe-site", slug)
                pg.wait_for_timeout(700)
                pg.locator("#pipe-palco").screenshot(path=str(OUT / f"{nome}.png"))
            pg.keyboard.press("7")
            pg.wait_for_timeout(300)
            pg.locator("#atalhos").screenshot(path=str(OUT / "studio-atalhos.png"))
            pg.evaluate("document.querySelector('#guia .card').scrollIntoView()")
            pg.locator("#guia .card").first.screenshot(path=str(OUT / "etapas.png"))

            # tema claro
            pg.keyboard.press("1")
            pg.keyboard.press("t")
            pg.evaluate("window.scrollTo(0, 0)")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / "studio-claro.png"))
            pg.keyboard.press("t")

            # celular
            cel = nav.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
            cel.goto(painel)
            cel.wait_for_timeout(1200)
            cel.screenshot(path=str(OUT / "studio-celular.png"))

            # catálogo de design system
            ds = nav.new_page(viewport={"width": 1440, "height": 900})
            ds.goto((raiz / "design-systems" / "novyra-future-lab" / "design-system.html").as_uri())
            ds.wait_for_timeout(1500)
            ds.screenshot(path=str(OUT / "ds-catalogo.png"))

            # templates em tamanho real
            for tpl in ("immersive-3d-studio", "cinematic-sci-fi", "tech-product", "studio-3d-light", "retro-glitch", "bio-data-mono"):
                t = nav.new_page(viewport={"width": 1440, "height": 900})
                t.goto((raiz / "templates" / tpl / "index.html").as_uri())
                t.wait_for_timeout(1000)
                t.screenshot(path=str(OUT / f"template-{tpl}.png"))
            nav.close()

    for f in sorted(OUT.glob("*.png")):
        print(f"  {f.relative_to(ROOT)}  {f.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
