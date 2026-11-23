---
name: combinar-ds
description: >-
  Recombina design systems já extraídos (pasta design-systems) num novo: cores de um, tipografia de outro,
  formas e movimento de um terceiro. Gera tokens, catálogo e DS.md, com checagem de contraste e uma aprovação.
  Use quando o usuário pedir /combinar-ds ou quiser misturar identidades visuais.
disable-model-invocation: true
---

# Combinar design systems

> **Runtime:** os caminhos abaixo apontam para a pasta onde o instalador colocou o NOVYRA. Se ela não existir (por exemplo, skill instalada só pelo plugin), use `~/Novyra` ou a variável `NOVYRA_HOME`; se também não existir, peça para a pessoa instalar: https://github.com/carlos-dataengineer/novyra#instalação

**O que permite:** criar uma identidade nova misturando grupos de regras de design systems extraídos com `/extrair-ds`.
**Benefício:** o resultado não fica preso à identidade de um único site. É a recombinação que gera conceitos novos.
**Resultado:** `design-systems/<nome>/` com `tokens.css`, `assets/componentes.css`, `design-system.html` e `DS.md`.

Exemplo:

```text
/combinar-ds nome=painel-noturno base=linear tipografia=stripe movimento=vercel
```

## Grupos que podem vir de lugares diferentes

| Grupo | O que leva |
|-------|------------|
| `cores` | papéis de cor, paleta e anel de foco |
| `tipografia` | famílias, pesos, tamanhos, alturas de linha |
| `formas` | raios, sombras, escala de espaçamento |
| `movimento` | durações, curva, animações |
| `fundos` | gradientes e vidro |

O que não for indicado vem da `base`.

## Processo

1. Listar os design systems disponíveis em `{{RAIZ}}/design-systems/` (pastas com `tokens.json`) e ler o `DS.md` de cada um envolvido.
2. Rodar `python -X utf8 "{{RAIZ}}/scripts/combinar_ds.py" --nome <nome> --base <a> [--cores x] [--tipografia y] [--formas z] [--movimento w] [--fundos v]`.
3. Se o script avisar **contraste < 4.5**, ajuste `text-muted` ou `on-accent` no `tokens.json` e rode `extrair_tokens.py <nome> --sem-recalcular`.
4. `gerar_ds_html.py <nome> --refazer-componentes`, depois edite `assets/componentes.css` para o comportamento combinar com o grupo `movimento` e as formas com o grupo `formas`.
5. Escrever o `DS.md` (mesmo formato do `/extrair-ds`), dizendo **de onde veio cada grupo** e qual a personalidade resultante. Desfaça conflitos com uma regra explícita (ex.: "tipografia leve do Stripe sobre fundo escuro do Linear: usar peso 400 no corpo para não sumir").
6. Print do catálogo (`capturar_tela.py`), abrir a imagem, mostrar ao usuário. **Gate:** só concluir com aprovação explícita. Registrar em `ESTADO.md` da pasta.

## Não fazer

- Combinar sem ler o `DS.md` das origens.
- Aceitar contraste abaixo de 4.5 em texto sem avisar o usuário.
- Copiar `fonte/` de uma origem para a pasta combinada.
