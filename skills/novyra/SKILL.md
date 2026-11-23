---
name: novyra
description: >-
  Abre o NOVYRA Studio, o painel da ferramenta NOVYRA (imagem ou ideia → site
  HTML + CSS em 5 etapas). Mostra o montador de comandos, os templates, os
  design systems e os sites já criados. Use quando o usuário chamar /novyra ou
  $novyra, ou pedir para abrir o NOVYRA, ver os sites criados ou escolher
  template/design system.
---

# NOVYRA Studio

> **Runtime:** os caminhos abaixo apontam para a pasta onde o instalador colocou o NOVYRA. Se ela não existir (por exemplo, skill instalada só pelo plugin), use `~/Novyra` ou a variável `NOVYRA_HOME`; se também não existir, peça para a pessoa instalar: https://github.com/carlos-dataengineer/novyra#instalação

**O que faz:** atualiza e abre o painel do NOVYRA, a mesma página que o instalador gerou.
**Onde fica:** `{{RAIZ}}/novyra.html` (runtime instalado em `{{RAIZ}}`).

## Passos

1. Atualize o painel com os sites e design systems atuais:

   ```bash
   python -X utf8 "{{RAIZ}}/scripts/gerar_painel.py"
   ```

   Se o Python falhar, avise o usuário e mostre o painel que já existe em `{{RAIZ}}/novyra.html`.

2. Entregue o painel pelo melhor caminho disponível, nesta ordem:

   - **A) Claude com a ferramenta de artefatos** (Claude Code no app, claude.ai): gere a versão sem links locais e publique-a como artefato.

     ```bash
     python -X utf8 "{{RAIZ}}/scripts/gerar_painel.py" --artefato
     ```

     Publique `{{RAIZ}}/novyra-artefato.html` com a ferramenta de artefatos (ícone `code`, título "NOVYRA Studio"). Se já foi publicado nesta conversa, republique no mesmo arquivo.
   - **B) Sem ferramenta de artefatos** (Codex, terminal): abra `{{RAIZ}}/novyra.html` no navegador padrão (`start ""` no Windows, `open` no macOS, `xdg-open` no Linux) e diga o caminho.

3. Responda em poucas linhas: quantos sites, templates e design systems existem, e o próximo comando sugerido. Exemplos:

   ```text
   /criar-site imagem="C:/caminho/tela.png" slug=meu-site ds=novyra-future-lab
   /extrair-ds url=https://exemplo.com slug=referencia
   ```

   No Codex troque a `/` por `$`.

## Referências futuristas

Se a pessoa pedir referências, modelos ou inspiração futurista, leia `{{RAIZ}}/referencias/futuristas.json` e responda com 3 a 5 referências que combinem com o pedido: nome, link, padrões, modelo NOVYRA e o comando `/criar-site ... ds=<modelo> template=<template>` (ou `/extrair-ds url=<site>` para medir). Nunca copie imagens, textos ou código dos sites.

## Regras

- Não crie nem altere sites aqui; para isso existe `/criar-site`.
- Não publique o painel em lugar público sem o usuário pedir: o artefato nasce privado.
- Se `{{RAIZ}}` não existir, o NOVYRA não está instalado: indique o comando de instalação do README (`https://github.com/carlos-dataengineer/novyra`).
