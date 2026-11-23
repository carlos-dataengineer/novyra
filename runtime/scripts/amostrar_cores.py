"""Conta-gotas: lê cores exatas da referência (pontos) ou a paleta dominante de uma região.

Exemplos:
    python amostrar_cores.py reference.png --pontos 10,10 720,40 1200,600
    python amostrar_cores.py reference.png --caixa 0,0,1440,80 --paleta 6
    python amostrar_cores.py reference.png --gradiente 0,0,1440,900 --passos 5
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from _comum import caixa, erro


def hexa(rgba) -> str:
    r, g, b = rgba[:3]
    a = rgba[3] if len(rgba) > 3 else 255
    base = f"#{r:02x}{g:02x}{b:02x}"
    return base if a == 255 else f"{base} (alpha {a / 255:.2f})"


def media(img: Image.Image, x: int, y: int, raio: int = 2):
    w, h = img.size
    px = [img.getpixel((i, j))
          for i in range(max(0, x - raio), min(w, x + raio + 1))
          for j in range(max(0, y - raio), min(h, y + raio + 1))]
    return tuple(round(sum(c[k] for c in px) / len(px)) for k in range(4))


def main() -> None:
    p = argparse.ArgumentParser(description="Amostragem de cores da referência")
    p.add_argument("imagem")
    p.add_argument("--pontos", nargs="*", help="lista de x,y")
    p.add_argument("--caixa", help="x,y,largura,altura para paleta")
    p.add_argument("--paleta", type=int, default=6)
    p.add_argument("--gradiente", help="x,y,largura,altura: amostra a diagonal da caixa")
    p.add_argument("--passos", type=int, default=5)
    args = p.parse_args()

    src = Path(args.imagem)
    if not src.exists():
        erro(f"imagem não encontrada: {src}")
    img = Image.open(src).convert("RGBA")

    if args.pontos:
        print("Ponto        Cor (média 5x5)")
        for pt in args.pontos:
            x, y = (int(v) for v in pt.split(","))
            print(f"{pt:<12} {hexa(media(img, x, y))}")
    if args.caixa:
        reg = img.crop(caixa(args.caixa)).convert("RGB")
        q = reg.quantize(colors=args.paleta, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()
        contagem = sorted(q.getcolors(), reverse=True)
        total = sum(n for n, _ in contagem)
        print(f"Paleta dominante de {args.caixa}:")
        for n, idx in contagem:
            r, g, b = pal[idx * 3: idx * 3 + 3]
            print(f"  #{r:02x}{g:02x}{b:02x}  {100 * n / total:5.1f}%")
    if args.gradiente:
        x0, y0, x1, y1 = caixa(args.gradiente)
        print(f"Diagonal de ({x0},{y0}) a ({x1 - 1},{y1 - 1}):")
        for i in range(args.passos):
            t = i / max(1, args.passos - 1)
            x = round(x0 + t * (x1 - 1 - x0))
            y = round(y0 + t * (y1 - 1 - y0))
            print(f"  {round(t * 100):>3}%  ({x},{y})  {hexa(media(img, x, y))}")
    if not (args.pontos or args.caixa or args.gradiente):
        erro("informe --pontos, --caixa ou --gradiente")


if __name__ == "__main__":
    main()
