# Referências visuais futuristas — NOVYRA

**Atualizada em:** 22/11/2026. Esta biblioteca organiza fontes públicas de repertório e padrões visuais para estudo. Os exemplos e modelos do NOVYRA são autorais; não copiam código, imagens, logos, textos ou assets de terceiros.

## Fontes de repertório

| Fonte | O que observar | Como usar no NOVYRA |
|---|---|---|
| [Lusion](https://lusion.co/) | Direção visual, storytelling, motion, 3D e desenvolvimento interativo. | Portfólios, campanhas e experiências com um protagonista visual. |
| [Lusion — Projects](https://lusion.co/projects/) | Projetos de web, design, desenvolvimento, 3D, WebGL e animação. | Estudar ritmo, composição e apresentação de projetos. |
| [DesignRush — Futuristic](https://www.designrush.com/best-designs/websites/futuristic) | Galeria de sites classificados como futuristas. | Descoberta de referências; não é um template único. |
| [DesignRush — AI](https://www.designrush.com/best-designs/websites/ai) | Sites de produtos de IA e tecnologia. | Observar demonstrações, benefícios e prova de valor. |
| [DesignRush — Technology](https://www.designrush.com/best-designs/websites/technology) | Sites de tecnologia com composições e densidades diferentes. | Comparar hierarquia, módulos e chamadas para ação. |
| [DesignRush — Interactive](https://www.designrush.com/best-designs/websites/interactive) | Projetos interativos, experimentais, 3D, motion e parallax. | Buscar padrões de interação e movimento. |

## Catálogo: 8 referências → modelos NOVYRA

Levantado em 23/11/2026 na [Lusion](https://lusion.co/) e na galeria [DesignRush Futuristic](https://www.designrush.com/best-designs/websites/futuristic) (7 designs). As observações são do NOVYRA; nada dos sites é redistribuído. O mesmo catálogo está em `runtime/referencias/futuristas.json` e na aba **Referências** do NOVYRA Studio, com o comando pronto de cada uma.

| Referência | Autoria | Categoria | Padrões observados | Modelo / template NOVYRA |
|---|---|---|---|---|
| [Lusion](https://lusion.co/) | Lusion (Bristol, Reino Unido) | Estúdio criativo | página clara, fundo branco; palco 3D emoldurado com cantos grandes; tipografia grotesca grande e fina; botões em pílula grafite e claros; marcadores + nas bordas; loader com contador | `studio-3d-light` / `studio-3d-light` |
| [Takamo Universe](https://visuable.co/case-study/takamo-universe) | Visuable (Londres) | Entretenimento | tela preta com naves pintadas; um único acento ciano elétrico; títulos Bebas Neue e rótulos Exo espaçados; campos de estrelas e nebulosas em loop; grade de facções do universo | `cinematic-sci-fi` / `cinematic-sci-fi` |
| [DataBahn](https://www.databahn.ai/) | Flowtrix (Bengaluru) | IA / B2B | azuis profundos e pretos; ciano e teal como acento; cards modulares para informação densa; brilhos e gráficos radiais de fluxo de dados | `futuristic-tech` / `tech-product` |
| [Nature Beyond Technology](https://nature-beyond.tech/) | Ronce Bleue (Lyon) | Ciência / storytelling de dados | fundo preto monocromático; árvore em partículas e wireframe; grade de precisão e colchetes de mira; módulos revelados na rolagem (00/07) | `bio-data-mono` / `bio-data-mono` |
| [GLIX Studio](https://glix.studio/) | Nockta | Moda / experimental | glitch art e interface retrô de sistema antigo; verde neon e sombras duras; tipografia pixelada; navegação fragmentada de propósito | `retro-glitch` / `retro-glitch` | Em nov/2026 o endereço redireciona para a loja da marca; o design premiado pode não estar mais no ar.
| [Moulds & More](https://www.designrush.com/best-designs/websites/moulds-and-more-website-design) | WD Strategies | Engenharia | interface escura inspirada em carros esportivos; produto no centro; molduras retangulares coloridas separando conteúdo | `futuristic-tech` / `tech-product` | A galeria não informa o endereço do site.
| [Bear Classes](https://www.designrush.com/best-designs/websites/bear-classes-website-design) | URich | Educação | gradientes azuis digitais; blocos 3D vetoriais; tipografia branca com toques de vermelho | `immersive-3d` / `immersive-3d-studio` | A galeria não informa o endereço do site.
| [Alex Gurghis](https://www.designrush.com/best-designs/websites/alex-gurghis-website-design) | Alex Gurghis | Portfólio | tema escuro de carro de luxo; rolagem horizontal e vertical combinadas; estudos de caso em tela cheia | `immersive-3d` / `immersive-3d-studio` | A galeria não informa o endereço do site.

### Três ações para cada referência

1. **Estudar:** abra o site e a ficha da galeria.
2. **Medir:** `/extrair-ds url=<site> slug=ref-<nome>`. Gera tokens, componentes e catálogo **no seu computador** (a pasta `fonte/` com prints nunca é publicada).
3. **Criar na direção, sem copiar:** `/criar-site brief="..." ds=<modelo> template=<template>`, usando o modelo autoral NOVYRA da tabela.

## Padrões para estudar

### Experiência 3D e storytelling → template `immersive-3d-studio`
- Um objeto ou cena principal conduz a narrativa.
- Movimento acompanha a história e não compete com o conteúdo.
- Navegação, mensagem e próximo passo continuam claros.
- WebGL/Three.js exige otimização, fallback e testes de performance.

### Sci-fi cinematográfico → template `cinematic-sci-fi`
- Fundo escuro, contraste alto e uma cor de acento controlada.
- Tipografia display para títulos e tipografia funcional para leitura.
- Profundidade com gradientes, luz e camadas.
- A arte reforça a arquitetura de informação, não a substitui.

### Tecnologia e IA → template `tech-product`
- Azul profundo, preto, ciano ou teal usados com moderação.
- Demonstrações e diagramas tornam a proposta concreta.
- Cards e gráficos precisam de hierarquia.
- Benefícios e CTAs devem continuar fáceis de entender.

## Processo de captura

1. Abra a fonte original e observe primeira dobra, navegação, seções, interação e comportamento mobile.
2. Separe observações da fonte de decisões autorais do NOVYRA.
3. Quando a página estiver acessível, use `/extrair-ds` para capturar DOM e estilos calculados.
4. Revise manualmente os tokens: inferências não são medições certificadas.
5. Use `/combinar-ds` para compor uma identidade coerente.
6. Teste contraste, acessibilidade, movimento reduzido, mobile e performance.

## Direitos e limites

Esta biblioteca não redistribui imagens, logos, fontes comerciais, modelos 3D ou código das fontes. Os modelos NOVYRA são conceituais e autorais. Não contorne login, captcha ou bloqueios. Confirme licença e autorização antes de usar assets de terceiros em produção.

## Relação com a pesquisa da Asimov Academy

A pesquisa sobre o conteúdo público da Asimov Academy deu o **método** (repertório → design system → wireframe → construção em camadas → revisão). Esta biblioteca dá o **repertório visual** para praticar o método. As duas origens ficam registradas no [NOTICE](../NOTICE).

## Referências em estudo

- **Pinterest** (https://br.pinterest.com/pin/946670784197253520/): céu estrelado com a Via Láctea, montanhas nevadas e pegadas rumo ao horizonte. Direção "jornada cósmica / exploração / portal para o desconhecido" para o NOVYRA Future Lab. A imagem não faz parte do repositório.
- **Arte do vórtice** enviada pelo autor: usada na demonstração [`examples/portal-novyra`](../examples/portal-novyra) com a mesma direção de portal.

