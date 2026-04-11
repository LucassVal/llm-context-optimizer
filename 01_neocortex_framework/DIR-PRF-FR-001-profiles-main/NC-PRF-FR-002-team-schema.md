#  NC-PRF-FR-002 - Team Profile Schema (Hierarchical)

> **Schema para perfis de equipe com hierarquias aninhadas, controle de acesso granular e conhecimento coletivo.**

---

##  Visao Geral

O **NeoCortex Team Profile** gerencia equipes de qualquer tamanho com:
- **Hierarquias aninhadas** (equipes dentro de equipes)
- **Controle de acesso baseado em funcao**
- **Conhecimento coletivo compartilhado**
- **Integracao com hierarquia de usuarios**
- **Multi-tenant para organizacoes complexas**

---

##  Estrutura do Schema

### **Arquivo:** `NC-PRF-TEM-{team_id}-profile.json`

```json
{
  "$schema": "neocortex-team-v1.0",
  "profile_type": "team",
  "version": "1.0.0",
  
  // ==================== IDENTIFICACAO ====================
  "identity": {
    "team_id": "panda_factory_core",
    "name": "Panda Factory Core Team",
    "description": "Equipe central de desenvolvimento do Panda Factory",
    "avatar_url": "optional_url",
    "created_at": "2026-02-18T00:00:00Z",
    "updated_at": "2026-04-10T10:00:00Z",
    "owner_id": "lucas_valerio"
  },
  
  // ==================== HIERARQUIA DA EQUIPE ====================
  "hierarchy": {
    "level": 3,                                    // Nivel na organizacao
    "parent_team_id": "org_panda_factory",         // Equipe pai
    "child_team_ids": ["team_frontend", "team_backend"], // Sub-equipes
    "organization_path": [                         // Caminho organizacional
      "root_global",
      "org_brazil", 
      "org_panda_factory",
      "team_core"
    ],
    
    "access_control": {
      "visibility": "restricted",                  // public/restricted/private
      "join_policy": "invite_only",                // open/approval/invite_only
      "read_access": ["members", "parent_teams"],  // Quem pode ler
      "write_access": ["owners", "admins"],        // Quem pode escrever
      "inherit_parent_permissions": true           // Herda permissoes do pai
    }
  },
  
  // ==================== MEMBROS ====================
  "members": {
    "total_count": 8,
    "active_count": 8,
    "list": [
      {
        "user_id": "lucas_valerio",
        "role": "founder_architect",
        "joined_at": "2026-02-18T00:00:00Z",
        "permissions": ["admin", "deploy", "finance", "invite"],
        "expertise_domains": ["system_architecture", "mcp", "trading"],
        "contribution_score": 95,
        "status": "active"
      },
      {
        "user_id": "dev_frontend_1",
        "role": "frontend_developer",
        "joined_at": "2026-03-15T00:00:00Z",
        "permissions": ["project:write", "code:review"],
        "expertise_domains": ["react", "css", "ui_ux"],
        "contribution_score": 78,
        "status": "active"
      }
    ],
    
    "roles_definition": {
      "founder_architect": {
        "description": "Arquiteto fundador com acesso total",
        "permissions": ["*"],
        "max_count": 1
      },
      "team_lead": {
        "description": "Lider de equipe com poderes administrativos",
        "permissions": ["admin", "deploy", "review"],
        "max_count": 3
      },
      "developer": {
        "description": "Desenvolvedor com acesso a projetos",
        "permissions": ["project:write", "code:review"],
        "max_count": 20
      }
    }
  },
  
  // ==================== CONHECIMENTO COLETIVO ====================
  "shared_knowledge": {
    "team_rules": [
      "Documentation_is_architecture",
      "Mock_before_real", 
      "Agentic_delegation",
      "Revenue_generating_tasks_first"
    ],
    
    "common_solutions": [
      {
        "problem": "CORS configuration issues in Firebase",
        "solution": "Use cors({ origin: ['https://yourdomain.com'] }) middleware",
        "code_snippet": "app.use(cors({ origin: ['https://panda-factory.com'] }))",
        "applied_by": ["lucas_valerio", "dev_backend_1"],
        "success_rate": "100%",
        "last_used": "2026-04-09",
        "tags": ["firebase", "cors", "backend"]
      },
      {
        "problem": "React state management in large forms",
        "solution": "Use React Hook Form with Zod validation",
        "code_snippet": "const form = useForm({ resolver: zodResolver(schema) })",
        "applied_by": ["dev_frontend_1", "dev_frontend_2"],
        "success_rate": "95%",
        "last_used": "2026-04-08",
        "tags": ["react", "forms", "validation"]
      }
    ],
    
    "project_templates": {
      "saas_crm": {
        "template_id": "template_saas_crm_v1",
        "description": "Template completo para SaaS CRM com autenticacao",
        "tech_stack": ["React", "Firebase", "MCP"],
        "created_by": "lucas_valerio",
        "usage_count": 3,
        "last_used": "2026-04-07"
      },
      "trading_bot": {
        "template_id": "template_trading_bot_v1",
        "description": "Bot de trading com cTrader e ML",
        "tech_stack": ["Python", "cTrader API", "scikit-learn"],
        "created_by": "lucas_valerio",
        "usage_count": 2,
        "last_used": "2026-04-06"
      }
    },
    
    "learning_resources": {
      "internal_docs": [
        "https://docs.panda-factory.com/mcp-integration",
        "https://docs.panda-factory.com/firebase-setup"
      ],
      "external_links": [
        "https://developers.google.com/apps-script",
        "https://firebase.google.com/docs"
      ]
    }
  },
  
  // ==================== COLABORACAO ====================
  "collaboration": {
    "communication_channels": [
      {
        "type": "mcp",
        "enabled": true,
        "description": "Comunicacao via MCP tools em tempo real"
      },
      {
        "type": "discord",
        "enabled": true,
        "url": "https://discord.gg/panda-factory"
      },
      {
        "type": "a2a_direct",
        "enabled": true,
        "port": 8770,
        "description": "Comunicacao direta agent-to-agent"
      }
    ],
    
    "workflow": {
      "code_review_required": true,
      "auto_merge_on_approval": true,
      "default_branch": "main",
      "deployment_gates": ["tests_passing", "security_scan"]
    },
    
    "sync_settings": {
      "frequency": "realtime",
      "conflict_resolution": "merge_auto",
      "offline_support": true,
      "max_offline_time": "24h"
    }
  },
  
  // ==================== PROJETOS ATIVOS ====================
  "active_projects": [
    {
      "project_id": "neocortex_framework",
      "name": "NeoCortex Framework",
      "description": "Framework de contexto para agentes de IA",
      "status": "active",
      "progress": 85,
      "team_members": ["lucas_valerio", "dev_frontend_1", "dev_backend_1"],
      "tech_stack": ["Python", "MCP", "FastAPI", "WebSocket"],
      "repository": "https://github.com/panda-factory/neocortex",
      "last_activity": "2026-04-10T10:00:00Z"
    },
    {
      "project_id": "panda_factory_ui",
      "name": "Panda Factory UI",
      "description": "Interface do Panda Factory SaaS",
      "status": "active",
      "progress": 95,
      "team_members": ["dev_frontend_1", "dev_frontend_2"],
      "tech_stack": ["React", "Vite", "Firebase"],
      "repository": "https://github.com/panda-factory/ui",
      "last_activity": "2026-04-09T15:30:00Z"
    }
  ],
  
  // ==================== METRICAS DA EQUIPE ====================
  "metrics": {
    "performance": {
      "velocity_weekly": 42,                      // Story points por semana
      "bug_resolution_time_avg": "6h",
      "deployment_frequency": "daily",
      "change_failure_rate": "2%"
    },
    
    "engagement": {
      "active_members_percentage": "100%",
      "average_session_duration": "3.2h",
      "knowledge_sharing_score": 88,
      "satisfaction_score": 92
    },
    
    "knowledge_growth": {
      "new_solutions_monthly": 15,
      "template_usage_increase": "25%",
      "skill_development_rate": "18%"
    }
  },
  
  // ==================== METADADOS ====================
  "metadata": {
    "privacy_level": "team_private",              // public/team_private/org_private
    "retention_policy": "keep_forever",
    "backup_schedule": "daily",
    "compliance": ["gdpr", "lgpd"],
    "tags": ["development", "ai", "saas", "trading"]
  }
}
```

---

##  Integracao com Hierarquia de Usuarios

### **Relacao Usuario-Equipe:**
```
Usuario (nivel 5)  Pertence a  Equipe (nivel 3)
                                  
Hierarquia pessoal          Hierarquia da equipe
```

### **Regras de Acesso Cruzado:**
1. **Usuario em equipe** herda visibilidade da equipe
2. **Equipe pode ver** apenas seus membros e equipes filhas
3. **Hierarquia dupla**: Usuario tem nivel pessoal + nivel na equipe

### **Exemplo: Escola**
```
Equipe ROOT: Escola (nivel 0)
   Equipe: Professores (nivel 1)
      Usuario: Prof. Silva (nivel 2 pessoal, nivel 1 na equipe)
      Usuario: Prof. Santos (nivel 2 pessoal, nivel 1 na equipe)
  
   Equipe: Alunos (nivel 1)
       Usuario: Joao (nivel 3 pessoal, nivel 1 na equipe)
       Usuario: Maria (nivel 3 pessoal, nivel 1 na equipe)
```

---

##  Casos de Uso Hierarquicos

### **1. Corporacao Multinacional**
```
Equipe ROOT: Corporacao Global (nivel 0)
 Equipe: America Latina (nivel 1)
    Equipe: Brasil (nivel 2)
       Equipe: Sao Paulo (nivel 3)
          Equipe: TI (nivel 4)
             Usuarios: Devs (nivel 5+)
```

### **2. Governo Estadual**
```
Equipe ROOT: Governo Estadual (nivel 0)
 Equipe: Secretaria Educacao (nivel 1)
    Equipe: Departamento Ensino (nivel 2)
       Equipe: Escolas (nivel 3)
 Equipe: Secretaria Saude (nivel 1)
    Equipe: Hospitais (nivel 2)
```

### **3. Lan House Franchise**
```
Equipe ROOT: Franquia (nivel 0)
 Equipe: Unidade Centro (nivel 1)
    Equipe: Funcionarios (nivel 2)
    Equipe: Maquinas (nivel 2)
 Equipe: Unidade Shopping (nivel 1)
    Equipe: Funcionarios (nivel 2)
    Equipe: Maquinas (nivel 2)
```

---

##  Controle de Acesso em Equipes

### **Matriz de Permissoes:**
| Acao | Dono | Admin | Membro | Convidado |
|------|------|-------|--------|-----------|
| **Ver equipe** |  |  |  |  |
| **Ver membros** |  |  |  |  |
| **Ver conhecimento** |  |  |  |  |
| **Adicionar solucao** |  |  |  |  |
| **Convidar membros** |  |  |  |  |
| **Excluir equipe** |  |  |  |  |
| **Ver metricas** |  |  |  |  |

### **Heranca Hierarquica:**
- **Equipe filha** herda regras de acesso da **equipe pai**
- **Usuario** herda permissoes da **equipe principal**
- **Acesso pode ser restrito** por nivel (ex: nivel 3+ nao ve financas)

---

##  API de Gerenciamento de Equipes

### **Endpoints Principais:**
```python
# Criar equipe
POST /teams { parent_id, name, visibility }

# Adicionar membro  
POST /teams/{team_id}/members { user_id, role }

# Compartilhar solucao
POST /teams/{team_id}/knowledge { problem, solution, tags }

# Verificar acesso
GET /teams/{team_id}/access { user_id, action }

# Listar equipes acessiveis
GET /users/{user_id}/accessible_teams
```

### **Verificacao de Acesso:**
```python
def team_can_access(user_team_level, resource_team_level, user_role):
    """
    Verifica acesso entre equipes hierarquicas.
    
    Niveis de equipe:
    0: ROOT (corporacao)
    1: Regiao/Departamento
    2: Unidade/Time
    3: Sub-time/Projeto
    
    Regras:
    - Equipes podem ver equipes do MESMO nivel (com permissao)
    - Equipes podem ver equipes de NIVEIS INFERIORES
    - Equipes NAO podem ver equipes de NIVEIS SUPERIORES
    - Roles definem acoes dentro da propria equipe
    """
    if user_team_level >= resource_team_level:
        # Equipe e SUPERIOR ou IGUAL  pode acessar
        return check_role_permission(user_role)
    else:
        # Equipe e INFERIOR  NAO pode acessar
        return False
```

---

##  Implementacao Gradual

### **Fase 1: Equipes Simples** (Sem hierarquia)
- [ ] Criar equipe unica
- [ ] Adicionar membros
- [ ] Compartilhar solucoes basicas

### **Fase 2: Hierarquia Basica** (2 niveis)
- [ ] Equipes pai/filha
- [ ] Heranca de permissoes
- [ ] Controle de visibilidade

### **Fase 3: Organizacoes Complexas** (N niveis)
- [ ] Hierarquias aninhadas ilimitadas
- [ ] Matriz de permissoes avancada
- [ ] Integracao com sistemas externos

### **Fase 4: Multi-tenancy Completo**
- [ ] Isolamento de dados por tenant
- [ ] Billing e limites por organizacao
- [ ] API de administracao multi-nivel

---

##  Metricas de Sucesso

- **Adocao de equipes**: >80% dos usuarios em pelo menos 1 equipe
- **Compartilhamento de conhecimento**: 5+ solucoes/equipe/mes
- **Reducao de duplicacao**: -40% codigo duplicado
- **Velocidade de onboarding**: -60% tempo para novos membros
- **Satisfacao com colaboracao**: >85% dos membros

---

**Versao:** 1.0.0  
**Data:** 2026-04-10  
**Status:** Draft  
**Proxima Revisao:** Apos implementacao do sistema basico