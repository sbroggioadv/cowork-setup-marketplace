#!/usr/bin/env python3
"""Acopla os plugins que o escritório tem — NENHUM é obrigatório. Sem plugin, a bancada funciona igual: o chefe produz na persona
do escritório (identidade/) a partir dos modelos de knowledge/modelos/, e a Corte usa o checklist R1-R4 genérico.
Fontes (unidas; a que não existir é ignorada em silêncio):
  1. --sessao "<lista>"  os plugins cujas skills o Claude VÊ nesta sessão (vale no app Code e no Cowork; é a fonte mais confiável)
  2. o registro do Claude nesta máquina (~/.claude/plugins: installed_plugins.json, synced/*/manifest.json, enabledPlugins)
     e o do Codex ($CODEX_HOME ou ~/.codex: plugins/cache/<marketplace>/<plugin>/<versão>/ + [plugins."<plugin>@<marketplace>"] no config.toml)
  3. as pastas-motor que os wizards /start-* criaram na raiz da bancada
Cada plugin é reconhecido pelo catálogo (espec/plugins.json: área, skill-mestre, Corte, motor). Plugin fora do catálogo também é
acoplado: o script procura nele a skill *-master e a de revisão final; a área dele o advogado diz (`area`).
Grava _sistema/plugins.json e atualiza a tabela de roteamento de identidade/05.
Uso:
  python3 plugins.py detectar [--sessao "trabalhista-adv-os, holding-architect:holding-master, …"] [--json]
  python3 plugins.py area <plugin> <area> [<area>…]      diz a área de um plugin fora do catálogo (ou muda a de um conhecido)
  python3 plugins.py mostrar [--json]
Opções: --raiz X"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

def claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or (Path.home() / ".claude")).expanduser()

def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex")).expanduser()

def registro_codex() -> dict:
    """{nome: {versao, installPath, habilitado}} a partir do Codex: cache de plugins instalados + chave enabled do config.toml.
    Plugin que está no cache mas aparece como enabled = false no config.toml conta como desligado."""
    h = codex_home(); out = {}
    try:
        cfg = {}
        tp = h / "config.toml"
        if tp.exists():
            txt = tp.read_text(encoding="utf-8", errors="ignore")
            try:
                import tomllib; cfg = {k.split("@")[0]: bool((v or {}).get("enabled", True)) for k, v in (tomllib.loads(txt).get("plugins") or {}).items()}
            except Exception:   # Python < 3.11 ou TOML que o tomllib recusa: leitura simples das tabelas [plugins."x@y"]
                for m in re.finditer(r'^\[plugins\."([^"@]+)@[^"]*"\]\s*\n(?:[^\[]*?\benabled\s*=\s*(true|false))?', txt, re.M):
                    cfg[m.group(1)] = m.group(2) != "false"
        cache = h / "plugins" / "cache"
        if cache.is_dir():
            for mk in cache.iterdir():
                if not mk.is_dir() or mk.name.startswith("."): continue
                for pl in mk.iterdir():
                    if not pl.is_dir() or pl.name.startswith(("." , "plugin-backup")): continue
                    vers = sorted((v for v in pl.iterdir() if v.is_dir() and not v.name.startswith(".")), key=lambda v: v.stat().st_mtime)
                    if not vers: continue
                    out[pl.name] = {"versao": vers[-1].name, "installPath": str(vers[-1]), "habilitado": cfg.get(pl.name, False)}
        for n, on in cfg.items():
            out.setdefault(n, {"habilitado": on})
    except Exception:
        return {}
    return out

def registro() -> dict:
    """{nome: {fontes:[…], versao, installPath?, habilitado, runtimes}} a partir do registro local do Claude e do Codex (o que for acessível).
    Habilitado em qualquer um dos dois = habilitado (a bancada é a mesma; o plugin precisa estar instalado no programa aberto)."""
    h = claude_home(); out = {}
    def add(nome, fonte, **kw):
        e = out.setdefault(nome, {"fontes": []})
        if fonte not in e["fontes"]: e["fontes"].append(fonte)
        for k, v in kw.items():
            if v is not None and k not in e: e[k] = v
    try:
        ip = ler_json(h / "plugins" / "installed_plugins.json", {}) or {}
        for chave, lst in (ip.get("plugins") or {}).items():
            nome = chave.partition("@")[0]
            for it in (lst if isinstance(lst, list) else [lst]):
                p = it.get("installPath")
                if p and not Path(p).expanduser().exists(): continue
                add(nome, "registro", versao=it.get("version"), installPath=p)
        syn = h / "plugins" / "synced"
        if syn.exists():
            for mf in syn.glob("*/manifest.json"):
                for pl in (ler_json(mf, {}) or {}).get("plugins", []):
                    n = pl.get("name")
                    if n: add(n, "registro", versao=pl.get("version"), installPath=str(mf.parent / n) if (mf.parent / n).exists() else None)
        st = ler_json(h / "settings.json", {}) or {}
        for chave, on in (st.get("enabledPlugins") or {}).items():
            nome = chave.split("@")[0]
            if on: add(nome, "registro")
            elif nome in out: out[nome]["habilitado"] = False
    except Exception:
        out = {}
    for e in out.values(): e.setdefault("habilitado", True); e["runtimes"] = ["claude"]
    for n, c in registro_codex().items():
        e = out.get(n)
        if e is None:
            out[n] = {"fontes": ["registro"], "runtimes": ["codex"], **{k: v for k, v in c.items() if v is not None}}
        else:
            e["runtimes"] = sorted(set(e["runtimes"]) | {"codex"}); e["habilitado"] = e.get("habilitado", True) or c.get("habilitado", True)
            if not e.get("installPath") and c.get("installPath"): e["installPath"] = c["installPath"]
    return out

def da_sessao(txt: str) -> set:
    """'trabalhista-adv-os:trabalhista-master, holding-architect' → {'trabalhista-adv-os', 'holding-architect'}"""
    out = set()
    for pedaco in re.split(r"[,\s;]+", txt or ""):
        n = pedaco.strip().strip("`/$@").split(":")[0]
        if re.match(r"^[a-z0-9][a-z0-9._-]{1,60}$", n): out.add(n)
    return out

def skills_de(install: str | None) -> list[str]:
    if not install: return []
    d = Path(install).expanduser() / "skills"
    return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.exists() else []

def detectar(root: Path, sessao: str = "") -> dict:
    cat = catalogo(); conhecidos = cat["plugins"]; ignorar = set(cat.get("ignorar", []))
    anterior = plugins_detectados(root).get("plugins", {})
    reg = registro(); ses = da_sessao(sessao)
    if not sessao:   # sem lista nova da sessão (ex.: abertura automática): mantém os que uma sessão anterior viu
        ses = {n for n, e in anterior.items() if "sessao" in (e.get("origem") or [])}
    motores = {d.name for d in root.iterdir() if eh_motor(d)} if root.exists() else set()
    nomes = {n for n, e in reg.items() if e.get("habilitado", True)} | ses
    for n, c in conhecidos.items():
        if c.get("motor") and c["motor"] in motores: nomes.add(n)
    res = {"data": agora(), "fontes": sorted({"sessao"} if ses else set()) + (["registro"] if reg else []) + (["motores"] if motores else []),
           "plugins": {}, "claude_for_legal": sorted(n for n in nomes if n in CLAUDE_FOR_LEGAL), "motores_sem_plugin": []}
    for n in sorted(nomes):
        if n in ignorar or n in CLAUDE_FOR_LEGAL: continue
        origem = (["sessao"] if n in ses else []) + (["registro"] if n in reg else [])
        rts = reg.get(n, {}).get("runtimes") or []
        if n in conhecidos:
            c = conhecidos[n]
            areas = anterior.get(n, {}).get("areas_manual") or [area_por_nome(a, root) or a for a in c.get("areas", [])]
            e = {"catalogo": True, "grupo": c.get("grupo"), "areas": areas, "skill_mestre": c.get("skill_mestre"), "corte": c.get("corte"),
                 "motor": c.get("motor"), "wizard": c.get("wizard")}
            if c.get("motor") and c["motor"] in motores: origem.append("motor")
        else:
            sk = skills_de(reg.get(n, {}).get("installPath"))
            mestre = next((s for s in sk if s.endswith("-master")), None)
            if not (n.endswith(("-os", "-adv-os")) or n in anterior or mestre or n in ses): continue   # plugin de outra natureza (design, dados…): fora
            corte = next((s for s in sk if s.startswith(("suprema-corte", "revisao-final")) or re.match(r"revisao-.*-final$", s)), None)
            e = {"catalogo": False, "grupo": "desconhecido", "areas": anterior.get(n, {}).get("areas_manual") or [],
                 "skill_mestre": mestre, "corte": corte, "motor": None, "wizard": next((s for s in sk if s.startswith("start-")), None)}
        e["origem"] = origem
        if rts: e["runtimes"] = rts
        if anterior.get(n, {}).get("areas_manual"): e["areas_manual"] = anterior[n]["areas_manual"]
        res["plugins"][n] = e
    donos = {e.get("motor") for e in res["plugins"].values() if e.get("motor")}
    res["motores_sem_plugin"] = sorted(motores - donos)
    gravar_json(sistema(root) / "plugins.json", res)
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "aplicar.py"), "--roteamento", "--raiz", str(root)], capture_output=True)
    return res

def resumo(res: dict) -> str:
    P = res.get("plugins", {})
    if not P:
        return ("Nenhum plugin acoplado — tudo funciona assim mesmo: o chefe produz na persona do escritório (identidade/) a partir dos "
                "modelos de knowledge/modelos/, e a Corte usa o checklist R1-R4 da bancada. Instalou um plugin depois? /cowork-setup → plugins.")
    L = ["Plugins acoplados:"]
    for n, e in sorted(P.items()):
        areas = ", ".join(e.get("areas") or []) or ("apoio" if e.get("grupo") in ("auxiliar", "fase", "interno") else "área a definir")
        L.append(f"  - {n}: {areas} · skill-mestre {e.get('skill_mestre') or '—'} · Corte {e.get('corte') or 'genérica'}"
                 + ("" if e.get("catalogo") else " · fora do catálogo"))
    sem = [n for n, e in P.items() if not e.get("catalogo") and not e.get("areas")]
    if sem: L.append("  ? Diga a área destes (plugins.py area <plugin> <area>): " + ", ".join(sem))
    if res.get("motores_sem_plugin"): L.append("  · Pastas-motor sem plugin ativo (ficam onde estão, sem uso): " + ", ".join(res["motores_sem_plugin"]))
    if res.get("claude_for_legal"): L.append("  · Suíte Claude for Legal instalada (direito dos EUA) — nunca entra no roteamento: " + ", ".join(res["claude_for_legal"]))
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("acao", nargs="?", default="mostrar", choices=["detectar", "area", "mostrar"]); ap.add_argument("arg", nargs="*")
    ap.add_argument("--sessao", default=""); ap.add_argument("--json", action="store_true"); ap.add_argument("--raiz")
    a = ap.parse_args(); root = raiz(a.raiz)
    if a.acao == "detectar": res = detectar(root, a.sessao)
    elif a.acao == "area":
        if len(a.arg) < 2: print("uso: area <plugin> <area> [<area>…]"); sys.exit(2)
        res = plugins_detectados(root); e = res.setdefault("plugins", {}).setdefault(a.arg[0], {"catalogo": False, "grupo": "desconhecido", "origem": ["manual"]})
        e["areas"] = e["areas_manual"] = [area_por_nome(x, root) or slug(x) for x in a.arg[1:]]
        gravar_json(sistema(root) / "plugins.json", res)
        subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "aplicar.py"), "--roteamento", "--raiz", str(root)], capture_output=True)
    else: res = plugins_detectados(root)
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else resumo(res))

if __name__ == "__main__":
    main()
