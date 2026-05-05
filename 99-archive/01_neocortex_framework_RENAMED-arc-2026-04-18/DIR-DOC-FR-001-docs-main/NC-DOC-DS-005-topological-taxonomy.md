---
domain: "documentation"
layer: "docs"
type: "taxonomy"
topology:
  parent: "NC-RULE-007-tagging-system.mdc"
  children: []
  dependence: []
  codependence: []
  tier: 3
keywords: [topology, tags, vector, metadata, frontmatter, taxonomy, RAG, graph]
hash: "auto-generated"
---
# NC-DOC-DS-005  Bblia Topolgica do NeoCortex

> **Documento Mestre SSOT** da taxonomia topolgica vetorial do NeoCortex Framework.  
> Este arquivo lista exaustivamente as **30 tags topolgicas vetoriais** e estabelece o padro obrigatrio de frontmatter YAML (Ruamel) para todos os arquivos do ecossistema.  
> **Atualizado:** 2026-04-14 | **Referncia:** NC-RULE-007-tagging-system.mdc

---

## 1. O Cabealho YAML/Header Obrigatrio (Ruamel)

**TODOS os arquivos do ecossistema NeoCortex devem possuir um bloco de metadados no topo**, formatado conforme a extenso do arquivo:

| Extenso          | Formato                                                                                                                                 |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Markdown (`.md`)  | Frontmatter YAML estrito delimitado por `---` (conforme exemplo acima).                                                                 |
| MDC (`.mdc`)      | Idem Markdown.                                                                                                                          |
| Python (`.py`)    | Bloco de comentrio de mltiplas linhas emulando frontmatter, usando `"""--- ... ---"""` como docstring no topo absoluto do arquivo.    |
| JavaScript/TypeScript (`.js`, `.ts`) | Bloco de comentrio `/**--- ... ---*/` no topo absoluto.                                                                       |
| JSON (`.json`)    | Chave raiz `"_meta": { ... }` contendo os metadados, mantendo o JSON vlido.                                                           |
| YAML (`.yaml`, `.yml`) | Chave raiz `_meta` ou seo separada com comentrio `# ---` antes dos dados principais.                                               |

### Por que Ruamel.yaml?

A biblioteca **ruamel.yaml**  obrigatria para parsing e escrita desses cabealhos porque:

1. **Preserva comentrios**  Metadados frequentemente evoluem; comentrios explicativos devem persistir.
2. **Mantm a ordem das chaves**  A ordem dos campos influencia a legibilidade humana e a consistncia dos diffs.
3. **Roundtrip safety**  Garante que o YAML gerado seja idntico ao original (exceto pelas alteraes intencionais).
4. **Suporte a tags customizadas**  Futuras extenses do schema podem requerer tags YAML personalizadas.

**Regra de ouro:** Nenhum script do NeoCortex deve usar `pyyaml` para manipular frontmatter; sempre use `ruamel.yaml`.

---

## 2. As 30 Tags Topolgicas Vetoriais

A tabela abaixo define cada tag, seu tipo, cardinalidade e exemplo.  
Todas as tags so **vetoriais**  podem ser indexadas por sistemas de busca semntica (Vector DB) e usadas para RAG (RetrievalAugmented Generation).

| #  | Tag (caminho)            | Tipo        | Cardinalidade | Descrio                                                                                                 | Exemplo                                                                 |
|----|--------------------------|-------------|---------------|-------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| 1  | `domain`                 | string      | 1             | **Bounded Context** do DomainDriven Design (DDD). Define o domnio de negcio ou funcional.                | `"orchestration"`, `"security"`, `"documentation"`                     |
| 2  | `context`                | string      | 1 (alternativo) | Sinnimo de `domain` para casos onde contexto  mais natural.                                           | `"agent_management"`                                                    |
| 3  | `layer`                  | string      | 1             | Camada arquitetural dentro do bounded context.                                                              | `"core"`, `"infra"`, `"utils"`, `"config"`, `"docs"`                   |
| 4  | `type`                   | string      | 1             | Tipologia do artefato.                                                                                      | `"service"`, `"tool"`, `"script"`, `"doc"`, `"module"`, `"template"`   |
| 5  | `keywords`               | array[string] | 0..n         | Palavraschave puras para busca textual (grep, FTS5).                                                       | `["agent", "task", "mcp", "sse"]`                                       |
| 6  | `tags`                   | array[string] | 0..n         | Etiquetas semnticas para classificao e filtragem.                                                        | `["critical", "deprecated", "experimental"]`                            |
| 7  | `hash`                   | string      | 1             | Assinatura criptogrfica (MD5/SHA256) do contedo do arquivo. Pode ser `"auto-generated"` na criao.      | `"a1b2c3d4e5f6"`                                                        |
| 8  | `topology.parent`        | string      | 0..1          | Entidade originadora, orquestradora ou mdulo **pai** no grafo de dependncias.                             | `"MissionControlCore"`, `"NC-RULE-007-tagging-system.mdc"`             |
| 9  | `topology.children`      | array[string] | 0..n         | Ndulos escravos ou submdulos (folhas do grafo).                                                          | `["HttpWorker", "TaskDispatcher"]`                                      |
| 10 | `topology.dependence`    | array[string] | 0..n         | Mdulos ou bibliotecas **estritas** para execuo (dependncias upstream).                                  | `["aiohttp", "ruamel.yaml"]`                                            |
| 11 | `topology.codependence`  | array[string] | 0..n         | Relaes de acoplamento bidirecional ou parapar (dependncias laterais).                                  | `["NC-TOOL-FR-022-session.py", "NC-TOOL-FR-023-orchestration.py"]`      |
| 12 | `topology.tier`          | integer     | 1             | Nvel de criticidade na arquitetura (1 = Kernel, 2 = Orchestrator, 3 = Adapter, 4 = UI).                    | `1`                                                                     |
| 13 | `criticality`            | string      | 0..1          | Grau de criticidade para operao do sistema (fora do topology.tier).                                       | `"high"`, `"medium"`, `"low"`                                           |
| 14 | `risk`                   | string      | 0..1          | Nvel de risco associado  alterao ou remoo do artefato.                                                | `"high"`, `"moderate"`, `"low"`                                         |
| 15 | `scope`                  | string      | 0..1          | Escopo de impacto: `"global"`, `"module"`, `"local"`.                                                       | `"module"`                                                              |
| 16 | `lifecycle`              | string      | 0..1          | Fase do ciclo de vida: `"experimental"`, `"active"`, `"deprecated"`, `"archived"`.                          | `"active"`                                                              |
| 17 | `status`                 | string      | 0..1          | Estado corrente: `"draft"`, `"review"`, `"approved"`, `"rejected"`.                                         | `"approved"`                                                            |
| 18 | `version`                | string      | 0..1          | Verso semntica do artefato (se aplicvel).                                                                | `"1.0.0"`                                                               |
| 19 | `author`                 | string      | 0..1          | Autor original (pessoa ou agente).                                                                          | `"T0"`, `"DeepSeekReasoner"`                                           |
| 20 | `created`                | datetime    | 0..1          | Data/hora de criao (ISO 8601).                                                                            | `"2026-04-14T10:30:00Z"`                                                |
| 21 | `modified`               | datetime    | 0..1          | Data/hora da ltima modificao (ISO 8601).                                                                 | `"2026-04-14T11:45:00Z"`                                                |
| 22 | `owner`                  | string      | 0..1          | Responsvel atual pelo artefato (role ou agente).                                                           | `"courier"`, `"engineer"`                                               |
| 23 | `component`              | string      | 0..1          | Componente maior ao qual o artefato pertence (ex: `"MissionControl"`, `"VectorDB"`).                        | `"KnowledgeGraphBuilder"`                                               |
| 24 | `subsystem`              | string      | 0..1          | Subsistema dentro do componente.                                                                            | `"embedding_generation"`                                                |
| 25 | `platform`               | string      | 0..1          | Plataforma de execuo: `"windows"`, `"linux"`, `"crossplatform"`.                                         | `"crossplatform"`                                                      |
| 26 | `language`               | string      | 0..1          | Linguagem de programao principal.                                                                         | `"python"`, `"javascript"`                                              |
| 27 | `framework`              | string      | 0..1          | Framework ou biblioteca dominante.                                                                          | `"neocortex"`, `"fastapi"`                                              |
| 28 | `dependencies`           | array[string] | 0..n         | Lista geral de dependncias (incluindo packages, mdulos internos).                                         | `["cachetools>=5.0", "rich>=13.0"]`                                     |
| 29 | `interfaces`             | array[string] | 0..n         | Interfaces expostas (APIs, endpoints, pontos de extenso).                                                  | `["/api/v1/tasks", "MCPSSE"]`                                          |
| 30 | `data_schema`            | string      | 0..1          | Schema de dados principal (JSON Schema, protobuf, etc.).                                                    | `"neocortex.schemas.ledger_schema.json"`                                |

> **Nota:** Tags com cardinalidade `0..1` so opcionais; `0..n` podem ter zero ou mais valores; `1` so obrigatrias.

---

## 3. Lgica da Taxonomia Topolgica

A taxonomia serve a trs objetivos simultneos:

1. **Busca vetorial**  Tags como `domain`, `layer`, `type` e `keywords` alimentam embeddings que permitem encontrar artefatos semanticamente similares.
2. **Anlise de impacto**  `topology.dependence`, `topology.codependence` e `criticality` permitem simular o efeito de mudanas (ex: se este servio for removido, quantos outros quebram?).
3. **Governana automatizada**  `lifecycle`, `status` e `owner` habilitam workflows de aprovao, depreciao e arquivamento sem interveno humana.

A obrigatoriedade do cabealho garante que **100% dos artefatos** sejam indexveis, criando um grafo completo de dependncias e codependncias.

---

## 4. Exemplos Cruis: Codependncia e RAG Perfeito

### Cenrio 1: Deleo Bloqueada por Codependncia

Suponha que o `server.py` tente deletar um arquivo `X` (ex: `NC-TOOL-FR-022-session.py`).  
O sistema de governana consulta o frontmatter de `X` e descobre:

```yaml
topology:
  codependence: ["NC-TOOL-FR-023-orchestration.py", "NC-SVC-FR-005-event-bus.py"]
```

Imediatamente, o **Graph Guard** impede a deleo e retorna:

>  `X`  codependente de `Y` e `Z`. Remover `X` quebraria os contratos laterais de `Y` e `Z`.  
> **Ao necessria:** Primeiro descouple a codependncia ou remova `Y` e `Z` simultaneamente.

### Cenrio 2: RAG (RetrievalAugmented Generation) com Tags Vetoriais

Um agente precisa encontrar todos os servios de orquestrao que dependem de aiohttp e esto em produo.  
A consulta vetorial traduzse em:

```python
filters = {
    "domain": "orchestration",
    "type": "service",
    "topology.dependence": {"$contains": "aiohttp"},
    "lifecycle": "active",
    "platform": "crossplatform"
}
```

O VectorDB retorna os artefatos exatos em **< 10 ms**, porque cada arquivo j carrega seus metadados como vetores prcomputados.

### Cenrio 3: Anlise de Impacto em Cadeia

Alterar o `MissionControlCore` (tier 1) dispara uma verificao recursiva:

1. Coleta todos os arquivos com `topology.parent: "MissionControlCore"`.
2. Para cada filho, coleta seus prprios filhos (transitivo).
3. Calcula o **risco agregado** usando `criticality` e `risk` de cada n.
4. Retorna um relatrio: Esta alterao impacta 47 artefatos, 12 com criticalidade alta.

Isso  possvel **apenas** porque cada arquivo declara explicitamente suas relaes topolgicas.

---

## 5. Integrao com o Ecossistema NeoCortex

- **NCRULE007**  Este documento  a expanso oficial da regra de tagging.
- **NCSCRFR003manifestfactory.py**  Deve ser atualizado para extrair e validar as 30 tags de cada arquivo.
- **NCTOOLFR024governance.py**  Usar a taxonomia para auditorias de compliance.
- **VectorDB (LanceDB/Chroma)**  Indexar as tags vetoriais para RAG de alta preciso.

---

## 6. Changelog

- **20260414**  Criao do documento SSOT por T0 (DeepSeekReasoner) como parte da tarefa NCDS048 (Saneamento de Lobos e SSOT).  
  Registrado em `NC-TODO-DS-001-roadmap-pre-mcp.md` e `NC-NAM-FR-001-naming-convention.md`.

---

## 7. Prximos Passos

1. **Atualizar `NC-TODO-DS-001-roadmap-pre-mcp.md`**  Logar a concluso desta tarefa.
2. **Atualizar `NC-NAM-FR-001-naming-convention.md`**  Registrar o novo arquivo SSOT no changelog central.
3. **Iniciar o Naming List**  Escrever a prpria Tag YAML Topolgica obrigatria da criao no escopo doc (exemplo abaixo).

### Tag YAML Topolgica desta Criao (Exemplo de Autoreferncia)

```yaml
---
domain: "documentation"
layer: "docs"
type: "taxonomy"
topology:
  parent: "NC-RULE-007-tagging-system.mdc"
  children: []
  dependence: []
  codependence: []
  tier: 3
keywords: [topology, tags, vector, metadata, frontmatter, taxonomy, RAG, graph]
hash: "auto-generated"
---
```

Este mesmo bloco j est presente no topo deste arquivo, demonstrando **autoconsistncia** e **aderncia imediata**  regra que define.

---

**Fim da Bblia Topolgica.**