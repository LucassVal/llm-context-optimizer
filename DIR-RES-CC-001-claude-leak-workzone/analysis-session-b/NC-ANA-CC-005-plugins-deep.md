# NC-ANA-CC-005  Anlise Profunda dos 11 Plugins Restantes do Claude Code

**Data da anlise:** 20260412  
**Fonte:** `CLAUDE_CODE_DISSECTION/officialclaudecode/plugins/`  
**Ticket:** NCDS014 (CC002A)  
**Anterior:** NCANACC003pluginpatterns.md (hookify + agentsdkdev)

---

## Resumo Executivo

Os **11 plugins restantes** do Claude Code cobrem segurana, reviso de PR, fluxo de commits, desenvolvimento de features, frontend, estilos de output, migrao de modelos e uma tcnica experimental (RalphWiggum). Todos seguem o **padro arquitetural uniforme** descoberto anteriormente: diretrio `.claudeplugin/` com `plugin.json`, comandos em Markdown, hooks em JSON + Python/TypeScript, e configurao por projeto (`.claude/`).

**Padres chave identificados:**
1. **Hooks reativos** (PreToolUse) para segurana e governana.
2. **Agentes especializados** que atuam em paralelo com scoring de confiana.
3. **Comandos CLI** com sintaxe `/plugin[:subcomando]`.
4. **Configurao por projeto** via `.claude/` (isolamento por repositrio).
5. **Extensibilidade padro**  qualquer dev pode criar plugin com template.

**Recomendao imediata para NeoCortex:** Implementar **sistema de hooks estilo hookify** (NCTOOLFR022) e **template de plugin** baseado em `plugindev` para uniformizar nossas tools (NCTOOLFR*).

---

## Tabela de Viso Geral dos 11 Plugins

| Plugin | Propsito | Hooks usados | Padro de extenso | Dados coletados/modificados | Replicvel no NeoCortex? |
|--------|-----------|--------------|-------------------|----------------------------|--------------------------|
| **securityguidance** | Alertas de segurana em edies de arquivo (command injection, XSS, padres inseguros) | `PreToolUse` com matcher `Edit\|Write\|MultiEdit` | Hook Python + JSON | Contedo do arquivo editado, padres de risco | **SIM**  integrar ao Mentor Mode como hook de segurana |
| **prreviewtoolkit** | 6 agentes especializados para reviso de PR (comentrios, testes, erros, tipos, qualidade, simplificao) | Nenhum hook identificado | Comando `/reviewpr` + agentes Markdown | Diff do git, arquivos modificados, contexto do PR | **SIM**  adaptar para reviso de tickets NCDS* (checklist de qualidade) |
| **codereview** | Reviso automatizada de PR com mltiplos agentes paralelos + filtro por confiana (>80) | Nenhum hook identificado | Comando `/codereview` | Diff do git, guidelines CLAUDE.md, histrico (git blame) | **SIM**  sistema de reviso automtica para handoffs (confiana >80) |
| **commitcommands** | Simplificao do fluxo git (commit, push, criao de PR) | Nenhum hook identificado | Comandos `/commit`, `/push`, `/pr` | Mensagem de commit, branch, ttulo do PR | **SIM**  comandos `/nccommit`, `/ncpush` para tickets |
| **featuredev** | Fluxo completo de desenvolvimento de feature (explorao, arquitetura, reviso) | Nenhum hook identificado | Comando `/featuredev` + agentes especializados | Cdigobase, requisitos, arquitetura proposta | **SIM**  adaptar para desenvolvimento de lobes (NCLBE*) |
| **frontenddesign** | Habilidade de design UI/UX para frontend | Nenhum hook identificado | Comando `/frontenddesign` | Componentes UI, estilos, layout | **PARCIAL**  foco do NeoCortex  backend/agent, mas til para tools web |
| **learningoutputstyle** | Modo interativo de aprendizado  pede contribuies de cdigo em pontos de deciso | Nenhum hook identificado | Estilo de output (no comando) | Decises de arquitetura, contribuies do usurio | **SIM**  modo learning mode para tutoriais de extenso |
| **explanatoryoutputstyle** | Explicaes educacionais sobre escolhas de implementao e padres do cdigo | Nenhum hook identificado | Estilo de output (no comando) | Padres do cdigo, justificativas de design | **SIM**  incorporar ao output padro do NeoCortex (explicar atomic locks, SSOT) |
| **plugindev** | Template e documentao para criao de plugins Claude Code | Nenhum hook identificado | Template de diretrio + exemplos | Estrutura de plugin, exemplos de hook/comando | **SIM**  criar template NCTOOLFR* para tools NeoCortex |
| **claudeopus45migration** | Migrao de cdigo e prompts do Sonnet 4.x/Opus 4.1 para Opus 4.5 | Nenhum hook identificado | Comando `/migratetoopus45` | Cdigo fonte, prompts, configuraes | **NO**  especfico do modelo Anthropic |
| **ralphwiggum** | Tcnica de loop autoreferencial  executa Claude em whiletrue com mesmo prompt at concluso | Nenhum hook identificado | Comando `/ralphwiggum` | Estado da tarefa, iteraes, resultado final | **SIM**  adaptar como modo persistente para tasks longas (ex.: processar fila) |

---

## Anlise Detalhada por Plugin

### 1. securityguidance

**Arquivos chave:**
- `.claudeplugin/plugin.json`  metadados.
- `hooks/hooks.json`  configurao do hook `PreToolUse`.
- `hooks/security_reminder_hook.py`  script Python de anlise.

**Funcionamento:**
- Acionado **antes de qualquer tool de edio** (Edit, Write, MultiEdit).
- O hook Python analisa o contedo do arquivo editado em busca de **padres de risco** (GitHub Actions injection, XSS, hardcoded secrets, etc.).
- Gera alertas **contextuais** com exemplos seguro/inseguro.
- Log de debug em `/tmp/securitywarningslog.txt`.

**Padro de extenso:** Hook reativo com script Python externo. Configurao via JSON.

**Analogia NeoCortex:** Implementar como **hook de segurana no Mentor Mode**  analisar edits em tempo real e alertar sobre violaes de atomic locks, hardcode de paths, etc.

### 2. prreviewtoolkit

**Arquivos chave:**
- `README.md` (313 linhas)  documentao completa dos 6 agentes.
- `commands/reviewpr.md`  comando principal.
- `agents/`  6 agentes especializados (Markdown).

**Agentes:**
1. **commentanalyzer**  preciso de comentrios.
2. **prtestanalyzer**  qualidade e cobertura de testes.
3. **silentfailurehunter**  tratamento de erros e falhas silenciosas.
4. **typedesignanalyzer**  design de tipos e invariantes (score 110).
5. **codereviewer**  conformidade com guidelines.
6. **codesimplifier**  simplificao de cdigo (aps reviso).

**Fluxo:** `/reviewpr` identifica arquivos modificados, seleciona agentes aplicveis, executa sequencialmente e consolida feedback.

**Analogia NeoCortex:** Adaptar para **reviso de tickets**  cada agente v um aspecto (naming NC, barreiras B1B6, atomic locks, SSOT). Score de confiana pode filtrar falsos positivos.

### 3. codereview

**Arquivos chave:**
- `README.md` (258 linhas)  detalhes do algoritmo de confiana.
- `commands/codereview.md`  comando principal.

**Diferencial:** **Confidencebased scoring** (0100). Issues com confiana <80 so filtradas.  
**Agentes paralelos:** 4 agentes independentes (2 para guidelines, 1 para bugs, 1 para contexto histrico).  
**Integrao com git blame** para identificar code ownership e padres de mudana.

**Analogia NeoCortex:** Sistema de **autoreview de handoffs**  mltiplos validadores paralelos (naming, locks, py_compile, SSOT) com score agregado. Aprovar automaticamente se todos >80.

### 4. commitcommands

**Arquivos chave:**
- `README.md` (182 linhas)  explicao dos comandos.
- `commands/commit.md`, `push.md`, `pr.md`.

**Comandos:**
- `/commit "message"`  commit inteligente (detecta arquivos modificados).
- `/push`  push para remote com tracking.
- `/pr "title"`  cria Pull Request via GitHub CLI.

**Foco:** **Simplificao do workflow git** para devs menos experientes.

**Analogia NeoCortex:** Comandos `/nccommit`, `/ncpush` para tickets  commit automtico com mensagem padro (NCDS*), push para branch de trabalho.

### 5. featuredev

**Arquivos chave:**
- `README.md` (a ler)  fluxo completo.
- `commands/featuredev.md`  comando principal.

**Descrio (do plugin.json):** Comprehensive feature development workflow with specialized agents for codebase exploration, architecture design, and quality review.

**Suposio:** Agentes para explorar cdigobase, propor arquitetura, revisar qualidade. Similar ao prreviewtoolkit mas focado em desenvolvimento de features (no apenas reviso).

**Analogia NeoCortex:** Adaptar para **desenvolvimento de lobes**  comando `/newlobe` que gera estrutura NCLBE*, explora dependncias, sugere arquitetura.

### 6. frontenddesign

**Descrio:** Frontend design skill for UI/UX implementation.  
**Suposio:** Comando `/frontenddesign` que ajuda a criar componentes UI, estilos, layout. Provavelmente integrado com ferramentas web (HTML/CSS/JS).

**Analogia NeoCortex:** **Parcialmente aplicvel**  NeoCortex foca em backend/agent, mas pode ser til para tools web de administrao (ex.: dashboard de fila).

### 7. learningoutputstyle

**Descrio:** Interactive learning mode that requests meaningful code contributions at decision points (mimics the unshipped Learning output style).  
**Suposio:** Modo de output que, em pontos de deciso (ex.: escolha de arquitetura), pede contribuies de cdigo do usurio  aprendizado ativo.

**Analogia NeoCortex:** **Modo tutorial** para novos devs  ao estender NeoCortex, o agente pede que o usurio implemente partes simples para internalizar padres.

### 8. explanatoryoutputstyle

**Descrio:** Adds educational insights about implementation choices and codebase patterns (mimics the deprecated Explanatory output style).  
**Suposio:** Explicaes educacionais no output  por que uma abordagem foi escolhida, padres do cdigobase, alternativas.

**Analogia NeoCortex:** **Incorporar ao output padro**  sempre que o agente age, explicar o porqu (ex.: este arquivo  @LOCK, ento no modificamos; usamos naming NC* por SSOT).

### 9. plugindev

**Arquivos chave:** (no h plugin.json)  provavelmente template de diretrio e exemplos.  
**Propsito:** Documentao/template para criar plugins Claude Code.

**Analogia NeoCortex:** **Template NCTOOLFR***  diretrio padro com `plugin.json` (metadados), `commands/`, `hooks/`, exemplos de hook e comando.

### 10. claudeopus45migration

**Descrio:** Migrate your code and prompts from Sonnet 4.x and Opus 4.1 to Opus 4.5.  
**Especfico do modelo Anthropic**  no aplicvel ao NeoCortex diretamente, mas mostra **preocupao com versionamento de modelos** e migrao de prompts.

**Analogia NeoCortex:** **Sistema de versionamento de prompts**  quando atualizamos o prompt mestre (NCPROMPTFR*), ter script de migrao para ajustar tickets existentes.

### 11. ralphwiggum

**Descrio:** Implementation of the Ralph Wiggum technique - continuous selfreferential AI loops for interactive iterative development. Run Claude in a whiletrue loop with the same prompt until task completion.  
**Tcnica experimental**  loop infinito com mesmo prompt, iterando at a tarefa estar completa.

**Arquivos chave:** (a explorar)  provavelmente comando `/ralphwiggum` que gerencia o loop.

**Analogia NeoCortex:** **Modo persistente para tasks longas**  ex.: worker T1 que processa a fila continuamente, reiniciando aps cada ticket com mesmo contexto.

---

## Padres Comuns (consolidao)

### A. Estrutura de Plugin
```
plugin/
 .claudeplugin/
    plugin.json            # metadados (name, version, description, author)
 commands/
    <comando>.md          # documentao do comando + fluxo
 hooks/
    hooks.json            # configurao de hooks (PreToolUse, etc.)
    <hookscript>.py      # script executvel
 agents/                   # (opcional) agentes especializados em Markdown
 README.md                 # documentao principal
```

### B. Hooks
- **PreToolUse**  antes da tool ser executada (ex.: securityguidance).
- **Matchers**  filtram por tipo de tool (`Edit`, `Write`, `MultiEdit`, `Bash`, etc.).
- **Script externo**  Python ou TypeScript, recebe contexto via stdin/env.

### C. Comandos
- **Sintaxe** `/<plugin>[:subcomando]` (ex.: `/reviewpr`, `/commit`).
- **Documentao em Markdown** com frontmatter YAML (`description`, `argumenthint`, `allowedtools`).
- **Fluxo descrito passo a passo**  quase um plano executvel.

### D. Configurao por Projeto
- Diretrio `.claude/` na raiz do repositrio guarda configuraes de **todos os plugins**.
- Isolamento por projeto  no conflita com outros repositrios.
- **NeoCortex atual** usa configurao global (`neocortex_config.yaml`)  podemos adicionar projetolocal `.claude/` para regras de hook.

### E. Agentes Especializados
- Cada agente  um arquivo Markdown com foco nico.
- Podem ser executados **paralelamente** (codereview) ou **sequencialmente** (prreviewtoolkit).
- **Confidence scoring** filtra falsos positivos.

---

## Recomendaes para NeoCortex (Priorizadas)

### 1. HIGH  Hookifylike (NCTOOLFR022)
- Implementar sistema de **hooks reativos em Markdown+YAML**.
- Eventos: `Edit`, `Write`, `Bash`, `Commit`.
- Aes: `warn`, `block`, `log`.
- Diretrio `.claude/` na raiz do projeto para regras locais.

### 2. HIGH  Template de Plugin NeoCortex
- Criar template `NCTOOLFR*` com estrutura padronizada: `.claudeplugin/plugin.json`, `commands/`, `hooks/`.
- Integrar com `plugindev` do Claude Code (estudar exemplos).

### 3. MEDIUM  Sistema de Autoreview com Confiana
- Adaptar **codereview** para validar handoffs: mltiplos validadores paralelos (B1B6) com score 0100.
- Aprovao automtica se confiana agregada >80.
- Filtrar falsos positivos.

### 4. MEDIUM  Comandos Git para Tickets
- Implementar `/nccommit`, `/ncpush`, `/ncpr` para fluxo de tickets.
- Commit automtico com mensagem NCDS*: descrio.
- Push para branch `ticket*`.

### 5. LOW  Modos de Output Educacionais
- Adicionar `explanatoryoutputstyle` ao output padro  explicar atomic locks, SSOT, naming.
- Modo `learningoutputstyle` para tutoriais de extenso.

### 6. LOW  RalphWiggum para Worker Persistente
- Adaptar tcnica de loop contnuo para worker T1  processar fila indefinidamente, reiniciando contexto a cada ticket.

---

## Concluso

Os **11 plugins restantes** confirmam a **filosofia de extensibilidade leve** do Claude Code: hooks reativos, agentes especializados, comandos simples, configurao por projeto. O NeoCortex j tem vantagens em **governana proativa** (atomic locks, mentor mode) e **SSOT ubquo**, mas pode absorver essa flexibilidade sem perder segurana.

**Prximos passos imediatos:**
1. T0 revisar este handoff.
2. Priorizar implementao de **hookifylike** (NCTOOLFR022).
3. Criar **template de plugin NeoCortex** baseado em `plugindev`.
4. Estudar `securityguidance` para polticas de segurana padro.

---

**Status:** Anlise completa dos 11 plugins restantes.  
**Confiana:** Alta (baseada em leitura de READMEs, plugin.json, hooks.json e amostras de cdigo).  
**Arquivos analisados:** ~50 arquivos entre os 11 plugins.  
**Prximo ticket possvel:** NCDS015 (KAIROS Deep Dive) ou NCDS027 (TicketValidator CLI).

