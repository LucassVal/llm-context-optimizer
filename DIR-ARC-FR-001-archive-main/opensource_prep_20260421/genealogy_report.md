# Relatrio do Genealogy Builder (NC-SCR-FR-070)

## Resumo Executivo

O script `NC-SCR-FR-070-genealogy-builder.py` varreu o projeto original (excluindo diretrios de backup, archive e mirror renomeado) e construiu um grafo de relaes utilizando a biblioteca `networkx`. O grafo mapeia:

1. **Imports Python**  dependncias entre mdulos
2. **Referncias a ferramentas MCP**  menes a `neocortex_*`, `NC-TOOL-FR-*` e a sigla `MCP`
3. **Menes a arquivos SSOT**  referncias a `NC-XXX-FR-XXX` e `@BOOT`/`@SSOT`

## Mtricas Gerais

- **Arquivos processados**: 634
- **Total de ns no grafo**: 1.457
- **Total de arestas (relaes)**: 7.262
- **Tipos de ns**:
  - Arquivos: 634
  - Imports: 188
  - Referncias MCP: 215
  - Menes SSOT: 420

## Distribuio de Relaes

| Tipo de Relao | Contagem | Descrio |
|----------------|----------|-----------|
| `mentions_ssot` | 3.657 | Menes a arquivos SSOT (NC-XXX-FR-XXX, @BOOT, @SSOT) |
| `references_mcp` | 2.189 | Referncias a ferramentas MCP |
| `imports` | 1.416 | Imports Python |

## Top 10 Arquivos com Mais Conexes de Sada

Os arquivos abaixo so os que mais se relacionam com outros elementos (imports, MCP, SSOT):

1. `DIR-DOC-FR-001-docs-main/artifact_catalog.json`  332 conexes
2. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_analysis_summary.yaml`  216 conexes
3. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan.yaml`  216 conexes
4. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2.yaml`  216 conexes
5. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2_dedup.yaml`  216 conexes
6. `DIR-DOC-FR-001-docs-main/rename_impact_analysis.json`  216 conexes
7. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-MAN-FR-001-project-manifest.json`  199 conexes
8. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/PROJECT_MAP.md`  199 conexes
9. `NC-IDX-FR-001-graph-extraction.json`  183 conexes
10. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/ssot_audit_report.json`  172 conexes

*Observao*: Arquivos JSON/YAML de catlogo e auditoria contm muitas menes a identificadores SSOT, o que explica a alta conectividade.

## Exemplo de Anlise para um Arquivo Core

**Arquivo**: `01_neocortex_framework/neocortex/mcp/sub_server.py`

- **Conexes de sada**: 62
  - Imports: `sys`, `neocortex.config`, `logging`, `importlib`, `pathlib`, `yaml`, `http.server`, `..config`, `mcp.server`, `neocortex.core.lobe_service`, etc.
  - Referncias MCP: `MCP` (presente no contedo)
  - Menes SSOT: `NC-CORE-FR-027-sub-server` (autoreferncia) e possivelmente outros.
- **Conexes de entrada**: 0 (nenhum outro arquivo importa ou menciona este especificamente no escano).

## Insights

1. **Alta densidade de menes SSOT**  O projeto faz uso intenso de arquivos de nomenclatura padro (NC-XXX-FR-XXX), especialmente em documentao e relatrios.
2. **Ferramentas MCP bem referenciadas**  As referncias a `neocortex_*` e `NC-TOOL-FR-*` aparecem em grande quantidade, indicando uma base de cdigo fortemente integrada ao Model Context Protocol.
3. **Imports Python diversificados**  Alm de bibliotecas padro, h muitos imports internos do prprio projeto (`neocortex.*`), incluindo imports relativos (ex. `..config`).

## Arquivos Gerados

- `genealogy_graph.json`  Grafo completo em formato JSON, compatvel com ferramentas de visualizao (ex. Gephi, Cytoscape) ou anlise programtica.
- `genealogy_summary.txt`  Estatsticas textuais e ranking de conectividade.
- `genealogy_report.md`  Este relatrio consolidado.

## Prximos Passos Sugeridos

- **Visualizao do grafo**: Utilizar `networkx` + `matplotlib` ou `pyvis` para gerar uma visualizao interativa das relaes.
- **Anlise de comunidades**: Aplicar algoritmos de deteco de comunidades (ex. Louvain) para identificar clusters de arquivos funcionalmente relacionados.
- **Impacto de mudanas**: Calcular centralidade de betweenness para identificar arquivos que atuam como pontes entre mdulos  teis para avaliao de riscos em refatoraes.
- **Validao de imports inexistentes**: Cruzar os ns do tipo `import` com a lista real de mdulos Python disponveis no projeto, sinalizando imports quebrados.

## Concluso

O Genealogy Builder produziu um mapa estrutural detalhado do projeto, capturando as trs dimenses de relacionamento solicitadas (imports, MCP, SSOT). O grafo gerado pode ser usado como base para anlises de arquitetura, auditoria de dependncias e planejamento de evoluo do cdigo.

*Script executado em*: 20260414  
*Ambiente*: Windows, Python 3.12, networkx