# Cinematic Sci-Fi

Atmosfera sci-fi cinematográfica: fundo espacial, acento ciano, títulos condensados em caixa alta e hierarquia editorial.

**Status:** modelo autoral NOVYRA. Não é extração de nenhum site; os valores foram definidos para esta direção visual.
**Melhor uso:** Entretenimento, jogos, ficção, eventos e catálogos narrativos.
**Template recomendado:** `cinematic-sci-fi`
**Catálogo vivo:** abra `design-system.html` nesta pasta.

## Fundamentos

| Papel | Token | Valor |
|---|---|---|
| Fundo | `--bg` | `#05070c` |
| Superfície | `--surface` / `--surface-alt` | `#101722` / `#172432` |
| Texto | `--text` | `#f5f8fc` (contraste 18.92:1) |
| Texto secundário | `--text-muted` | `#98a7b8` (contraste 8.21:1) |
| Ação principal | `--accent` | `#20d9f5`, texto `#05070c` (11.81:1) |
| Acento de apoio | `--accent-2` | `#8ceeff` |
| Títulos | `--font-title` | Bebas Neue |
| Corpo | `--font-body` | Exo 2 |
| Raios | `--radius-sm/md/lg` | 4 / 12 / 22 px |
| Movimento | `--dur-*`, `--ease` | [180, 360, 800] ms, `cubic-bezier(0.65, 0, 0.35, 1)` (atmospheric and restrained) |

## Regras para a IA seguir

1. Use **só** as variáveis de `tokens.css`; nunca escreva cores ou tamanhos soltos.
2. `--accent` é para a ação principal e para no máximo um destaque por seção. `--accent-2` só em detalhes (linhas, brilhos, ícones).
3. Títulos com `.h1/.h2/.h3`, textos com `.t1/.t2/.t3`, botões com `.btn` (principal) e `.btn2` (secundário).
4. Profundidade vem dos gradientes de fundo (`.grad-*` no catálogo) e das sombras `--shadow-md/lg`, não de bordas grossas.
5. Respeite `prefers-reduced-motion`: anime só opacidade e transform, com `--dur-*` e `--ease`.
6. Mantenha contraste mínimo de 4.5:1 em texto corrido; confira no catálogo.
