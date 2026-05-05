# NC-PROMPT-DS-018  PIC-001: Instalar PicoClaw no Windows
<!-- Agente: A | Porta: 59520 | Ticket: PIC-001 | Data: 2026-04-13 -->

## GOAL
Instale o PicoClaw no Windows, verifique que o binrio funciona e confirme que o gateway pode subir na porta 18790. Entregue handoff YAML com resultado.

## STEP-0 (OBRIGATRIO  execute primeiro)
```powershell
python --version
python -m ruff --version
winget --version
```
Reporte exatamente o que retornou. Se falhar, pare e registre no handoff.

## LOCKS (@LOCKS  NO TOQUE)
- server.py, sub_server.py, neocortex_config.yaml, NC-NAM-FR-001

## WRITE ZONE
- Binrio PicoClaw: instale via winget ou coloque em `C:\Program Files\PicoClaw\`
- Configurao de teste: `DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json`
- NO crie arquivos fora dessas zonas

## CONTEXTO
- PicoClaw  um gateway Go ultra-leve (sipeed/picoclaw, v0.2.6)
- Site: picoclaw.io | Repo: github.com/sipeed/picoclaw
- Gateway expe porta 18790 com endpoints /health e /ready
- Lobe de referncia: NC-LBE-INT-001-picoclaw-architecture.mdc (605L  leia antes)

## PASSOS

### 1. Tentativa via winget
```powershell
winget search picoclaw
winget install sipeed.picoclaw
```
Se no encontrar via winget, v para o passo 2.

### 2. Download manual (fallback)
- Acesse: https://picoclaw.io/download ou https://github.com/sipeed/picoclaw/releases
- Baixe o arquivo `.exe` ou `.zip` para Windows x64
- Extraia em `C:\Program Files\PicoClaw\`
- Adicione ao PATH do usurio

### 3. Verificao
```powershell
picoclaw --version
# Deve retornar: picoclaw version v0.x.x
```

### 4. Config mnima de teste
Crie `DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json`:
```json
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 18790,
    "log_level": "info"
  },
  "model_list": []
}
```

### 5. Teste do gateway
```powershell
picoclaw --config DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json &
Start-Sleep 3
Invoke-WebRequest -Uri http://127.0.0.1:18790/health -UseBasicParsing
```
Capture o status HTTP retornado.

## HANDOFF TEMPLATE
```yaml
ticket_id: PIC-001
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 59520
files_modified:
  - DIR-DS-000-agent-config/NC-CFG-PIC-001-picoclaw-config.json
summary: |
  [Resultado da instalao: verso instalada, mtodo, /health status]
metrics:
  picoclaw_version: ""
  gateway_health: ""  # HTTP status de /health
  install_method: ""  # winget ou manual
  write_zone_respected: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  handoff_yaml_complete: true
```

Salve o handoff em: `DIR-DS-002-audit-logs/PIC-001-handoff-{YYYYMMDD-HHMMSS}.yaml`
