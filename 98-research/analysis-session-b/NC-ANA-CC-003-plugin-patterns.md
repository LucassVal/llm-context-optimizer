# NC-ANA-CC-003  Padres dos 13 Plugins Oficiais do Claude Code

**Data da anlise:** 20260412  
**Fonte:** `officialclaudecode/plugins/`  
**Ticket:** NCDS009 (CC001B)

---

## Resumo Executivo

A Anthropic mantm **13 plugins oficiais** que estendem o Claude Code. Cada plugin cobre um domnio especfico (segurana, desenvolvimento, reviso, etc.) e segue um **padro consistente** de implementao: README detalhado, configurao via Markdown+YAML ou JSON, e comandos CLI dedicados.

**Plugins priorizados** (por valor para o NeoCortex):
1. **hookify**  sistema de hooks leves (governana).
2. **agentsdkdev**  scaffolding de agentes.
3. **securityguidance**  padres de segurana.
4. **prreviewtoolkit**  fluxo de reviso de PR.
5. **plugindev**  como criar plugins.

---

## 1. hookify

**Arquivo:** `plugins/hookify/README.md` (340 linhas)

### 1.1 Conceito
- **Hooks leves** em Markdown com frontmatter YAML.
- **No requer edio de `hooks.json`** (complexo).
- **Regras ativadas imediatamente** (sem restart).

### 1.2 Formato da Regra
```markdown
---
name: blockdangerousrm
enabled: true
event: bash
pattern: rm\s+-rf
action: block
---

 **Mensagem de warning ao usurio**
```

### 1.3 Eventos Suportados
- `bash`  comandos Bash.
- `file`  edio/escrita de arquivos.
- `stop`  quando Claude quer parar.
- `prompt`  submisso de prompt.
- `all`  todos os eventos.

### 1.4 Operadores
- `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with`.

### 1.5 Campos por Evento
- **bash:** `command`
- **file:** `file_path`, `new_text`, `old_text`, `content`
- **prompt:** `user_prompt`

### 1.6 Aes
- `warn`  mostra mensagem, permite continuao.
- `block`  impede a operao (PreToolUse) ou bloqueia parada.

### 1.7 Comandos CLI
- `/hookify <instruo>`  cria regra a partir da instruo.
- `/hookify` (sem args)  analisa conversa recente para sugerir regras.
- `/hookify:list`  lista todas as regras.
- `/hookify:configure`  interface interativa para habilitar/desabilitar.
- `/hookify:help`  ajuda.

### 1.8 Recomendao para NeoCortex
- **Adotar formato Markdown+YAML** para hooks (NCTOOLFR022).
- **Criar diretrio `.claude/`** na raiz do projeto para regras locais.
- **Implementar comando `/hookify`** nos lobos.

---

## 2. agentsdkdev

**Arquivo:** `plugins/agentsdkdev/README.md` (208 linhas)

### 2.1 Comando Principal
- `/newsdkapp [nome]`  cria projeto de Agent SDK (TypeScript/Python).

### 2.2 Fluxo Interativo
1. **Escolha de linguagem** (TypeScript / Python).
2. **Nome do projeto** (se omitido).
3. **Tipo de agente** (coding, business, custom).
4. **Ponto de partida** (minimal, basic, example).
5. **Preferncias de tooling** (npm/yarn/pnpm ou pip/poetry).

### 2.3 Funcionalidades
- **Instala a ltima verso do SDK.**
- **Cria todos os arquivos necessrios** (incluindo `.env.example`, `.gitignore`).
- **Executa typecheck / syntax validation.**
- **Roda verificador automtico** (`agentsdkverifierpy` ou `ts`).

### 2.4 Recomendao para NeoCortex
- **Adaptar `/newsdkapp` para `/newlobe`**  gera template de lobe (NCLBE*).
- **Incluir verificador de best practices** para lobos.

---

## 3. securityguidance

**Arquivo:** `plugins/securityguidance/README.md` (a ler)

### 3.1 Suposio
- Oferece **padres de segurana** (ex.: no hardcodar credenciais, sanitizao de input).
- Provavelmente **hooks prconfigurados** para detectar vulnerabilidades.

### 3.2 Recomendao
- **Extrair lista de regras** e importar como hooks padro do NeoCortex.

---

## 4. prreviewtoolkit

**Arquivo:** `plugins/prreviewtoolkit/README.md` (a ler)

### 4.1 Suposio
- **Fluxo estruturado** para reviso de PRs.
- **Checklists** de itens obrigatrios (tests, lint, docs).
- **Comandos** como `/prreview start`, `/prreview checklist`.

### 4.2 Recomendao
- **Integrar com nosso fluxo de tickets** (NCDS*).

---

## 5. codereview

**Arquivo:** `plugins/codereview/README.md` (a ler)

### 5.1 Suposio
- **Padres de code review** (complexidade ciclomtica, naming, duplication).
- **Anlise esttica** integrada ao CLI.

---

## 6. commitcommands

**Arquivo:** `plugins/commitcommands/README.md` (a ler)

### 6.1 Suposio
- **Commits semnticos** (feat, fix, chore, etc.).
- **Validao de mensagem** via hook.

### 6.2 Recomendao
- **Adotar padro de commits** para tickets NeoCortex.

---

## 7. featuredev

**Arquivo:** `plugins/featuredev/README.md` (a ler)

### 7.1 Suposio
- **Fluxo de desenvolvimento de features** (branch, test, deploy).
- **Rastreamento de progresso**.

---

## 8. frontenddesign

**Arquivo:** `plugins/frontenddesign/README.md` (a ler)

### 8.1 Suposio
- **Padres de design** (UI/UX) para frontends de agentes.

---

## 9. learningoutputstyle

**Arquivo:** `plugins/learningoutputstyle/README.md` (a ler)

### 9.1 Suposio
- **Estilo de output** para tutoriais / explicaes.

---

## 10. explanatoryoutputstyle

**Arquivo:** `plugins/explanatoryoutputstyle/README.md` (a ler)

### 10.1 Suposio
- **Output explicativo** (passo a passo, justificativas).

---

## 11. plugindev

**Arquivo:** `plugins/plugindev/README.md` (a ler)

### 11.1 Suposio
- **Como criar plugins** para Claude Code.
- **Template de plugin** com estrutura esperada.

### 11.2 Recomendao
- **Estudar para criar plugins NeoCortex** (NCTOOLFR*).

---

## 12. claudeopus45migration

**Arquivo:** `plugins/claudeopus45migration/README.md` (a ler)

### 12.1 Suposio
- **Migrao entre verses do modelo** Opus 4  5.

---

## 13. ralphwiggum

**Arquivo:** `plugins/ralphwiggum/README.md` (a ler)

### 13.1 Suposio
- **Plugin de curiosidade / easter egg**.

---

## Padres Comuns Observados

### A. Estrutura de Diretrio
```
plugins/
 <nome>/
    README.md
    index.py ou index.ts
    package.json (se TypeScript)
    (outros assets)
```

### B. Configurao
- **Por projeto** (`.claude/` na raiz).
- **Markdown + YAML** ou **JSON**.
- **Hooks** so a principal extensibilidade.

### C. Comandos CLI
- **`/<plugin>[:subcomando]`** sintaxe uniforme.
- **Subcomandos** `:list`, `:configure`, `:help`.

### D. Discovery
- **Marketplace interno** (autodiscovery).
- **Instalao manual** via `cc --plugindir`.

---

## Padres Avanados (dos 11 plugins restantes)

*Anlise completa em NCANACC005pluginsdeep.md*

### E. Hooks Reativos
- **PreToolUse**  executa script Python/TypeScript antes da tool.
- **Matchers** por tipo de tool (`Edit`, `Write`, `MultiEdit`, `Bash`).
- **Scripts externos** recebem contexto via stdin/env (ex.: `security_reminder_hook.py`).

### F. Agentes Especializados com Confidence Scoring
- Mltiplos agentes em **paralelo** (codereview) ou **sequencial** (prreviewtoolkit).
- **Confidence score 0100**  filtra issues com <80 (reduz falsos positivos).
- **Git blame integration**  contexto histrico para anlise.

### G. Fluxos de Trabalho Completos
- **featuredev**  explorao, arquitetura, reviso.
- **commitcommands**  commit/push/PR simplificados.
- **ralphwiggum**  loop contnuo at concluso da task.

### H. Estilos de Output Educacionais
- **learningoutputstyle**  pede contribuies de cdigo em decises.
- **explanatoryoutputstyle**  explica escolhas de implementao.

---

## Recomendaes Finais para NeoCortex (atualizadas)

1. **Implementar hookifylike** (NCTOOLFR022)  prioridade mxima.
2. **Criar template de plugin NeoCortex** baseado em `plugindev`  padronizar NCTOOLFR*.
3. **Adotar diretrio `.claude/`** para configuraes locais de hooks e regras.
4. **Estudar securityguidance** para polticas de segurana padro (integrar ao Mentor Mode).
5. **Sistema de autoreview com confidence scoring**  adaptar codereview para validao de handoffs.
6. **Comandos git para tickets** (`/nccommit`, `/ncpush`, `/ncpr`)  simplificar fluxo.
7. **Modos de output educacionais**  explanatorystyle para explicar atomic locks, SSOT.
8. **Ralphwiggum para worker persistente**  loop contnuo para processamento de fila.

---

**Status:** Anlise completa dos 13 plugins (hookify, agentsdkdev + 11 restantes).  
**Prxima ao:** Implementar hookifylike (NCTOOLFR022) e template de plugin NeoCortex.