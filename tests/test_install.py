"""Teste de ponta a ponta do instalador, numa pasta temporária (não toca no seu ~/.claude).

1. instala (sem pip, sem abrir navegador) em <tmp>/home;
2. confere skills no Claude Code, Codex e pasta compartilhada, com {{RAIZ}} trocado;
3. cria sites com e sem design system e template, e regenera o painel;
4. reinstala (idempotente) e confere que os sites continuam lá;
5. confere que uma skill de outra origem com o mesmo nome é preservada;
6. desinstala e confere que só sites/ ficou.

    python tests/test_install.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = ("novyra", "criar-site", "wireframe", "extrair-ds", "combinar-ds")


def rodar(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run([sys.executable, "-X", "utf8", *args], capture_output=True, text=True,
                       encoding="utf-8", env=env)
    return r


def checar(cond: bool, msg: str) -> None:
    if not cond:
        print(f"FALHOU: {msg}")
        sys.exit(1)
    print(f"  ok  {msg}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    with tempfile.TemporaryDirectory() as tmp:
        user = Path(tmp) / "user"
        raiz = user / "Novyra"
        env = {**os.environ, "CODEX_HOME": str(user / ".codex")}
        env.pop("NOVYRA_SITES", None)
        base = [str(REPO / "scripts" / "install_novyra.py"), "--home", str(raiz), "--user-home", str(user),
                "--skip-deps", "--no-open"]

        # skill alheia com o mesmo nome deve ser preservada
        alheia = user / ".agents" / "skills" / "wireframe"
        alheia.mkdir(parents=True)
        (alheia / "SKILL.md").write_text("---\nname: wireframe\ndescription: outra\n---\n", encoding="utf-8")

        r = rodar(*base, env=env)
        print(r.stdout)
        checar(r.returncode == 1, "instalador avisa (código 1) quando pula uma skill alheia")
        checar("outra" in (alheia / "SKILL.md").read_text(encoding="utf-8"), "skill alheia preservada")

        for pasta in (user / ".claude" / "skills", user / ".codex" / "skills"):
            for nome in SKILLS:
                sk = pasta / nome / "SKILL.md"
                checar(sk.exists(), f"{sk.relative_to(user)} instalada")
                checar("{{RAIZ}}" not in sk.read_text(encoding="utf-8"), f"{nome}: marcador trocado")
            checar((pasta / "criar-site" / "agents" / "openai.yaml").exists(), "openai.yaml copiado")
        checar((raiz / "novyra.html").exists(), "ferramenta NOVYRA Studio gerada")

        s = str(raiz / "scripts")
        checar(rodar(f"{s}/novo_site.py", "demo-base", "--ds", "novyra-future-lab").returncode == 0, "site com DS")
        checar(":root" in (raiz / "sites/demo-base/assets/styles.css").read_text(encoding="utf-8"), "tokens no CSS")
        checar(rodar(f"{s}/novo_site.py", "demo-tech", "--template", "tech-product", "--ds", "futuristic-tech").returncode == 0,
               "site com template de arquivo único + DS")
        checar((raiz / "sites/demo-tech/assets/ds-tokens.css").exists(), "tokens ligados por <link>")
        checar(rodar(f"{s}/novo_site.py", "../fora").returncode != 0, "slug com caminho é recusado")
        checar(rodar(f"{s}/gerar_painel.py").returncode == 0, "painel regenerado")
        painel = (raiz / "novyra.html").read_text(encoding="utf-8")
        checar("demo-tech" in painel and "Futuristic Tech" in painel, "painel lista sites e design systems")
        checar(rodar(f"{s}/gerar_painel.py", "--artefato").returncode == 0, "versão para artefato gerada")
        checar("file:///" not in (raiz / "novyra-artefato.html").read_text(encoding="utf-8"), "artefato sem links locais")
        checar(rodar(f"{s}/validar_site.py", str(raiz / "sites/demo-base")).returncode in (0, 1), "validador roda")

        r = rodar(*base, env=env)
        checar((raiz / "sites" / "demo-tech").exists(), "reinstalar mantém os sites")

        r = rodar(*base, "--uninstall", env=env)
        checar(r.returncode == 0, "desinstalação")
        checar(not (user / ".claude" / "skills" / "criar-site").exists(), "skills removidas")
        checar(alheia.exists(), "skill alheia continua após desinstalar")
        checar((raiz / "sites" / "demo-tech").exists(), "sites preservados")
        checar(not (raiz / "scripts").exists(), "runtime removido")
    print("\nOK: instalação, uso e desinstalação funcionam.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
