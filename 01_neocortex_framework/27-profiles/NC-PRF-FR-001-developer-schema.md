#  NC-PRF-FR-001 - Developer Profile Schema (Hierarchical)

> **Schema para perfis de desenvolvedor com suporte a hierarquias ilimitadas, controle de acesso e multi-tenancy.**

---

##  Visao Geral

O **NeoCortex Developer Profile** estende a estrutura pessoal (baseada no `Lucas.json`) para suportar:
- **Hierarquias ilimitadas** (usuarios, hosts, organizacoes)
- **Controle de acesso baseado em nivel** (ler iguais/laterais/inferiores, nao superiores)
- **Multi-tenancy** (empresas, lan houses, escolas, governos)
- **Escalabilidade horizontal** (sem limites de usuarios)

---

##  Estrutura do Schema

### **Arquivo:** `NC-PRF-USR-{user_id}-profile.json`

```json
{
  "$schema": "neocortex-profile-v1.0",
  "profile_type": "developer",
  "version": "1.0.0",
  
  // ==================== IDENTIFICACAO ====================
  "identity": {
    "user_id": "lucas_valerio",                    // ID unico (email/uuid)
    "display_name": "Lucas Valerio",
    "email": "lucas@example.com",
    "avatar_url": "optional_url",
    "created_at": "2026-02-18T00:00:00Z",
    "updated_at": "2026-04-10T10:00:00Z"
  },
  
  // ==================== HIERARQUIA ====================
  "hierarchy": {
    "level": 5,                                    // Nivel hierarquico (0 = root)
    "parent_id": "org_panda_factory",              // ID do pai direto
    "children_ids": ["user_dev1", "user_dev2"],    // IDs dos filhos diretos
    "ancestors": [                                 // Caminho ate a raiz
      "root_global",
      "org_brazil",
      "org_sao_paulo", 
      "org_panda_factory"
    ],
    "descendants_count": 2,                        // Numero total de descendentes
    "sibling_ids": ["user_colleague1"],            // IDs dos irmaos (mesmo nivel)
    "visibility_rules": {
      "can_read_upwards": false,                   // Pode ler niveis superiores? (NAO)
      "can_read_siblings": true,                   // Pode ler irmaos/laterais? (SIM)
      "can_read_descendants": true,                // Pode ler inferiores? (SIM)
      "max_read_depth": -1,                        // -1 = todos os inferiores
      "write_permission": ["self", "descendants"]  // Onde pode escrever
    }
  },
  
  // ==================== PERMISSOES ====================
  "permissions": {
    "roles": ["developer", "admin", "mentor"],     // Roles funcionais
    "scopes": [
      "project:read",
      "project:write", 
      "team:manage",
      "billing:view",
      "user:invite"
    ],
    "constraints": {
      "max_projects": 50,                          // Limites por usuario
      "max_storage_mb": 1024,
      "max_api_calls_per_day": 10000
    }
  },
  
  // ==================== PADROES PESSOAIS ====================
  "personal_patterns": {
    "productivity": {
      "peak_hours": ["09:00-12:00", "21:00-02:00"],
      "session_duration_avg": "2.5h",
      "context_switch_tolerance": "high",
      "preferred_days": ["segunda", "terca", "quarta", "quinta", "sexta"]
    },
    
    "tech_preferences": {
      "frontend": ["React + Vite", "Vanilla CSS", "tldraw"],
      "backend": ["Google Apps Script", "Firebase RTDB", "Python"],
      "trading": ["cTrader", "Deriv API", "ML Python"],
      "automation": ["MCP", "Google Sheets", "Web Scraping"],
      "mastery_levels": {
        "mcp": "advanced",
        "react": "intermediate", 
        "python": "advanced",
        "gas": "intermediate_advanced"
      }
    },
    
    "communication": {
      "preferred_languages": ["pt-BR", "en"],
      "message_style": "fragmented",               // Mensagens fragmentadas
      "response_expectation": "fast",              // Espera respostas rapidas
      "syntax_patterns": [
        "Usa metaforas de software para vida",
        "Mistura portugues e ingles naturalmente",
        "Envia 3-5 mensagens onde outros enviariam 1 paragrafo"
      ]
    }
  },
  
  // ==================== MOTOR DE APRENDIZADO ====================
  "learning_engine": {
    "common_mistakes": [
      {
        "error": "Esquecer aliases no tsconfig.json",
        "solution": "Adicionar automaticamente via scaffold",
        "context": "frontend_projects",
        "occurrences": 5,
        "last_occurrence": "2026-04-09",
        "severity": "medium",
        "prevention_strategy": "check_aliases_on_init"
      }
    ],
    
    "historical_patterns": {
      "project_completion_rate": "85%",
      "bug_resolution_time_avg": "1.2h",
      "feature_development_speed": "3.5 dias",
      "preferred_project_size": "medium"           // small/medium/large
    },
    
    "prediction_model": {
      "next_best_action_accuracy": "85%",
      "stack_suggestion_accuracy": "92%",
      "time_estimation_accuracy": "78%",
      "last_training_date": "2026-04-10"
    }
  },
  
  // ==================== CONTEXTO ATUAL ====================
  "current_context": {
    "active_projects": ["neocortex_framework", "panda_factory"],
    "current_focus": "mcp_hub_development",
    "available_hours_weekly": 40,
    "location": {
      "city": "Americana",
      "state": "Sao Paulo", 
      "country": "Brasil",
      "timezone": "America/Sao_Paulo"
    },
    "device_preferences": ["desktop", "dual_monitor"]
  },
  
  // ==================== INTEGRACOES ====================
  "integrations": {
    "mcp_servers": ["antigravity", "vscode", "cursor"],
    "external_tools": ["github", "linear", "discord"],
    "api_keys": {                                  // Referencias apenas, nao valores
      "firebase": "configured",
      "gemini": "configured",
      "stripe": "configured"
    }
  },
  
  // ==================== METADADOS ====================
  "metadata": {
    "source": "lucas.json_v6.2.0_converted",
    "conversion_date": "2026-04-10",
    "privacy_level": "private",                    // private/team/public
    "sync_status": "local",                        // local/cloud/synced
    "backup_frequency": "daily"
  }
}
```

---

##  Regras de Controle de Acesso Hierarquico

### **Principio Fundamental:**
> **"Um usuario pode ler informacoes de niveis iguais, laterais e inferiores, mas NAO pode ler informacoes de niveis superiores."**

### **Exemplo Pratico:**
```
Nivel 0: ROOT (Governo Federal)
   Nivel 1: Estado (Sao Paulo)
      Nivel 2: Cidade (Campinas)
         Nivel 3: Escola (Escola Tec)
            Nivel 4: Professor (Prof. Silva)
               Nivel 5: Aluno (Joao)    Nivel atual
```

**Permissoes do Aluno (Nivel 5):**
-  **Pode ler:** Alunos (nivel 5), Professor (4), Escola (3), Cidade (2), Estado (1), ROOT (0)
-  **Nao pode ler:** Informacoes sensiveis de niveis superiores (ex: salario do professor)
-  **Pode escrever:** Apenas seu proprio perfil (5)
-  **Pode ver:** Media da turma (laterais), notas pessoais (inferior = self)

**Permissoes do Professor (Nivel 4):**
-  **Pode ler:** Professores (4), Escola (3), Cidade (2), Estado (1), ROOT (0)
-  **Pode escrever:** Alunos (5), seu proprio perfil (4)
-  **Nao pode ler:** Outros professores (laterais) so com permissao explicita

---

##  Casos de Uso

### **1. Empresa Corporativa**
```
ROOT (CEO)
 Diretoria (CTO, CFO)
    Gerentes
       Team Leads
          Desenvolvedores
```

### **2. Lan House / Cyber Cafe**
```
ROOT (Proprietario)
 Funcionarios (Admin)
    Maquinas (Grupos)
       Usuarios (Clientes por hora)
```

### **3. Escola / Universidade**
```
ROOT (Reitoria)
 Departamentos
    Professores
       Turmas
          Alunos
```

### **4. Governo Municipal**
```
ROOT (Prefeitura)
 Secretarias
    Departamentos
       Funcionarios
          Cidadaos (acesso publico)
```

---

##  API de Verificacao de Acesso

### **Funcao:** `can_access(resource_level, user_level, resource_owner_id)`
```python
def can_access(resource_level, user_level, resource_owner_id, user_id):
    """
    Verifica se usuario pode acessar recurso baseado em hierarquia.
    
    Regras:
    1. Usuario pode acessar recursos do MESMO nivel se for dono OU se recurso for publico
    2. Usuario pode acessar recursos de NIVEIS INFERIORES sempre
    3. Usuario NAO pode acessar recursos de NIVEIS SUPERIORES
    4. Recursos laterais (mesmo nivel, dono diferente) requerem permissao explicita
    
    Retorna: { "allowed": bool, "reason": str }
    """
    if user_level > resource_level:
        # Usuario e SUPERIOR ao recurso  PERMITIDO
        return {"allowed": True, "reason": "hierarchy_superior"}
    
    elif user_level == resource_level:
        # Mesmo nivel  verificar ownership
        if resource_owner_id == user_id:
            return {"allowed": True, "reason": "self_ownership"}
        else:
            # Recurso lateral  precisa de permissao explicita
            return {"allowed": False, "reason": "lateral_access_requires_permission"}
    
    else:
        # Usuario e INFERIOR ao recurso  NEGADO
        return {"allowed": False, "reason": "hierarchy_inferior_cannot_read_upwards"}
```

---

##  Migracao do Lucas.json Existente

### **Script de Conversao:**
```bash
python DIR-PRF-FR-001-profiles-main/NC-PRF-FR-003-profile-loader.py \
  --input "C:/Users/Lucas Valerio/Desktop/JSON LUCAS/Lucas.json" \
  --output "DIR-PRF-FR-001-profiles-main/users/lucas_valerio/NC-PRF-USR-001-profile.json" \
  --hierarchy_level 5 \
  --parent_id "org_panda_factory"
```

### **Mapeamento de Campos:**
| Campo Lucas.json | Campo NeoCortex Profile | Transformacao |
|-----------------|------------------------|---------------|
| `work_style.session_pattern` | `personal_patterns.productivity.peak_hours` | Parse para array |
| `knowledge_graph.tech_stack_mastery` | `personal_patterns.tech_preferences` | Reestruturacao |
| `linguistic_fingerprint` | `personal_patterns.communication` | Mapeamento direto |
| `operating_principles` | `metadata.personal_rules` | Array de strings |
| `pf_hive_mind_council` | `integrations.expert_network` | Simplificacao |
| `active_directives` | `current_context.active_projects` | Extracao |

---

##  Proximos Passos

1. **Criar template JSON** (`NC-PRF-TMP-001-dev-profile-template.json`)
2. **Implementar loader** (`NC-PRF-FR-003-profile-loader.py`)
3. **Converter Lucas.json** para novo schema
4. **Adicionar verificacao hierarquica** no MCP server
5. **Testar com 3 niveis hierarquicos** simulados

---

**Versao:** 1.0.0  
**Data:** 2026-04-10  
**Status:** Draft  
**Proxima Revisao:** Apos implementacao do loader