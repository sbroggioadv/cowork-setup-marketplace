#!/usr/bin/env python3
"""Súmulas sob demanda: consulta o repertório embarcado no plugin (vendor/sumulas/ — STF súmulas e vinculantes, STF repercussão geral, STJ súmulas
e temas repetitivos/IAC, TST súmulas/OJs/PNs, TJSP, TRT-15, CJF, FONAJE; ~8.000 verbetes, retrato datado) SEM copiar 18 MB para cada bancada.
A bancada guarda só knowledge/jurisprudencia/sumulas/README.md (2 linhas: como consultar); quem quiser cópia offline usa --copiar.
Lê direto de <plugin>/vendor/sumulas/ (resolvido a partir deste arquivo — nunca caminho absoluto gravado). É texto de referência, nível 1 —
**confirmar a vigência na fonte oficial antes de citar** (o retrato tem data); cancelados ficam na base para reconhecer citação adversa desatualizada.
Uso:
  python3 sumulas.py buscar <termos…> [--tribunal STF|SV|STF-RG|STJ|STJ-TEMAS|IAC|TST|TJSP|TRT15|CJF|FONAJE] [--tema <slug>] [--n 10] [--cancelados] [--json]
                     todos os termos precisam aparecer (sem acento, sem maiúscula); termo "entre aspas" = expressão exata; --cancelados inclui os cancelados
  python3 sumulas.py ver <id> [--integral] [--json]      id como a busca mostra: "STJ 479" · "STF 473" · "SV 10" · "STF Tema 796" · "STJ Tema 1113" ·
                     "STJ IAC 1" · "TST 331" (= TST Súmula 331) · "TST OJ SDI-1 2" · "TST PN 1" · "TJSP 1" · "TRT15 13" · "FONAJE 15" · "CJF civil 2"
                     (ambíguo → lista os candidatos, exit 2). Mostra enunciado + metadados; --integral traz o bloco inteiro (precedentes, histórico).
  python3 sumulas.py temas [--json]                       temas e subtemas do índice temático (e se o arquivo temas/<tema>.md está embarcado)
  python3 sumulas.py status [--json] [--raiz X]           retrato (data), fontes e contagens; na bancada: cópia offline, só o README, ou nada
  python3 sumulas.py readme [--raiz X]                    grava knowledge/jurisprudencia/sumulas/README.md na bancada (2 linhas; idempotente)
  python3 sumulas.py --copiar <pasta relativa à bancada> [--raiz X]   cópia offline (ex.: knowledge/jurisprudencia/sumulas): copia só o que mudou
                     (md5), nunca apaga, recusa pasta fora da bancada; depois `jusia_index.py` indexa
Exit: 0 ok · 1 uso · 2 recusa/erro (repertório ausente, pasta fora da bancada, id ambíguo, tema não embarcado) · 3 id não encontrado."""
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

VENDOR_SUMULAS = Path(__file__).resolve().parent.parent / "vendor" / "sumulas"   # resolvido em runtime: nunca caminho absoluto no arquivo
BANCADA_REL = "knowledge/jurisprudencia/sumulas"
AVISO = "Retrato datado — confirmar a vigência na fonte oficial antes de citar (nível 1 só depois de conferido)."
RE_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
RE_NAO_VIGENTE = re.compile(r"cancel|superad|revog|substitu|prejudic")
TRIBUNAIS = {   # alias de --tribunal → fontes (rótulo interno)
    "STF": ("STF",), "SV": ("SV",), "VINCULANTE": ("SV",), "STF-RG": ("STF Tema",), "RG": ("STF Tema",), "STF-TEMA": ("STF Tema",),
    "STJ": ("STJ",), "STJ-TEMAS": ("STJ Tema", "STJ IAC"), "TEMAS": ("STJ Tema",), "STJ-TEMA": ("STJ Tema",), "IAC": ("STJ IAC",),
    "TST": ("TST",), "TJSP": ("TJSP",), "TRT15": ("TRT-15",), "TRT-15": ("TRT-15",), "CJF": ("CJF",), "FONAJE": ("FONAJE",),
}
CJF_ARQ = (("direito civil", "cjf/direito-civil.md"), ("direito comercial", "cjf/direito-comercial.md"), ("processual civil", "cjf/processo-civil.md"),
           ("solucao extrajudicial", "cjf/solucao-extrajudicial.md"))
TST_SECOES = {"sumulas": ("Súmula", "## Súmula {n} —"), "oj-sdi1": ("OJ SDI-1", "## OJ SDI-1 {n} —"), "oj-sdi1-transitoria": ("OJ Transitória SDI-1", "## OJ Transitória SDI-1 {n} —"),
              "oj-sdi2": ("OJ SDI-2", "## OJ SDI-2 {n} —"), "oj-sdc": ("OJ SDC", "## OJ SDC {n} —"), "oj-pleno": ("OJ Tribunal Pleno", "## OJ Tribunal Pleno {n} —"),
              "precedentes-normativos": ("PN", "## Precedente Normativo {n} —")}

def erro(msg: str, code: int = 2):
    print(msg); sys.exit(code)

def exigir_repertorio() -> Path:
    if not (VENDOR_SUMULAS / "INDEX.md").exists(): erro(f"repertório de súmulas ausente no plugin ({rel(PLUGIN, VENDOR_SUMULAS)}/INDEX.md) — reinstale ou atualize o plugin", 2)
    return VENDOR_SUMULAS

def data_retrato() -> str:
    for nome in ("INDEX.md", "README.md"):
        m = re.search(r"[Gg]erado em (\d{4}-\d{2}-\d{2})", ler(VENDOR_SUMULAS / nome))
        if m: return m.group(1)
    return "?"

# ---------- leitura dos índices (uma linha por verbete) ----------
def _cells(line: str) -> list[str] | None:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")) or len(s) < 3: return None
    return [c.strip() for c in re.split(r" \| ", s[1:-1])]

def _tabelas(p: Path):
    """Gera (secao, cabecalho, celulas) para cada linha de tabela do arquivo; cabeçalho = a última linha `| nº | … |` vista.
    Linha que começa com `|` e não fecha (quebra de linha dentro da célula, ex.: STF 63) é emendada com as seguintes até fechar."""
    secao = ""; cab: list[str] | None = None; pend = ""
    for line in ler(p).splitlines():
        if pend:
            pend += " " + line.strip()
            if not line.rstrip().endswith("|"): continue
            line, pend = pend, ""
        if line.startswith("## "): secao = line[3:].strip(); cab = None; continue
        if line.startswith("|") and not line.rstrip().endswith("|"): pend = line.strip(); continue
        c = _cells(line)
        if c is None: continue
        if all(re.fullmatch(r":?-+:?", x) for x in c if x): continue   # linha |---|
        if cab is None or c[0].lower() in ("nº", "n°", "tema", "iac", "conjunto", "jornada", "fonte", "ramo"):
            if cab is None or not re.match(r"\d", c[0]): cab = c; continue
        if len(c) < 2 or not re.match(r"\[?\d", c[0]): continue
        if len(c) > len(cab): c = c[:len(cab) - 1] + [" | ".join(c[len(cab) - 1:])]
        yield secao, cab, c

def _num(cell: str) -> tuple[str, str]:
    """`[331](tst/sumulas-tst.md)` → ('331', 'tst/sumulas-tst.md'); `12` → ('12', '')."""
    m = RE_LINK.match(cell)
    return (m.group(1).strip(), m.group(2).strip()) if m else (cell.strip(), "")

def _link(cell: str) -> str:
    m = RE_LINK.search(cell or ""); return m.group(2).strip() if m else ""

def _rec(fonte, tipo, numero, titulo, texto, status="", situacao="", arquivo="", heading="", extra=None) -> dict:
    id_ = {"STF": f"STF {numero}", "SV": f"SV {numero}", "STJ": f"STJ {numero}", "TJSP": f"TJSP {numero}", "FONAJE": f"FONAJE {numero}",
           "STF Tema": f"STF Tema {numero}", "STJ Tema": f"STJ Tema {numero}", "STJ IAC": f"STJ IAC {numero}", "TRT-15": f"TRT-15 Súmula {numero}"}.get(fonte)
    if id_ is None: id_ = f"{fonte} {tipo} {numero}"
    vig = not RE_NAO_VIGENTE.search(norm(f"{status} {situacao}"))
    return {"id": id_, "fonte": fonte, "tipo": tipo, "numero": numero, "titulo": titulo or "", "texto": texto or "", "status": status or "", "situacao": situacao or "",
            "vigente": vig, "arquivo": arquivo, "heading": heading, **(extra or {})}

def carregar(v: Path) -> list[dict]:
    """Todos os verbetes dos INDEX-*.md (INDEX-STJ-POR-MATERIA é classificação, não entra: duplicaria)."""
    R: list[dict] = []
    for sec, cab, c in _tabelas(v / "INDEX-STF.md"):
        n, _ = _num(c[0]); R.append(_rec("STF", "Súmula", n, "", c[1], c[2], "", _link(c[4]) if len(c) > 4 else "", f"## Súmula {n}", {"aprovacao": c[3] if len(c) > 3 else ""}))
    for sec, cab, c in _tabelas(v / "INDEX-STF-VINCULANTES.md"):
        n, _ = _num(c[0]); R.append(_rec("SV", "Súmula Vinculante", n, "", c[1], c[2], "", _link(c[4]) if len(c) > 4 else "", f"## Súmula Vinculante {n}", {"publicacao": c[3] if len(c) > 3 else ""}))
    for sec, cab, c in _tabelas(v / "INDEX-STJ.md"):
        n, _ = _num(c[0]); R.append(_rec("STJ", "Súmula", n, c[1], c[2], c[5] if len(c) > 5 else "", "", "stj/verbetes-stj.md", f"## Súmula {n} —",
                                         {"orgao": c[3] if len(c) > 3 else "", "julgado_em": c[4] if len(c) > 4 else "", "inteiro_teor": _link(c[6]) if len(c) > 6 else ""}))
    for sec, cab, c in _tabelas(v / "INDEX-TST.md"):
        slug_ = sec.split(" — ")[0].strip()
        if slug_ not in TST_SECOES: continue
        tipo, head = TST_SECOES[slug_]; n, arq = _num(c[0])
        R.append(_rec("TST", tipo, n, c[1], c[2] if len(c) > 2 else "", c[3] if len(c) > 3 else "", "", arq, head.format(n=n)))
    for sec, cab, c in _tabelas(v / "INDEX-TJSP.md"):
        n, _ = _num(c[0]); R.append(_rec("TJSP", "Súmula", n, "", c[1], c[2] if len(c) > 2 else "", "", "tjsp/sumulas-tjsp.md", f"## Súmula {n}"))
    for sec, cab, c in _tabelas(v / "INDEX-TRT15.md"):
        n, _ = _num(c[0]); R.append(_rec("TRT-15", "Súmula", n, c[1], c[2] if len(c) > 2 else "", c[3] if len(c) > 3 else "", "", "trt15/sumulas-trt15.md", f"## Súmula {n}"))
    for sec, cab, c in _tabelas(v / "INDEX-CJF.md"):
        if not sec or cab[0].lower() == "jornada": continue
        n, _ = _num(c[0]); arq = next((a for k, a in CJF_ARQ if k in norm(sec)), "cjf/outras-jornadas.md")
        R.append(_rec("CJF", f"{sec} — Enunciado", n, sec, c[1], "", "", arq, f"## {sec} — Enunciado {n}"))
    for sec, cab, c in _tabelas(v / "INDEX-FONAJE.md"):
        n, _ = _num(c[0]); R.append(_rec("FONAJE", "Enunciado", n, "", c[1], c[2] if len(c) > 2 else "", "", "fonaje/enunciados-civeis.md", f"## Enunciado {n}"))
    for sec, cab, c in _tabelas(v / "INDEX-STF-RG.md"):
        n, _ = _num(c[0]); R.append(_rec("STF Tema", "Tema de repercussão geral", n, "", c[3] if len(c) > 3 else "", "", c[2] if len(c) > 2 else "", _link(c[4]) if len(c) > 4 else "",
                                         f"## STF Tema {n} —", {"repercussao_geral": c[1] if len(c) > 1 else ""}))
    for sec, cab, c in _tabelas(v / "INDEX-STJ-TEMAS.md"):
        n, _ = _num(c[0])
        if cab[0].upper() == "IAC" or sec.upper().startswith("IAC"):
            R.append(_rec("STJ IAC", "IAC", n, c[1], c[3] if len(c) > 3 else "", "", c[2] if len(c) > 2 else "", "stj/temas-repetitivos/iac.md", f"## STJ IAC {n} —"))
        else:
            R.append(_rec("STJ Tema", "Tema repetitivo", n, c[1], c[3] if len(c) > 3 else "", "", c[2] if len(c) > 2 else "", _link(c[4]) if len(c) > 4 else "", f"## STJ Tema {n} —"))
    for r in R: r["_hay_t"] = norm(f"{r['id']} {r['titulo']}"); r["_hay"] = norm(r["texto"])
    return R

def publico(r: dict) -> dict: return {k: v for k, v in r.items() if not k.startswith("_")}

# ---------- tema (índice temático: temas/<slug>.md, quando embarcado ou copiado) ----------
def arquivo_tema(root: Path | None, slug_: str) -> Path | None:
    for base in (VENDOR_SUMULAS, (root / BANCADA_REL) if root else None):
        if base is not None and (base / "temas" / f"{slug_}.md").exists(): return base / "temas" / f"{slug_}.md"
    return None

def ids_do_tema(p: Path) -> set[str]:
    return {norm(m.group(1)).replace("-", "") for m in re.finditer(r"^- \*\*([^*]+)\*\*", ler(p), re.M)}

def temas_do_indice(v: Path) -> list[dict]:
    """`### Nome — [`temas/x.md`](temas/x.md)` + `- [Subtema](…) — N vigentes, M cancelados` da seção "Caminho rápido — por tema" do INDEX.md."""
    out: list[dict] = []; t = ler(v / "INDEX.md"); dentro = False
    for line in t.splitlines():
        if line.startswith("## "): dentro = "caminho rapido" in norm(line); continue
        if not dentro: continue
        m = re.match(r"### (.+?) — .*?\(temas/([a-z0-9_-]+)\.md\)", line)
        if m: out.append({"tema": m.group(2), "nome": m.group(1).strip(), "subtemas": [], "vigentes": 0, "cancelados": 0, "embarcado": (v / "temas" / f"{m.group(2)}.md").exists()}); continue
        m = re.match(r"- \[(.+?)\]\(temas/[a-z0-9_-]+\.md#([^)]+)\) — (\d+) vigentes(?:, (\d+) cancelados)?", line)
        if m and out:
            out[-1]["subtemas"].append({"nome": m.group(1), "ancora": m.group(2), "vigentes": int(m.group(3)), "cancelados": int(m.group(4) or 0)})
            out[-1]["vigentes"] += int(m.group(3)); out[-1]["cancelados"] += int(m.group(4) or 0)
    return out

# ---------- buscar ----------
def termos_de(lista: list[str]) -> list[str]: return [norm(x) for x in lista if norm(x)]

def pontuar(r: dict, termos: list[str]) -> int:
    s = 0
    for t in termos:
        c = r["_hay"].count(t) + r["_hay_t"].count(t)
        if c == 0: return 0
        s += c + (3 if t in r["_hay_t"] else 0)
    return s

def resumo_txt(s: str, n: int = 260) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[:n].rstrip() + "…"

def cmd_buscar(a, root: Path):
    v = exigir_repertorio(); termos = termos_de(a.termos)
    if not termos: erro("informe ao menos um termo: sumulas.py buscar <termos…>", 1)
    fontes = None
    if a.tribunal:
        k = a.tribunal.strip().upper().replace("_", "-")
        if k not in TRIBUNAIS: erro(f"--tribunal desconhecido: {a.tribunal} (use {', '.join(sorted(TRIBUNAIS))})", 1)
        fontes = set(TRIBUNAIS[k])
    R = carregar(v); tema_ids = None; tema_arq = None
    if a.tema:
        tema_arq = arquivo_tema(root, slug(a.tema))
        if tema_arq is None:
            erro(f"tema '{a.tema}' não está embarcado nesta versão do plugin (sem {rel(PLUGIN, VENDOR_SUMULAS)}/temas/{slug(a.tema)}.md) — filtre por --tribunal e termos; "
                 f"`sumulas.py temas` lista os temas do índice", 2)
        tema_ids = ids_do_tema(tema_arq)
    hits = []
    for r in R:
        if fontes and r["fonte"] not in fontes: continue
        if not a.cancelados and not r["vigente"]: continue
        if tema_ids is not None and norm(r["id"]).replace("-", "") not in tema_ids: continue
        s = pontuar(r, termos)
        if s: hits.append((s, r))
    hits.sort(key=lambda x: (-x[0], x[1]["fonte"], int(re.sub(r"\D", "", x[1]["numero"]) or 0)))
    top = [r for _, r in hits[:max(1, a.n)]]; data = data_retrato()
    if a.json:
        print(json.dumps({"termos": termos, "tribunal": a.tribunal, "tema": a.tema, "retrato": data, "total_lidos": len(R), "encontrados": len(hits),
                          "resultados": [dict(publico(r), ver=f'sumulas.py ver "{r["id"]}"') for r in top], "aviso": AVISO}, ensure_ascii=False, indent=2)); return
    if not hits:
        print(f"nenhum verbete com {' + '.join(termos)}" + (f" em {a.tribunal}" if a.tribunal else "") + f" (entre {len(R)} verbetes lidos, retrato de {data}). "
              "Súmula e tese qualificada são a exceção: sem verbete, vá aos bancos de acórdãos (/jurisprudencia buscar) e registre em pesquisas/."); return
    for i, r in enumerate(top, 1):
        vig = "vigente" if r["vigente"] else "NÃO VIGENTE (" + (r["status"] or r["situacao"]) + ")"
        cab = f"{i}. {r['id']} · {vig} · {r['tipo']}" + (f" — {resumo_txt(r['titulo'], 120)}" if r["titulo"] and r["fonte"] != "CJF" else "") + (f" · {r['situacao']}" if r["situacao"] else "")
        print(cab); print("   " + resumo_txt(r["texto"]))
    print(f"{len(hits)} resultado(s) entre {len(R)} verbetes (retrato de {data})" + (f" · mostrando {len(top)}" if len(hits) > len(top) else "") + f' · íntegra: sumulas.py ver "<id>"')
    print(AVISO)

# ---------- ver ----------
def _toks(s: str) -> list[str]: return norm(s).replace("-", "").split()

def localizar(R: list[dict], id_: str) -> tuple[list[dict], str]:
    u = _toks(id_)
    if len(u) >= 3 and u[0] == "trt" and u[1] == "15": u = ["trt15"] + u[2:]
    if len(u) < 2 or not u[-1].isdigit(): return [], "id precisa terminar no número (ex.: \"STJ 479\", \"STF Tema 796\", \"TST OJ SDI-1 2\")"
    fonte, numero, meio = u[0], u[-1], u[1:-1]
    if fonte in ("stf", "stj", "sv", "tjsp", "fonaje") and "sumula" in meio: meio = [x for x in meio if x != "sumula"]
    if fonte == "stf" and ("vinculante" in meio or "sv" in meio): fonte = "sv"; meio = [x for x in meio if x not in ("vinculante", "sv")]
    if fonte in ("tst", "trt15") and not meio: meio = ["sumula"]
    cands = []
    for r in R:
        t = _toks(r["id"])
        if t[0] != fonte or t[-1] != numero: continue
        if all(m in t[1:-1] for m in meio): cands.append(r)
    if len(cands) > 1 and not meio: cands = [r for r in cands if len(_toks(r["id"])) == 2] or cands   # "STF 10" = súmula, não Tema/SV
    if len(cands) > 1:   # o id mais curto que contém tudo o que o usuário digitou vence ("TST OJ SDI-1 2" ≠ OJ Transitória; "CJF I Jornada de Direito Civil 2" ≠ Processual)
        cands.sort(key=lambda r: len(_toks(r["id"])))
        if len(_toks(cands[0]["id"])) < len(_toks(cands[1]["id"])): cands = cands[:1]
    return cands, ""

def bloco_de(v: Path, r: dict) -> tuple[str, str]:
    """(arquivo relativo ao repertório, bloco `## …` do verbete) — bloco vai até o próximo `## `. Vazio se não achou."""
    arqs = [r["arquivo"]] if r["arquivo"] else []
    if r["fonte"] == "CJF": arqs = [r["arquivo"]] + [a for _, a in CJF_ARQ if a != r["arquivo"]] + ["cjf/outras-jornadas.md"]
    for arq in arqs:
        p = v / arq
        if not p.exists(): continue
        linhas = ler(p).splitlines(); h = r["heading"]; ini = None
        for i, l in enumerate(linhas):
            if l == h or l.startswith(h + " ") or l == h.rstrip(" —") or l.startswith(h.rstrip(" —") + " —"): ini = i; break
        if ini is None: continue
        fim = next((j for j in range(ini + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas))
        return arq, "\n".join(linhas[ini:fim]).rstrip()
    return "", ""

def cmd_ver(a, root: Path):
    v = exigir_repertorio(); R = carregar(v); cands, msg = localizar(R, a.id)
    if msg: erro(msg, 1)
    if not cands: erro(f"não encontrado: {a.id} (ids como \"STJ 479\", \"STF 473\", \"SV 10\", \"STF Tema 796\", \"STJ Tema 1113\", \"TST 331\", \"TST OJ SDI-1 2\", \"TJSP 1\", \"TRT15 13\", \"FONAJE 15\", \"CJF civil 2\")", 3)
    if len(cands) > 1:
        print(f"id ambíguo: {a.id} — candidatos:"); [print(f"  - {r['id']}" + (f" — {resumo_txt(r['titulo'], 90)}" if r["titulo"] and r["fonte"] != "CJF" else "")) for r in cands[:30]]
        sys.exit(2)
    r = cands[0]; arq, bloco = bloco_de(v, r); data = data_retrato()
    if a.json: print(json.dumps(dict(publico(r), retrato=data, arquivo_integra=arq, bloco=bloco, aviso=AVISO), ensure_ascii=False, indent=2)); return
    vig = "vigente" if r["vigente"] else "NÃO VIGENTE (" + (r["status"] or r["situacao"]) + ")"
    print(f"{r['id']} · {r['tipo']} · {vig}" + (f" · {r['situacao']}" if r["situacao"] else "") + f" · retrato de {data}")
    if not bloco:
        print("> " + resumo_txt(r["texto"], 2000)); print(f"(íntegra não localizada em {rel(PLUGIN, VENDOR_SUMULAS)}/{r['arquivo'] or '?'} — o enunciado acima é o do índice)")
    else:
        linhas = bloco.splitlines(); lim = None if a.integral else 40
        print("\n".join(linhas[:lim] if lim else linhas))
        if lim and len(linhas) > lim: print(f"… (+{len(linhas) - lim} linhas: precedentes, histórico) — `sumulas.py ver \"{r['id']}\" --integral` · arquivo {rel(PLUGIN, VENDOR_SUMULAS)}/{arq}")
        if r.get("inteiro_teor"): print(f"inteiro teor (precedentes originários): {rel(PLUGIN, VENDOR_SUMULAS)}/{r['inteiro_teor']}")
    print(AVISO)

# ---------- temas · status · readme · copiar ----------
def cmd_temas(a, root: Path):
    v = exigir_repertorio(); T = temas_do_indice(v)
    if a.json: print(json.dumps({"retrato": data_retrato(), "temas": T}, ensure_ascii=False, indent=2)); return
    if not T: print("índice temático não encontrado no INDEX.md do repertório"); return
    emb = sum(1 for t in T if t["embarcado"])
    print(f"{len(T)} tema(s) · {sum(len(t['subtemas']) for t in T)} subtema(s) · retrato de {data_retrato()} · arquivos temas/<tema>.md embarcados: {emb}/{len(T)}")
    for t in T:
        print(f"- {t['tema']} — {t['nome']} · {len(t['subtemas'])} subtemas · {t['vigentes']} vigentes" + (f", {t['cancelados']} cancelados" if t["cancelados"] else "") + (" · embarcado" if t["embarcado"] else ""))
        for s in t["subtemas"]: print(f"    · {s['nome']} ({s['vigentes']})")
    if emb < len(T): print("Filtro --tema precisa do arquivo temas/<tema>.md (não embarcado nesta versão): use --tribunal e termos — as palavras-chave dos subtemas acima são bons termos.")

def estado_bancada(root: Path) -> tuple[str, str]:
    d = root / BANCADA_REL
    if (d / "INDEX.md").exists():
        m = re.search(r"[Gg]erado em (\d{4}-\d{2}-\d{2})", ler(d / "INDEX.md")); return "copia", (m.group(1) if m else "?")
    if (d / "README.md").exists(): return "readme", ""
    return "nada", ""

def cmd_status(a, root: Path):
    v = exigir_repertorio(); R = carregar(v); por: dict[str, int] = {}
    for r in R: por[r["fonte"]] = por.get(r["fonte"], 0) + 1
    tam = sum(f.stat().st_size for f in v.rglob("*") if f.is_file() and not any(p.startswith(".") for p in f.relative_to(v).parts))
    temas_emb = (v / "temas").is_dir(); est, dt = estado_bancada(root)
    r = {"retrato": data_retrato(), "repertorio": rel(PLUGIN, v), "tamanho_mb": round(tam / 1048576, 1), "verbetes": len(R), "por_fonte": por, "temas_embarcados": temas_emb,
         "bancada": {"pasta": BANCADA_REL, "estado": est, "copia_gerada_em": dt or None}}
    if a.json: print(json.dumps(r, ensure_ascii=False, indent=2)); return
    print(f"súmulas: retrato de {r['retrato']} · {len(R)} verbetes em {rel(PLUGIN, v)}/ ({r['tamanho_mb']} MB, lidos do plugin sob demanda) · temas/: {'embarcado' if temas_emb else 'não embarcado (busca por --tribunal e termos)'}")
    print("  " + " · ".join(f"{k} {n}" for k, n in sorted(por.items())))
    if est == "copia": print(f"  bancada: cópia offline em {BANCADA_REL}/ (gerada em {dt}) — o plugin já tem {r['retrato']}; `--copiar {BANCADA_REL}` atualiza")
    elif est == "readme": print(f"  bancada: só {BANCADA_REL}/README.md (consulta pelo plugin, nada copiado) ✓")
    else: print(f"  bancada: sem {BANCADA_REL}/README.md — rode `sumulas.py readme` (2 linhas: como consultar)")
    print("  " + AVISO)

def texto_readme() -> str:
    return ("# Súmulas — consulta pelo plugin (nada copiado nesta pasta)\n"
            "Repertório STF · STJ · TST · TJSP · TRT-15 · CJF · FONAJE vive no plugin: `python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/sumulas.py\" buscar <termos> [--tribunal STJ]` · "
            f"`ver \"STJ 479\"` · `temas` · `status`. Retrato datado ({data_retrato()}): confirmar a vigência na fonte oficial antes de citar. "
            f"Cópia offline (≈18 MB, opcional): `sumulas.py --copiar {BANCADA_REL}`.\n")

def cmd_readme(a, root: Path):
    exigir_repertorio(); p = root / BANCADA_REL / "README.md"; novo = texto_readme()
    if p.exists() and p.read_text(encoding="utf-8") == novo: print(f"{rel(root, p)} já está atualizado (2 linhas)"); return
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(novo, encoding="utf-8"); print(f"gravado {rel(root, p)} (2 linhas: como consultar pelo plugin; nada copiado)")

def cmd_copiar(a, root: Path):
    v = exigir_repertorio(); bruto = (a.destino or "").strip(); destino = bruto.replace("\\", "/").rstrip("/")
    if not destino: erro("informe a pasta de destino relativa à bancada: sumulas.py --copiar knowledge/jurisprudencia/sumulas", 1)
    absoluto = Path(bruto).is_absolute() or bruto.startswith(("/", "\\", "~")) or re.match(r"^[A-Za-z]:", bruto) is not None   # checado ANTES de qualquer strip
    alvo = (root / destino).resolve(); rr = root.resolve()
    if absoluto or ".." in Path(destino).parts or alvo == rr or not alvo.is_relative_to(rr): erro(f"destino fora da bancada: {a.destino} (use caminho relativo à raiz, ex.: {BANCADA_REL})", 2)
    copiados = iguais = 0; tam = 0
    for f in sorted(v.rglob("*")):
        if not f.is_file() or any(p.startswith(".") for p in f.relative_to(v).parts) or f.name == ".DS_Store": continue
        d = alvo / f.relative_to(v); tam += f.stat().st_size
        if d.exists() and d.stat().st_size == f.stat().st_size and assinatura(d) == assinatura(f): iguais += 1; continue
        d.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, d); copiados += 1
    print(f"cópia offline em {rel(root, alvo)}/: {copiados} copiado(s) · {iguais} igual(is) · {round(tam / 1048576, 1)} MB · retrato de {data_retrato()} · nada apagado")
    print(f"  Indexar: python3 \"${{CLAUDE_PLUGIN_ROOT}}/scripts/jusia_index.py\" · a consulta pelo plugin (sumulas.py buscar/ver) continua valendo; {AVISO}")

def main():
    argv = sys.argv[1:]
    if "--copiar" in argv:   # atalho documentado: `sumulas.py --copiar <pasta>` == `sumulas.py copiar <pasta>`
        i = argv.index("--copiar"); argv = argv[:i] + ["copiar"] + argv[i + 1:]
    comum = argparse.ArgumentParser(add_help=False); comum.add_argument("--raiz", default=argparse.SUPPRESS)
    ap = argparse.ArgumentParser(description=__doc__.split("Uso:")[0], epilog=AVISO, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz"); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("buscar", parents=[comum], help="termos (todos) nos verbetes; --tribunal, --tema, --n, --cancelados, --json"); s.add_argument("termos", nargs="+")
    s.add_argument("--tribunal"); s.add_argument("--tema"); s.add_argument("--n", type=int, default=10); s.add_argument("--cancelados", action="store_true"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_buscar)
    s = sub.add_parser("ver", parents=[comum], help="enunciado e metadados de um verbete pelo id"); s.add_argument("id"); s.add_argument("--integral", action="store_true"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_ver)
    s = sub.add_parser("temas", parents=[comum]); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_temas)
    s = sub.add_parser("status", parents=[comum]); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("readme", parents=[comum], help=f"grava {BANCADA_REL}/README.md na bancada (2 linhas)"); s.set_defaults(fn=cmd_readme)
    s = sub.add_parser("copiar", parents=[comum], help="cópia offline do repertório para <destino> (relativo à bancada)"); s.add_argument("destino"); s.set_defaults(fn=cmd_copiar)
    a = ap.parse_args(argv); a.fn(a, raiz(getattr(a, "raiz", None)))

if __name__ == "__main__":
    main()
