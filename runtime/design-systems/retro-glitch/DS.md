# Retro Glitch

Estética de internet antiga com glitch: janelas estilo sistema operacional dos anos 90, bordas chanfradas, sombras duras deslocadas, verde neon e magenta, tipografia pixelada e monoespaçada.

**Status:** modelo autoral NOVYRA. Os valores foram definidos para esta direção visual; nada foi copiado da referência (código, imagens, textos ou fontes comerciais).
**Repertório que inspirou a direção:** GLIX Studio na galeria DesignRush Futuristic (glitch art, retro UI, pixel type).
**Melhor uso:** Marca de moda/streetwear, estúdio experimental, evento, música, jogos indie.
**Template recomendado:** `retro-glitch`
**Catálogo vivo:** abra `design-system.html` nesta pasta.

## Fundamentos

| Papel | Token | Valor |
|---|---|---|
| Fundo | `--bg` | `#d9d9d9` |
| Superfície | `--surface` / `--surface-alt` | `#ffffff` / `#c0c0c0` |
| Texto | `--text` | `#121212` (contraste 13.27:1) |
| Texto secundário | `--text-muted` | `#3a3a3a` (contraste 8.06:1) |
| Ação principal | `--accent` | `#39ff14`, texto `#05070c` (14.86:1) |
| Acento de apoio | `--accent-2` | `#ff2bd6` |
| Títulos | `--font-title` | VT323 |
| Corpo | `--font-body` | IBM Plex Mono |
| Mono | `--font-mono` | IBM Plex Mono |
| Raios | `--radius-sm/md/lg` | 0 / 0 / 0 px |
| Movimento | `--dur-*`, `--ease` | [60, 120, 240] ms, `steps(4, end)` (snappy, stepped and glitchy) |

## Regras para a IA seguir

1. Use **só** as variáveis de `tokens.css`; nunca escreva cores ou tamanhos soltos.
2. Nada de cantos arredondados (`--radius-*` = 0) nem desfoque: profundidade só com sombra dura (`--shadow-md/lg`).
3. Verde neon `--accent` para a ação principal; magenta `--accent-2` para o glitch (sombras de texto deslocadas).
4. Títulos em VT323 caixa alta; todo o resto em IBM Plex Mono.
5. O glitch é decoração: o texto real continua legível e o layout continua usável.
6. Respeite `prefers-reduced-motion` e mantenha contraste mínimo de 4.5:1 em texto corrido.
