"""Recombina design systems já extraídos num novo (etapa B, passo 'recombinar').

Cada grupo de tokens vem de um design system de origem; o que não for indicado vem da --base.
Grupos: cores (inclui paleta e anel de foco), tipografia, formas (raios, sombras, espaços),
movimento, fundos (gradientes e vidro).

Saída: design-systems/<nome>/tokens.json + tokens.css (sem pasta fonte/; a origem de
cada grupo fica registrada). Depois rode gerar_ds_html.py <nome>.

Exemplo:
    python combinar_ds.py --nome meu-ds --base linear --tipografia stripe --movimento vercel
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date

from _comum import DESIGN_SYSTEMS, erro, resolver
from extrair_tokens import contraste, gerar_css

GRUPOS = {
    "cores": ("cores", "paleta", "anel_foco"),
    "tipografia": ("tipografia",),
    "formas": ("formas",),
    "movimento": ("movimento",),
    "fundos": ("fundos",),
}


def rgb(hx: str):
    if hx.startswith("#"):
        return [int(hx[i:i + 2], 16) for i in (1, 3, 5)] + [1]
    nums = hx[hx.index("(") + 1:hx.index(")")].split(",")
    return [int(float(n)) for n in nums[:3]] + [float(nums[3]) if len(nums) > 3 else 1]


def main() -> None:
    p = argparse.ArgumentParser(description="Combina grupos de tokens de vários design systems")
    p.add_argument("--nome", required=True, help="slug do novo design system")
    p.add_argument("--base", required=True, help="design system que fornece tudo o que não for indicado")
    for g in GRUPOS:
        p.add_argument(f"--{g}", help=f"design system de onde vem o grupo '{g}'")
    p.add_argument("--substituir", action="store_true")
    args = p.parse_args()
    for k in ("base", "cores", "tipografia", "formas", "movimento", "fundos"):
        if hasattr(args, k):
            setattr(args, k, resolver(getattr(args, k)))

    origem = {g: getattr(args, g) or args.base for g in GRUPOS}
    tokens_por_ds = {}
    for slug in set(origem.values()):
        arq = DESIGN_SYSTEMS / slug / "tokens.json"
        if not arq.exists():
            erro(f"design system '{slug}' não tem tokens.json (rode extrair_tokens.py {slug})")
        tokens_por_ds[slug] = json.loads(arq.read_text(encoding="utf-8"))

    destino = DESIGN_SYSTEMS / args.nome
    if destino.exists():
        if not args.substituir:
            erro(f"já existe {destino}. Use --substituir para refazer.")
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    novo = {"origem": {"url": "combinação", "titulo": args.nome, "extraido_em": date.today().isoformat(),
                       "combinado_de": origem}}
    for grupo, chaves in GRUPOS.items():
        fonte = tokens_por_ds[origem[grupo]]
        for k in chaves:
            if k in fonte:
                novo[k] = fonte[k]
    novo["estados"] = tokens_por_ds[origem["cores"]].get("estados", {})
    novo["variaveis_originais"] = {}

    (destino / "tokens.json").write_text(json.dumps(novo, ensure_ascii=False, indent=2), encoding="utf-8")
    (destino / "tokens.css").write_text(gerar_css(novo), encoding="utf-8")

    print(f"Design system combinado em: {destino}")
    for g, s in origem.items():
        print(f"  {g:<11} ← {s}")
    c = novo["cores"]
    for par in (("text", "bg"), ("text-muted", "bg"), ("on-accent", "accent")):
        v = contraste(rgb(c[par[0]]), rgb(c[par[1]]))
        if v < 4.5:
            print(f"  ATENÇÃO: contraste {par[0]}/{par[1]} = {v} (< 4.5)")
    print(f"Próximo passo: python gerar_ds_html.py {args.nome}")


if __name__ == "__main__":
    main()
