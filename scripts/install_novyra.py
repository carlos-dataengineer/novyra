"""Núcleo do instalador do NOVYRA (chamado por install.sh e install.ps1).

O que faz, nesta ordem:
  1. copia o runtime (scripts, templates, design systems) para NOVYRA_HOME (padrão ~/Novyra),
     sem tocar em sites/ nem nos design systems e templates que você criou;
  2. instala as dependências Python (Pillow e Playwright) com pip --user;
  3. instala as 5 skills no Claude Code (~/.claude/skills) e no Codex
     (~/.codex/skills e ~/.agents/skills), apontando para NOVYRA_HOME;
  4. gera a ferramenta, o NOVYRA Studio (NOVYRA_HOME/novyra.html), e abre no navegador.

Segurança: só substitui uma skill que o próprio NOVYRA instalou (arquivo .novyra dentro dela).
Uma skill de mesmo nome vinda de outra origem é preservada, e o instalador avisa.

Uso (a partir da raiz do repositório):
    python scripts/install_novyra.py
    python scripts/install_novyra.py --home D:/Novyra --skip-codex --no-open
    python scripts/install_novyra.py --uninstall          # remove skills e runtime; mantém sites/
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

MARCA = ".novyra"
REPO = Path(__file__).resolve().parent.parent
SKILLS = ("novyra", "criar-site", "wireframe", "extrair-ds", "combinar-ds")

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

COR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(cod: str, txt: str) -> str:
    return f"\033[{cod}m{txt}\033[0m" if COR else txt


def passo(t: str) -> None:
    print(f"  {_c('36', '>')} {t}")


def ok(t: str) -> None:
    print(f"  {_c('32', '✓')} {t}")


def aviso(t: str) -> None:
    print(f"  {_c('33', '!')} {t}")


def destinos(home: Path, claude: bool, codex: bool) -> list[tuple[Path, str]]:
    out = []
    if claude:
        out.append((home / ".claude" / "skills", "Claude Code"))
    if codex:
        codex_home = Path(os.environ.get("CODEX_HOME") or home / ".codex")
        out.append((codex_home / "skills", "Codex"))
        out.append((home / ".agents" / "skills", "agentes (pasta compartilhada)"))
    return out


def eh_nossa(pasta: Path) -> bool:
    return (pasta / MARCA).exists()


def instalar_skills(raiz: Path, alvos: list[tuple[Path, str]], forcar: bool) -> int:
    puladas = 0
    for base, rotulo in alvos:
        feitas = []
        for nome in SKILLS:
            origem = REPO / "skills" / nome
            alvo = base / nome
            if alvo.exists():
                if not (eh_nossa(alvo) or forcar):
                    aviso(f"{alvo} já existe e não foi instalada pelo NOVYRA. Pulei (use --force para substituir).")
                    puladas += 1
                    continue
                shutil.rmtree(alvo)
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(origem, alvo)
            for arq in alvo.rglob("*"):
                if arq.is_file() and arq.suffix in (".md", ".yaml", ".yml"):
                    txt = arq.read_text(encoding="utf-8")
                    if "{{RAIZ}}" in txt:
                        arq.write_text(txt.replace("{{RAIZ}}", raiz.as_posix()), encoding="utf-8")
            (alvo / MARCA).write_text(f"Instalada pelo NOVYRA. Runtime: {raiz.as_posix()}\n", encoding="utf-8")
            feitas.append(nome)
        if feitas:
            ok(f"{rotulo}: {', '.join(feitas)} em {base}")
    return puladas


def copiar_runtime(raiz: Path) -> None:
    rt = REPO / "runtime"
    raiz.mkdir(parents=True, exist_ok=True)
    # scripts: sempre a versão do pacote
    if (raiz / "scripts").exists():
        shutil.rmtree(raiz / "scripts")
    shutil.copytree(rt / "scripts", raiz / "scripts", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # templates e design systems embutidos: substitui só os do pacote; os seus ficam
    for grupo in ("templates", "design-systems", "referencias"):
        (raiz / grupo).mkdir(exist_ok=True)
        for item in (rt / grupo).iterdir():
            alvo = raiz / grupo / item.name
            if item.is_dir():
                if alvo.exists():
                    shutil.rmtree(alvo)
                shutil.copytree(item, alvo)
            else:
                shutil.copy2(item, alvo)
    (raiz / "sites").mkdir(exist_ok=True)
    for arq in ("requirements.txt", ".env.example"):
        shutil.copy2(rt / arq, raiz / arq)
    shutil.copy2(REPO / "VERSION", raiz / "VERSION")
    (raiz / MARCA).write_text("Runtime do NOVYRA. sites/ e o que você criar aqui são seus.\n", encoding="utf-8")
    ok(f"Runtime copiado para {raiz}")


def instalar_deps(raiz: Path) -> None:
    passo("Instalando dependências Python (Pillow, Playwright)")
    cmd = [sys.executable, "-m", "pip", "install", "--user", "--quiet", "--disable-pip-version-check",
           "-r", str(raiz / "requirements.txt")]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception as exc:  # noqa: BLE001
        aviso(f"pip não rodou ({exc}). Instale depois: {' '.join(cmd)}")
        return
    if r.returncode != 0:
        # ambientes gerenciados (PEP 668) recusam --user; tente de novo sem
        r2 = subprocess.run([c for c in cmd if c != "--user"], capture_output=True, text=True, timeout=600)
        if r2.returncode != 0:
            aviso("Não consegui instalar as dependências. Rode manualmente:")
            print(f"      {sys.executable} -m pip install -r \"{raiz / 'requirements.txt'}\"")
            return
    ok("Dependências instaladas (o Playwright usa o Chrome que você já tem)")


def gerar_painel(raiz: Path, abrir: bool) -> Path | None:
    painel = raiz / "novyra.html"
    r = subprocess.run([sys.executable, "-X", "utf8", str(raiz / "scripts" / "gerar_painel.py")],
                       capture_output=True, text=True, cwd=str(raiz / "scripts"))
    if r.returncode != 0 or not painel.exists():
        aviso("Não consegui gerar o painel: " + (r.stderr.strip().splitlines() or ["erro desconhecido"])[-1])
        return None
    ok(f"Ferramenta gerada: {painel}")
    if abrir:
        try:
            webbrowser.open(painel.as_uri())
            ok("Aberta no navegador")
        except Exception:  # noqa: BLE001
            aviso(f"Abra manualmente: {painel}")
    return painel


def desinstalar(raiz: Path, alvos: list[tuple[Path, str]]) -> int:
    for base, rotulo in alvos:
        for nome in SKILLS:
            alvo = base / nome
            if alvo.exists() and eh_nossa(alvo):
                shutil.rmtree(alvo)
                ok(f"Removida {rotulo}: {alvo}")
    if raiz.exists() and eh_nossa(raiz):
        for item in ("scripts", "novyra.html", "novyra-artefato.html", "requirements.txt", ".env.example", "VERSION"):
            alvo = raiz / item
            if alvo.is_dir():
                shutil.rmtree(alvo)
            elif alvo.exists():
                alvo.unlink()
        for grupo in ("templates", "design-systems", "referencias"):
            for item in (REPO / "runtime" / grupo).iterdir():
                alvo = raiz / grupo / item.name
                if alvo.is_dir():
                    shutil.rmtree(alvo)
                elif alvo.exists():
                    alvo.unlink()
            pasta = raiz / grupo
            if pasta.is_dir() and not any(pasta.iterdir()):
                pasta.rmdir()
        if (raiz / "sites").is_dir() and not any((raiz / "sites").iterdir()):
            (raiz / "sites").rmdir()
        ok(f"Runtime removido de {raiz}")
        restos = [p.name for p in raiz.iterdir() if p.name != MARCA]
        if restos:
            print(f"    Mantive o que é seu em {raiz}: {', '.join(sorted(restos))}")
        else:
            (raiz / MARCA).unlink()
            raiz.rmdir()
    print("\n  NOVYRA desinstalado.\n")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Instala o NOVYRA no Claude Code e no Codex")
    p.add_argument("--home", default=os.environ.get("NOVYRA_HOME") or str(Path.home() / "Novyra"),
                   help="onde fica o runtime e os sites (padrão: ~/Novyra ou NOVYRA_HOME)")
    p.add_argument("--user-home", default=str(Path.home()), help=argparse.SUPPRESS)
    p.add_argument("--skip-claude", action="store_true", default=os.environ.get("NOVYRA_SKIP_CLAUDE") == "1")
    p.add_argument("--skip-codex", action="store_true", default=os.environ.get("NOVYRA_SKIP_CODEX") == "1")
    p.add_argument("--skip-deps", action="store_true", default=os.environ.get("NOVYRA_SKIP_DEPS") == "1")
    p.add_argument("--no-open", action="store_true", default=os.environ.get("NOVYRA_NO_OPEN") == "1")
    p.add_argument("--force", action="store_true", help="substitui skills de mesmo nome de outra origem")
    p.add_argument("--uninstall", action="store_true")
    a = p.parse_args()

    if sys.version_info < (3, 10):
        print("O NOVYRA precisa de Python 3.10 ou mais novo.", file=sys.stderr)
        return 1
    raiz = Path(a.home).expanduser().resolve()
    alvos = destinos(Path(a.user_home), not a.skip_claude, not a.skip_codex)

    if a.uninstall:
        return desinstalar(raiz, alvos)

    print(f"\n  NOVYRA {(REPO / 'VERSION').read_text(encoding='utf-8').strip()} · imagem ou ideia vira site\n")
    if raiz.exists() and any(raiz.iterdir()) and not eh_nossa(raiz):
        print(f"A pasta {raiz} já existe e não é do NOVYRA. Use --home para escolher outra.", file=sys.stderr)
        return 1
    copiar_runtime(raiz)
    if not a.skip_deps:
        instalar_deps(raiz)
    puladas = instalar_skills(raiz, alvos, a.force) if alvos else 0
    painel = gerar_painel(raiz, not a.no_open)

    print("\n  Pronto. Como usar:")
    if not a.skip_claude:
        print('    Claude Code  /novyra abre o painel · /criar-site imagem="C:/tela.png" slug=meu-site')
    if not a.skip_codex:
        print('    Codex        $novyra abre o painel · $criar-site imagem="C:/tela.png" slug=meu-site')
    if painel:
        print(f"    Navegador    {painel}")
    print(f"    Seus sites   {raiz / 'sites'}")
    print("\n  Abra uma conversa nova para o agente reconhecer as skills.\n")
    return 1 if puladas else 0


if __name__ == "__main__":
    sys.exit(main())
