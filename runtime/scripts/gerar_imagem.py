"""(Opcional) Gera ou recria imagens pela Image API do OpenRouter. Serviço PAGO.

Gera imagens via OpenRouter usando só a biblioteca padrão do Python (opcional e pago).
Chave: OPENROUTER_API_KEY no .env da raiz do projeto ou em ~/.env (nunca commitar o .env).
Segurança: o prompt e a imagem de entrada saem do computador. Exige --confirmo-envio.

Exemplos:
    python gerar_imagem.py --prompt "Recreate this UI icon exactly. Transparent background." ^
        --entrada assets/crops/ico-logo.png --saida assets/ico-logo.png --modelo gpt2 --proporcao 1:1 --confirmo-envio
    python gerar_imagem.py --prompt "Dashboard escuro com cards de vendas" --saida mocks/painel.png --confirmo-envio
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from pathlib import Path

from _comum import carregar_env, erro

API = "https://openrouter.ai/api/v1/images"
APELIDOS = {
    "pro": "google/gemini-3-pro-image",
    "flash": "google/gemini-3.1-flash-image",
    "gpt2": "openai/gpt-image-2",
    "flux": "black-forest-labs/flux.2-pro",
    "flux-max": "black-forest-labs/flux.2-max",
    "seedream": "bytedance-seed/seedream-5-0-lite",
    "qwen": "qwen/qwen-image-3-pro",
}


def main() -> None:
    p = argparse.ArgumentParser(description="Geração de imagem via OpenRouter (pago)")
    p.add_argument("--prompt", required=True)
    p.add_argument("--saida", required=True)
    p.add_argument("--entrada", help="imagem de referência (recorte) para recriar/editar")
    p.add_argument("--modelo", default="gpt2", help="apelido (" + ", ".join(APELIDOS) + ") ou slug")
    p.add_argument("--resolucao", default="1K")
    p.add_argument("--proporcao", default="1:1")
    p.add_argument("--confirmo-envio", action="store_true",
                   help="confirma que a imagem/prompt pode sair da empresa para o OpenRouter")
    args = p.parse_args()

    if not args.confirmo_envio:
        erro("este comando envia o prompt" + (" e a imagem de entrada" if args.entrada else "")
             + " para o OpenRouter (serviço externo e pago).\n"
             "Não use com telas, dados ou nomes internos da empresa.\n"
             "Se o conteúdo pode sair, rode de novo com --confirmo-envio.")

    carregar_env()
    chave = os.environ.get("OPENROUTER_API_KEY")
    if not chave:
        erro("defina OPENROUTER_API_KEY no .env da raiz do projeto ou em ~/.env")

    corpo = {"model": APELIDOS.get(args.modelo, args.modelo), "prompt": args.prompt, "n": 1,
             "resolution": args.resolucao, "aspect_ratio": args.proporcao}
    if args.entrada:
        f = Path(args.entrada)
        if not f.exists():
            erro(f"entrada não encontrada: {f}")
        mime = mimetypes.guess_type(f.name)[0] or "image/png"
        url = f"data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"
        corpo["input_references"] = [{"type": "image_url", "image_url": {"url": url}}]

    req = urllib.request.Request(
        API, data=json.dumps(corpo).encode(), method="POST",
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json",
                 "X-Title": "criador-de-sites"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            dados = json.loads(r.read())
    except urllib.error.HTTPError as e:
        erro(f"OpenRouter HTTP {e.code}: {e.read()[:600].decode(errors='replace')}")
    itens = dados.get("data") or []
    if not itens or not itens[0].get("b64_json"):
        erro(f"resposta sem imagem: {json.dumps(dados)[:400]}")
    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_bytes(base64.b64decode(itens[0]["b64_json"]))
    print(f"Imagem salva em: {saida.resolve()}")
    custo = (dados.get("usage") or {}).get("cost")
    if custo is not None:
        print(f"Custo: US$ {custo}")


if __name__ == "__main__":
    main()
