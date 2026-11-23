# Biblioteca de modelos futuristas

O NOVYRA oferece seis direções visuais reutilizáveis e uma direção original de marca, mapeadas a partir de 8 referências reais (veja o [catálogo](referencias-visuais.md)). São modelos autorais; nenhum é extraído de um site.

| Modelo | Direção visual | Melhor uso | Template |
|---|---|---|---|
| `immersive-3d` | Editorial, objeto protagonista, palco escuro e motion narrativo. | Portfólio, estúdio, campanha ou produto imersivo. | `immersive-3d-studio` |
| `cinematic-sci-fi` | Sci-fi cinematográfico, atmosfera espacial, ciano e narrativa de universo. | Entretenimento, jogos, ficção e catálogo narrativo. | `cinematic-sci-fi` |
| `futuristic-tech` | Tecnologia corporativa escura, azul profundo, ciano/teal e módulos de dados. | SaaS, IA, dados, cibersegurança e B2B. | `tech-product` |
| `novyra-future-lab` | Identidade original NOVYRA: obsidian, violeta elétrico e ciano. | Landing pages e projetos alinhados à marca. | Qualquer template + DS NOVYRA |
| `studio-3d-light` | Estúdio em página clara: palco 3D emoldurado, grotesca fina e enorme, pílulas grafite. (repertório: Lusion) | Estúdio criativo, agência, produto premium. | `studio-3d-light` |
| `retro-glitch` | Internet antiga com glitch: janelas chanfradas, verde neon, magenta, sombras duras, pixel. (repertório: GLIX Studio) | Moda, música, estúdio experimental, jogos indie. | `retro-glitch` |
| `bio-data-mono` | Natureza como dados: preto monocromático, grade, mira, módulos numerados. (repertório: Nature Beyond Technology) | Ciência, clima, deep tech, storytelling de dados. | `bio-data-mono` |

## Nomes antigos (v0.1.x)

Na v0.2.0 os modelos ganharam nomes neutros, sem marcas de terceiros. Os nomes antigos continuam funcionando como apelidos em `ds=` e `template=`:

| Nome antigo | Nome atual | Repertório que inspirou a direção |
|---|---|---|
| `lusion-immersive-3d` | `immersive-3d` | Interpretação escura de objeto protagonista e 3D. A direção fiel à Lusion (página clara) agora é o `studio-3d-light`. |
| `takamo-cinematic-sci-fi` | `cinematic-sci-fi` | Galeria DesignRush Futuristic |
| `databahn-futuristic-tech` | `futuristic-tech` | Galerias DesignRush AI e Technology |
| `lusion-3d-immersive` (template) | `immersive-3d-studio` | Lusion |
| `takamo-cinematic-sci-fi` (template) | `cinematic-sci-fi` | DesignRush Futuristic |
| `databahn-tech-product` (template) | `tech-product` | DesignRush AI e Technology |

## Fluxo recomendado

1. Defina objetivo e público antes dos efeitos.
2. Separe referências de composição, tipografia, cor, movimento e conteúdo.
3. Gere ou revise o Design System antes de construir todas as seções.
4. Comece pela primeira dobra e valide hierarquia, leitura e CTA.
5. Construa o restante reutilizando tokens e componentes.
6. Revise mobile, acessibilidade, performance e movimento reduzido.

## Comandos

```text
/criar-site brief="Portfólio de estúdio 3D" slug=portfolio-studio template=immersive-3d-studio ds=immersive-3d
```

Ou direto pelo script:

```bash
python -X utf8 ~/Novyra/scripts/novo_site.py portfolio-studio --template immersive-3d-studio --ds immersive-3d
python -X utf8 ~/Novyra/scripts/novo_site.py universo-sci-fi --template cinematic-sci-fi --ds cinematic-sci-fi
python -X utf8 ~/Novyra/scripts/novo_site.py produto-ia --template tech-product --ds futuristic-tech
```

## Extração fiel e qualidade

Os modelos são conceituais. Para medir uma fonte real, use `/extrair-ds` em uma URL pública acessível e compare a captura com o site original. Não contorne autenticação ou bloqueios. Respeite `prefers-reduced-motion`, contraste, mobile e carregamento progressivo. WebGL/Three.js real é uma decisão técnica adicional; os exemplos HTML publicados usam CSS demonstrativo.
