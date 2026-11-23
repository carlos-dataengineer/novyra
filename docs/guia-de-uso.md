# Guia de uso

Do primeiro comando ao site pronto. Para a visão geral, veja o [README](../README.md).

## 1. Instalar

macOS / Linux / WSL / Git Bash:

```bash
curl -fsSL https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/install.sh | bash
```

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/install.ps1 | iex
```

O instalador:

1. copia o runtime para `~/Novyra` (scripts, templates, design systems e a pasta `sites/`);
2. instala Pillow e Playwright com `pip --user` (o Playwright usa o Chrome que você já tem);
3. instala as 5 skills em `~/.claude/skills` (Claude Code), `~/.codex/skills` e `~/.agents/skills` (Codex);
4. **gera a ferramenta**, o NOVYRA Studio (`~/Novyra/novyra.html`), e abre no navegador.

Depois, **abra uma conversa nova** no Claude Code ou no Codex para as skills aparecerem.

### Opções

| Variável | Opção do `install.sh` | Efeito |
|---|---|---|
| `NOVYRA_HOME=D:/Novyra` | `--home D:/Novyra` | muda a pasta do runtime e dos sites |
| `NOVYRA_NO_OPEN=1` | `--no-open` | não abre o navegador |
| `NOVYRA_SKIP_CLAUDE=1` | `--skip-claude` | não instala no Claude Code |
| `NOVYRA_SKIP_CODEX=1` | `--skip-codex` | não instala no Codex |
| `NOVYRA_SKIP_DEPS=1` | `--skip-deps` | não roda o `pip install` |
| `NOVYRA_REF=v0.2.0` | `--ref v0.2.0` | instala uma versão marcada |
| `NOVYRA_SITES=D:/sites` | — | sites em outra pasta (vale na hora de usar) |

No PowerShell, defina antes: `$env:NOVYRA_HOME = "D:\Novyra"; irm ... | iex`.

## 2. Abrir o painel

- Claude Code: `/novyra` (no app do Claude, o painel abre como artefato).
- Codex: `$novyra`.
- Navegador: abra `~/Novyra/novyra.html`.

No painel, a aba **Criar** monta o comando para você: escolha imagem ou ideia, nome, template e design system, e copie.

## 3. Criar um site a partir de uma imagem

```text
/criar-site imagem="C:/Users/voce/Desktop/tela.png" slug=minha-landing
```

No Codex: `$criar-site imagem="..." slug=minha-landing`.

O agente cria `~/Novyra/sites/minha-landing/` e segue as 5 etapas. **Cada etapa termina com uma captura e espera você responder.**

| Etapa | O que você vê | O que responder |
|---|---|---|
| 1. Wireframe + plano | a planta ASCII da tela e a tabela região → técnica | `aprovado` ou "o card da direita é um gráfico, não uma imagem" |
| 2. Fundo | só o fundo, comparado com a referência | `aprovado` ou "o gradiente está mais roxo que o original" |
| 3. Componentes + fontes | estrutura, textos e componentes | `aprovado` ou "a fonte do título é mais estreita" |
| 4. Assets | ícones, fotos, avatares | `aprovado` (pulada se não houver assets) |
| 5. Revisão final | lado a lado + nota de semelhança + validação | `aprovado` |

Para retomar depois: `/criar-site slug=minha-landing` (o agente lê o `ESTADO.md`).

## 4. Criar a partir de uma ideia

```text
/criar-site brief="Landing de uma plataforma de IA com hero imersivo, 3 recursos e CTA" slug=plataforma-ia ds=novyra-future-lab template=tech-product
```

Sem imagem não há comparação por pixels; a referência passa a ser o catálogo do design system.

## 5. Usar um design system

Quatro vêm prontos: `novyra-future-lab`, `immersive-3d`, `cinematic-sci-fi`, `futuristic-tech`. Abra o catálogo de cada um em `~/Novyra/design-systems/<slug>/design-system.html`.

Extrair de um site público (só páginas sem login):

```text
/extrair-ds url=https://exemplo.com slug=referencia
```

Combinar vários:

```text
/combinar-ds nome=minha-marca base=novyra-future-lab tipografia=cinematic-sci-fi movimento=immersive-3d
```

Depois use `ds=minha-marca` no `/criar-site`.

## 6. Só o wireframe

```text
/wireframe formato=svg imagem="C:/mocks/tela.png" saida="C:/mocks/tela.wireframe.svg"
/wireframe formato=ascii brief="Dashboard com sidebar, 4 KPIs e tabela"
```

## 7. Scripts à mão

Todos ficam em `~/Novyra/scripts` e rodam com `python -X utf8`:

```bash
cd ~/Novyra/scripts
python -X utf8 novo_site.py meu-site --imagem "C:/mocks/tela.png" --ds futuristic-tech
python -X utf8 recortar.py ../sites/meu-site/reference.png --grade 100
python -X utf8 amostrar_cores.py ../sites/meu-site/reference.png --caixa 0,0,1440,80 --paleta 6
python -X utf8 capturar_tela.py ../sites/meu-site --igual-referencia
python -X utf8 comparar.py ../sites/meu-site/reference.png ../sites/meu-site/_capturas/captura-1440x900.png --lado-a-lado
python -X utf8 validar_site.py ../sites/meu-site
python -X utf8 gerar_painel.py
```

## 8. Publicar um site

Cada site é uma pasta com `index.html` e `assets/`. Funciona em qualquer hospedagem estática (GitHub Pages, Netlify, Vercel, um servidor próprio). Antes, rode `validar_site.py` e **apague `reference.*` e `_capturas/`** se a referência for confidencial.

## 9. Atualizar e desinstalar

Atualizar: rode o mesmo comando de instalação. Seus sites e os design systems que você criou ficam.

Desinstalar:

```bash
curl -fsSL https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/uninstall.sh | bash
```

```powershell
irm https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/uninstall.ps1 | iex
```

A desinstalação remove as skills e o runtime, e **mantém `~/Novyra/sites`**.

## 10. Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| A skill não aparece | sessão aberta antes da instalação | abra uma conversa nova |
| "Python 3.10 ou mais novo" | Python ausente ou antigo | instale em python.org (no Windows marque *Add to PATH*) |
| `capturar_tela.py` não gera imagem | Chrome não encontrado ou Edge bloqueado por política | instale o Chrome ou defina `NAVEGADOR` com o caminho do executável |
| `No module named PIL` | dependências não instaladas | `python -m pip install -r ~/Novyra/requirements.txt` |
| "já existe e não foi instalada pelo NOVYRA" | você tem outra skill com o mesmo nome | renomeie a sua ou rode o instalador com `--force` |
| `/extrair-ds` falha numa URL | página com login, captcha ou bloqueio | use outra URL pública; o NOVYRA não contorna bloqueios |
