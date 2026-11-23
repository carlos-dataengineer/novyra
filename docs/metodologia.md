# Metodologia: imagem → site em camadas

## Origem

O método vem de uma pesquisa sobre o conteúdo público da **Asimov Academy** (Vibe Design e a formação AI Designer): primeiro a linguagem visual, depois o código. O fluxo estudado tem 7 passos, e o NOVYRA cobre todos:

| Fluxo estudado | No NOVYRA |
|---|---|
| 1. Reunir imagens, prints, sites e referências | `imagem=` do `/criar-site`, `url=` do `/extrair-ds`, [referências visuais](referencias-visuais.md) |
| 2. Extrair ou definir o design system | `/extrair-ds`, `/combinar-ds` ou um dos 4 modelos prontos |
| 3. Briefing, wireframe e plano | etapa 1 (`/wireframe`) |
| 4. Fundo, atmosfera, estrutura, componentes e fontes | etapas 2 e 3 |
| 5. Inserir assets | etapa 4 |
| 6. Revisar, comparar, ajustar e validar | etapa 5 (`comparar.py`, `validar_site.py`) |
| 7. Exportar e publicar | a pasta do site já é o pacote final (HTML + CSS) |

Só material público foi usado; nenhuma aula fechada foi assistida ou reproduzida.

## Por que não pedir tudo de uma vez

Ao receber uma imagem pronta, um modelo precisa decidir ao mesmo tempo layout, textos, espaçamentos, componentes, cores, fontes, imagens e fundo. Os erros se misturam e o resultado varia a cada tentativa.

Este projeto separa essas decisões em camadas, de baixo para cima. Cada camada só começa quando a anterior foi aprovada, então um erro de fundo nunca contamina a tipografia, e vice-versa.

O ciclo de cada camada:

```text
construir ─► capturar ─► comparar com a referência ─► ajustar ─► mostrar ─► [aprovação]
     ▲                                                   │
     └───────────────────────────────────────────────────┘
```

## As 5 camadas

| # | Camada | Decide | Ferramentas |
|---|--------|--------|-------------|
| 1 | Wireframe + plano | o que existe na tela e com que técnica cada parte será feita | `/wireframe` |
| 2 | Fundo | cores base, gradientes, manchas, imagem de fundo | grade, conta-gotas, captura, comparação |
| 3 | Componentes + fontes | estrutura, superfícies, tipografia, espaçamento | recorte com zoom, conta-gotas, comparação por região |
| 4 | Assets | ícones, fotos, avatares | recortes, SVG, geração opcional |
| 5 | Revisão | integração e validação final | comparação geral, validador |

## O wireframe é o contrato

Cada região do wireframe vira uma classe CSS e cada tag tipada vira uma classe utilitária:

| No wireframe | No HTML/CSS |
|--------------|-------------|
| caixa `card` | `<article class="card">` + `.card { … }` |
| caixa `card2` | `.card2` (variação visual) |
| `[h1: Título]` | `<h1 class="h1">Título</h1>` |
| `[btn: Entrar]` | `<button class="btn">Entrar</button>` |
| `[lnk: Planos]` | `<a class="lnk">Planos</a>` |

Assim, mesmo id significa mesmo visual, e a revisão da estrutura (etapa 1) já fixa a organização do CSS.

## Medir em vez de chutar

| Pergunta | Script | Resposta |
|----------|--------|----------|
| Onde fica esse bloco? | `recortar.py --grade` | coordenadas na imagem |
| Qual é essa cor? | `amostrar_cores.py --pontos` | hex exato |
| Quais cores dominam aqui? | `amostrar_cores.py --paleta` | paleta com % |
| Como é esse gradiente? | `amostrar_cores.py --gradiente` | stops ao longo da diagonal |
| Que fonte é essa? | `recortar.py --zoom 3` | recorte ampliado para comparar |
| Ficou igual? | `capturar_tela.py` + `comparar.py` | nota %, mapa de calor e as 5 piores regiões |
| Segue as regras? | `validar_site.py` | erros e avisos |

## Escolha de técnica

| Elemento | Técnica |
|----------|---------|
| Cor sólida, gradiente, borda, sombra, forma simples | CSS |
| Foto, ilustração, textura, 3D | imagem (recorte ou geração) |
| Composição que precisa de ajustes independentes | camadas separadas |
| Texto e controles | sempre HTML real |

## Como ler a nota de semelhança

O `comparar.py` aplica um leve desfoque (para não punir a suavização do texto) e conta os pixels que diferem mais que a tolerância.

| Nota | Leitura |
|------|---------|
| ≥ 95% | praticamente idêntico |
| 85–95% | bom; diferenças em detalhes (ícones, fontes aproximadas) |
| < 85% | há uma região com problema: olhe as "piores regiões" e o `.diff.png` |

Na etapa 2 a nota é naturalmente baixa, porque o conteúdo ainda não existe. Use `--caixa` para avaliar só a parte que está sendo trabalhada.
