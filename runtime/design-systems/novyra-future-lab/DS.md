# NOVYRA Future Lab

Identidade original do NOVYRA: obsidian profundo, violeta elétrico e ciano, superfícies imersivas e brilho controlado.

**Status:** modelo autoral NOVYRA. Não é extração de nenhum site; os valores foram definidos para esta direção visual.
**Melhor uso:** Landing pages de produto, lançamentos e páginas de IA.
**Template recomendado:** `tech-product ou immersive-3d-studio`
**Catálogo vivo:** abra `design-system.html` nesta pasta.

## Fundamentos

| Papel | Token | Valor |
|---|---|---|
| Fundo | `--bg` | `#080b16` |
| Superfície | `--surface` / `--surface-alt` | `#11172a` / `#1a2340` |
| Texto | `--text` | `#e5e7f0` (contraste 15.91:1) |
| Texto secundário | `--text-muted` | `#a7b0c4` (contraste 9.02:1) |
| Ação principal | `--accent` | `#8757ff`, texto `#05070c` (4.64:1) |
| Acento de apoio | `--accent-2` | `#20d9f5` |
| Títulos | `--font-title` | Space Grotesk |
| Corpo | `--font-body` | Inter |
| Raios | `--radius-sm/md/lg` | 6 / 18 / 28 px |
| Movimento | `--dur-*`, `--ease` | [120, 220, 480] ms, `cubic-bezier(0.22, 1, 0.36, 1)` (precise and responsive) |

## Regras para a IA seguir

1. Use **só** as variáveis de `tokens.css`; nunca escreva cores ou tamanhos soltos.
2. `--accent` é para a ação principal e para no máximo um destaque por seção. `--accent-2` só em detalhes (linhas, brilhos, ícones).
3. Títulos com `.h1/.h2/.h3`, textos com `.t1/.t2/.t3`, botões com `.btn` (principal) e `.btn2` (secundário).
4. Profundidade vem dos gradientes de fundo (`.grad-*` no catálogo) e das sombras `--shadow-md/lg`, não de bordas grossas.
5. Respeite `prefers-reduced-motion`: anime só opacidade e transform, com `--dur-*` e `--ease`.
6. Mantenha contraste mínimo de 4.5:1 em texto corrido; confira no catálogo.
