import { tool } from "@opencode-ai/plugin"
import { $ } from "bun"
import { readdir } from "fs/promises"

const ROOT = "C:/Users/Lucas Valerio/Desktop/TURBOQUANT_V42"
const FW = `${ROOT}/01_neocortex_framework`

export default tool({
  description: "NeoCortex validate — pipeline R6 completo para todos os tipos de arquivo (py+yaml+mdc+json)",
  args: {
    file: tool.schema.string().describe("Arquivo a validar"),
    type: tool.schema.enum(["py","yaml","mdc","json","auto"]).default("auto").describe("Tipo de arquivo (auto-detecta pela extensao)"),
  },
  async execute(args) {
    const env = { ...process.env, PYTHONPATH: FW }
    const ext = args.type === "auto" ? args.file.split(".").pop() : args.type
    const results: string[] = []

    if (ext === "py") {
      const ruff = await $`"C:/Program Files/Python312/python.exe" -m ruff check --fix "${args.file}"`.env(env).quiet().nothrow()
      results.push(`ruff: ${ruff.exitCode === 0 ? "PASS" : ruff.stderr.toString().slice(0, 200)}`)

      const compile = await $`"C:/Program Files/Python312/python.exe" -m py_compile "${args.file}"`.env(env).quiet().nothrow()
      results.push(`py_compile: ${compile.exitCode === 0 ? "PASS" : "FAIL"}`)
    } else if (ext === "yaml" || ext === "yml") {
      const yamlCheck = await $`"C:/Program Files/Python312/python.exe" -c "import yaml; yaml.safe_load(open('${args.file.replace(/\\/g,"/")}')); print('YAML OK')"`.env(env).quiet().nothrow()
      results.push(`yaml: ${yamlCheck.exitCode === 0 ? "PASS" : yamlCheck.stderr.toString().slice(0, 200)}`)
    } else if (ext === "json") {
      const jsonCheck = await $`"C:/Program Files/Python312/python.exe" -c "import json; json.load(open('${args.file.replace(/\\/g,"/")}')); print('JSON OK')"`.env(env).quiet().nothrow()
      results.push(`json: ${jsonCheck.exitCode === 0 ? "PASS" : jsonCheck.stderr.toString().slice(0, 200)}`)
    } else if (ext === "mdc") {
      const content = await Bun.file(args.file).text()
      const hasHash = content.includes("NC-READ-HASH")
      const hasFrontmatter = content.trimStart().startsWith("---")
      results.push(`mdc frontmatter: ${hasFrontmatter ? "OK" : "MISSING"}`)
      results.push(`mdc hash: ${hasHash ? "OK" : "MISSING"}`)
    }

    // Naming check
    const name = args.file.split("/").pop() || args.file.split("\\").pop() || ""
    const isNC = name.startsWith("NC-")
    results.push(`naming NC-: ${isNC ? "OK" : "NON-NC (verificar R01)"}`)

    return results.join("\n")
  },
})
