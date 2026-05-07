# 🧠 NC-AUD-FR-005 — DeepSeek Optimization Blueprint (V. INDUSTRIAL SUPREMA)

## 1. 🌍 3W — Visão de Eficiência de Produção
| 3W | Descrição |
|----|-----------|
| **WHAT** | Análise tática de 25 práticas de otimização de custo e performance para DeepSeek. |
| **WHY** | Eliminar o "vazamento de tokens" e atingir a eficiência de segunda ordem. |
| **WHERE** | Camada de Interface MCP e Serviços de Orquestração (`server.py` e hooks). |

## 2. 🛡️ R21 — Zero Suposições (Auditoria de Eficiência)
- **Custo:** O `neocortex_ledger` (SUPER-014) rastreia o uso bruto, mas não otimiza o cache.
- **Poda:** Verificado no `NC-HK-FR-004` -> `max_turns: 1000` (Inaceitável para produção).
- **Segurança:** Chaves injetadas via variáveis de ambiente, sem hardcoding detectado.

---

## 🧠 Aspecto 1: Engenharia de Prompt (O Comando)

| # | Prática | Diagnóstico NeoCortex R21 | RCA da Falha / GAP | Ação de Otimização |
|---|---------|:---|:---|:---|
| 1 | **Think Max** | **FALHA:** Não injetado explicitamente. | O sistema confia no potencial padrão sem forçar o modo analítico. | Injetar instrução `"Reasoning Effort: Absolute maximum"` no Kernel. |
| 2 | **Estrutura 4D** | **ATIVO:** Templates `NC-TPL-FR-002`. | N/A | Garantir que [Exemplos] sejam sempre incluídos em tarefas complexas. |
| 3 | **Saída Estruturada**| **PARCIAL:** Usado em algumas tools. | Falta de enforcement global via `response_format`. | Forçar `json_object` no orquestrador central de ferramentas. |
| 4 | **CoT (Step-by-Step)**| **PARCIAL:** Ativado pelo modelo nativo. | Não instruído explicitamente no prompt de sistema das tools. | Adicionar "Decomponha o problema passo a passo" no dispatch de agentes. |
| 5 | **Refat. Prompts** | **FALHA:** Prompts de sistema estáticos. | Diferença entre resultado medíocre e excepcional ignorada no loop. | Implementar testes A/B de prompts de sistema no `PulseScheduler`. |

---

## 💰 Aspecto 2: Estratégia de Custos (A Disciplina)

| # | Prática | Diagnóstico NeoCortex R21 | RCA da Falha / GAP | Ação de Otimização |
|---|---------|:---|:---|:---|
| 1 | **Context Caching** | **FALHA:** Injeção dinâmica instável. | Adição de lobos em ordens variadas invalida o cache de 40k tokens. | **CONGELAR** o prefixo de regras como bloco imutável absoluto. |
| 2 | **Estabilização** | **FALHA:** Mudanças em comentários de MDC. | Falta de versionamento do "Contrato de Prompt". | Criar `NC-CFG-FR-010-stable-prefix.yaml` para cache fixo. |
| 3 | **Poda Histórico** | **FALHA CRÍTICA:** 1000 turnos ativos. | **LADRÃO DE TOKENS:** Destrói o cache e encarece a entrada. | Reduzir para **15 turnos** com compressão semântica via Lexico. |
| 4 | **Novas Sessões** | **ATIVO:** Via Handoffs. | N/A | Iniciar nova sessão com resumo a cada 10 rodadas (Ciclo 2). |
| 5 | **Modelos Flash** | **FALHA:** Roteamento inativo. | Tarefas simples (linting) custam o preço de "Pro". | Implementar roteamento para modelos Flash em tarefas de rotina. |

---

## 🛡️ Aspecto 3: Resiliência e Tratamento de Erros (A Muralha)

| # | Prática | Diagnóstico NeoCortex R21 | RCA da Falha / GAP | Ação de Otimização |
|---|---------|:---|:---|:---|
| 1 | **Retry-After** | **GAP:** Backoff básico genérico. | O sistema ignora o cabeçalho 429 da API DeepSeek. | Integrar leitura de `Retry-After` no cliente HTTP core. |
| 2 | **Token Bucket** | **GAP:** Ausente no core. | Dependência do Rate Limit do provedor causa rejeição silenciosa. | Implementar algoritmo Balde de Fichas (3 req/s máx). |
| 3 | **Tratamento 502** | **GAP:** Falta de invalidação. | Tentativa de reuso de cache expirado causa loops. | Invalidar cache local imediatamente em Bad Gateway. |
| 4 | **Content Filter** | **ATIVO:** Tratado como erro. | Falta de sanitização automática de saída. | Isolar requisição e reiniciá-la com prompt sanitizado. |
| 5 | **Plano B (Fallback)**| **GAP:** Dependência Cloud. | Falta de integração com Qwen local (GPU RTX 3050). | **ATIVAR OLLAMA FALLBACK EM NC-CFG-FR-002.** |

---

## ⚡ Aspecto 4: Infraestrutura e Desempenho (O Motor)

| # | Prática | Diagnóstico NeoCortex R21 | RCA da Falha / GAP | Ação de Otimização |
|---|---------|:---|:---|:---|
| 1 | **Batch API** | **GAP:** Somente Online. | Auditorias consomem tokens em janelas de pico. | Mover processamento de logs noturnos para Batch API (-50% custo). |
| 2 | **Streaming** | **ATIVO:** Via MCP. | N/A | Garantir que o TTFT seja monitorado no Dashboard. |
| 3 | **Context Compr.** | **PARCIAL:** Nativo do V4. | Subutilização por falta de unificação de contexto. | Enviar contextos > 32k para aproveitar compressão CSA/HCA. |
| 4 | **Protobuf** | **GAP:** JSON somente. | Overhead de rede em grandes massas de dados de ledger. | Avaliar Protobuf para serialização de Auditoria Industrial. |
| 5 | **Cache Local** | **GAP:** Sem Redis. | Chamadas redundantes para tarefas idênticas. | Camada de `HashCache` (Redis/LanceDB) à frente da API. |

---

## 🔒 Aspecto 5: Segurança (As Muralhas do Castelo)

| # | Prática | Diagnóstico NeoCortex R21 | RCA da Falha / GAP | Ação de Otimização |
|---|---------|:---|:---|:---|
| 1 | **Chaves Segredo** | **ATIVO:** Variáveis de Ambiente. | N/A | Proibir logging de env vars no Mission Control. |
| 2 | **JWT / Vida Curta** | **GAP:** Chaves Estáticas. | Janela de ataque longa em caso de vazamento de credencial. | Proxy de autenticação com tokens de vida curta. |
| 3 | **Prompt Injection** | **PARCIAL:** Mordaças básicas. | Falta blindagem de persona inegociável. | Injetar cláusula de "Persona Imutável" no System Prompt. |
| 4 | **Privacidade** | **ATIVO:** BashGuard/DelGuard. | N/A | Isole dados sensíveis em VPC para deploys futuros. |
| 5 | **Menor Privilégio** | **GAP:** Chave única mestra. | Comprometimento total em caso de leak. | Segmentar chaves API por lobe/agente (Escopo limitado). |

---
**Assinado:** T0 Antigravity (Arquiteto de Eficiência Industrial)
