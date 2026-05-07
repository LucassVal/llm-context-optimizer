# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
import yaml, os
from datetime import datetime

base = r'C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-001-tickets'
ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

tickets = [
    ('NC-DS-250','URGENT','DeepSeek Cache Hit Monitor — instrumentar gateway para extrair prompt_cache_hit_tokens','CICLO 5: API EFICIENCIA',
     'RCA: Cache da API nao monitorado porque PulseScheduler foi desenhado para cache interno (lobes/WAL), nao para cache do provedor externo. 3W: WHAT=Extrair usage.prompt_cache_hit_tokens da resposta DeepSeek e expor como KPI. WHY=Sem isso, nao ha distincao entre custo caiu por cache vs menos uso. WHERE=NC-SVC-FR-102-gateway (borda API). KISS: <200 linhas. Extrair 2 campos do JSON de resposta. VALIDACAO: ruff+mypy+py_compile no gateway modificado. SANDBOX: Copiar gateway → editar → testar com chamada real → verificar KPI aparece. HANDOFF: YAML em DIR-DS-002 com metricas antes/depois. ESFORCO: Baixo. IMPACTO: Visibilidade total de custo. DEPENDENCIAS: Nenhuma.'),
    
    ('NC-DS-251','URGENT','Pipeline 2 Estagios (Lexico → Prefix → API) — orquestrador de otimizacao','CICLO 5: API EFICIENCIA',
     'RCA: Componentes operam isolados porque foram desenvolvidos em momentos diferentes sem contrato de interface. 3W: WHAT=Criar pipeline-orchestrator.py com Stage1(Lexico compress) → Stage2(Prefix stabilize) → API. WHY=Compressao sem prefixo estavel quebra cache. Prefixo sem compressao desperdica tokens. WHERE=01_neocortex_framework/neocortex/core/ (novo engine FR-174). KISS: <300 linhas. Orquestrador chama modulos existentes. VALIDACAO: ruff+mypy+py_compile. Teste: prompt bruto → saida comprimida+prefixada → medir tokens antes/depois. SANDBOX: Criar em paralelo, testar com prompts reais do log. HANDOFF: YAML com comparacao de tokens. ESFORCO: Medio. IMPACTO: Multiplicador de eficiencia. DEPENDENCIAS: NC-DS-250 (Cache Monitor para validar ganho).'),
    
    ('NC-DS-252','HIGH','Template-Leveled Lexicon Injection — poda contextual do ULQ por template','CICLO 5: API EFICIENCIA',
     'RCA: ULQ completo injetado quando apenas 20% dos simbolos sao relevantes para a tarefa. 3W: WHAT=Cada template recebe sub-dicionario apenas com termos ULQ do seu dominio. WHY=200-400 tokens desperdicados por chamada em simbolos irrelevantes. WHERE=LexicoService (NC-CORE-FR-116). KISS: <150 linhas. Filtrar ULQ por dominio do template. VALIDACAO: ruff+mypy+py_compile. Teste: template cortex → ULQ filtrado → medir tokens antes/depois. SANDBOX: Testar com template existente. HANDOFF: YAML com reducao de tokens. ESFORCO: Baixo. IMPACTO: Economia direta de tokens. DEPENDENCIAS: NC-DS-251 (Pipeline 2 Estagios).'),
    
    ('NC-DS-253','HIGH','Output Vocabulary Pruner — logit_bias para suprimir tokens raros','CICLO 5: API EFICIENCIA',
     'RCA: Controle de output limitado a truncar apos geracao (reativo), nao a prevenir geracao de tokens desnecessarios (proativo). 3W: WHAT=Analisar top 80% tokens frequentes por template e passar como logit_bias na API. WHY=Menos tokens gerados = menor custo + menor latencia. WHERE=Borda da API no gateway (NC-SVC-FR-102). KISS: <200 linhas. Whitelist de tokens. VALIDACAO: ruff+mypy+py_compile. Teste: com e sem pruner → medir output tokens. SANDBOX: Testar com respostas reais. HANDOFF: YAML com reducao de output tokens. ESFORCO: Medio. IMPACTO: 25-30% menos tokens de saida. DEPENDENCIAS: NC-DS-250 (Cache Monitor para calibrar).'),
    
    ('NC-DS-254','HIGH','Multi-Model Cascade com Cost-Aware Routing — flash p/ queries simples, pro p/ complexas','CICLO 5: API EFICIENCIA',
     'RCA: Toda query usa o modelo mais caro (deepseek-v4-pro) independente da complexidade. 3W: WHAT=Estimar custo por token count comprimido: <$0.001 usa flash, <$0.005 usa pro, acima tenta Qwen local. WHY=Pro e 3x mais caro que flash. Queries simples tem qualidade equivalente. WHERE=NC-SUPER-005-llm-router.py (#LLM). KISS: <250 linhas. Decision tree simples. VALIDACAO: ruff+mypy+py_compile. Teste: queries de complexidade variada → verificar modelo escolhido. SANDBOX: Testar com log de queries reais. HANDOFF: YAML com custo antes/depois. ESFORCO: Medio. IMPACTO: 30-50% reducao de custo. DEPENDENCIAS: NC-DS-250 (Cache Monitor) + NC-DS-251 (Pipeline).'),
    
    ('NC-DS-255','HIGH','Semantic Response Cache com Embedding Similarity — eliminar chamadas a API','CICLO 5: API EFICIENCIA',
     'RCA: Infraestrutura existe (KG + LanceDB + Semantic Router) mas cache ainda e visto como hash exato, nao similaridade semantica. 3W: WHAT=Indexar respostas da API no LanceDB com embedding. Novo prompt: similaridade >0.92 → retorna cache sem chamar API. WHY=Elimina completamente a chamada. 15-25% de reuso economiza esse percentual do custo total. WHERE=Semantic Router (FR-165) + KG. KISS: <300 linhas. Usar infra existente. VALIDACAO: ruff+mypy+py_compile. Teste: prompts similares → verificar cache hit. SANDBOX: Testar com log de prompts. HANDOFF: YAML com taxa de cache hit. ESFORCO: Alto. IMPACTO: Eliminacao de chamadas API. DEPENDENCIAS: Nenhuma (infra existe).'),
]

count = 0
for t in tickets:
    tid, priority, title, front, desc = t
    yaml_data = {
        'ticket_id': tid,
        'status': 'OPEN',
        'priority': priority,
        'title': title,
        'front': front,
        'description': desc,
        'created_at': ts,
        'created_by': 'T0-Antigravity',
        'roadmap_ref': 'CICLO_5',
        'protocol': {
            'rca_applied': True,
            'three_w_applied': True,
            'kiss_check': True,
            'validation': ['ruff','mypy','py_compile','bandit'],
            'sandbox_required': True,
            'handoff_required': True,
            'handoff_template': 'DIR-DS-001-tickets/NC-DS-HANDOFF-TEMPLATE.yaml',
            'handoff_dest': 'DIR-DS-002-audit-logs/',
        },
    }
    filepath = os.path.join(base, f'{tid}-ticket.yaml')
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    count += 1

print(f'Created {count} tickets with full protocol (RCA+3W+KISS+Sandbox+Handoff)')
