# Política de segurança / Security policy

## Versões com suporte

| Versão | Suporte |
|---|---|
| 0.2.x | Sim |
| < 0.2 | Não |

## Como relatar uma vulnerabilidade

**Não abra uma issue pública.** Use o relato privado do GitHub:

1. Acesse [Security → Report a vulnerability](https://github.com/carlos-dataengineer/novyra/security/advisories/new).
2. Descreva o problema, como reproduzir e o impacto que você enxerga.

A primeira resposta chega em até 7 dias. Se o problema for confirmado, a correção sai em uma nova versão, com crédito para você se quiser.

## O que está no escopo

- **Instaladores** (`install.sh`, `install.ps1`, `scripts/install_novyra.py`): escrita fora das pastas documentadas (`~/Novyra`, `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`) ou execução de código inesperado.
- **Skills** (`skills/*/SKILL.md`): instruções que levem o agente a agir além do pedido da pessoa, ler ou escrever fora da pasta do site.
- **Scripts** (`runtime/scripts`): caminhos que escapam da pasta do site, captura de páginas que exigem login.
- **NOVYRA Studio**: injeção de HTML/script a partir de nomes de sites, tokens ou templates.

## O que o NOVYRA faz e não faz

- Roda **só no seu computador**. Não há servidor, telemetria nem conta.
- `/extrair-ds` abre apenas a URL pública que você passar, no seu Chrome, sem login. Não contorna captcha nem bloqueios.
- `gerar_imagem.py` é o único script que fala com um serviço pago (OpenRouter), e só se você criar um `.env` com a chave.

## Boas práticas para quem instala

- Leia o script antes de rodar. Ele é curto e comentado.
- Prefira instalar uma versão marcada: `NOVYRA_REF=v0.2.0`.
- Não coloque telas com dados confidenciais em sites que você vai publicar.
