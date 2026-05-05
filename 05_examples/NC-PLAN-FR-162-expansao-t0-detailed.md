# T0 Expansion: Mentor + Auto-Learning + Auto-Evolve (Versão Expandida)

## 🎯 **Visão Expandida com SOTA 2025/2026**

Baseado no plano original e pesquisa arXiv, aqui está uma visão expandida com conceitos adicionais:

### 🔍 **Conceitos SOTA Adicionais Identificados:**

1. **"Chain of Hindsight"** - Para Mentor Mode: T0 mostra não só o erro, mas o caminho correto
2. **"Process Supervision"** vs "Outcome Supervision" - Criticar o processo, não só o resultado
3. **"Mixture of Experts"** - Para Agent Forest: diferentes especialistas para diferentes tipos de erro
4. **"Constitutional AI"** - Para Auto-Evolve: evolução baseada em princípios/constitucionais
5. **"Recursive Criticism"** - T0 critica suas próprias críticas (meta-critique)

## 🧠 **Arquitetura Expandida**

### **MENTOR MODE 2.0** (`brain.mentor`)
**Melhorias sobre plano original:**

1. **Agent Forest com Mixture of Experts**:
   - `expert_coding`: Especialista em erros de código
   - `expert_logic`: Especialista em falhas lógicas  
   - `expert_process`: Especialista em processos/etapas
   - `expert_security`: Especialista em riscos de segurança

2. **Chain of Hindsight Integration**:
   ```python
   # Não só "está errado", mas "aqui está o caminho correto"
   feedback = {
       "error": "Falta validação de input",
       "hindsight_path": [
           "1. Validar input com regex",
           "2. Tratar edge cases", 
           "3. Adicionar logging",
           "4. Retornar erro descritivo"
       ]
   }
   ```

3. **Process Supervision**:
   - Criticar **como** o agente pensou, não só **o que** produziu
   - Analisar chain of thought (se disponível)
   - Identificar vieses cognitivos

4. **Handoff "Bronca" com Severity Matrix**:
   ```yaml
   handoff_type: "mentor_bronca"
   severity: "ALTA"  # BAIXA, MÉDIA, ALTA, CRÍTICA
   agent_id: "T1-ENGINEER-001"
   error_category: "security_risk"
   correction_required: True
   deadline: "24h"  # Tempo para corrigir
   ```

### **AUTO-LEARNING 2.0** (`brain.auto_learn`)
**Melhorias com Self-Discover avançado:**

1. **Self-Discover Reasoning Modules**:
   - `pattern_extraction`: Extrai padrões de sucesso/falha
   - `causal_analysis`: Identifica relações causa-efeito
   - `generalization`: Generaliza lições específicas para princípios
   - `meta_learning`: Aprende como aprender melhor

2. **Learning Curriculum Auto-Generation**:
   ```python
   curriculum = {
       "weak_areas": ["input_validation", "error_handling"],
       "training_exercises": [
           {"type": "code_review", "difficulty": "medium"},
           {"type": "bug_fix", "difficulty": "hard"}
       ],
       "progress_tracking": True
   }
   ```

3. **Cross-Session Pattern Analysis**:
   - Conecta lições entre diferentes sessões
   - Identifica padrões recorrentes entre diferentes agentes
   - Cria "learning trajectories"

### **AUTO-EVOLVE 2.0** (`brain.auto_evolve`)  
**Melhorias com Constitutional AI + LATS:**

1. **Constitutional Evolution Principles**:
   ```python
   constitution = [
       "Nunca comprometer segurança",
       "Manter compatibilidade retroativa",
       "Preservar simplicidade",
       "Respeitar limites de performance"
   ]
   ```

2. **LATS Tree Search Aprimorado**:
   - **Branch**: Proposta de mudança
   - **Evaluate**: Score baseado em constitution + métricas
   - **Prune**: Remove branches que violam princípios
   - **Expand**: Desenvolve branches promissores

3. **Evolution Safeguards**:
   - **Dry-run obrigatório** para todas as evoluções
   - **Human-in-the-loop** para mudanças críticas
   - **Rollback mechanism** automático
   - **A/B testing** virtual antes de aplicar

## 🏗️ **Implementação Concreta**

### **Fase 1: Mentor Mode (Sprint 1-2 semanas)**
```python
# Adicionar ao NC-SUPER-007-brain.py
def _mentor(agent_output, agent_id, context, error_type=None):
    # 1. Classificar tipo de erro
    error_category = classify_error(agent_output, error_type)
    
    # 2. Selecionar experts apropriados
    experts = select_experts(error_category)
    
    # 3. Agent Forest evaluation
    evaluations = [expert.evaluate(agent_output, context) for expert in experts]
    
    # 4. Voting + consensus
    consensus, confidence = voting_mechanism(evaluations)
    
    # 5. Chain of Hindsight
    hindsight_path = generate_hindsight_path(agent_output, consensus)
    
    # 6. Criar handoff bronca
    if consensus["severity"] >= "MEDIA":
        create_bronca_handoff(
            agent_id=agent_id,
            error=consensus["error"],
            hindsight=hindsight_path,
            severity=consensus["severity"],
            deadline=calculate_deadline(consensus["severity"])
        )
    
    # 7. Registrar no AKL
    akl_add_lesson(
        agent_id=agent_id,
        lesson=consensus,
        hindsight=hindsight_path,
        confidence=confidence
    )
    
    return formatted_feedback(consensus, hindsight_path)
```

### **Fase 2: Auto-Learning (Sprint 2-3 semanas)**
```python
def _auto_learn(session_id, n_turns=50):
    # 1. Coletar histórico da sessão
    history = get_session_history(session_id, n_turns)
    
    # 2. Self-Discover reasoning structure
    reasoning_modules = self_discover_modules(history)
    structure = compose_structure(reasoning_modules)
    
    # 3. Aplicar estrutura para extrair lições
    lessons = apply_reasoning_structure(history, structure)
    
    # 4. Generalizar e categorizar
    generalized = generalize_lessons(lessons)
    categorized = categorize_lessons(generalized)
    
    # 5. Criar learning curriculum
    curriculum = generate_curriculum(categorized)
    
    # 6. Persistir em lobe
    create_learned_lobe(
        lessons=categorized,
        reasoning_structure=structure,
        curriculum=curriculum,
        session_id=session_id
    )
    
    return {
        "lessons_extracted": len(categorized),
        "reasoning_structure": structure,
        "curriculum_generated": bool(curriculum)
    }
```

### **Fase 3: Auto-Evolve (Sprint 3-4 semanas)**
```python
def _auto_evolve(target_lobe, dry_run=True, evolution_scope="safe"):
    # 1. Verificar se lobe é elegível para evolução
    if not is_evolvable(target_lobe, evolution_scope):
        return {"error": "Lobe não elegível para evolução"}
    
    # 2. Constitutional constraints
    constraints = get_constitutional_constraints(evolution_scope)
    
    # 3. LATS tree search
    proposals = lats_tree_search(
        target_lobe=target_lobe,
        constraints=constraints,
        max_depth=3,
        beam_width=5
    )
    
    # 4. Avaliar com constitution
    scored_proposals = []
    for proposal in proposals:
        score = evaluate_with_constitution(proposal, constraints)
        if score >= EVOLUTION_THRESHOLD:
            scored_proposals.append((proposal, score))
    
    # 5. Selecionar melhor proposta
    if scored_proposals:
        best_proposal, best_score = max(scored_proposals, key=lambda x: x[1])
        
        # 6. Aplicar (se não for dry-run)
        if not dry_run and best_score >= APPLY_THRESHOLD:
            result = apply_evolution(best_proposal, target_lobe)
            
            # 7. Criar handoff de evolução
            create_evolution_handoff(
                lobe_id=target_lobe,
                proposal=best_proposal,
                score=best_score,
                result=result,
                constraints_used=constraints
            )
            
            return {
                "evolution_applied": True,
                "lobe": target_lobe,
                "score": best_score,
                "handoff_created": True
            }
        else:
            return {
                "dry_run": dry_run,
                "best_proposal": best_proposal["summary"],
                "best_score": best_score,
                "apply_threshold": APPLY_THRESHOLD,
                "would_apply": best_score >= APPLY_THRESHOLD
            }
    
    return {"evolutions_found": 0, "reason": "No proposals above threshold"}
```

## 🛡️ **Safeguards e Controles**

### **Lobe de Controle: NC-LBE-FR-MENTOR-001.mdc**
```yaml
# Conteúdo do lobe de controle
version: "1.0"
type: "control_lobe"
protected: True

evolution_constraints:
  never_modify:
    - "NC-RULE-001-core-ssot.mdc"
    - "NC-LBE-FR-CORE-OPS-001.mdc"
    - "NC-CONSTITUTION-001.mdc"
  
  require_human_approval:
    - severity: "HIGH"
    - scope: "architecture"
    - performance_impact: ">10%"
  
  auto_evolve_limits:
    max_evolutions_per_day: 3
    max_scope: "non_critical"
    dry_run_required: True

mentor_mode:
  severity_matrix:
    BAIXA: ["code_style", "minor_optimization"]
    MÉDIA: ["logic_error", "missing_validation"]
    ALTA: ["security_risk", "data_loss"]
    CRÍTICA: ["system_crash", "privilege_escalation"]
  
  bronca_deadlines:
    BAIXA: "7d"
    MÉDIA: "72h"
    ALTA: "24h"
    CRÍTICA: "IMMEDIATE"

auto_learning:
  min_turns_for_analysis: 10
  lesson_extraction_threshold: 0.7
  curriculum_update_frequency: "weekly"
```

## 📊 **Métricas e Monitoramento**

### **Métricas de Sucesso:**
1. **Mentor Mode**:
   - Reduction in repeat errors: Target: -40%
   - Feedback quality score: Target: ≥8/10
   - Time to correction: Target: < deadline in 90% cases

2. **Auto-Learning**:
   - Lessons extracted per session: Target: ≥5
   - Curriculum effectiveness: Target: +25% task success rate
   - Pattern discovery rate: Target: ≥2 new patterns/week

3. **Auto-Evolve**:
   - Successful evolutions: Target: ≥1/week
   - Zero regressions: Target: 100%
   - Constitution compliance: Target: 100%

## 🚀 **Roadmap de Implementação**

### **Week 1-2: Mentor Mode MVP**
- Implementar `brain.mentor` básico
- Agent Forest com 2 experts
- Handoff bronca simples
- Testes com erros simulados

### **Week 3-4: Auto-Learning MVP**
- Implementar `brain.auto_learn`
- Self-Discover básico
- Lobe generation
- Testes com sessões históricas

### **Week 5-6: Auto-Evolve MVP**
- Implementar `brain.auto_evolve`
- LATS tree search básico
- Constitutional constraints
- Dry-run mode completo

### **Week 7-8: Integração e Refinamento**
- Integrar todos os modos
- Adicionar safeguards avançados
- Performance optimization
- Documentação completa

## 💡 **Inovações Propostas**

1. **"Bronca Chain"** - Rastreamento de correções de erro
2. **"Evolution DNA"** - Histórico genético de cada lobe
3. **"Learning Transfer"** - Transferir lições entre agentes
4. **"Meta-Mentor"** - T0 aprende a ser melhor mentor

## ⚠️ **Riscos e Mitigações**

| Risco | Mitigação |
|-------|-----------|
| Over-evolution | Constitutional constraints + dry-run |
| Negative feedback loops | Confidence thresholds + human oversight |
| Performance degradation | Caching + incremental processing |
| Security vulnerabilities | Security expert in Agent Forest |

## 🎯 **Conclusão**

Esta expansão transforma o T0 de um agente estático para um **sistema de aprendizado e evolução contínua**. Com Mentor Mode 2.0, Auto-Learning com Self-Discover, e Auto-Evolve constitucional, o NeoCortex se torna verdadeiramente auto-aprimorável enquanto mantém segurança e controle.

**Próximo passo**: Implementar `brain.mentor` com Agent Forest e handoff bronca.