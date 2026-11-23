"""Compara a captura do site com a referência: nota geral, mapa de diferenças e piores regiões.

Exemplos:
    python comparar.py ../sites/painel/reference.png ../sites/painel/_capturas/captura-1440x900.png
    python comparar.py ref.png cap.png --caixa 0,0,1440,80     # só a nav
    python comparar.py ref.png cap.png --lado-a-lado           # gera imagem ref | site | diff
Saídas ao lado da captura: <captura>.diff.png e, com --lado-a-lado, <captura>.lado.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from _comum import caixa, erro


def main() -> None:
    p = argparse.ArgumentParser(description="Diferença visual referência x site")
    p.add_argument("referencia")
    p.add_argument("captura")
    p.add_argument("--caixa", help="x,y,largura,altura: compara só essa região")
    p.add_argument("--celulas", type=int, default=8, help="grade NxN para ranquear regiões")
    p.add_argument("--tolerancia", type=int, default=24, help="diferença (0-255) ignorada por canal")
    p.add_argument("--lado-a-lado", action="store_true")
    args = p.parse_args()

    ref_p, cap_p = Path(args.referencia), Path(args.captura)
    for f in (ref_p, cap_p):
        if not f.exists():
            erro(f"arquivo não encontrado: {f}")
    ref = Image.open(ref_p).convert("RGB")
    cap = Image.open(cap_p).convert("RGB")
    if cap.size != ref.size:
        print(f"Aviso: tamanhos diferentes (ref {ref.size}, captura {cap.size}); captura redimensionada.")
        cap = cap.resize(ref.size, Image.LANCZOS)
    if args.caixa:
        b = caixa(args.caixa)
        ref, cap = ref.crop(b), cap.crop(b)

    # leve desfoque reduz ruído de antialiasing de texto
    diff = ImageChops.difference(ref.filter(ImageFilter.GaussianBlur(1)),
                                 cap.filter(ImageFilter.GaussianBlur(1))).convert("L")
    w, h = diff.size
    hist = diff.histogram()
    total = w * h
    fora = sum(hist[args.tolerancia + 1:])
    media = sum(i * n for i, n in enumerate(hist)) / total
    nota = max(0.0, 100.0 - 100.0 * fora / total)
    print(f"Semelhança: {nota:.1f}%  (pixels fora da tolerância: {100 * fora / total:.1f}%, "
          f"diferença média {media:.1f}/255)")

    n = args.celulas
    cw, ch = w / n, h / n
    piores = []
    for i in range(n):
        for j in range(n):
            bx = (round(j * cw), round(i * ch), round((j + 1) * cw), round((i + 1) * ch))
            cel = diff.crop(bx)
            hh = cel.histogram()
            piores.append((sum(hh[args.tolerancia + 1:]) / max(1, cel.width * cel.height), bx))
    piores.sort(reverse=True)
    print("Regiões com mais diferença (x,y,largura,altura -> % divergente):")
    for frac, (x0, y0, x1, y1) in piores[:5]:
        print(f"  {x0},{y0},{x1 - x0},{y1 - y0}  -> {100 * frac:.0f}%")

    mapa = Image.blend(ref.convert("L").convert("RGB"),
                       Image.merge("RGB", (diff.point(lambda v: min(255, v * 4)),
                                           Image.new("L", diff.size, 0),
                                           Image.new("L", diff.size, 0))), 0.6)
    d = ImageDraw.Draw(mapa)
    for _, (x0, y0, x1, y1) in piores[:5]:
        d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(255, 220, 0), width=2)
    saida = cap_p.with_name(cap_p.stem + ".diff.png")
    mapa.save(saida)
    print(f"Mapa de diferenças: {saida}")

    if args.lado_a_lado:
        lado = Image.new("RGB", (w * 3, h), "white")
        lado.paste(ref, (0, 0))
        lado.paste(cap, (w, 0))
        lado.paste(mapa, (w * 2, 0))
        s2 = cap_p.with_name(cap_p.stem + ".lado.png")
        lado.save(s2)
        print(f"Lado a lado (ref | site | diff): {s2}")


if __name__ == "__main__":
    main()
