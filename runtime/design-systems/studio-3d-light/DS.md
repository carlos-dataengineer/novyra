# Studio 3D Light

Estúdio criativo em página clara: um grande palco 3D emoldurado com cantos arredondados, tipografia grotesca enorme e fina, botões em pílula grafite e claros, marcadores “+” nas bordas da grade.

**Status:** modelo autoral NOVYRA. Os valores foram definidos para esta direção visual; nada foi copiado da referência (código, imagens, textos ou fontes comerciais).
**Repertório que inspirou a direção:** Lusion (lusion.co): página clara com palco 3D, pílulas e tipografia grotesca.
**Melhor uso:** Portfólio de estúdio, agência criativa, produto premium, lançamento com objeto 3D.
**Template recomendado:** `studio-3d-light`
**Catálogo vivo:** abra `design-system.html` nesta pasta.

## Fundamentos

| Papel | Token | Valor |
|---|---|---|
| Fundo | `--bg` | `#ffffff` |
| Superfície | `--surface` / `--surface-alt` | `#eef0f6` / `#e4e6ef` |
| Texto | `--text` | `#0b0c10` (contraste 19.55:1) |
| Texto secundário | `--text-muted` | `#4a4e5c` (contraste 8.28:1) |
| Ação principal | `--accent` | `#2b2e3a`, texto `#ffffff` (13.51:1) |
| Acento de apoio | `--accent-2` | `#1f3dff` |
| Títulos | `--font-title` | Inter Tight |
| Corpo | `--font-body` | Inter Tight |
| Mono | `--font-mono` | JetBrains Mono |
| Raios | `--radius-sm/md/lg` | 9 / 28 / 38 px |
| Movimento | `--dur-*`, `--ease` | [200, 450, 1000] ms, `cubic-bezier(0.19, 1, 0.22, 1)` (slow, weighted and cinematic) |

## Regras para a IA seguir

1. Use **só** as variáveis de `tokens.css`; nunca escreva cores ou tamanhos soltos.
2. O palco 3D é o protagonista: uma moldura grande com `--radius-lg`, fundo `--surface` e sombra `--shadow-lg`.
3. Títulos enormes e finos (peso 400) com espaçamento negativo; nunca negrito.
4. Botões sempre em pílula: `.btn` grafite (`--accent` = `#2b2e3a`) e `.btn2` claro.
5. Azul elétrico `--accent-2` só nos objetos 3D e em um detalhe por tela.
6. Respeite `prefers-reduced-motion` e mantenha contraste mínimo de 4.5:1 em texto corrido.
