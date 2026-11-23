# Roadmap da NOVYRA

Este roadmap registra uma direção de evolução. Os itens futuros são propostas e não devem ser confundidos com funcionalidades já entregues.

## v0.1.x — Experimental

- [x] Skills de criação de sites, wireframe, extração e combinação de design systems.
- [x] Scripts de captura, comparação, medição e validação.
- [x] Templates e design systems autorais.

## v0.2.0 — Instalável (atual)

- [x] Instalação com um comando no Claude Code e no Codex (macOS, Linux e Windows).
- [x] NOVYRA Studio gerado na instalação e skill `/novyra`.
- [x] Teste de ponta a ponta e CI em Ubuntu, macOS e Windows.
- [x] README bilíngue com capturas.

## v0.2.x — Integrações pendentes

- [ ] Trazer o app **Future Lab 0.2.1** (editor visual das 5 etapas, prévia desktop/celular, assets, exportação em ZIP) para `apps/future-lab`, depois de inspecionar o pacote real.
- [ ] Ligar o Future Lab ao motor (camada C): cada aprovação no app executa a etapa pelo agente e pelos scripts, não só muda o estado visual.
- [ ] Gates reais: guardar artefatos, versões, logs e evidências de validação de cada etapa.
- [ ] Referência da Via Láctea como direção visual do NOVYRA Future Lab.
- [ ] Teste de instalação limpa em outro computador Windows, registrando versões.

## v0.3.0 — Experiência de criação

- [ ] Mais templates (dashboard, portfólio, e-commerce) e design systems claros.
- [ ] Revisão responsiva automática (captura em 390 px e 768 px na etapa 5).
- [ ] Verificações de acessibilidade (contraste por região, foco, `alt`).
- [ ] Exportar o site para Astro ou Next.js como etapa opcional.

## Próximas versões

- [ ] Etapas de vídeo e 3D (hero animado, objeto protagonista em WebGL) com fallback.
- [ ] Galeria pública de sites feitos com o NOVYRA, com autorização de quem criou.
- [ ] Publicação no marketplace de plugins do Claude Code.

## Como considero uma versão pronta

Antes de marcar uma versão como estável, quero:

1. Instalar o projeto do zero seguindo a documentação.
2. Executar cada skill principal com um exemplo real.
3. Conferir arquivos produzidos e dependências.
4. Validar os sites gerados em desktop e mobile.
5. Registrar limitações conhecidas e resultados dos testes.
6. Atualizar o changelog e criar uma release correspondente.
