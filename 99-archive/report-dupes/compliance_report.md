# Relatrio de Governana NeoCortex

**Data da Auditoria:** 2026-04-20T20:36:22.744558
**Ambiente:** original
**Caminho Base:** 01_neocortex_framework

## 1. Sistema de Arquivos
- **Total de arquivos:** 422
- **.py:** 303
- **.yaml:** 30
- **.md:** 55
- **.json:** 34

- **Conformidade NC-:** 54.3% (229/422)
- **Arquivos no conformes:** 191

## 2. Dependncias PIP
- **Pacotes instalados:** 330
- **Vulnerabilidades:** C:\Program Files\Python312\python.exe: No module named pip_audit


## 3. Conformidade com Governana de IA
### R04: Nomenclatura Padronizada: todos os arquivos seguem NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext
 **Status:** True
**Detalhes:** 229 arquivos seguem padro NC-

### R05: Segregao de Ambientes: manter ambientes separados para desenvolvimento, teste e produo
 **Status:** True
**Detalhes:** Ambiente detectado: original

### R11: Versionamento de Artefatos: todos os artefatos de governana versionados (Git) com hashes de integridade
 **Status:** True
**Detalhes:** 4 de 11 YAMLs de governana possuem hash

### R01: Inventrio de Ativos de IA: manter catlogo completo de modelos, ferramentas, agentes e fontes de dados
 **Status:** False
**Detalhes:** artifact_catalog.json: True, mcp_tools_inventory.json: True, genealogy_graph.json: False

### R02: Poltica Formalizada: polticas de governana escritas, versionadas e acessveis como cdigo ou documentos SSOT
 **Status:** True
**Detalhes:** NC-NAM-FR-001: True, NC-SEC-FR-001: True, NC-CFG-FR-002: True, NC-GOV-FR-003: True

### R06: Identidade para Agentes: cada agente deve ter identidade nica e verificvel
 **Status:** False
**Detalhes:** Handoff directory exists: True, handoff files: 0

### R07: Privilgio Mnimo (PoLP): agentes tm apenas permisses estritamente necessrias
 **Status:** True
**Detalhes:** Agent policy template exists: True

### R08: Atomic Locks (Path-Based): arquivos crticos protegidos contra modificao
 **Status:** True
**Detalhes:** Atomic locks file exists: True

### R09: Segregao de Zonas de Escrita: agentes de diferentes domnios no podem escrever nos mesmos diretrios
 **Status:** True
**Detalhes:** Write zones defined in policy: True

### R10: Trilha de Auditoria Imutvel: todas as aes registradas em log  prova de adulterao
 **Status:** True
**Detalhes:** Audit log directory exists: True

### R12: Handoffs Formais: toda tarefa delegada a um agente documentada em handoff YAML
 **Status:** False
**Detalhes:** Handoff files: 0

### R13: Checkpoints e Save Points: estado do sistema salvo periodicamente e antes de operaes crticas
 **Status:** False
**Detalhes:** Checkpoint tool exists: False

### R14: STEP 0 (Validao Pr-Ao): validar tarefa contra Regression Buffer e polticas antes de executar
 **Status:** True
**Detalhes:** mentor_step_0 function exists: True

### R15: STEP -1 (Save Point): snapshot do estado antes de aes de escrita para possvel rollback
 **Status:** False
**Detalhes:** Save point tool exists: False

### R18: Ciclo de Vida de Tickets: toda tarefa registrada como ticket e seguir fluxo formal
 **Status:** True
**Detalhes:** Tickets directory exists: True, ticket files: 4

### R19: Rotina de 4 Ciclos: trabalho deve seguir rotina diria/semanal para garantir continuidade e limpeza
 **Status:** True
**Detalhes:** Cycle validation document exists: True

### R20: Reviso e Arquivo de Artefatos: artefatos antigos arquivados periodicamente para evitar acmulo
 **Status:** True
**Detalhes:** Archive directory exists: True

### MCP_EXTRA: MCP & Mission Control Integration Health
 **Status:** True
**Detalhes:** MCP server exists: True, Mission Control adapter exists: True

### R03: Estrutura de Diretrios Cannica: definir e impor estrutura padronizada
 **Status:** pending_implementation
**Detalhes:** Verificao no implementada nesta verso

### R16: Circuit Breaker: se um agente falhar repetidamente, deve ser suspenso para evitar loops de falha
 **Status:** pending_implementation
**Detalhes:** Verificao no implementada nesta verso

### R17: Rate Limiting por Ferramenta: limitar frequncia de chamadas a ferramentas crticas ou caras
 **Status:** pending_implementation
**Detalhes:** Verificao no implementada nesta verso


## 4. Discrepncias
- **Arquivos no no catlogo:** 0

## 5. Recomendaes
1. Executar auditoria regularmente (Ciclo 4 - Limpeza Semanal)
2. Corrigir arquivos que no seguem conveno NC-
3. Atualizar catlogo de artefatos com arquivos ausentes
4. Implementar verificaes completas para todas as 20 regras
