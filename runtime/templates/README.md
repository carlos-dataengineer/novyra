# Templates

Pontos de partida do `/criar-site` (`template=<slug>`). Abra qualquer `index.html` direto no navegador.

| Template | Perfil | Design system que combina |
|---|---|---|
| `site-base` | Base limpa com `styles.css` organizado em camadas. É o padrão para recriar um mock pixel a pixel. | qualquer um |
| `immersive-3d-studio` | Portfólio/landing com objeto protagonista, palco escuro e narrativa. | `immersive-3d` |
| `cinematic-sci-fi` | Universo sci-fi, atmosfera espacial e conteúdo editorial. | `cinematic-sci-fi` |
| `tech-product` | Produto B2B de IA/tecnologia com dados e módulos claros. | `futuristic-tech`, `novyra-future-lab` |
| `studio-3d-light` | Estúdio em página clara com palco 3D emoldurado e pílulas. | `studio-3d-light` |
| `retro-glitch` | Janelas de sistema antigo, glitch, verde neon e sombras duras. | `retro-glitch` |
| `bio-data-mono` | Natureza como dados: preto, grade, mira e módulos na rolagem. | `bio-data-mono` |

Os temáticos são arquivos únicos (CSS dentro do HTML). Com `ds=`, o `novo_site.py` liga `tokens.css` e `componentes.css` do design system; na etapa 3 o agente troca as variáveis próprias do template pelas do DS.

Os elementos 3D são representações em CSS, não cenas WebGL. Todos são autorais: nenhum usa logos, imagens ou código de terceiros.

Para criar o seu: copie uma pasta, renomeie em kebab-case e mantenha um `index.html`. O instalador nunca apaga templates que você criou.
