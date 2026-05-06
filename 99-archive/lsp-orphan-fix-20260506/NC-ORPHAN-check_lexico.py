import json

with open("01_neocortex_framework/.neocortex/lexico/NC-LEXICO-LATEST.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print("=== LEXICO v{} ===".format(d.get("version", "?")))
print("engines:", d.get("total_engines"))
print("tools:", d.get("total_tools"))
print("services:", d.get("total_services"))
print()

# Spot-check key IDs
for lookup in ["NC-CORE-FR-154", "NC-CORE-FR-174", "NC-SUPER-001", "NC-HK-FR-009", "NC-LLM-FR-001"]:
    all_entries = d.get("engines", []) + d.get("tools", []) + d.get("services", [])
    found = [e for e in all_entries if e["id"] == lookup]
    status = "FOUND: " + found[0]["path"] if found else "NOT FOUND"
    print(lookup + ": " + status)

# Check for small files that might be stubs/wrappers
print()
engines = d.get("engines", [])
tiny = [e for e in engines if e["size"] < 300]
print("Tiny engines (<300 bytes, possible stubs/wrappers): " + str(len(tiny)))
for s in tiny[:15]:
    print("  {}: {}b".format(s["id"], s["size"]))

# Check strangler wrappers
print()
all_entries = engines + d.get("tools", []) + d.get("services", [])
stranglers = [e for e in all_entries if "strangler" in e.get("desc", "").lower() or "wrapper" in e.get("desc", "").lower()]
print("Strangler wrappers: " + str(len(stranglers)))
for s in stranglers[:10]:
    print("  {}: {} ({}b)".format(s["id"], s["desc"], s["size"]))
