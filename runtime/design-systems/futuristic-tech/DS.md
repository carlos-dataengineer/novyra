# Futuristic Tech

Tecnologia B2B escura com azul profundo, ciano/teal e módulos de dados claros; foco em clareza e confiança.

**Status:** modelo autoral NOVYRA. Não é extração de nenhum site; os valores foram definidos para esta direção visual.
**Melhor uso:** SaaS, IA, dados, cibersegurança e B2B.
**Template recomendado:** `tech-product`
**Catálogo vivo:** abra `design-system.html` nesta pasta.

## Fundamentos

| Papel | Token | Valor |
|---|---|---|
| Fundo | `--bg` | `#06101c` |
| Superfície | `--surface` / `--surface-alt` | `#0d1b2a` / `#14283a` |
| Texto | `--text` | `#f2f7fa` (contraste 17.71:1) |
| Texto secundário | `--text-muted` | `#9db2c1` (contraste 8.71:1) |
| Ação principal | `--accent` | `#19c6cf`, texto `#05070c` (9.61:1) |
| Acento de apoio | `--accent-2` | `#6ae5e0` |
| Títulos | `--font-title` | Manrope |
| Corpo | `--font-body` | Inter |
| Raios | `--radius-sm/md/lg` | 4 / 14 / 24 px |
| Movimento | `--dur-*`, `--ease` | [100, 180, 320] ms, `cubic-bezier(0.4, 0, 0.2, 1)` (subtle and purposeful) |

## Regras para a IA seguir

1. Use **só** as variáveis de `tokens.css`; nunca escreva cores ou tamanhos soltos.
2. `--accent` é para a ação principal e para no máximo um destaque por seção. `--accent-2` só em detalhes (linhas, brilhos, ícones).
3. Títulos com `.h1/.h2/.h3`, textos com `.t1/.t2/.t3`, botões com `.btn` (principal) e `.btn2` (secundário).
4. Profundidade vem dos gradientes de fundo (`.grad-*` no catálogo) e das sombras `--shadow-md/lg`, não de bordas grossas.
5. Respeite `prefers-reduced-motion`: anime só opacidade e transform, com `--dur-*` e `--ease`.
6. Mantenha contraste mínimo de 4.5:1 em texto corrido; confira no catálogo.
