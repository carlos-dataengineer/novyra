# Histórico de versões / Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões seguem [SemVer](https://semver.org/lang/pt-BR/).

## [0.2.0] — 2026-11-23

Primeira versão instalável com um comando.

### Adicionado
- **Instalador de um comando** para macOS/Linux (`install.sh`) e Windows (`install.ps1`), com desinstaladores. Instala as skills no Claude Code e no Codex, copia o runtime para `~/Novyra`, instala Pillow e Playwright e gera a ferramenta.
- **NOVYRA Studio** (`~/Novyra/novyra.html`): painel gerado na instalação com montador de comandos (Claude Code ou Codex), prévia ao vivo dos templates, galeria de design systems, lista dos seus sites com progresso das etapas e atalhos de teclado.
- **Skill `/novyra`** (`$novyra` no Codex): atualiza o painel e, no Claude, publica como artefato.
- **Suporte ao Codex**: cada skill traz `agents/openai.yaml`.
- Plugin do Claude Code (`.claude-plugin/`).
- Os 4 design systems autorais agora têm catálogo vivo (`design-system.html`), `componentes.css` e regras para a IA no `DS.md`.
- `novo_site.py --template` aplica design system também em templates de arquivo único.
- CI (validação, ShellCheck, instalação em Ubuntu/macOS/Windows), release automático, templates de issue e PR, CONTRIBUTING, SECURITY, SUPPORT, CODE_OF_CONDUCT e NOTICE.
- README bilíngue (PT/EN) com capturas de tela e uma demonstração completa (`examples/portal-novyra`), criada a partir de uma arte do autor.
- `capturar_tela.py` usa o Playwright quando instalado, para capturar no tamanho exato (o Chrome pela linha de comando não desce de ~500 px de largura).

- **Pipeline de agentes** no NOVYRA Studio (tecla 5): as 5 etapas de cada site como agentes em cards neon ligados por fluxos de luz animados, com status do `ESTADO.md`, barra de progresso, artefatos reais encontrados na pasta e scripts de cada etapa. Botão **Ver pipeline** em Meus sites.
- **Referências futuristas:** catálogo com 8 sites reais (Lusion + os 7 designs da galeria DesignRush Futuristic) em `runtime/referencias/futuristas.json`, com padrões observados e o modelo NOVYRA de cada um. Nova aba **Referências** no NOVYRA Studio (tecla 6) com botões para `/extrair-ds`, criar na direção e usar o modelo.
- **3 modelos novos** (design system + template autorais): `studio-3d-light` (repertório Lusion: página clara, palco 3D), `retro-glitch` (GLIX Studio: janelas antigas, neon, glitch) e `bio-data-mono` (Nature Beyond Technology: preto monocromático, grade, módulos).
- Créditos: o método é atribuído à pesquisa sobre o conteúdo público da Asimov Academy (Vibe Design, AI Designer); Lusion e DesignRush como repertório (NOTICE, metodologia, referências, README).
- Arquitetura documentada em três camadas: A repertório, B interface (NOVYRA Studio), C motor (Claude Code/Codex + scripts).
- Os nomes antigos dos modelos (`lusion-immersive-3d`, `takamo-cinematic-sci-fi`, `databahn-futuristic-tech`, `lusion-3d-immersive`, `databahn-tech-product`) continuam aceitos como apelidos.

### Alterado
- Estrutura: `skills/`, `runtime/` (scripts, templates, design systems) e `docs/`.
- Templates e design systems com nomes neutros: `immersive-3d-studio`, `cinematic-sci-fi`, `tech-product`; `immersive-3d`, `cinematic-sci-fi`, `futuristic-tech`.
- Sites passam a ficar em `~/Novyra/sites` (ou `NOVYRA_SITES`).

### Removido
- A skill `expert-asimov`/`expert-novyra` e a base de resumos de vídeos ficam fora do pacote público (a atribuição ao método continua).

## [0.1.1] — 2026-11-22

- Biblioteca de referências visuais futuristas.
- Três templates HTML autorais: experiência imersiva, sci-fi cinematográfico e produto de tecnologia/IA.
- Design systems conceituais e a direção original NOVYRA Future Lab.

## [0.1.0] — Primeira publicação experimental

- Organização inicial; documentação de identidade, arquitetura, casos de uso e roadmap.
