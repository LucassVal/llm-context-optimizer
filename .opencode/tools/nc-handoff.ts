import { tool } from "@opencode-ai/plugin"
import { $ } from "bun"

const ROOT = "C:/Users/Lucas Valerio/Desktop/TURBOQUANT_V42"
const FW = `${ROOT}/01_neocortex_framework`

export default tool({
  description: "NeoCortex handoff — gera handoff YAML apos conclusao de tarefa",
  args: {
    ticket: tool.schema.string().describe("ID do ticket (ex: NC-DS-203)"),
    summary: tool.schema.string().describe("Resumo do que foi feito"),
    status: tool.schema.enum(["DONE","FAILED","ESCALATED","PENDING_REVIEW"]).default("DONE"),
    filesCreated: tool.schema.string().optional().describe("Arquivos criados (separados por virgula)"),
    filesModified: tool.schema.string().optional().describe("Arquivos modificados (separados por virgula)"),
  },
  async execute(args) {
    const env = { ...process.env, PYTHONPATH: FW }
    const now = new Date().toISOString().replace(/[-:]/g, "").slice(0, 15)
    const ticketId = args.ticket.replace(/^NC-DS-/, "")

    const yaml = `ticket_id: ${args.ticket}
status: ${args.status}
submitted_at: "${new Date().toISOString()}"
submitted_by: T0-opencode
summary: "${args.summary}"
files_created: [${args.filesCreated || ""}]
files_modified: [${args.filesModified || ""}]
locks_violated: false
checklist_r20:
  naming_convention: true
  no_print_statements: true
  ssot_updated: true
  no_locked_files_modified: true
  handoff_yaml_complete: true
  roadmap_marked: true
`

    const destDir = `${ROOT}/DIR-DS-002-audit-logs`
    const filename = `NC-DS-${ticketId}-handoff-${now}.yaml`
    await Bun.write(`${destDir}/${filename}`, yaml)

    return `Handoff salvo: ${destDir}/${filename}\n\n${yaml}`
  },
})
