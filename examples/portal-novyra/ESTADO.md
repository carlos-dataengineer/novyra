# Estado do site: portal-novyra

Criado em: 2026-11-23
Entrada: imagem `reference.jpg` (arte 736x1308 enviada pelo autor para a demo do README)

| Etapa | Status | Observação |
|-------|--------|------------|
| 1. Wireframe + plano | feito | arte vira fundo do hero; interface na paleta medida |
| 2. Fundo completo | feito | 100% de semelhança com a arte em 736x1308; no desktop a arte vai para a metade direita |
| 3. Estrutura, componentes e fontes | feito | nav, hero "Create Beyond Limits", método, camadas A/B/C, modelos, instalar, rodapé com créditos; identidade NOVYRA; sem estouro em 390 px |
| 4. Assets restantes | feito | pulada: a referência não tem ícones nem fotos além da arte |
| 5. Revisão final | feito | 736x1308: 91,4% na página inteira, 100% na região da arte; validar_site OK |

## Decisões e aproximações
- A referência é uma arte (não uma tela de interface). Ela é usada como fundo do hero (assets/crops/vortex.jpg).
- Paleta medida com amostrar_cores.py: fundo #010103/#04050c/#0f1225, índigo #2d355d/#434b7a/#7b81af, anel #fbfbf8, estrela #fef9e2.
- Fontes: Space Grotesk (títulos) e Inter (corpo), as mesmas da marca NOVYRA.
- Medição: no tamanho da referência (736x1308) o fundo é comparado com a arte; o conteúdo é avaliado por região.

| Região | Etapa | Técnica |
|---|---|---|
| Fundo da página | 2 | cor #02030a + vórtice como imagem de fundo (cover, foco no buraco negro) |
| Fade da arte para o conteúdo | 2 | gradientes CSS na paleta medida |
| Nav, hero, etapas, agentes, instalar, rodapé | 3 | HTML/CSS; Space Grotesk 600 / Inter 400 |
| Ícones | 4 | pulada: não há ícones na referência |
| Página inteira | 5 | captura 736x1308 + 1440x900 + 390 px, comparação e validação |
