#!/usr/bin/env bash
# Instala o NOVYRA: as skills para Claude Code e Codex, o runtime e a ferramenta (NOVYRA Studio).
#
#   curl -fsSL https://raw.githubusercontent.com/carlos-dataengineer/novyra/main/install.sh | bash
#
# Opções (também como variáveis de ambiente):
#   --home <pasta>  onde ficam runtime e sites (padrão ~/Novyra)   NOVYRA_HOME=~/Novyra
#   --no-open       não abre o navegador                           NOVYRA_NO_OPEN=1
#   --skip-claude   não instala no Claude Code                     NOVYRA_SKIP_CLAUDE=1
#   --skip-codex    não instala no Codex                           NOVYRA_SKIP_CODEX=1
#   --skip-deps     não roda pip install                           NOVYRA_SKIP_DEPS=1
#   --ref <ref>     branch ou tag (padrão: main)                   NOVYRA_REF=v0.2.0
set -euo pipefail

REPO="carlos-dataengineer/novyra"
REF="${NOVYRA_REF:-main}"
ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --ref) shift; REF="${1:?informe a branch ou tag}" ;;
    --home) shift; ARGS+=("--home" "${1:?informe a pasta}") ;;
    --no-open|--skip-claude|--skip-codex|--skip-deps|--force|--uninstall) ARGS+=("$1") ;;
    -h|--help) sed -n '2,13p' "$0" 2>/dev/null || true; exit 0 ;;
    *) echo "Opção desconhecida: $1" >&2; exit 1 ;;
  esac
  shift
done

# Python 3.10+
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "O NOVYRA precisa do Python 3.10 ou mais novo. Instale em https://www.python.org/downloads/ e rode de novo." >&2
  exit 1
fi

TMP=""
cleanup() { if [ -n "$TMP" ] && [ -d "$TMP" ]; then rm -rf -- "$TMP"; fi; }
trap cleanup EXIT

SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/scripts/install_novyra.py" ]; then
  ROOT="$SCRIPT_DIR"
  printf '  > Usando os arquivos locais em %s\n' "$ROOT"
else
  command -v curl >/dev/null || { echo "Instale o curl e tente de novo." >&2; exit 1; }
  command -v tar >/dev/null || { echo "Instale o tar e tente de novo." >&2; exit 1; }
  TMP="$(mktemp -d)"
  case "$REF" in v[0-9]*) KIND="tags" ;; *) KIND="heads" ;; esac
  printf '  > Baixando %s (%s)\n' "$REPO" "$REF"
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/$KIND/$REF" | tar -xz -C "$TMP"
  ROOT="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [ -f "$ROOT/scripts/install_novyra.py" ] || { echo "O pacote baixado não tem scripts/install_novyra.py." >&2; exit 1; }
fi

"$PY" -X utf8 "$ROOT/scripts/install_novyra.py" ${ARGS[@]+"${ARGS[@]}"}
