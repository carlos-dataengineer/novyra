# Arquitetura

O NOVYRA tem três partes: **skills** (o que o agente sabe fazer), **runtime** (os scripts que medem e geram) e a **ferramenta** (o painel NOVYRA Studio). Tudo roda no computador de quem usa; não há servidor.

```text
            repositório                              computador de quem instala
┌──────────────────────────────────┐  install   ┌───────────────────────────────────────┐
│ skills/<nome>/SKILL.md           │ ─────────► │ ~/.claude/skills/<nome>  (Claude Code)│
│ skills/<nome>/agents/openai.yaml │ {{RAIZ}} → │ ~/.codex/skills/<nome>   (Codex)      │
│                                  │  ~/Novyra  │ ~/.agents/skills/<nome>  (compart.)   │
│ runtime/scripts/*.py             │ ─────────► │ ~/Novyra/scripts                      │
│ runtime/templates/<slug>/        │            │ ~/Novyra/templates                    │
│ runtime/design-systems/<slug>/   │            │ ~/Novyra/design-systems               │
│                                  │            │ ~/Novyra/sites/<slug>/  (seus sites)  │
│ runtime/scripts/gerar_painel.py  │ ─ gera ──► │ ~/Novyra/novyra.html (NOVYRA Studio)  │
└──────────────────────────────────┘            └───────────────────────────────────────┘
```

## As três camadas

| Camada | O que é | No NOVYRA hoje |
|---|---|---|
| **A. Repertório** | Pesquisa, modelos, design systems e tokens | `runtime/design-systems`, `runtime/templates`, [biblioteca de modelos](biblioteca-modelos-futuristas.md), [referências](referencias-visuais.md) |
| **B. Interface** | Onde a pessoa escolhe, acompanha e revisa | NOVYRA Studio (`novyra.html`); o app Future Lab 0.2.1 (editor visual das etapas) ainda não está neste repositório |
| **C. Motor** | Quem analisa a imagem, planeja, constrói, mede e valida | Claude Code ou Codex executando as skills e os scripts reais (`capturar_tela.py`, `comparar.py`, `validar_site.py`…) |

A camada C não é um backend próprio: é o agente que você já usa. Cada aprovação no chat faz o agente executar a etapa seguinte com os scripts, e o `ESTADO.md` guarda as decisões e o progresso.

## Skills

| Skill | Papel | Invocação |
|---|---|---|
| `novyra` | Atualiza e abre o painel; no Claude publica como artefato | `/novyra` · `$novyra` (o agente também pode chamar sozinho) |
| `criar-site` | Orquestra as 5 etapas com aprovação | `/criar-site` · `$criar-site` (só quando você chama) |
| `wireframe` | Planta tipada (ASCII/SVG); etapa 1 do criar-site | `/wireframe` · `$wireframe` |
| `extrair-ds` | Captura uma URL pública e gera tokens, componentes e catálogo | `/extrair-ds` · `$extrair-ds` |
| `combinar-ds` | Recombina grupos de tokens de vários design systems | `/combinar-ds` · `$combinar-ds` |

As skills que alteram arquivos têm `disable-model-invocation: true` (Claude) e `allow_implicit_invocation: false` (Codex): só rodam quando você pede.

## Runtime

| Script | Entrada → saída |
|---|---|
| `novo_site.py` | slug, imagem, template, DS → `sites/<slug>/` com `ESTADO.md` |
| `recortar.py` | imagem → grade de coordenadas, recortes e zoom |
| `amostrar_cores.py` | imagem + pontos/caixa → hex, paleta, gradiente |
| `capturar_tela.py` | pasta do site → PNG no tamanho da referência (Chrome headless) |
| `comparar.py` | referência + captura → lado a lado, mapa de diferenças, nota % |
| `validar_site.py` | pasta do site → erros e avisos (assets, caminhos, inline, CDNs) |
| `capturar_site.py` | URL → DOM e estilos calculados (Playwright + Chrome) |
| `extrair_tokens.py` | captura → `tokens.json` + `tokens.css` |
| `gerar_ds_html.py` | tokens → `design-system.html` + `componentes.css` |
| `combinar_ds.py` | vários DS → um novo |
| `gerar_painel.py` | runtime → `novyra.html` (ou `novyra-artefato.html`) |
| `gerar_imagem.py` | opcional e pago (OpenRouter) → ícones e imagens |

Todos usam `_comum.py` para achar as pastas: `RAIZ` é a pasta do runtime; `SITES` pode ser trocada com `NOVYRA_SITES`.

## Formato de um design system

```text
design-systems/<slug>/
├── tokens.json              fonte da verdade (cores, paleta, tipografia, formas, movimento, fundos)
├── tokens.css               :root com as variáveis
├── assets/componentes.css   .btn .btn2 .lnk .card .nav .in .selo .h1…t3, só com tokens
├── design-system.html       catálogo vivo para revisar e comparar
├── DS.md                    regras e intenções para a IA
└── fonte/                   (só em DS extraídos; nunca vai para o git)
```

## Formato de um site

```text
sites/<slug>/
├── index.html           HTML semântico, sem CSS/JS inline
├── assets/styles.css    tokens → reset → fundo → layout → regiões → tags tipadas
├── assets/crops/        recortes da referência usados no site
├── reference.png        a imagem de entrada (não publique se for confidencial)
├── wireframe.txt        o contrato da etapa 1
├── ESTADO.md            etapas, aprovações e decisões
└── _capturas/           capturas e comparações de cada etapa
```

## Instalador

`install.sh` e `install.ps1` só baixam o pacote (ou usam o clone) e acham um Python 3.10+. Toda a lógica está em [`scripts/install_novyra.py`](../scripts/install_novyra.py), testada em [`tests/test_install.py`](../tests/test_install.py):

- marca cada skill instalada com um arquivo `.novyra` e **nunca** substitui uma skill sem essa marca (a não ser com `--force`);
- ao atualizar, troca só `scripts/` e os templates e design systems do pacote; `sites/` e o que você criou ficam;
- ao desinstalar, remove só o que instalou.
