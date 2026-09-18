#!/usr/bin/env python3
"""F4 — Auditoria de ponta a ponta: 12 verificações PASS/FAIL/AVISO com evidência. Grava _sistema/migracao/AUDITORIA-AAAA-MM-DD.md.
Uso: python3 auditar.py [--raiz X] [--corrigir] [--json]     Exit 2 = há FAIL · 0 = ok (avisos não barram)."""
import argparse, json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raiz"); ap.add_argument("--corrigir", action="store_true"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(); root = raiz(a.raiz); esp = espec(); S = Path(__file__).resolve().parent
    R = []  # (n, nome, status, evidencia)
    def add(n, nome, ok, ev, aviso=False): R.append((n, nome, "PASS" if ok else ("AVISO" if aviso else "FAIL"), ev))
    ABS = re.compile(esp["nome"]["caminho_absoluto"])

    # 1 estrutura (lint)
    if a.corrigir: subprocess.run([sys.executable, str(S / "lint.py"), "--corrigir"], cwd=root, capture_output=True, text=True)
    lint = subprocess.run([sys.executable, str(S / "lint.py"), "--json"], cwd=root, capture_output=True, text=True)
    try: lj = json.loads(lint.stdout)
    except Exception: lj = {"erros": [{"codigo": "LINT", "caminho": "", "motivo": lint.stderr[-300:]}], "avisos": []}
    add(1, "Estrutura (lint contra a espec)", not lj["erros"], (f"{len(lj['erros'])} erro(s): " + "; ".join(f"{e['codigo']} {e['caminho']}" for e in lj["erros"][:6])) if lj["erros"] else f"0 erros · {len(lj['avisos'])} aviso(s)")
    # 2 integridade (nada perdido) — só se houve censo/migração
    censo = ler_json(root / "_sistema" / "censo.json", {}) or {}
    if censo.get("arquivos_lista"):
        sys.path.insert(0, str(S)); from aplicar import arquivos_perdidos
        perd = arquivos_perdidos(root)
        add(2, "Integridade (todo arquivo original reencontrado)", not perd, "0 perdidos ✓" if not perd else f"{len(perd)} perdido(s): " + "; ".join(perd[:5]))
    else:
        add(2, "Integridade", True, "sem censo de migração (pasta nova) — nada a conferir")
    # 3 legado antigo na raiz
    lg = esp["legado_antigo"]; rest = []
    for f in root.iterdir():
        if f.name in ("CLAUDE.md", "TASKS.md"): continue
        if f.is_file() and f.name in lg["raiz_arquivos"]: rest.append(f.name)
        if f.is_dir() and f.name in lg["raiz_pastas"] and f.name != lg["raiz_pastas"][f.name]: rest.append(f.name + "/")
    add(3, "Formato antigo na raiz (CLIENTES/, PERSONA.md, MEMORY.md, BASE DE CONHECIMENTO…)", not rest, "nenhum ✓" if not rest else "ainda existem: " + ", ".join(rest))
    # 4 constituição
    cl = root / "CLAUDE.md"; t = ler(cl); secs = [f"## {i}." for i in range(1, 9)]; falt = [s for s in secs if s not in t]
    ph = PLACEHOLDER.findall(t)
    add(4, "CLAUDE.md (constituição) + TASKS.md", cl.exists() and not falt and not ph and (root / "TASKS.md").exists(),
        ("ok ✓" if cl.exists() and not falt and not ph else f"faltam seções {falt} · placeholders {ph}") + ("" if (root / "TASKS.md").exists() else " · sem TASKS.md"))
    # 5 identidade
    idd = root / "identidade"; falt = [f for f in esp["identidade"]["arquivos"] if not (idd / f).exists()]
    ph = []; apre = []
    for f in esp["identidade"]["arquivos"]:
        tx = ler(idd / f); ph += [f"{f}:{p}" for p in PLACEHOLDER.findall(tx)]
        if "[A PREENCHER]" in tx: apre.append(f)
    ok5 = not falt and not ph and "01-QUEM-SOU.md" not in apre
    add(5, "identidade/ 00–06 (sem {{placeholder}}; 01 sem [A PREENCHER])", ok5, ("ok ✓" if ok5 else f"faltam {falt} · placeholders {ph[:5]} · [A PREENCHER] em {apre}"))
    if apre and ok5: add(5.1, "identidade/ com [A PREENCHER] (completar quando puder)", False, ", ".join(apre), aviso=True)
    # 6 knowledge
    kt = root / "knowledge" / "templates"; falt = [f for f in esp["knowledge"]["templates"] if not (kt / f).exists()]
    add(6, "knowledge/ (README + 4 templates)", (root / "knowledge" / "README.md").exists() and not falt, "ok ✓" if not falt else "faltam: " + ", ".join(falt))
    # 7 sistema
    vs = ler(root / "_sistema" / "versao").strip()
    add(7, "_sistema/ (versao = plugin, areas.json)", vs == versao_plugin() and (root / "_sistema" / "areas.json").exists(), f"versao {vs or '—'} vs plugin {versao_plugin()}")
    # 8 plano aprovado (se migração)
    pl = ler_json(root / "_sistema" / "migracao" / "plano.json")
    if pl:
        pend = [o for o in pl["ops"] if o.get("status") == "pendente"]
        add(8, "Plano de migração aprovado e sem operação pendente", pl.get("aprovado") and not pend, f"aprovado={pl.get('aprovado')} · pendentes={len(pend)}")
    else:
        add(8, "Plano de migração", True, "não houve migração (pasta nova)")
    # 9 roteamento
    r5 = ler(idd / "05-ROTEAMENTO-PLUGINS.md"); local = ler_json(root / "_sistema" / "areas.json", {"areas": {}}) or {"areas": {}}
    sem = [x for x in local.get("areas", {}) if f"| {x} |" not in r5]
    add(9, "Roteamento (toda área registrada tem linha em identidade/05)", not sem, "ok ✓" if not sem else "áreas sem linha: " + ", ".join(sem) + " — rode /cowork-setup atualizar")
    # 10 caminhos absolutos
    abs_ = []
    for f in root.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in (".md", ".txt", ".json", ".html", ".yaml", ".yml", ".py", ".sh"): continue
        if ".claude" in f.parts or "_sistema" in f.parts or f.name in ("cowork-state.json", ".hook-state.json"): continue
        if any(eh_motor(p, esp) for p in f.parents if p != root and p.parent == root): continue
        if ABS.search(ler(f)): abs_.append(rel(root, f))
    add(10, "Nenhum caminho absoluto de máquina em arquivo da bancada", not abs_, "ok ✓" if not abs_ else "; ".join(abs_[:6]))
    # 11 motores
    mots = [d.name for d in root.iterdir() if d.is_dir() and eh_motor(d, esp)]
    add(11, "Motores dos plugins intactos na raiz", True, ", ".join(mots) or "nenhum (instale/rode /start-* dos plugins que usar)", aviso=not mots)
    # 12 hook de sessão
    ses = root / "_sistema" / ".sessao"
    add(12, "Hook de sessão do plugin já rodou nesta pasta", ses.exists(), "ok ✓" if ses.exists() else "ainda não — feche e reabra a pasta no Cowork; se não aparecer, use /comecar e /encerrar", aviso=True)
    # 13 triagem
    tri = root / "_legado" / "triagem"; n = sum(1 for f in tri.rglob("*") if f.is_file()) if tri.exists() else 0
    add(13, "_legado/triagem/ (decisões do advogado pendentes)", n == 0, "vazio ✓" if not n else f"{n} arquivo(s) esperando decisão", aviso=True)

    fails = [r for r in R if r[2] == "FAIL"]; avisos = [r for r in R if r[2] == "AVISO"]
    L = [f"# AUDITORIA — {root.name} · {agora()} · plugin {versao_plugin()}", "", f"**Resultado: {'APROVADA' if not fails else 'REPROVADA'}** — {len(fails)} FAIL · {len(avisos)} AVISO · {len(R) - len(fails) - len(avisos)} PASS", "",
         "| # | Verificação | Status | Evidência |", "|---|---|---|---|"] + [f"| {n} | {nome} | **{st}** | {ev} |" for n, nome, st, ev in R]
    if lj["avisos"]:
        L += ["", "## Avisos do lint (não barram)", ""] + [f"- `{x['codigo']}` {x['caminho']} — {x['motivo']}" for x in lj["avisos"][:40]]
    L += ["", "Auditoria repetível: `/cowork-setup` → auditar. FAIL some com correção; AVISO é lista de trabalho do advogado.", ""]
    mig = sistema(root) / "migracao"; mig.mkdir(exist_ok=True); out = mig / f"AUDITORIA-{hoje()}.md"; out.write_text("\n".join(L), encoding="utf-8")
    if a.json: print(json.dumps({"fails": len(fails), "avisos": len(avisos), "itens": R}, ensure_ascii=False, indent=2))
    else:
        for n, nome, st, ev in R: print(f"[{st:5}] {n:>4} {nome} — {ev}")
        print(f"\n{'APROVADA' if not fails else 'REPROVADA'} · {len(fails)} FAIL · {len(avisos)} AVISO · relatório: {rel(root, out)}")
    sys.exit(2 if fails else 0)

if __name__ == "__main__":
    main()
