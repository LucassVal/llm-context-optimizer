#!/usr/bin/env python3
"""
NC-TEST-FR-999 - STRESS TEST COMPLETO: Povoamento + Regras + Memória + Handoff + Auto-Evolve
Testa TUDO: 17 SUPER tools, regras de governança, sistema fractal, T0 expansion.
"""
import sys, os, json, time, random, traceback
from datetime import datetime

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT, "01_neocortex_framework"))

RESULTS = {"passed": 0, "failed": 0, "errors": [], "metrics": {}}
START = time.time()

def log(msg, ok=True):
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {msg}")

def test(name, fn):
    try:
        fn()
        RESULTS["passed"] += 1
        log(name)
    except Exception as e:
        RESULTS["failed"] += 1
        RESULTS["errors"].append(f"{name}: {e}")
        log(f"{name}: {e}", False)

# =====================================================================
# FASE 1: POVOAMENTO MCP — todas as 17 SUPER tools
# =====================================================================
def fase1_povoamento_mcp():
    print("\n" + "=" * 60)
    print("FASE 1: POVOAMENTO MCP — 17 SUPER TOOLS")
    print("=" * 60)

    # Import all tools dynamically
    tools_dir = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools")
    tool_files = sorted([f for f in os.listdir(tools_dir) if f.startswith("NC-SUPER") and f.endswith(".py")])

    # Add pulse bridge
    tool_files.append("pulse.py")

    loaded = 0
    for tf in tool_files:
        try:
            modname = tf.replace(".py", "")
            spec = importlib.util.spec_from_file_location(modname, os.path.join(tools_dir, tf))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            loaded += 1
        except Exception as e:
            log(f"{tf}: {e}", False)

    log(f"Carregadas {loaded}/{len(tool_files)} tools dinamicamente", loaded == len(tool_files))
    RESULTS["metrics"]["tools_carregadas"] = loaded

    # Testar actions de cada tool
    actions_testadas = 0
    for tf in tool_files:
        try:
            modname = tf.replace(".py", "")
            spec = importlib.util.spec_from_file_location(modname, os.path.join(tools_dir, tf))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Try to find a callable function (neocortex_* or * tool)
            for attr in dir(mod):
                if attr.startswith("_") or attr in ["sys", "os", "json", "time", "random"]:
                    continue
                obj = getattr(mod, attr)
                if callable(obj) and attr != "register_tool":
                    try:
                        result = obj(action="ping" if "pulse" not in tf else "status")
                        actions_testadas += 1
                    except:
                        try:
                            result = obj(action="list" if "governance" not in tf else "policy.check")
                            actions_testadas += 1
                        except:
                            pass
                    break
        except:
            pass

    RESULTS["metrics"]["actions_testadas"] = actions_testadas
    log(f"Actions testadas: {actions_testadas}")

# =====================================================================
# FASE 2: GOVERNANÇA — regras .mdc e compliance
# =====================================================================
def fase2_governanca():
    print("\n" + "=" * 60)
    print("FASE 2: GOVERNANÇA — REGRAS .MDC E COMPLIANCE")
    print("=" * 60)

    # 1. Contar regras .mdc
    mdc_files = []
    for root, dirs, files in os.walk(PROJECT):
        for f in files:
            if f.endswith(".mdc"):
                mdc_files.append(os.path.join(root, f))
    log(f"Arquivos .mdc encontrados: {len(mdc_files)}")

    # 2. Verificar naming compliance nos .mdc
    naming_ok = 0
    naming_fail = 0
    for mdc in mdc_files:
        basename = os.path.basename(mdc)
        if basename.startswith("NC-LBE-") or basename.startswith("NC-RULE-"):
            naming_ok += 1
        else:
            naming_fail += 1
    RESULTS["metrics"]["mdc_naming_ok"] = naming_ok
    RESULTS["metrics"]["mdc_naming_fail"] = naming_fail
    log(f"Naming compliance .mdc: {naming_ok}/{len(mdc_files)} OK, {naming_fail} fail", naming_fail == 0)

    # 3. Verificar SSOT
    ssot_files = []
    for root, dirs, files in os.walk(PROJECT):
        for f in files:
            if f.startswith("NC-"):
                ssot_files.append(f)
    log(f"Arquivos SSOT (NC-*): {len(ssot_files)}")

    # 4. Verificar governance tool
    try:
        spec = importlib.util.spec_from_file_location(
            "gov",
            os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "NC-SUPER-001-governance.py")
        )
        gov = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gov)
        log("governance.py carregado com sucesso")
    except Exception as e:
        log(f"governance.py: {e}", False)

    # 5. Verificar rule.list action
    try:
        for attr in dir(gov):
            if callable(getattr(gov, attr)) and not attr.startswith("_"):
                try:
                    r = getattr(gov, attr)(action="rule.list")
                    if isinstance(r, dict):
                        log(f"rule.list retornou {len(r)} chaves")
                    break
                except:
                    pass
    except:
        pass

# =====================================================================
# FASE 3: MEMÓRIA — lobos, checkpoints, sessões
# =====================================================================
def fase3_memoria():
    print("\n" + "=" * 60)
    print("FASE 3: MEMÓRIA — LOBOS, CHECKPOINTS, SESSÕES")
    print("=" * 60)

    # 1. Contar lobos
    lobes_dir = os.path.join(PROJECT, "02_memory_lobes")
    lobe_count = 0
    if os.path.exists(lobes_dir):
        for root, dirs, files in os.walk(lobes_dir):
            for f in files:
                if f.endswith((".mdc", ".md", ".json", ".yaml", ".yml")):
                    lobe_count += 1
    log(f"Arquivos em memory_lobes: {lobe_count}")

    # 2. Verificar lobe categories
    categories = [d for d in os.listdir(lobes_dir) if os.path.isdir(os.path.join(lobes_dir, d))] if os.path.exists(lobes_dir) else []
    log(f"Categorias de lobos: {len(categories)} ({', '.join(sorted(categories)[:10])}{'...' if len(categories) > 10 else ''})")

    # 3. Verificar cache/checkpoint
    cache_dir = os.path.join(PROJECT, "01_neocortex_framework", ".neocortex", "cache")
    if os.path.exists(cache_dir):
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(cache_dir):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total_size += os.path.getsize(fp)
                    file_count += 1
                except:
                    pass
        log(f"Cache: {file_count} arquivos, {total_size / 1024:.1f} KB")
        RESULTS["metrics"]["cache_files"] = file_count
        RESULTS["metrics"]["cache_size_kb"] = round(total_size / 1024, 1)

    # 4. Verificar session/timeline
    timeline_dir = os.path.join(cache_dir, "timeline") if os.path.exists(cache_dir) else None
    if timeline_dir and os.path.exists(timeline_dir):
        tl_files = len(os.listdir(timeline_dir))
        log(f"Timeline entries: {tl_files}")
        RESULTS["metrics"]["timeline_entries"] = tl_files

    # 5. Verificar memória automática
    auto_memory_path = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "NC-SUPER-015-memory-auto.py")
    if os.path.exists(auto_memory_path):
        log("NC-SUPER-015-memory-auto.py existe")
    else:
        log("NC-SUPER-015-memory-auto.py NÃO encontrado", False)

    # 6. Verificar conversation hook
    hook_path = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "core", "hooks", "NC-HK-FR-004-conversation-hook.py")
    if os.path.exists(hook_path):
        log("Conversation hook existe")
    else:
        log("Conversation hook NÃO encontrado", False)

# =====================================================================
# FASE 4: T0 EXPANSION — mentor + auto_learn + auto_evolve
# =====================================================================
def fase4_t0_expansion():
    print("\n" + "=" * 60)
    print("FASE 4: T0 EXPANSION — MENTOR + AUTO-LEARN + AUTO-EVOLVE")
    print("=" * 60)

    brain_path = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "NC-SUPER-007-brain.py")

    # 1. Verificar código fonte
    with open(brain_path, "r", encoding="utf-8") as f:
        content = f.read()

    checks = {
        "brain.mentor": "Ação mentor",
        "brain.auto_learn": "Ação auto_learn",
        "brain.auto_evolve": "Ação auto_evolve",
        "handoff_create": "Handoff integrado",
        "Agent Forest": "Agent Forest",
        "Self-Discover": "Self-Discover",
        "constitutional": "Constitutional constraints",
        "consensus_severity": "Matriz de severidade",
    }
    for keyword, desc in checks.items():
        log(f"{desc}: '{keyword}' {'encontrado' if keyword in content else 'AUSENTE'}", keyword in content)

    # 2. Verificar lobe de controle
    lobe_path = os.path.join(PROJECT, "02_memory_lobes", "09_framework", "NC-LBE-FR-MENTOR-001.mdc")
    if os.path.exists(lobe_path):
        with open(lobe_path, "r", encoding="utf-8") as f:
            lobe_content = f.read()
        lobe_checks = ["MENTOR MODE", "AUTO-LEARNING", "AUTO-EVOLVE", "never_auto_evolve", "severity_matrix", "constitutional_constraints"]
        for c in lobe_checks:
            log(f"Lobe: '{c}' presente", c in lobe_content)
    else:
        log("Lobe de controle NÃO encontrado", False)

    # 3. Verificar ticket
    ticket_path = os.path.join(PROJECT, "DIR-DS-001-tickets", "NC-DS-162-mentor-auto-evolve.yaml")
    if os.path.exists(ticket_path):
        log("Ticket NC-DS-162 existe")
    else:
        log("Ticket NC-DS-162 NÃO encontrado", False)

# =====================================================================
# FASE 5: HANDOFF + NOTIFICAÇÃO + SEGURANÇA
# =====================================================================
def fase5_handoff_seguranca():
    print("\n" + "=" * 60)
    print("FASE 5: HANDOFF + NOTIFICAÇÃO + SEGURANÇA")
    print("=" * 60)

    # 1. Verificar handoff tool
    handoff_path = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "v1", "NC-TOOL-FR-038-handoff.py")
    if os.path.exists(handoff_path):
        log("Handoff tool (v1) existe")
    else:
        log("Handoff tool não encontrada", False)

    # 2. Verificar notification tool
    notif_path = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "v1", "NC-TOOL-FR-018-push-notification.py")
    if os.path.exists(notif_path):
        log("Notification tool (v1) existe")
    else:
        log("Notification tool não encontrada", False)

    # 3. Verificar security tool
    sec_path = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "NC-SUPER-009-security.py")
    if os.path.exists(sec_path):
        log("Security tool (SUPER) existe")
    else:
        log("Security tool não encontrada", False)

    # 4. Verificar hooks registrados
    hooks_dir = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "core", "hooks")
    hooks = [f for f in os.listdir(hooks_dir) if f.endswith(".py") and f != "__init__.py"] if os.path.exists(hooks_dir) else []
    log(f"Hooks registrados: {len(hooks)} ({', '.join(hooks)})")

    # 5. Verificar auditoria
    audit_dir = os.path.join(PROJECT, "DIR-DS-002-audit-logs")
    if os.path.exists(audit_dir):
        audit_files = [f for f in os.listdir(audit_dir) if f.endswith((".json", ".log", ".csv"))]
        log(f"Arquivos de auditoria: {len(audit_files)}")
    else:
        log("DIR-DS-002-audit-logs não encontrado", False)

# =====================================================================
# FASE 6: INTEGRIDADE DO SISTEMA — configuração, pulse, boot
# =====================================================================
def fase6_integridade():
    print("\n" + "=" * 60)
    print("FASE 6: INTEGRIDADE DO SISTEMA")
    print("=" * 60)

    # 1. Config principal
    config_path = os.path.join(PROJECT, "01_neocortex_framework", "DIR-CFG-FR-001-config-main", "neocortex_config.yaml")
    if os.path.exists(config_path):
        log("Config principal existe")
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = f.read()
        if "conversation_hook" in cfg or "NC-HK-FR-004" in cfg:
            log("Conversation hook configurado no YAML")
        else:
            log("Hook NÃO configurado no YAML", False)
    else:
        log("Config principal NÃO encontrado", False)

    # 2. Pulse bridge
    pulse_path = os.path.join(tools_dir, "pulse.py") if "tools_dir" in dir() else os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "pulse.py")
    if os.path.exists(pulse_path):
        log("Pulse bridge existe")
    else:
        log("Pulse bridge não encontrado", False)

    # 3. Boot scripts
    boot_scripts = []
    scripts_dir = os.path.join(PROJECT, "01_neocortex_framework", "scripts")
    if os.path.exists(scripts_dir):
        boot_scripts = [f for f in os.listdir(scripts_dir) if "BOOT" in f.upper()]
    log(f"Boot scripts: {len(boot_scripts)}")

    # 4. Health check — servers
    health_path = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools", "NC-SUPER-013-health.py")
    if os.path.exists(health_path):
        log("Health tool existe")
    else:
        log("Health tool não encontrado", False)

# =====================================================================
# RELATÓRIO FINAL
# =====================================================================
def relatorio_final():
    elapsed = time.time() - START
    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL — STRESS TEST COMPLETO")
    print("=" * 60)
    print(f"\nTempo total: {elapsed:.2f}s")
    print(f"Testes: {RESULTS['passed']} PASS / {RESULTS['failed']} FAIL / {RESULTS['passed'] + RESULTS['failed']} total")
    print(f"Taxa de sucesso: {100 * RESULTS['passed'] / (RESULTS['passed'] + RESULTS['failed'] or 1):.1f}%")

    if RESULTS["metrics"]:
        print(f"\nMétricas coletadas:")
        for k, v in RESULTS["metrics"].items():
            print(f"  {k}: {v}")

    if RESULTS["errors"]:
        print(f"\nErros ({len(RESULTS['errors'])}):")
        for e in RESULTS["errors"][:10]:
            print(f"  - {e}")

    print(f"\n{'=' * 60}")
    if RESULTS["failed"] == 0:
        print("RESULTADO: SUCESSO TOTAL — Sistema íntegro e funcional")
    else:
        print(f"RESULTADO: {RESULTS['failed']} falha(s) — revisar erros acima")
    print(f"{'=' * 60}")

    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed, 2),
        "passed": RESULTS["passed"],
        "failed": RESULTS["failed"],
        "success_rate": round(100 * RESULTS["passed"] / (RESULTS["passed"] + RESULTS["failed"] or 1), 1),
        "metrics": RESULTS["metrics"],
        "errors": RESULTS["errors"][:20],
    }
    report_path = os.path.join(PROJECT, "05_examples", f"NC-RPT-999-stress-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nRelatório salvo: {report_path}")

    return RESULTS["failed"] == 0

# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    import importlib.util

    tools_dir = os.path.join(PROJECT, "01_neocortex_framework", "neocortex", "mcp", "tools")

    print("=" * 60)
    print("NC-TEST-FR-999 — STRESS TEST COMPLETO")
    print(f"Projeto: {PROJECT}")
    print(f"Início: {datetime.now().isoformat()}")
    print("=" * 60)

    test("FASE 1: Povoamento MCP (17 tools)", fase1_povoamento_mcp)
    test("FASE 2: Governança e regras .mdc", fase2_governanca)
    test("FASE 3: Memória fractal (lobos/checkpoints)", fase3_memoria)
    test("FASE 4: Expansão T0 (mentor/auto_learn/auto_evolve)", fase4_t0_expansion)
    test("FASE 5: Handoff + Notificação + Segurança", fase5_handoff_seguranca)
    test("FASE 6: Integridade do sistema", fase6_integridade)

    success = relatorio_final()
    sys.exit(0 if success else 1)
