import pathlib, re

r = pathlib.Path(r"C:\TQ")
fw = r / "01_neocortex_framework" / "neocortex"
tagged = 0

for fn in [
    "locking_config.py", "NC-CFG-FR-001-logging-config.py",
    "NC-CORE-FR-016-kg-service.py",
    "NC-CORE-FR-017-policy-loader.py",
    "NC-CORE-FR-022-save-point-service.py",
]:
    for d in [fw / "core"]:
        fp = d / fn
        if fp.exists():
            c = fp.read_text("utf-8", errors="replace")
            if "@Legacy" not in c[:300]:
                tag = "@LegacyService"
                if c.strip().startswith('"""'):
                    # Insert tag after docstring
                    c = c.replace('"""', '# ' + tag + '\n"""', 1)
                else:
                    c = "# " + tag + "\n" + c
                fp.write_text(c, "utf-8")
                tagged += 1
                break

print(f"ULQ-tagged legacy files: {tagged}")

# Also tag the non-NC legacy files (agent_service.py, etc.)
legacy = [f for f in (fw / "core").glob("*.py") if not f.name.startswith("NC-") and f.name != "__init__.py"]
for fp in legacy[:10]:
    c = fp.read_text("utf-8", errors="replace")
    if "@Legacy" not in c[:300]:
        tag = "@LegacyService" if "service" in fp.name.lower() else "@LegacyHelper"
        c = "# " + tag + " (protected by .neocortex_ignore)\n" + c
        fp.write_text(c, "utf-8")
        tagged += 1

print(f"Total tagged: {tagged}")
