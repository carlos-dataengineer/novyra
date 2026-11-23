# Bio Data Mono

Natureza vista como sistema de dados: fundo preto, tudo em monocromático azul-acinzentado, linhas finas de grade, colchetes de mira nos cantos, contador de módulos (00/07) e partículas.

**Status:** modelo autoral NOVYRA. Os valores foram definidos para esta direção visual; nada foi copiado da referência (código, imagens, textos ou fontes comerciais).
**Repertório que inspirou a direção:** Nature Beyond Technology na galeria DesignRush Futuristic (monocromático, partículas, grade de precisão).
**Melhor uso:** Ciência, clima, sustentabilidade, deep tech, relatórios e storytelling de dados.
**Template recomendado:** `bio-data-mono`
**Catálogo vivo:** abra `design-system.html` nesta pasta.

## Fundamentos

| Papel | Token | Valor |
|---|---|---|
| Fundo | `--bg` | `#000000` |
| Superfície | `--surface` / `--surface-alt` | `#0b0c0e` / `#15171a` |
| Texto | `--text` | `#dfe3ea` (contraste 16.31:1) |
| Texto secundário | `--text-muted` | `#8a9099` (contraste 6.53:1) |
| Ação principal | `--accent` | `#dfe3ea`, texto `#05070c` (15.65:1) |
| Acento de apoio | `--accent-2` | `#9fb4c8` |
| Títulos | `--font-title` | Inter |
| Corpo | `--font-body` | Inter |
| Mono | `--font-mono` | JetBrains Mono |
| Raios | `--radius-sm/md/lg` | 4 / 2 / 12 px |
| Movimento | `--dur-*`, `--ease` | [240, 600, 1400] ms, `cubic-bezier(0.25, 1, 0.5, 1)` (scroll-driven, slow and precise) |

## Regras para a IA seguir

1. Use **só** as variáveis de `tokens.css`; nunca escreva cores ou tamanhos soltos.
2. Uma só cor de texto (`--text`) e uma de apoio (`--text-muted`); sem cores de destaque saturadas.
3. Estrutura em linhas de 1 px (`--border`) e colchetes de canto; nada de cards preenchidos.
4. Conteúdo em módulos numerados (00/07, 01/07…), revelados um por vez na rolagem.
5. Títulos leves (peso 300); números e rótulos em mono.
6. Respeite `prefers-reduced-motion` e mantenha contraste mínimo de 4.5:1 em texto corrido.
