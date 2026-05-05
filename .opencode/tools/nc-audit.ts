import { tool } from "@opencode-ai/plugin"
import { $ } from "bun"

const ROOT = "C:/Users/Lucas Valerio/Desktop/TURBOQUANT_V42"
const FW = `${ROOT}/01_neocortex_framework`

export default tool({
  description: "NeoCortex audit 3 niveis — compile + runtime + operational. Gera relatorio de compliance.",
  args: {
    level: tool.schema.enum(["1","2","3","all"]).default("all").describe("Nivel da auditoria: 1=compile, 2=runtime, 3=operational, all=todos"),
    output: tool.schema.string().optional().describe("Caminho para salvar relatorio JSON"),
  },
  async execute(args) {
    const env = { ...process.env, PYTHONPATH: FW }
    const auditPy = `${FW}/neocortex/core/NC-CORE-FR-173-mcp-audit-3-levels.py`

    const result = await $`"C:/Program Files/Python312/python.exe" -c "
import sys; sys.path.insert(0, '${FW}')
from neocortex.core.NC_CORE_FR_173_mcp_audit_3_levels import MCPAudit3Levels
import json
auditor = MCPAudit3Levels()
if '${args.level}' == 'all':
    report = auditor.audit_all_levels()
else:
    camada = 'audit_camada_' + '${args.level}'
    report = getattr(auditor, camada)()
print(json.dumps(report, indent=2, default=str))
"`.env(env).quiet()

    return result.stdout.toString()
  },
})
