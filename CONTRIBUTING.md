# Como contribuir / Contributing

Obrigado pelo interesse! Este guia mostra como o repositório está organizado e como testar uma mudança.

## Estrutura

| Pasta | O que tem | Vai para o computador de quem instala? |
|---|---|---|
| `skills/` | As 5 skills (`SKILL.md` + `agents/openai.yaml` para o Codex) | Sim: `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills` |
| `runtime/scripts/` | Scripts Python de medição, captura, design system e o gerador do painel | Sim: `~/Novyra/scripts` |
| `runtime/templates/` | Pontos de partida dos sites | Sim: `~/Novyra/templates` |
| `runtime/design-systems/` | Design systems autorais (tokens, componentes, catálogo) | Sim: `~/Novyra/design-systems` |
| `scripts/` | Instalador (`install_novyra.py`) e gerador de capturas do README | Não |
| `tests/` | Validação do repositório e teste de instalação | Não |
| `docs/` | Documentação e imagens do README | Não |

As skills usam o marcador `{{RAIZ}}` para caminhos. O instalador troca pelo caminho real do runtime (`~/Novyra` ou `NOVYRA_HOME`).

## Rodar localmente

```bash
git clone https://github.com/carlos-dataengineer/novyra.git
cd novyra
python tests/validate_repo.py      # estrutura, frontmatter, manifestos, links do README
python tests/test_install.py       # instala numa pasta temporária, cria sites, gera o painel e desinstala
bash install.sh --no-open          # instala de verdade a partir do clone (Windows: .\install.ps1)
```

## Regras

1. **Nada de material de terceiros sem licença.** Nada de prints, CSS ou fontes comerciais de outros sites. A pasta `fonte/` dos design systems nunca entra no git.
2. **Skills portáteis.** Caminhos sempre via `{{RAIZ}}`. Funcionam no Claude Code (`/nome`) e no Codex (`$nome`).
3. **Gates de aprovação.** O `/criar-site` nunca avança de etapa sem o "aprovado" de quem usa.
4. **Scripts só com Python padrão + Pillow/Playwright.** Sem build, sem framework nos sites gerados.
5. **Registre a mudança** em `CHANGELOG.md` e atualize o README se a interface mudar (`python scripts/screenshots.py`).

## Commits e versões

- Mensagens no imperativo, curtas: `feat: template de portfólio`, `fix: caminho do painel no Windows`.
- Versão em `VERSION` e `.claude-plugin/*.json` (semver). Uma tag `vX.Y.Z` dispara o workflow de release.
