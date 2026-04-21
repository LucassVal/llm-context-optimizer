# NC-SEC-FR-001  Atomic Locks: Arquivos Protegidos do NeoCortex
<!-- Verso: 1.0 | 20260414 | Criado por opencode (DeepSeekReasoner) -->
<!-- Documentao do sistema de locks atmicos para SecurityService -->

## Propsito

Definir **arquivos e diretrios protegidos** que nenhum agente pode modificar sem autorizao explcita do T0. O SecurityService usa esta lista para bloquear escritas no autorizadas em runtime.

**Companion YAML**: `NCSECFR001atomiclocks.yaml` (machinereadable)

---

## 1. VISO GERAL

Os **atomic locks** so a camada de segurana mais bsica do NeoCortex. Eles garantem que:

1. **Arquivos de configurao** no sejam corrompidos por modificaes em runtime
2. **Crtex central** (estado do T0) permanea ntegro
3. **Documentao SSOT** seja modificada apenas por deciso consciente do usurio
4. **Servidor MCP** (cdigo de produo) no seja alterado sem reviso
5. **Isolamento entre lobos** seja respeitado
6. **Backups e arquivos histricos** sejam somente leitura

---

## 2. CATEGORIAS DE LOCKS

### 2.1. Arquivos de Configurao (`config_files`)
- **Descrio**: Arquivos de configurao central  imutveis durante execuo.
- **Ao**: `block_write`
- **Paths**:
  - `DIRCFGFR001configmain/neocortex_config.yaml`
  - `DIRCFGFR001configmain/**/*.yaml`
  - `.agents/rules/**`

### 2.2. Crtex Central (`cortex_files`)
- **Descrio**: Crtex central  modificado apenas pelo T0 via `neocortex_cortex`.
- **Ao**: `block_write`
- **Paths**:
  - `DIRCOREFR001corecentral/.agents/rules/NCCTXFR001cortexcentral.mdc`
  - `DIRCOREFR001corecentral/NCLEDFR001frameworkledger.json`
  - `DIRCOREFR001corecentral/*.json`

### 2.3. Documentao SSOT (`ssot_docs`)
- **Descrio**: Documentao SSOT  alterada apenas mediante instruo explcita do usurio.
- **Ao**: `block_write`
- **Paths**:
  - `DIRDOCFR001docsmain/NCNAMFR001namingconvention.md`
  - `DIRDOCFR001docsmain/NCTODOFR001projectroadmapconsolidated.md`
  - `DIRDOCFR001docsmain/NCSECFR001atomiclocks.yaml`
  - `DIRDOCFR001docsmain/NCCFGFR001agentpolicytemplate.yaml`
  - `DIRDOCFR001docsmain/NCAPPFR001technicalappendix.md`

### 2.4. Servidor MCP (`mcp_server`)
- **Descrio**: Cdigo do servidor MCP  modificao requer reviso e reinicializao.
- **Ao**: `block_write`
- **Paths**:
  - `neocortex/mcp/server.py`
  - `neocortex/mcp/sub_server.py`
  - `neocortex/mcp/__init__.py`
  - `neocortex/config.py`

### 2.5. Isolamento entre Lobos (`cross_lobe_isolation`)
- **Descrio**: Agentes no podem modificar lobos de outros agentes.
- **Ao**: `block_cross_write`
- **Poltica**: Um agente com `lobe_dir='lobes/courier'` NO pode escrever em:
  - `lobes/engineer/`
  - `lobes/guardian/`
  - `lobes/backend_dev/`
  - Apenas o T0 tem permisso de escrita crosslobe.

### 2.6. Backups e Arquivos Histricos (`backups`)
- **Descrio**: Arquivos de backup  somente leitura aps criao.
- **Ao**: `block_write`
- **Paths**:
  - `DIRBAKFR001backupmain/**`
  - `DIRARCFR001archivemain/**`

### 2.7. Arquivos na Raiz do Projeto (`root_files`)
- **Descrio**: Arquivos na raiz do projeto  modificao requer autorizao.
- **Ao**: `block_write`
- **Paths**:
  - `../.gitignore`
  - `../start_neocortex_mcp.bat`
  - `../start_neocortex_mcp.ps1`
  - `../antigravity_neocortex_config.json`
  - `../NCPROMPTFR001mastercontext.md`

---

## 3. EXCEES AUTORIZADAS

| Agente | Recurso Permitido | Tipo de Acesso | Razo |
|--------|-------------------|----------------|-------|
| `guardian` | `DIRCOREFR001corecentral/NCLEDFR001frameworkledger.json` | Leitura | Guardian l o ledger para auditoria, mas no escreve |
| `engineer` | `DIRTESTFR001testsmain/**` | Escrita | Engineer pode criar e modificar arquivos de teste |

---

## 4. INTEGRAO COM SECURITYSERVICE

O SecurityService (`neocortex.core.security_service`) consulta este lock file em runtime:

```python
from neocortex.core.security_service import SecurityService

svc = SecurityService()
# Retorna True se o path NO est bloqueado, False se est bloqueado
permitted = svc.validate_access(path="/path/to/file")
```

**Fluxo**:
1. Agente tenta modificar arquivo
2. SecurityService verifica path contra `atomic_locks`
3. Se path est em lista bloqueada  retorna `False` e operao  abortada
4. Se h exceo para role do agente  permite acesso conforme regra

---

## 5. ATUALIZAO DOS LOCKS

**Apenas o T0** pode modificar `NCSECFR001atomiclocks.yaml`. Processo:

1. **Justificativa**: Identificar necessidade de adicionar/remover lock
2. **Anlise de impacto**: Verificar quais agentes sero afetados
3. **Modificao**: Editar YAML e MD simultaneamente (padro "dupla mordaa")
4. **Validao**: Executar `NCSCRFR009sanitizeallyamls.py` para verificar hash
5. **Comunicao**: Notificar agentes sobre mudanas (se necessrio)

---

## 6. CHECKLIST DE VALIDAO

- [ ] YAML possui seo `meta` com `hash` vlido
- [ ] MD correspondente existe e est atualizado
- [ ] Todos os paths existem (ou so padres glob vlidos)
- [ ] Excees so necessrias e justificadas
- [ ] SecurityService consegue carregar YAML sem erros
- [ ] Nenhum lock conflita com write zones de `NCCFGFR002rulespolicy.yaml`

---

## 7. PRXIMOS PASSOS

1. **Integrar validao de hash** no SecurityService
2. **Criar script de auditoria** para verificar conformidade de locks
3. **Documentar processo de exceo** para novos agents

---

**Hash do documento**: `ATOMICLOCKSv1.020260414`  
**Atualizado em**: 20260414  
**Responsvel**: opencode (DeepSeekReasoner)  
**Integridade**: `sha256:$(sha256sum NCSECFR001atomiclocks.md | cut -d' ' -f1)`