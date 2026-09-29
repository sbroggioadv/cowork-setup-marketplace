#!/usr/bin/env python3
"""Stop hook do cowork-setup (regra 9, sem git): se houve arquivo alterado em clientes/<x>/… nesta sessão sem o STATE.md
do projeto (ou do cliente) também alterado, OU se o cliente tocado ficou com erro de estrutura, bloqueia o encerramento UMA vez.
Base de comparação: carimbo _sistema/.sessao gravado pelo SessionStart. Sem carimbo → não bloqueia."""
import json, os, subprocess, sys
from pathlib import Path
try: inp = json.load(sys.stdin)
except Exception: inp = {}
if inp.get("stop_hook_active"): sys.exit(0)
root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
ses = root / "_sistema" / ".sessao"
if not ses.exists(): sys.exit(0)
try: ts = float(ses.read_text().strip())
except Exception: sys.exit(0)
base = root / "clientes"
if not base.exists(): sys.exit(0)
S = Path(__file__).resolve().parent.parent / "scripts"
def projeto_de(f: Path) -> Path:
    r = f.relative_to(base).parts   # <cli>/<tipo>/<area>/<proj>/... ou <cli>/holding/... ou <cli>/...
    if len(r) >= 2 and r[1] == "holding": return base / r[0] / "holding"
    if len(r) >= 4: return base / r[0] / r[1] / r[2] / r[3]
    return base / r[0]
faltando = set()
for f in base.rglob("*"):
    if not f.is_file() or f.name in (".DS_Store",) or f.stat().st_mtime <= ts: continue
    if f.name == "STATE.md": continue
    p = projeto_de(f); cli = base / f.relative_to(base).parts[0]
    ok = any((d / "STATE.md").exists() and (d / "STATE.md").stat().st_mtime > ts for d in (p, cli))
    if not ok: faltando.add(str(p.relative_to(root)))
motivos = []
if faltando:
    motivos.append("Regra 9: houve alteração em pasta de cliente sem atualizar o STATE.md correspondente: " + "; ".join(sorted(faltando))
                   + ". Atualize Fase atual / Próximo passo / Histórico no STATE.md do projeto (ou use /encerrar).")
lint = subprocess.run([sys.executable, str(S / "lint.py"), "--desde", str(ts), "--so-erros"], cwd=root, capture_output=True, text=True)
erros = [l for l in lint.stdout.splitlines() if l.startswith("E ")]
if erros:
    motivos.append("Estrutura com erro no cliente tocado — corrija ou justifique ao advogado: " + " | ".join(erros[:6]) + (f" | +{len(erros)-6}" if len(erros) > 6 else "") + ". Use /lint-estrutura.")
if not motivos: sys.exit(0)
print(json.dumps({"decision": "block", "reason": " ".join(motivos)})); sys.exit(0)
