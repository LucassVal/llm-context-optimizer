import { tool } from "@opencode-ai/plugin"
import { $ } from "bun"

const ROOT = "C:/Users/Lucas Valerio/Desktop/TURBOQUANT_V42"
const FW = `${ROOT}/01_neocortex_framework`
const PYTHON = "C:/Program Files/Python312/python.exe"

export default tool({
  description: "NeoCortex lint — ruff check + mypy em arquivos .py",
  args: {
    file: tool.schema.string().describe("Caminho do arquivo .py a verificar"),
    full: tool.schema.boolean().default(false).describe("Executar pipeline completo (ruff + mypy + bandit)"),
  },
  async execute(args) {
    const env = { ...process.env, PYTHONPATH: FW }
    const file = args.file.replace(/\\/g, "/")

    const results: string[] = []

    const ruff = await $`"${PYTHON}" -m ruff check --fix "${file}"`.env(env).quiet().nothrow()
    results.push(`ruff: ${ruff.exitCode === 0 ? "PASS" : "FAIL"}`)
    if (ruff.exitCode !== 0) results.push(ruff.stderr.toString().slice(0, 500))

    const fmt = await $`"${PYTHON}" -m ruff format "${file}"`.env(env).quiet().nothrow()
    results.push(`format: ${fmt.exitCode === 0 ? "OK" : "FAIL"}`)

    if (args.full) {
      const mypy = await $`"${PYTHON}" -m mypy "${file}" --ignore-missing-imports`.env(env).quiet().nothrow()
      results.push(`mypy: ${mypy.exitCode === 0 ? "PASS" : "FAIL"}`)
    }

    return results.join("\n")
  },
})
