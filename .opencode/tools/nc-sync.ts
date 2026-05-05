import { tool } from "@opencode-ai/plugin"
import { $ } from "bun"

const ROOT = "C:/Users/Lucas Valerio/Desktop/TURBOQUANT_V42"
const FW = `${ROOT}/01_neocortex_framework`

export default tool({
  description: "NeoCortex boot sync — sincroniza @BOOT e regenera artifact_catalog.json",
  args: {
    runCatalog: tool.schema.boolean().default(true).describe("Tambem regenerar artifact_catalog.json"),
  },
  async execute(args) {
    const env = { ...process.env, PYTHONPATH: FW }

    const results: string[] = []

    const sync = await $`"C:/Program Files/Python312/python.exe" -c "
import sys; sys.path.insert(0, '${FW}')
from scripts.NC_SCR_FR_066_bootup_sync import main
main()
"`.env(env).quiet().nothrow()
    results.push(`bootup.sync: ${sync.exitCode === 0 ? "OK" : sync.stderr.toString().slice(0, 300)}`)

    if (args.runCatalog) {
      const cat = await $`"C:/Program Files/Python312/python.exe" "${FW}/scripts/NC-SCR-FR-064-artifact-catalog.py"`.env(env).quiet().nothrow()
      results.push(`catalog: ${cat.exitCode === 0 ? "OK" : cat.stderr.toString().slice(0, 300)}`)
    }

    return results.join("\n")
  },
})
