# Design systems

| Slug | Direção visual | Títulos / corpo |
|---|---|---|
| `novyra-future-lab` | Identidade original NOVYRA: obsidian, violeta elétrico e ciano. | Space Grotesk / Inter |
| `immersive-3d` | Experiência editorial com objeto protagonista e movimento narrativo. | Space Grotesk / Inter |
| `cinematic-sci-fi` | Sci-fi cinematográfico, ciano, títulos condensados em caixa alta. | Bebas Neue / Exo 2 |
| `futuristic-tech` | Tecnologia B2B escura, azul profundo e teal. | Manrope / Inter |
| `studio-3d-light` | Estúdio em página clara, palco 3D, pílulas grafite. | Inter Tight |
| `retro-glitch` | Internet antiga, glitch, verde neon e magenta. | VT323 / IBM Plex Mono |
| `bio-data-mono` | Preto monocromático, grade e módulos de dados. | Inter / JetBrains Mono |

Cada pasta tem `tokens.json` (fonte da verdade), `tokens.css`, `assets/componentes.css`, o catálogo vivo `design-system.html` e as regras para a IA em `DS.md`. Todos são autorais: os valores foram definidos para cada direção, não extraídos de sites.

Para criar os seus: `/extrair-ds url=<página pública> slug=<nome>` ou `/combinar-ds nome=<novo> base=<a> cores=<b> ...`. Eles ficam em `~/Novyra/design-systems/` e o instalador nunca os apaga. A pasta `fonte/` de um DS extraído tem prints e CSS do site de origem: é só para você, não publique.
