# Immersive 3D

Experiência editorial com um objeto protagonista, profundidade, palco escuro e movimento narrativo lento.

**Status:** modelo autoral NOVYRA. Não é extração de nenhum site; os valores foram definidos para esta direção visual.
**Melhor uso:** Portfólio, estúdio criativo, campanha ou produto imersivo.
**Template recomendado:** `immersive-3d-studio`
**Catálogo vivo:** abra `design-system.html` nesta pasta.

## Fundamentos

| Papel | Token | Valor |
|---|---|---|
| Fundo | `--bg` | `#080d18` |
| Superfície | `--surface` / `--surface-alt` | `#101d31` / `#172a43` |
| Texto | `--text` | `#f4f8fc` (contraste 18.2:1) |
| Texto secundário | `--text-muted` | `#9fb1c5` (contraste 8.85:1) |
| Ação principal | `--accent` | `#38bdf8`, texto `#05070c` (9.41:1) |
| Acento de apoio | `--accent-2` | `#c6f1ff` |
| Títulos | `--font-title` | Space Grotesk |
| Corpo | `--font-body` | Inter |
| Raios | `--radius-sm/md/lg` | 6 / 18 / 28 px |
| Movimento | `--dur-*`, `--ease` | [200, 420, 900] ms, `cubic-bezier(0.16, 1, 0.3, 1)` (slow and narrative) |

## Regras para a IA seguir

1. Use **só** as variáveis de `tokens.css`; nunca escreva cores ou tamanhos soltos.
2. `--accent` é para a ação principal e para no máximo um destaque por seção. `--accent-2` só em detalhes (linhas, brilhos, ícones).
3. Títulos com `.h1/.h2/.h3`, textos com `.t1/.t2/.t3`, botões com `.btn` (principal) e `.btn2` (secundário).
4. Profundidade vem dos gradientes de fundo (`.grad-*` no catálogo) e das sombras `--shadow-md/lg`, não de bordas grossas.
5. Respeite `prefers-reduced-motion`: anime só opacidade e transform, com `--dur-*` e `--ease`.
6. Mantenha contraste mínimo de 4.5:1 em texto corrido; confira no catálogo.
