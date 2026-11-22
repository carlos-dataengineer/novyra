# Biblioteca de modelos futuristas

O NOVYRA oferece três direções visuais reutilizáveis e uma direção original de marca. São modelos autorais de estudo, não cópias exatas dos sites usados como repertório.

| Modelo | Direção visual | Melhor uso | Template |
|---|---|---|---|
| `lusion-immersive-3d` | Editorial, objeto protagonista, palco escuro e motion narrativo. | Portfólio, estúdio, campanha ou produto imersivo. | `lusion-3d-immersive` |
| `takamo-cinematic-sci-fi` | Sci-fi cinematográfico, atmosfera espacial, ciano e narrativa de universo. | Entretenimento, jogos, ficção e catálogo narrativo. | `takamo-cinematic-sci-fi` |
| `databahn-futuristic-tech` | Tecnologia corporativa escura, azul profundo, ciano/teal e módulos de dados. | SaaS, IA, dados, cibersegurança e B2B. | `databahn-tech-product` |
| `novyra-future-lab` | Identidade original NOVYRA: obsidian, violeta elétrico e ciano. | Landing pages e projetos alinhados à marca. | Qualquer template + DS NOVYRA |

## Fluxo recomendado

1. Defina objetivo e público antes dos efeitos.
2. Separe referências de composição, tipografia, cor, movimento e conteúdo.
3. Gere ou revise o Design System antes de construir todas as seções.
4. Comece pela primeira dobra e valide hierarquia, leitura e CTA.
5. Construa o restante reutilizando tokens e componentes.
6. Revise mobile, acessibilidade, performance e movimento reduzido.

## Comandos previstos no pacote completo

```bash
python 02_scripts/novo_site.py portfolio-studio --template lusion-3d-immersive --ds lusion-immersive-3d
python 02_scripts/novo_site.py universo-sci-fi --template takamo-cinematic-sci-fi --ds takamo-cinematic-sci-fi
python 02_scripts/novo_site.py produto-ia --template databahn-tech-product --ds databahn-futuristic-tech
```

## Extração fiel e qualidade

Os modelos são conceituais. Para medir uma fonte real, use `/extrair-ds` em uma URL pública acessível e compare a captura com o site original. Não contorne autenticação ou bloqueios. Respeite `prefers-reduced-motion`, contraste, mobile e carregamento progressivo. WebGL/Three.js real é uma decisão técnica adicional; os exemplos HTML publicados usam CSS demonstrativo.
