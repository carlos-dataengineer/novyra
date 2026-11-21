# Guia de instalação e uso

Este guia reúne o caminho mais direto para preparar a NOVYRA e começar a trabalhar com o Criador de Sites.

## 1. O que preciso ter instalado

- Claude Code, no aplicativo desktop ou no terminal.
- Python 3.10 ou superior.
- Microsoft Edge ou Google Chrome.
- Acesso ao terminal do sistema.

Algumas tarefas também usam Playwright. A geração de imagens é opcional e depende de uma chave OpenRouter.

## 2. Instalar as dependências Python

Abra o terminal na pasta do projeto e execute:

```bash
cd 02_criador-de-sites\npython -m pip install -r requirements.txt
```

Para os fluxos de captura com Playwright, instale o navegador:

```bash
python -m playwright install chromium
```

O projeto também documenta uso do Chrome ou Edge já instalado para capturas. Se a configuração do navegador exigir ajustes, consulte a ajuda do script correspondente.

## 3. Instalar as skills

Na raiz da pasta do Criador de Sites:

```bash
python 02_criador-de-sites/01_skills/instalar_skills.py
```

Depois, reinicie a sessão do Claude Code para que as skills apareçam.

## 4. Criar um site a partir de uma imagem

Tenha uma imagem de referência salva no computador. Depois, no Claude Code, use:

```text
/criar-site imagem="C:/mocks/painel.png" slug=painel-vendas
```

A NOVYRA prepara a pasta do site, monta o wireframe e apresenta o plano de implementação. O processo só avança depois da aprovação de cada etapa.

## 5. Criar um site a partir de um briefing

Quando não houver imagem, descreva o que precisa:

```text
/criar-site brief="Landing de cafeteria com hero, cardápio em 3 cards e rodapé" slug=landing-cafe
```

Nesse modo, a IA usa o briefing para montar a estrutura. A comparação por pixels com uma referência não se aplica quando não existe imagem original.

## 6. Usar um design system

Primeiro, extraia a identidade visual de um site que você pode usar como referência:

```text
/extrair-ds url=https://linear.app slug=linear
```

A skill organiza os fundamentos e os componentes em etapas de revisão. Depois, você pode usar esse sistema na criação de um site:

```text
/criar-site brief="Landing de produto com hero e três recursos" slug=landing-produto ds=linear
```

Para misturar características de diferentes sistemas:

```text
/combinar-ds nome=painel-noturno base=linear tipografia=stripe
```

Use apenas referências que você tem autorização para analisar. A identidade visual deve ser interpretada e documentada; não copie logotipos, textos, fotos ou ilustrações da fonte.

## 7. Scripts úteis

Todos os scripts podem exibir suas opções com `--help`.

```bash
python 02_criador-de-sites/02_scripts/novo_site.py meu-site --imagem "C:/mocks/tela.png"
python 02_criador-de-sites/02_scripts/recortar.py 04_sites/meu-site/reference.png --grade 100
python 02_criador-de-sites/02_scripts/amostrar_cores.py 04_sites/meu-site/reference.png --caixa 0,0,1440,80 --paleta 6
python 02_criador-de-sites/02_scripts/capturar_tela.py 04_sites/meu-site --igual-referencia
python 02_criador-de-sites/02_scripts/comparar.py 04_sites/meu-site/reference.png 04_sites/meu-site/_capturas/captura-1440x900.png --lado-a-lado
python 02_criador-de-sites/02_scripts/validar_site.py 04_sites/meu-site
```

## 8. Geração opcional de imagens

A geração de imagens usa OpenRouter e pode gerar cobrança.

1. Crie uma chave no serviço OpenRouter.
2. Copie `.env.example` para `.env`.
3. Preencha `OPENROUTER_API_KEY`.
4. Antes de enviar qualquer imagem ou prompt, confira o conteúdo e confirme que pode compartilhá-lo com o serviço externo.
5. Não envie informações internas, dados pessoais ou materiais confidenciais.

Nunca publique o arquivo `.env`.

## 9. Como funciona a aprovação

Em cada etapa, a skill deve:

1. Mostrar o resultado e os arquivos produzidos.
2. Explicar decisões e aproximações.
3. Pedir aprovação ou correção.
4. Parar até receber uma aprovação explícita.
5. Registrar o estado da etapa.

A aprovação humana faz parte do método. Não é necessário aceitar um resultado só porque a IA o produziu.

## 10. Problemas comuns

### A skill não aparece no Claude Code
Confira se o instalador foi executado sem erro e reinicie a sessão.

### O Python não encontra uma biblioteca
Instale novamente as dependências com `cd 02_criador-de-sites\npython -m pip install -r requirements.txt`.

### A captura não abre ou falha
Confira se Edge ou Chrome está instalado e se o navegador está acessível. Para fluxos Playwright, execute `python -m playwright install chromium`.

### A comparação não fica alta
Veja o mapa de diferenças e as regiões com maior divergência. A nota é uma referência de diagnóstico, não uma garantia de qualidade visual.

### A geração de imagens não funciona
Confira a chave OpenRouter, a conexão, os limites da conta e se a chamada foi autorizada.

## 11. Observação sobre a skill expert-asimov

A skill `expert-asimov` depende de uma base complementar em `../01_pesquisa/canal-asimov-expert/`. A base de pesquisa está organizada em `01_pesquisa/`, na raiz do repositório. O Criador de Sites fica em `02_criador-de-sites/`. Essa relação de pastas é necessária para a skill `expert-asimov` localizar os materiais.
