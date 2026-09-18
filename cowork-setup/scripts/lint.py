#!/usr/bin/env python3
"""Verificador de estrutura (regra em código, não em prosa). Confere clientes/ e os motores contra espec/estrutura.json. Sem git.
Uso:
  python3 lint.py                      tudo
  python3 lint.py --cliente <slug>     um cliente
  python3 lint.py --desde <epoch>      só clientes com arquivo modificado depois do carimbo (hook Stop)
  python3 lint.py --resumo             1 linha (hook SessionStart)
  python3 lint.py --so-erros | --strict | --json
  python3 lint.py --corrigir [--cliente x]   cria o que só adiciona: FICHA.md, entrada/, pesquisas/ (nunca move nem apaga)
Saída: `E CODIGO caminho — motivo` (erro) · `A CODIGO caminho — motivo` (aviso). Exit 2 = há erro; 1 = só avisos com --strict; 0 = limpo.
Códigos: CLIENTE (sem STATE/CADASTRO) · NOME (pasta fora do padrão slug) · NUM (prefixo numérico) · VERS (_versoes/backup — regra 10) ·
FICHA (T≥2 tocado sem FICHA) · ANAT (T≥2 sem entrada/ ou pesquisas/) · CRU (STATE ainda é template) · SECAO (STATE sem seção fixa) ·
BLOAT (Gates com mais de uma rodada) · PESQ (pesquisas/ sem AAAA-MM-DD-) · LUGAR (entregável fora de pasta de projeto) · AVULSO (CLAUDE.md/MEMORY.md do formato antigo dentro de projeto) ·
LEGADO (_memoria-cowork.md por absorver) · INDICE (projeto fora do STATE do cliente) · HOLDING (holding sem STATE/FICHA) · ABS (caminho absoluto de máquina) ·
CASOS (arquivos em <motor>/casos/ — conferir dado de cliente) · TRIAGEM (itens em _legado/triagem/)."""
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

ap = argparse.ArgumentParser()
ap.add_argument("--raiz"); ap.add_argument("--cliente"); ap.add_argument("--desde", type=float); ap.add_argument("--resumo", action="store_true")
ap.add_argument("--so-erros", action="store_true"); ap.add_argument("--strict", action="store_true"); ap.add_argument("--json", action="store_true")
ap.add_argument("--corrigir", action="store_true")
a = ap.parse_args(); root = raiz(a.raiz); esp = espec(); base = root / "clientes"
NOME = re.compile(esp["nome"]["regex"]); NUM = re.compile(esp["nome"]["prefixo_numerico_proibido"])
VERS = re.compile(esp["nome"]["versoes_proibidas"], re.I); ABS = re.compile(esp["nome"]["caminho_absoluto"])
TEXTO = {".md", ".py", ".txt", ".html", ".json", ".yaml", ".yml", ".sh"}; ENTREG = set(esp["projeto"]["entregaveis"])
SEC_PROJ = esp["projeto"]["state_secoes"]; SEC_CLI = esp["cliente"]["state_secoes"]; IGN = {".DS_Store", ".gitkeep"}
achados = []
def E(c, p, m): achados.append(("E", c, p, m))
def A(c, p, m): achados.append(("A", c, p, m))
corrigidos = []

def tocado_desde(d: Path, ts: float) -> bool:
    return any(f.stat().st_mtime > ts for f in d.rglob("*") if f.is_file())

alvo = None
if a.cliente: alvo = {a.cliente}
if a.desde is not None and base.exists():
    alvo = {c.name for c in base.iterdir() if c.is_dir() and tocado_desde(c, a.desde)}
    if not alvo:
        print("RESUMO: nada alterado em clientes/"); sys.exit(0)

def eh_projeto(d: Path) -> bool:
    return (d / "STATE.md").exists() and d != base and d.parent != base

def checar_state(st: Path, secoes, projeto: bool):
    t = ler(st); faltam = [s for s in secoes if s not in t]
    if faltam: A("SECAO", rel(root, st), "sem seção fixa: " + ", ".join(faltam))
    if projeto:
        g = t.split("## Gates")[1].split("\n## ")[0] if "## Gates" in t else ""
        nc = sum(1 for l in g.splitlines() if l.startswith("Corte")); nt = sum(1 for l in g.splitlines() if l.startswith("Thor"))
        if nc > 1 or nt > 1: A("BLOAT", rel(root, st), f"Gates com {nc} Corte / {nt} Thor — só a última rodada; anteriores em historico/")

if base.exists():
    for cli in sorted(base.iterdir()):
        if not cli.is_dir() or cli.name in IGN: continue
        if alvo is not None and cli.name not in alvo: continue
        if not NOME.match(cli.name): E("NOME", rel(root, cli), "nome de pasta fora do padrão (minúsculas, hífen, sem acento) — renomear via /lint-estrutura")
        if not (cli / "STATE.md").exists(): E("CLIENTE", rel(root, cli), "sem STATE.md (índice do cliente)")
        else: checar_state(cli / "STATE.md", SEC_CLI, False)
        if not (cli / "cadastro" / "CADASTRO.md").exists(): E("CLIENTE", rel(root, cli), "sem cadastro/CADASTRO.md")
        if (cli / "_memoria-cowork.md").exists(): A("LEGADO", rel(root, cli / "_memoria-cowork.md"), "absorver em Decisões fixadas do índice e apagar")
        for f in cli.iterdir():
            if f.is_file() and f.name not in IGN and f.name not in ("STATE.md",) + tuple(esp["cliente"]["arquivos_tolerados"]):
                A("LUGAR", rel(root, f), "arquivo solto na raiz do cliente — mover para cadastro/documentos/ ou para o projeto")
            if f.is_dir() and f.name not in esp["cliente"]["pastas_permitidas"] and f.name not in IGN:
                A("LUGAR", rel(root, f), f"pasta fora da anatomia do cliente ({' · '.join(esp['cliente']['pastas_permitidas'])})")
        idx = ler(cli / "STATE.md")
        for d in sorted(cli.rglob("*")):
            if not d.is_dir() or "historico" in d.parts or d.name in IGN: continue
            if any(p.name == "holding" for p in d.relative_to(cli).parents) or d.name == "holding": continue   # holding: nomenclatura livre
            if not NOME.match(d.name): A("NOME", rel(root, d), "nome de pasta fora do padrão slug (minúsculas, hífen, sem acento)")
            if NUM.match(d.name): A("NUM", rel(root, d), "prefixo numérico vetado — renomear quando tocar")
            if VERS.match(d.name): E("VERS", rel(root, d), "versão antiga vive em historico/ (regra 10) — mover o conteúdo para lá")
            if eh_projeto(d):
                st = d / "STATE.md"; t = tier_de(st); cru_ = cru(st)
                if cru_: A("CRU", rel(root, st), "STATE ainda com texto do template — preencher quando o caso for tocado")
                else:
                    checar_state(st, SEC_PROJ, True)
                    if t in ("T2", "T3") and not (d / "FICHA.md").exists():
                        if a.corrigir:
                            (d / "FICHA.md").write_text(template_bancada(root, "FICHA.template.md"), encoding="utf-8"); corrigidos.append(rel(root, d / "FICHA.md"))
                        else: E("FICHA", rel(root, d), f"{t} sem FICHA.md (`--corrigir` cria)")
                    for sub in esp["projeto"]["tier2_pastas"]:
                        if t in ("T2", "T3") and not (d / sub).exists():
                            if a.corrigir: (d / sub).mkdir(); corrigidos.append(rel(root, d / sub))
                            else: A("ANAT", rel(root, d), f"{t} sem {sub}/ (`--corrigir` cria)")
                if d.name != "holding" and f"`{rel(cli, d)}/`" not in idx: A("INDICE", rel(root, d), "projeto não consta na tabela do STATE.md do cliente")
                if (d / "_memoria-cowork.md").exists(): A("LEGADO", rel(root, d / "_memoria-cowork.md"), "absorver em Decisões fixadas/FICHA e apagar")
                for f in d.iterdir():
                    if f.name in ("MEMORY.md", "memory.md", "CLAUDE.md") : A("AVULSO", rel(root, f), "arquivo do formato antigo dentro de projeto — absorver no STATE e apagar")
                for f in (d / "pesquisas").glob("*.md") if (d / "pesquisas").exists() else []:
                    if not re.match(esp["projeto"]["pesquisa_regex"], f.name): A("PESQ", rel(root, f), "nome deve ser AAAA-MM-DD-tema.md")
        h = cli / "holding"
        if h.exists():
            if not (h / "STATE.md").exists(): E("HOLDING", rel(root, h), "holding sem STATE.md")
            elif not cru(h / "STATE.md") and not (h / "FICHA.md").exists(): E("FICHA", rel(root, h), "holding sem FICHA.md (## Documentos lista cada arquivo)")
        for f in cli.rglob("*"):
            if not f.is_file() or f.name in IGN or "historico" in f.parts: continue
            if f.suffix.lower() in ENTREG:
                dentro = any(eh_projeto(p) or p.name == "holding" for p in f.parents if p != cli and cli in p.parents) or (f.parent.name == "documentos" and f.parent.parent.name == "cadastro")
                if not dentro: E("LUGAR", rel(root, f), "entregável fora de pasta de projeto (precisa estar em <tipo>/<area>/<projeto>/, holding/ ou cadastro/documentos/)")
            if f.suffix.lower() in TEXTO and ABS.search(ler(f)): E("ABS", rel(root, f), "caminho absoluto de máquina em arquivo da bancada")

if alvo is None:
    for d in sorted(root.iterdir()):
        if d.is_dir() and eh_motor(d, esp) and (d / "casos").exists():
            n = sum(1 for f in (d / "casos").rglob("*") if f.is_file() and f.name not in IGN)
            if n: A("CASOS", rel(root, d / "casos"), f"{n} arquivo(s) em casos/ — rascunho pode; dado nominativo e versão final vão para clientes/ (/entregar)")
    tri = root / "_legado" / "triagem"
    if tri.exists():
        n = sum(1 for f in tri.rglob("*") if f.is_file() and f.name not in IGN)
        if n: A("TRIAGEM", "_legado/triagem", f"{n} arquivo(s) esperando decisão do advogado")

erros = [x for x in achados if x[0] == "E"]; avisos = [x for x in achados if x[0] == "A"]
if a.json:
    print(json.dumps({"erros": [dict(zip(("nivel","codigo","caminho","motivo"), x)) for x in erros], "avisos": [dict(zip(("nivel","codigo","caminho","motivo"), x)) for x in avisos], "corrigidos": corrigidos}, ensure_ascii=False, indent=2)); sys.exit(2 if erros else 0)
if a.resumo:
    from collections import Counter
    ce = Counter(x[1] for x in erros); ca = Counter(x[1] for x in avisos)
    print(f"estrutura: {len(erros)} erro(s) [{' · '.join(f'{k} {v}' for k, v in ce.items())}] · {len(avisos)} aviso(s) [{' · '.join(f'{k} {v}' for k, v in ca.items())}]" if achados else "estrutura: limpa")
    sys.exit(2 if erros else 0)
for x in (erros if a.so_erros else achados): print(f"{x[0]} {x[1]} {x[2]} — {x[3]}")
for c in corrigidos: print(f"+ criado {c}")
if not achados: print("estrutura: limpa")
sys.exit(2 if erros else (1 if a.strict and avisos else 0))
