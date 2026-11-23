"""Recorta regiões da referência e gera uma grade de coordenadas para localizar caixas.

Exemplos:
    # grade com réguas a cada 100 px, para descobrir coordenadas
    python recortar.py reference.png --grade 100
    # recorte de uma região (x,y,largura,altura) para assets/crops/
    python recortar.py reference.png --caixa 40,30,64,64 --saida assets/crops/ico-logo.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from _comum import caixa, erro


def grade(img: Image.Image, passo: int) -> Image.Image:
    out = img.convert("RGB").copy()
    d = ImageDraw.Draw(out)
    w, h = out.size
    for x in range(0, w, passo):
        d.line([(x, 0), (x, h)], fill=(255, 0, 80), width=1)
        d.text((x + 2, 2), str(x), fill=(255, 0, 80))
    for y in range(0, h, passo):
        d.line([(0, y), (w, y)], fill=(0, 140, 255), width=1)
        d.text((2, y + 2), str(y), fill=(0, 140, 255))
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Recortes e grade de coordenadas")
    p.add_argument("imagem")
    p.add_argument("--caixa", help="x,y,largura,altura")
    p.add_argument("--grade", type=int, help="desenha grade a cada N px")
    p.add_argument("--zoom", type=int, default=1, help="amplia o recorte N vezes (só para inspeção)")
    p.add_argument("--saida")
    args = p.parse_args()

    src = Path(args.imagem)
    if not src.exists():
        erro(f"imagem não encontrada: {src}")
    img = Image.open(src)
    print(f"Tamanho da imagem: {img.size[0]}x{img.size[1]}")

    if args.grade:
        saida = Path(args.saida) if args.saida else src.with_name(f"{src.stem}.grade.png")
        grade(img, args.grade).save(saida)
        print(f"Grade salva em: {saida}")
        return
    if not args.caixa:
        erro("informe --caixa ou --grade")
    rec = img.crop(caixa(args.caixa))
    if args.zoom > 1:
        rec = rec.resize((rec.width * args.zoom, rec.height * args.zoom), Image.NEAREST)
    saida = Path(args.saida) if args.saida else src.with_name(f"crop-{args.caixa.replace(',', '_')}.png")
    saida.parent.mkdir(parents=True, exist_ok=True)
    rec.save(saida)
    print(f"Recorte salvo em: {saida} ({rec.width}x{rec.height})")


if __name__ == "__main__":
    main()
