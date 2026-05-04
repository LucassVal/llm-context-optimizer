# NC-SOP-FR-003 — Padrão de Criação de Lobos
**Procedimento Operacional Padrão — Rotina completa de criação de qualquer novo lobo NeoCortex**
**Hash:** `SOP-LOBE-v1.0-20260504` | **ULQ:** `#SOP_LOBES`

---

## 1. 3W — VISÃO GERAL

| 3W | Resposta |
|----|----------|
| **WHAT** | Rotina padrão obrigatória de 10 passos para criar QUALQUER novo lobo no sistema NeoCortex. Cobre desde a verificação do manifesto até a validação final. |
| **WHY** | Evitar lobos fantasmas (registrados no CSV mas sem arquivo .mdc), UBL/LEXICO ausentes (seções inencontráveis), e formatos inconsistentes. Todo lobo DEVE seguir o mesmo padrão para ser indexável, buscável e auditável. |
| **WHERE** | `02_memory_lobes/{domain}/` + `DIR-DS-003-lobe-manifest/NC-MAN-LOBE-001.csv` + `NC-CHG-FR-001-changelog.yaml` |

**Princípio KISS:** 1 lobo por vez. Validar. Só depois criar o próximo.

---

## 2. EISENHOWER — PRIORIDADES

| Quadrante | O que | Quando |
|-----------|-------|--------|
| 🔴 **URG+IMP** | Consultar NC-MAN-LOBE-001.csv pelo próximo ID disponível | Antes de QUALQUER criação |
| 🟡 **IMP+N_URG** | Criar arquivo .mdc com frontmatter + 3W + UBL/LEXICO | Após ID reservado |
| 🟢 **URG+N_IMP** | Registrar no CSV + CHANGELOG + validar | Após arquivo criado |
| ⚪ **N_URG+N_IMP** | Wire em @LOCKS se necessário + documentar no SSOT | Iteração contínua |

---

## 3. FORMATO OBRIGATÓRIO DO LOBO (.mdc)

Antes de criar qualquer arquivo, verifique se o lobo ATENDE TODOS os 6 requisitos de formato:

### 3.1 Requisito 1 — YAML Frontmatter

Todo lobo DEVE abrir com frontmatter YAML entre `---` contendo os campos obrigatórios:

```yaml
---
lobe_id: "NC-LBE-{DOMAIN}-{NNN}"
name: "Nome legível do lobo"
status: "active"            # active | draft | archived
version: "1.0"
created_at: "2026-05-04"
tags: ["tag1", "tag2", "tag3"]
domain: "01_architecture"   # diretório dentro de 02_memory_lobes/
layer: "framework"          # camada lógica
---
```

| Campo | Obrigatório? | Descrição | Exemplo |
|-------|-------------|-----------|---------|
| `lobe_id` | ✅ SIM | ID único seguindo NC-LBE-{DOMAIN}-{NNN} | `NC-LBE-FR-ARCH-007` |
| `name` | ✅ SIM | Nome legível para busca semântica | `Arquitetura de Runtime` |
| `status` | ✅ SIM | `active`, `draft`, ou `archived` | `active` |
| `version` | ✅ SIM | Versão semântica | `1.0` |
| `created_at` | ✅ SIM | Data ISO 8601 (YYYY-MM-DD) | `2026-05-04` |
| `tags` | ✅ SIM | Array de tags para LEXICO | `["runtime", "hooks", "mcp"]` |
| `domain` | ✅ SIM | Subdiretório em 02_memory_lobes/ | `01_architecture` |
| `layer` | ✅ SIM | Camada lógica do sistema | `framework` |

### 3.2 Requisito 2 — Bloco 3W (What / Why / Where)

Após o frontmatter, o lobo DEVE conter o bloco 3W como cabeçalhos H2:

```markdown
## What
[Descrição em 1 frase do que É este lobo — funcionalidade, escopo, propósito direto]

## Why
[Por que este lobo EXISTE — problema que resolve, lacuna que preenche, rastreabilidade]

## Where
[Caminho físico do arquivo + diretório + relação com outros lobos]
```

**Regra R42:** O 3W NUNCA deve ser genérico ("Módulo: NC LBE FR XYZ" é INSUFICIENTE). Deve descrever o CONTEÚDO REAL.

### 3.3 Requisito 3 — @UBL + LEXICO em TODO H1

**TODA** seção H1 (`#`) DEVE ser precedida por:

```markdown
@UBL {NomeDoTopico}
LEXICO: #tag1 #tag2 #tag3
# 1. Título da Seção
```

- `@UBL {NomeDoTopico}` — âncora semântica para bookmarking (ex: `@UBL DeepSeek-V4`)
- `LEXICO: #tag1 #tag2` — tags para busca por tópico no LEXICO
- Espaçamento: 1 linha em branco entre LEXICO e o heading

### 3.4 Requisito 4 — @UBL + LEXICO em TODO H2

**TODA** seção H2 (`##`) também DEVE ser precedida por @UBL + LEXICO:

```markdown
@UBL {NomeDoTopico}
LEXICO: #subtema1 #subtema2
## 1.1 Subtítulo da Seção
```

### 3.5 Requisito 5 — Numeração de Seções

TODAS as seções DEVEM ser numeradas hierarquicamente:

```markdown
# 1. Primeiro Tópico
## 1.1 Subtítulo
## 1.2 Subtítulo
### 1.2.1 Detalhe
# 2. Segundo Tópico
## 2.1 Subtítulo
```

**Regra:** O número acompanha o nível de profundidade. H1 = `# N.`, H2 = `## N.M`, H3 = `### N.M.P`.

### 3.6 Requisito 6 — Nomenclatura do Arquivo

O nome do arquivo DEVE seguir o padrão:

```
NC-LBE-{DOMAIN}-{NNN}-{description}.mdc
```

| Parte | Significado | Exemplo |
|-------|-------------|---------|
| `NC-` | Prefixo obrigatório NeoCortex | `NC-` |
| `LBE-` | Tipo: Lobe | `LBE-` |
| `{DOMAIN}` | Sigla do domínio (2-4 letras) | `FR`, `INT`, `DS`, `CC`, `USR` |
| `{NNN}` | Número sequencial de 3 dígitos | `001`, `042`, `157` |
| `{description}` | Descrição curta com hífens | `mcp-specification` |
| `.mdc` | Extensão de lobo (Markdown com Commentary) | `.mdc` |

**Exemplo completo:** `NC-LBE-INT-006-mcp-specification.mdc`

---

@UBL Creation-Routine
LEXICO: #sop #creation #routine #10-steps
# 4. ROTINA DE CRIAÇÃO (10 PASSOS)

A rotina abaixo DEVE ser executada NA ORDEM, sem pular passos. Cada passo inclui verificações e comandos.

---

@UBL Step-1
LEXICO: #step1 #manifest #next-id #csv
## 4.1 Step 1 — Consultar NC-MAN-LOBE-001.csv pelo Próximo ID

**Objetivo:** Descobrir qual o próximo número sequencial disponível no domínio alvo.

### Procedimento:

```bash
# 1. Ler o manifesto completo
Get-Content "DIR-DS-003-lobe-manifest/NC-MAN-LOBE-001.csv"

# 2. Identificar TODAS as entradas do domínio alvo
#    Exemplo para domínio FR:
rg "^NC-LBE-FR-" DIR-DS-003-lobe-manifest/NC-MAN-LOBE-001.csv

# 3. Extrair o maior NNN + 1
#    Se o maior é NC-LBE-FR-058, o próximo é NC-LBE-FR-059
```

### Formato do CSV:

```
NC-LBE-{DOMAIN}-{NNN}|{SIZE_BYTES}|{PATH}
```

Cada linha contém: `ID|Tamanho|Caminho relativo`

### Checklist:
- [ ] Li o CSV completo (R21: NUNCA assumir o próximo número)
- [ ] Confirmei que o número NÃO está em uso
- [ ] Anotei o próximo ID: `NC-LBE-{DOMAIN}-{NNN}`

---

@UBL Step-2
LEXICO: #step2 #directory #write-zone #create-file
## 4.2 Step 2 — Criar Arquivo no Diretório Correto

**Objetivo:** Criar o arquivo .mdc no subdiretório de domínio correto dentro de `02_memory_lobes/`.

### Estrutura de diretórios:

```
02_memory_lobes/
├── 01_architecture/     # ARQ, FR (framework architecture)
├── 01_framework/         # FR (framework components)
├── 02_integrations/      # INT (external integrations)
├── 03_agents/            # DS, AGT (agent designs)
├── 04_cc_patterns/       # CC (cerebral cortex patterns)
├── 05_machine_memory/    # MEM (machine memory)
├── 05_user/              # USR (user-facing)
├── 06_governance/        # GOV (governance rules)
├── 08_sessions/          # SES (session records)
└── 09_framework/         # FR (framework extensions)
```

### Mapeamento Domínio → Diretório:

| Sigla Domínio | Diretório | Uso |
|---------------|-----------|-----|
| `ARQ` | `01_architecture/` | Arquitetura de sistema |
| `FR` | `01_framework/` ou `01_architecture/` ou `09_framework/` | Framework (verificar CSV por precedentes) |
| `INT` | `02_integrations/` | Integrações externas |
| `DS` | `03_agents/` | Design de agentes |
| `CC` | `04_cc_patterns/` | Cerebral Cortex patterns |
| `MEM` | `05_machine_memory/` | Memória de máquina |
| `USR` | `05_user/` | User-facing |
| `GOV` | `06_governance/` | Governança |
| `SES` | `08_sessions/` | Registros de sessão |

### Procedimento:

```bash
# 1. Navegar para o diretório de domínio
Set-Location "02_memory_lobes/{domain}/"

# 2. Criar o arquivo
New-Item -Name "NC-LBE-{DOMAIN}-{NNN}-{description}.mdc" -ItemType File
```

### Checklist:
- [ ] O diretório alvo EXISTE? (`Test-Path`, R21)
- [ ] Já existe outro lobo com este domínio neste diretório? (ver precedentes no CSV)
- [ ] Nome do arquivo segue o padrão NC-LBE-{DOMAIN}-{NNN}-{description}.mdc

---

@UBL Step-3
LEXICO: #step3 #frontmatter #yaml #metadata
## 4.3 Step 3 — Adicionar YAML Frontmatter

**Objetivo:** Inserir o bloco YAML frontmatter como PRIMEIRO conteúdo do arquivo.

### Template base:

```yaml
---
lobe_id: "NC-LBE-{DOMAIN}-{NNN}"
name: "{Nome Legível do Lobo}"
status: "active"
version: "1.0"
created_at: "{YYYY-MM-DD}"
tags: ["{tag1}", "{tag2}", "{tag3}"]
domain: "{subdiretório}"     # ex: "01_architecture"
layer: "{camada}"            # ex: "framework"
---
```

### Regras para tags:
- Use `snake_case` ou `kebab-case` (ex: `mcp-protocol`, `deepseek`)
- Mínimo 2 tags, máximo 8
- Tags DEVEM corresponder a entradas existentes no LEXICO ou serem novas tags justificadas
- Tags em inglês ou português — consistente com o LEXICO

### Checklist:
- [ ] Frontmatter entre `---` (abertura e fechamento)
- [ ] Todos os 8 campos obrigatórios presentes
- [ ] `lobe_id` coincide com o nome do arquivo
- [ ] `created_at` no formato ISO 8601 (YYYY-MM-DD)
- [ ] `status` é `active`, `draft`, ou `archived`

---

@UBL Step-4
LEXICO: #step4 #3w #what-why-where #metadata
## 4.4 Step 4 — Adicionar Bloco 3W

**Objetivo:** Inserir os metadados What / Why / Where como cabeçalhos H2.

### Template:

```markdown
## What
[1-2 frases descrevendo CONTEÚDO REAL do lobo]

## Why
[1-2 frases explicando PROBLEMA QUE RESOLVE ou LACUNA QUE PREENCHE]

## Where
[Caminho do arquivo: 02_memory_lobes/{domain}/NC-LBE-...mdc]
```

### Exemplo concreto:

```markdown
## What
Especificação técnica completa do protocolo MCP 2025-03-26 — transportes, mensagens, inicialização, ferramentas, recursos, prompts, sampling. Baseado na documentação oficial do modelcontextprotocol.io.

## Why
Centralizar TODA a spec MCP em UM lobo indexado por @UBL. Antes, o conhecimento MCP estava disperso em 6+ arquivos e web fetches repetidos. Agora qualquer agente consulta 1 fonte.

## Where
02_memory_lobes/02_integrations/NC-LBE-INT-006-mcp-specification.mdc
```

### Checklist:
- [ ] WHAT descreve conteúdo, não só nome
- [ ] WHY tem justificativa real (não genérica)
- [ ] WHERE tem caminho completo e correto

---

@UBL Step-5
LEXICO: #step5 #ubl #lexico #headings #content
## 4.5 Step 5 — Escrever Conteúdo com @UBL + LEXICO em Todo H1/H2

**Objetivo:** Escrever o conteúdo do lobo garantindo que TODO H1 e TODO H2 tenha @UBL + LEXICO.

### Regra de Ouro:

```
ANTES de cada # ou ##:
  → @UBL {NomeDoTopico}
  → LEXICO: #tag1 #tag2
  → (linha em branco)
  → # N. Título ou ## N.M Subtítulo
```

### Exemplo correto:

```markdown
@UBL MCP-Transport
LEXICO: #mcp #transport #sse #stdio
# 3. MCP Transport Layer

@UBL MCP-Transport-SSE
LEXICO: #mcp #sse #server-sent-events #http
## 3.1 SSE Transport (Server-Sent Events)
```

### Exemplo INCORRETO (NÃO FAZER):

```markdown
# 3. MCP Transport Layer          ← SEM @UBL + LEXICO = REPROVADO
## 3.1 SSE Transport               ← SEM @UBL + LEXICO = REPROVADO
```

### Checklist por seção:
- [ ] TODO `# ` precedido por `@UBL ...` + `LEXICO: ...`
- [ ] TODO `## ` precedido por `@UBL ...` + `LEXICO: ...`
- [ ] Nomes de @UBL são únicos dentro do lobo
- [ ] Tags LEXICO são relevantes ao conteúdo da seção

---

@UBL Step-6
LEXICO: #step6 #numbering #sections #hierarchy
## 4.6 Step 6 — Numerar Todas as Seções

**Objetivo:** Garantir que toda seção tenha numeração hierárquica consistente.

### Padrão:

| Nível | Markdown | Formato | Exemplo |
|-------|----------|---------|---------|
| H1 | `# N.` | Número simples + ponto | `# 1. Introdução` |
| H2 | `## N.M` | H1.H2 + ponto | `## 1.1 Contexto` |
| H3 | `### N.M.P` | H1.H2.H3 + ponto | `### 1.1.1 Detalhe` |
| H4 | `#### N.M.P.Q` | Raramente usado | `#### 1.1.1.1 Exceção` |

### Exemplo de hierarquia completa:

```markdown
# 1. Visão Geral
## 1.1 Contexto
### 1.1.1 Histórico
### 1.1.2 Motivação
## 1.2 Escopo
# 2. Transport Layer
## 2.1 SSE
### 2.1.1 Conexão
### 2.1.2 Mensagens
## 2.2 STDIO
# 3. Mensagens
...
```

### Checklist:
- [ ] Números são sequenciais e consistentes
- [ ] Sem saltos (ex: `# 1.`, depois `# 3.` sem `# 2.` = erro)
- [ ] Hierarquia respeitada (H3 dentro de H2, H2 dentro de H1)

---

@UBL Step-7
LEXICO: #step7 #csv #manifest #register
## 4.7 Step 7 — Registrar no NC-MAN-LOBE-001.csv

**Objetivo:** Adicionar uma nova linha no manifesto de lobos para que o sistema saiba da existência do lobo.

### Procedimento:

```bash
# 1. Calcular tamanho do arquivo em bytes
$size = (Get-Item "02_memory_lobes/{domain}/NC-LBE-{DOMAIN}-{NNN}-{description}.mdc").Length

# 2. Adicionar linha ao CSV (PowerShell)
$line = "NC-LBE-{DOMAIN}-{NNN}|" + $size + "B|02_memory_lobes\{domain}\NC-LBE-{DOMAIN}-{NNN}-{description}.mdc"
Add-Content -Path "DIR-DS-003-lobe-manifest/NC-MAN-LOBE-001.csv" -Value $line
```

### Formato da linha:

```
NC-LBE-{DOMAIN}-{NNN}|{SIZE}B|{RELATIVE_PATH}
```

### Exemplo:

```
NC-LBE-FR-ARCH-059|4521B|02_memory_lobes\01_architecture\NC-LBE-FR-ARCH-059-runtime-hooks.mdc
```

### Checklist:
- [ ] Linha adicionada no formato correto (pipe-separated)
- [ ] Tamanho em bytes está correto (não estimado)
- [ ] Caminho relativo usa backslash (Windows) e está correto (Test-Path)
- [ ] ID não duplica nenhum existente

---

@UBL Step-8
LEXICO: #step8 #changelog #kaizen #nc-chg
## 4.8 Step 8 — Atualizar @CHANGELOG (NC-CHG-FR-001-changelog.yaml)

**Objetivo:** Registrar a criação do lobo no changelog unificado com entrada kaizen.

### Procedimento:

Adicionar nova entrada na lista `entries:` do arquivo `NC-CHG-FR-001-changelog.yaml`:

```yaml
  - date: "{YYYY-MM-DD}"
    type: "LOBE"
    kaizen: true
    what: "Lobo NC-LBE-{DOMAIN}-{NNN} criado: {descrição do conteúdo}. Inclui {N} seções com @UBL + LEXICO. Formato validado conforme NC-SOP-FR-003."
    why: "{Razão da criação — lacuna, ticket, demanda}"
    files: ["02_memory_lobes/{domain}/NC-LBE-{DOMAIN}-{NNN}-{description}.mdc", "DIR-DS-003-lobe-manifest/NC-MAN-LOBE-001.csv"]
```

### Checklist:
- [ ] Entrada com `kaizen: true`
- [ ] Tipo `LOBE` (ou `ARCHITECTURE` se for lobo estrutural)
- [ ] `what` descreve conteúdo real do lobo
- [ ] `why` tem justificativa rastreável
- [ ] `files` lista o .mdc E o CSV atualizado

---

@UBL Step-9
LEXICO: #step9 #validate #ruff #mypy #nc-validate
## 4.9 Step 9 — Executar nc-validate no Novo Lobo

**Objetivo:** Validar o arquivo .mdc criado usando o pipeline R6 completo.

### Procedimento:

```bash
# Validação completa
nc-validate --file "02_memory_lobes/{domain}/NC-LBE-{DOMAIN}-{NNN}-{description}.mdc" --type mdc
```

### O que é verificado:

| Check | Descrição | Bloqueante? |
|-------|-----------|-------------|
| MDC frontmatter | YAML válido entre `---` com campos obrigatórios | ✅ SIM |
| @UBL presence | Todo H1/H2 tem @UBL + LEXICO | ✅ SIM |
| 3W block | What / Why / Where presentes | ✅ SIM |
| Section numbering | Numeração sequencial sem saltos | ✅ SIM |
| File naming | Padrão NC-LBE-{DOMAIN}-{NNN}-{desc}.mdc | ✅ SIM |
| CSV consistency | Entrada no NC-MAN-LOBE-001.csv existe e confere | ⚠️ Warn |
| LEXICO tags | Tags usadas existem ou são novas (justificadas) | ⚠️ Warn |

### Se falhar:

1. Ler a mensagem de erro
2. Corrigir APENAS o que falhou
3. Re-executar `nc-validate`
4. Repetir até PASSAR em todos os checks bloqueantes

### Checklist:
- [ ] nc-validate executado
- [ ] 0 erros bloqueantes
- [ ] Warnings revisados e justificados (se houver)

---

@UBL Step-10
LEXICO: #step10 #locks #wire #atomic-locks
## 4.10 Step 10 — Wire em @LOCKS (se Necessário)

**Objetivo:** Se o lobo contém informações críticas de segurança ou configuração, adicioná-lo ao arquivo de atomic locks.

### Critérios para @LOCKS:

Adicione ao @LOCKS se o lobo:
- Contém regras de enforcement (R01-R20)
- Define políticas de segurança
- Mapeia arquivos protegidos
- É fonte de verdade (SSOT) para configuração

### Procedimento:

```bash
# 1. Abrir o arquivo de atomic locks
#    C:\...\NC-SEC-FR-001-atomic-locks.yaml

# 2. Se o domínio já tem seção, adicionar o path
# 3. Se for novo domínio crítico, criar nova seção
```

### Exemplo de entrada:

```yaml
  lobe_files:
    description: "Lobos de conhecimento — imutáveis sem revisão."
    action: "block_write"
    paths:
      - "02_memory_lobes/06_governance/NC-LBE-FR-RULES-MULTILAYER-001.mdc"
      - "02_memory_lobes/01_architecture/NC-LBE-FR-CONSTITUTION-001.mdc"
      # NOVO:
      - "02_memory_lobes/{domain}/NC-LBE-{DOMAIN}-{NNN}-{description}.mdc"
```

### Checklist:
- [ ] Avaliei se o lobo É crítico para @LOCKS
- [ ] Se SIM: adicionei entrada no YAML de atomic locks
- [ ] Se NÃO: documentei que não requer @LOCKS (passo concluído)

---

@UBL Finding-Routine
LEXICO: #sop #finding #search #ubl #lexico
# 5. ROTINA DE LOCALIZAÇÃO (FINDING)

Como encontrar lobos e seções após criados:

---

@UBL Finding-UBL
LEXICO: #finding #ubl #bookmark #jump
## 5.1 Por @UBL (Bookmark Semântico)

Use `@UBL {NomeDoTopico}` para pular diretamente para qualquer seção dentro de um lobo.

```bash
# Buscar @UBL específico em todos os lobos
rg "@UBL DeepSeek-V4" 02_memory_lobes/

# Retorna: arquivo.mdc:35:@UBL DeepSeek-V4
#          arquivo.mdc:50:@UBL DeepSeek-V4
```

---

@UBL Finding-CSV
LEXICO: #finding #csv #manifest #lookup
## 5.2 Por NC-MAN-LOBE-001.csv (Lookup Rápido)

Use o manifesto CSV para descobrir qual arquivo contém um dado @UBL tag:

```bash
# 1. Encontrar qual arquivo contém o @UBL
rg "@UBL DeepSeek-V4" 02_memory_lobes/ -l

# 2. Confirmar no CSV
rg "DeepSeek" DIR-DS-003-lobe-manifest/NC-MAN-LOBE-001.csv
```

---

@UBL Finding-LEXICO
LEXICO: #finding #lexico #tags #topic-search
## 5.3 Por LEXICO Tags (Busca por Tópico)

Use as tags LEXICO (`#tag`) para busca temática:

```bash
# Encontrar todas as seções sobre MCP
rg "LEXICO:.*#mcp" 02_memory_lobes/

# Encontrar todas as seções sobre segurança
rg "LEXICO:.*#security" 02_memory_lobes/

# Combinar tags
rg "LEXICO:.*#mcp.*#sse" 02_memory_lobes/
```

---

@UBL Finding-Fulltext
LEXICO: #finding #grep #fulltext #search
## 5.4 Por Full-Text Search (grep/rg)

Para busca textual completa em todos os lobos:

```bash
# Busca textual em todos os .mdc
rg "thinking_mode" 02_memory_lobes/

# Busca com contexto (3 linhas antes/depois)
rg -C 3 "Chain-of-Thought" 02_memory_lobes/

# Busca apenas nomes de arquivo
rg -l "deepseek" 02_memory_lobes/
```

---

@UBL Complete-Example
LEXICO: #example #lobe #template #reference
# 6. EXEMPLO COMPLETO DE LOBO

Abaixo, um lobo didático completo demonstrando TODOS os requisitos de formato:

```markdown
---
lobe_id: "NC-LBE-FR-DEMO-001"
name: "Lobo de Demonstração — Exemplo Completo"
status: "draft"
version: "1.0"
created_at: "2026-05-04"
tags: ["demo", "tutorial", "example", "sop"]
domain: "01_framework"
layer: "tutorial"
---

## What
Lobo de demonstração que exemplifica TODOS os requisitos de formato definidos em NC-SOP-FR-003. Serve como template de referência para criação de novos lobos.

## Why
Centralizar um exemplo concreto e validado do formato. Reduz ambiguidade na interpretação dos requisitos escritos. Todo criador de lobo pode copiar esta estrutura.

## Where
02_memory_lobes/01_framework/NC-LBE-FR-DEMO-001-example.mdc

---

@UBL Demo-Overview
LEXICO: #demo #overview #purpose
# 1. Visão Geral do Lobo Demo

Este lobo demonstra na prática como estruturar conteúdo com @UBL e LEXICO.

@UBL Demo-Context
LEXICO: #demo #context #background
## 1.1 Contexto

A padronização de lobos foi estabelecida em 2026-05-04 para garantir consistência em todos os 57+ lobos do sistema.

@UBL Demo-Motivation
LEXICO: #demo #motivation #why
## 1.2 Motivação

Antes deste padrão, lobos tinham formatos inconsistentes — alguns com frontmatter, outros sem; alguns com UBL, outros não. A busca semântica era impossível.

---

@UBL Demo-Technical
LEXICO: #demo #technical #specs
# 2. Especificação Técnica

@UBL Demo-Architecture
LEXICO: #demo #architecture #components
## 2.1 Arquitetura

O lobo segue o padrão MDC (Markdown with Commentary) com metadados YAML no frontmatter.

@UBL Demo-Validation
LEXICO: #demo #validation #checklist
## 2.2 Validação

Todo lobo DEVE passar pelo nc-validate antes de ser considerado ativo. Consulte NC-SOP-FR-003 Step 9.

---

@UBL Demo-Reference
LEXICO: #demo #reference #links
# 3. Referências

| Documento | Relação |
|-----------|---------|
| NC-SOP-FR-003 | Este SOP — define a rotina de criação |
| NC-MAN-LOBE-001.csv | Manifesto de lobos |
| NC-CHG-FR-001-changelog.yaml | Changelog unificado |
```

---

@UBL Erros-Comuns
LEXICO: #errors #common-mistakes #antipatterns
# 7. ERROS COMUNS (NÃO REPETIR)

| # | Erro | Sintoma | Correção |
|---|------|---------|----------|
| 1 | **ID duplicado** no CSV | Dois lobos com mesmo NC-LBE-{DOMAIN}-{NNN} | Consultar CSV (Step 1) antes de criar |
| 2 | **@UBL ausente** em H2 | Seção sem âncora — inencontrável | Step 5: todo H1/H2 DEVE ter @UBL + LEXICO |
| 3 | **Frontmatter incompleto** | Campos obrigatórios faltando (ex: sem `layer`) | Step 3: verificar 8 campos obrigatórios |
| 4 | **3W genérico** | "Módulo NC LBE FR XYZ" — não descreve conteúdo | Step 4: WHAT deve descrever CONTEÚDO REAL |
| 5 | **Numeração com saltos** | `# 1.`, depois `# 3.` sem `# 2.` | Step 6: numeração sequencial |
| 6 | **CSV não atualizado** | Lobo existe mas não está no manifesto | Step 7: SEMPRE registrar no CSV |
| 7 | **CHANGELOG não atualizado** | Criação não rastreável | Step 8: entrada kaizen obrigatória |
| 8 | **nc-validate não executado** | Erros de formato não detectados | Step 9: validar SEMPRE |
| 9 | **Tags LEXICO inconsistentes** | Tags não existem no LEXICO nem são novas | Step 5: verificar LEXICO ou justificar nova tag |
| 10 | **Arquivo no diretório errado** | Lobe FR em 02_integrations/ | Step 2: verificar mapeamento domínio→diretório |

---

@UBL Stop-0
LEXICO: #stop0 #mentor-mode #checklist #preflight
# 8. STOP-0 — MENTOR MODE (PRÉ-CRIAÇÃO)

> **R09:** Toda violação registrada no Regression Buffer.  
> **R21:** NUNCA assumir — verificar antes de afirmar.  
> **R53:** KISS — 1 lobo por vez.

### Checklist Pré-Criação (ANTES de começar):

```
☐ CSV:      Li NC-MAN-LOBE-001.csv — sei qual é o próximo ID?
☐ DIR:      Test-Path no diretório alvo — EXISTE?
☐ NAME:     Nome segue NC-LBE-{DOMAIN}-{NNN}-{desc}.mdc?
☐ DUPL:     Verifiquei que NÃO existe lobo com mesmo ID?
☐ DOMAIN:   O domínio existe no mapeamento (Step 2)?
☐ TAGS:     As tags que vou usar existem no LEXICO?
☐ CONTENT:  Tenho conteúdo suficiente para justificar um lobo?
☐ RCA:      Este lobo resolve uma causa raiz ou é duplicado?
☐ PRECED:   Existe lobo similar que posso estender em vez de criar novo?
☐ KAIZEN:   Vou registrar no CHANGELOG com kaizen=true?
```

**FALHOU qualquer ☐ = PARAR. Resolver ANTES de criar.**

---

@UBL Quick-Reference
LEXICO: #reference #commands #table #cheatsheet
# 9. TABELA DE REFERÊNCIA RÁPIDA

| Passo | Ação | Comando/Ferramenta |
|-------|------|--------------------|
| 1 | Próximo ID | `rg "NC-LBE-{DOMAIN}-" NC-MAN-LOBE-001.csv` |
| 2 | Criar arquivo | `New-Item "02_memory_lobes/{domain}/NC-LBE-{DOMAIN}-{NNN}-{desc}.mdc"` |
| 3 | Frontmatter | Editar .mdc → adicionar YAML entre `---` |
| 4 | Bloco 3W | Adicionar `## What` / `## Why` / `## Where` |
| 5 | @UBL + LEXICO | Antes de cada `#` e `##` |
| 6 | Numerar | `# 1.` → `## 1.1` → `### 1.1.1` |
| 7 | CSV | `Add-Content NC-MAN-LOBE-001.csv "ID|SIZE|PATH"` |
| 8 | CHANGELOG | Nova entrada em `entries:` com `kaizen: true` |
| 9 | Validar | `nc-validate --file ... --type mdc` |
| 10 | @LOCKS | Avaliar criticidade → adicionar se necessário |

---

@UBL SSOT-Registry
LEXICO: #ssot #registry #cross-reference
# 10. SSOT — REGISTRO CRUZADO

| Arquivo | O que registrar |
|---------|----------------|
| `NC-MAN-LOBE-001.csv` | ID, tamanho, path do novo lobo |
| `NC-CHG-FR-001-changelog.yaml` | Entrada kaizen com data, tipo LOBE, descrição |
| `NC-NAM-FR-001-*.md` | Atualizar changelog section se aplicável |
| `NC-SEC-FR-001-atomic-locks.yaml` | Se lobo crítico: adicionar path ao atomic locks |
| `NC-LEXICO-LATEST.json` | Se novas tags: registrar no LEXICO |

---

**Hash:** `SOP-LOBE-v1.0-20260504` | **Próxima revisão:** Após primeiros 5 lobos criados com este SOP
