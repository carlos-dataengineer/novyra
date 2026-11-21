# Casos de uso da NOVYRA

A NOVYRA foi pensada para apoiar quem precisa transformar uma ideia ou referência visual em uma interface construída com método. Estes exemplos mostram situações em que as skills e os scripts podem ajudar.

## 1. Recriar uma tela a partir de um mockup

**Cenário:** tenho uma imagem de uma landing page ou dashboard e quero transformá-la em uma página navegável.

**Como usar:**

```text
/criar-site imagem="C:/referencias/dashboard.png" slug=dashboard
```

**O que acontece:** o processo começa com wireframe e plano. Depois, fundo, componentes, tipografia, assets e revisão são tratados em etapas.

**Resultado esperado:** uma pasta com HTML, CSS e recursos locais, além do registro das decisões e aprovações.

## 2. Criar uma landing page a partir de uma ideia

**Cenário:** tenho uma ideia, mas ainda não tenho layout pronto.

**Como usar:**

```text
/criar-site brief="Landing para um produto digital, com hero, benefícios, depoimentos e CTA" slug=produto-digital
```

**O que acontece:** a estrutura é planejada com base no briefing. Como não existe imagem de referência, a comparação por pixels não é aplicável.

## 3. Criar uma identidade visual consistente

**Cenário:** gosto da linguagem visual de um site e quero usar princípios semelhantes em um projeto próprio.

**Como usar:**

```text
/extrair-ds url=https://exemplo.com slug=referencia
```

**O que acontece:** a skill captura a referência, organiza tokens e componentes e pede aprovação dos fundamentos e das regras.

**Cuidado:** a intenção é entender e documentar regras visuais, não copiar marca, textos ou imagens protegidas.

## 4. Combinar referências diferentes

**Cenário:** quero a paleta de um projeto, a tipografia de outro e as formas de um terceiro.

**Como usar:**

```text
/combinar-ds nome=identidade-nova base=linear cores=posthog tipografia=stripe
```

**O que acontece:** a skill combina grupos de tokens e gera um novo catálogo para revisão.

## 5. Validar um site antes de entregar

**Cenário:** terminei a implementação e quero conferir se os arquivos estão organizados corretamente.

**Como usar:**

```bash
python 02_criador-de-sites/02_scripts/validar_site.py 02_criador-de-sites/04_sites/meu-site
```

O validador procura problemas como arquivos ausentes, caminhos que saem da pasta do site, estilos ou scripts inline e referências a frameworks/CDNs não permitidos pelas regras do projeto.

## 6. Medir sem depender apenas do olhar

**Cenário:** preciso descobrir se uma cor, posição ou região está próxima da imagem original.

**Ferramentas:**

- `02_criador-de-sites/02_scripts/recortar.py`: cria grades e recortes para localizar regiões.
- `02_criador-de-sites/02_scripts/amostrar_cores.py`: identifica cores e paletas.
- `02_criador-de-sites/02_scripts/capturar_tela.py`: gera uma captura do site.
- `02_criador-de-sites/02_scripts/comparar.py`: mostra diferenças entre referência e resultado.

A medição ajuda a encontrar problemas, mas a decisão final continua sendo visual e humana.

## Para quem a NOVYRA pode ser útil

- Designers que querem transformar referências em páginas funcionais.
- Desenvolvedores que desejam estruturar o trabalho com IA em etapas.
- Criadores de produtos digitais que precisam de landing pages e interfaces.
- Pessoas que querem estudar e reutilizar design systems.
- Equipes que precisam revisar visualmente uma implementação.

## O que não deve ser prometido nesta versão

A NOVYRA não deve ser apresentada como um construtor de sites hospedado, uma plataforma SaaS, um modelo próprio de IA ou um sistema de machine learning treinado automaticamente. O pacote documentado é um conjunto experimental de skills e ferramentas auxiliares executadas no ambiente local com Claude Code.
