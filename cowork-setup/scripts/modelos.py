#!/usr/bin/env python3
"""Modelos canônicos do escritório em knowledge/modelos/<area>/ — a base de onde o chefe redige.
O advogado DESPEJA arquivos em knowledge/modelos/_novos/ (ou numa pasta qualquer dentro de modelos/) e o plugin organiza sozinho:
descobre a área pelo caminho, pelo nome e pelo começo do texto, renomeia em minúsculas (sem acento, sem espaço, sem número na frente),
leva para modelos/<area>/[<tema>/] e refaz os índices. O que não souber classificar vai para modelos/geral/ marcado [área?].
Nunca apaga: arquivo idêntico a um que já existe vai para _legado/duplicados/; nome repetido com conteúdo diferente ganha -2.
Cada movimento fica em _sistema/modelos.log (o mapa de desfazer).
Uso:
  python3 modelos.py esqueleto                        cria knowledge/{modelos/_novos, jurisprudencia, doutrina, legislacao} e os README (só o que falta)
  python3 modelos.py organizar [--simular] [--resumo] organiza _novos/ e o que estiver fora do lugar em modelos/ (padrão: executa)
  python3 modelos.py importar <pasta ou arquivo>      COPIA para _novos/ (o original fica onde está) e organiza
  python3 modelos.py mover <arquivo em modelos/> <area>[/<tema>]   corrige a área de um modelo (ex.: um que caiu em geral/)
  python3 modelos.py indexar                          regrava modelos/<area>/INDEX.md, modelos/INDEX.md e knowledge/README.md
  python3 modelos.py ler <arquivo>                    imprime o texto de um modelo (.docx .odt .pdf .md .txt) para o chefe ler
Opções: --raiz X · --json"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, zipfile, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

IGN = {".DS_Store", "Thumbs.db", "desktop.ini", "Icon\r", ".gitkeep"}
SISTEMA_MODELOS = {"README.md", "INDEX.md"}
NAO_RENOMEAR = SISTEMA_MODELOS | {"CLAUDE.md"}   # CLAUDE.md numa subpasta é instrução para o Claude: renomear desligaria
PASTAS_NEUTRAS = {"contencioso", "consultivo", "modelos", "modelo", "templates", "template", "base-de-conhecimento", "knowledge", "novos",
                  "_novos", "pecas", "documentos", "arquivos", "diversos", "outros"}
GENERICOS = {"contrato", "contratos", "contratual", "prestacao-de-servicos", "modelo", "modelos"}
TIPOS = (("contestac", "contestação"), ("peticao-inicial", "petição inicial"), ("inicial", "petição inicial"), ("replica", "réplica"),
         ("apelac", "apelação"), ("agravo", "agravo"), ("embargo", "embargos"), ("recurso", "recurso"), ("contrarraz", "contrarrazões"),
         ("memoria", "memoriais"), ("mandado-de-seguranca", "mandado de segurança"), ("tese", "tese"), ("parecer", "parecer"),
         ("notific", "notificação"), ("procurac", "procuração"), ("substabelec", "substabelecimento"), ("honorar", "honorários"),
         ("aditivo", "aditivo"), ("distrato", "distrato"), ("confiss", "confissão de dívida"), ("cessao", "cessão"), ("nda", "NDA"),
         ("confidencialidade", "NDA"), ("acordo-de-socio", "acordo de sócios"), ("acordo", "acordo"), ("contrato-social", "contrato social"),
         ("alteracao-contratual", "alteração contratual"), ("contrato", "contrato"), ("checklist", "checklist"), ("roteiro", "roteiro"),
         ("playbook", "playbook"), ("minuta", "minuta"), ("linha-do-tempo", "linha do tempo"), ("cof", "COF"))

def K(root: Path) -> Path: return root / "knowledge"
def M(root: Path) -> Path: return K(root) / "modelos"
def CAIXA(root: Path) -> Path: return M(root) / espec()["knowledge"]["modelos"]["caixa"]

def log(root: Path, msg: str) -> None:
    p = sistema(root) / "modelos.log"
    with p.open("a", encoding="utf-8") as fh: fh.write(f"{agora()} · {msg}\n")

# ---------- esqueleto ----------
def esqueleto(root: Path) -> list[str]:
    """Cria o que falta de knowledge/ (nunca sobrescreve um README que o advogado editou)."""
    esp = espec()["knowledge"]; feitos = []
    pastas = ["modelos/" + esp["modelos"]["caixa"]] + [f"jurisprudencia/{p}" for p in esp["jurisprudencia"]["pastas"]] \
             + [f"doutrina/{p}" for p in esp["doutrina"]["pastas"]] + ["legislacao"]
    for p in pastas:
        d = K(root) / p
        if not d.exists(): d.mkdir(parents=True, exist_ok=True); feitos.append(f"knowledge/{p}/")
    for p in ("modelos/README.md", "jurisprudencia/README.md", "doutrina/README.md", "legislacao/README.md"):
        dst = K(root) / p
        if not dst.exists():
            dst.write_text(template("knowledge/" + p), encoding="utf-8"); feitos.append(f"knowledge/{p}")
    s = K(root) / "jurisprudencia" / "sumulas" / "README.md"
    if not s.exists():
        s.write_text("# Súmulas e precedentes qualificados\n\nO repertório (STF · STJ · TST · TJSP · TRT-15 · CJF · FONAJE) vem **embarcado no plugin** e é lido sob demanda: "
                     "`/jurisprudencia sumulas` ou `python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/sumulas.py\" buscar <termos>`. Nível 1 — conferir a vigência na fonte oficial antes de citar.\n",
                     encoding="utf-8"); feitos.append("knowledge/jurisprudencia/sumulas/README.md")
    return feitos

# ---------- texto ----------
def _xml_texto(x: str) -> str:
    x = re.sub(r"</w:p>|</text:p>|<w:br/>|<text:line-break/>", "\n", x)
    x = re.sub(r"<[^>]+>", "", x)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'")): x = x.replace(a, b)
    return re.sub(r"[ \t]+", " ", x)

def texto_de(f: Path, limite: int | None = 6000) -> str:
    suf = f.suffix.lower()
    try:
        if suf in (".md", ".txt", ".html", ".htm"): t = ler(f)
        elif suf in (".docx", ".odt"):
            with zipfile.ZipFile(f) as z:
                nome = "word/document.xml" if suf == ".docx" else "content.xml"
                t = _xml_texto(z.read(nome).decode("utf-8", "ignore"))
        elif suf == ".pdf" and shutil.which("pdftotext"):
            r = subprocess.run(["pdftotext", "-layout", "-l", "3" if limite else "999", str(f), "-"], capture_output=True, text=True, timeout=60)
            t = r.stdout
        else: t = ""
    except Exception: t = ""
    return t[:limite] if limite else t

def titulo_de(f: Path) -> str:
    t = texto_de(f, 3000)
    for l in t.splitlines():
        l = l.strip().lstrip("#").strip()
        if len(l) >= 4 and not l.startswith(("|", "<", "---")): return l[:100]
    return ""

def nome_modelo(nome: str) -> str:
    """nome_arquivo(), mas nunca 'index.md'/'readme.md' (colidiriam com o índice que o plugin grava em disco que não distingue caixa)."""
    n = nome_arquivo(nome)
    if n in ("index.md", "readme.md"): n = n[:-3] + "-antigo.md"
    return n

def tipo_de(nome: str) -> str:
    n = "-" + slug(nome) + "-"
    for k, t in TIPOS:
        if k in n: return t
    return "modelo"

# ---------- classificação ----------
def tabela(root: Path) -> dict:
    """{categoria: [(alias_slug, peso)]} — áreas do plugin + áreas registradas na bancada + honorarios/procuracoes."""
    esp = espec()["knowledge"]["modelos"]; tab = {}
    fontes = [areas_espec().get("areas", {}), (ler_json(root / "_sistema" / "areas.json", {}) or {}).get("areas", {})]
    for f in fontes:
        for a, info in f.items():
            al = {slug(a)} | {slug(x) for x in info.get("nomes", [])}
            tab.setdefault(a, set()).update(x for x in al if x)
    for c, al in esp["categorias_extras"].items():
        tab.setdefault(c, set()).update(slug(x) for x in al + [c])
    return {c: [(a, 0.4 if a in GENERICOS else (1.6 if c in esp["categorias_extras"] else 1.0)) for a in sorted(al)] for c, al in tab.items()}

def categorias_conhecidas(root: Path) -> set:
    return set(tabela(root)) | {espec()["knowledge"]["modelos"]["geral"]}

def pontuar(texto_slug: str, tab: dict, fator: float) -> dict:
    s = "-" + texto_slug + "-"; out = {}
    for c, als in tab.items():
        for a, peso in als:
            n = s.count("-" + a + "-")
            if n: out[c] = out.get(c, 0) + fator * peso * (1 + a.count("-")) * min(n, 5)
    return out

def classificar(caminho_rel: str, texto: str, tab: dict) -> tuple[str | None, dict]:
    """Área pelo caminho/nome (peso alto) + começo do texto (peso baixo). Decide só se houver vencedor claro."""
    sc = pontuar(slug(caminho_rel.replace("/", " ")), tab, 3.0)
    for c, v in pontuar(slug(texto[:4000]), tab, 0.5).items(): sc[c] = sc.get(c, 0) + v
    if not sc: return None, sc
    orden = sorted(sc.items(), key=lambda x: -x[1])
    if len(orden) == 1 or orden[0][1] >= 1.5 * orden[1][1]: return orden[0][0], sc
    return None, sc

# ---------- mover ----------
def _destino_livre(dst: Path, src: Path) -> tuple[Path, bool]:
    """(destino, duplicado?) — mesmo conteúdo = duplicado; mesmo nome e conteúdo diferente = sufixo -2, -3…"""
    k = 2; base = dst
    while dst.exists():
        if assinatura(dst) == assinatura(src): return dst, True
        dst = base.with_name(f"{base.stem}-{k}{base.suffix}"); k += 1
    return dst, False

def _mesmo(a: Path, b: Path) -> bool:
    try: return a.exists() and b.exists() and a.samefile(b)
    except Exception: return False

def _renomear(root: Path, src: Path, dst: Path) -> None:
    """Renomeia em dois passos (mudança só de maiúscula/minúscula em disco que não distingue caixa: APFS, NTFS)."""
    tmp = src.with_name(src.name + ".__renomeando__"); src.rename(tmp); tmp.rename(dst); log(root, f"renomeado `{rel(root, src)}` → `{rel(root, dst)}`")

def mover_arquivo(root: Path, src: Path, dst: Path, simular: bool) -> str:
    if _mesmo(src, dst):
        if src.name != dst.name and not simular: _renomear(root, src, dst)
        return f"`{rel(root, dst)}`"
    dst, dup = _destino_livre(dst, src)
    if dup:
        alvo = root / "_legado" / "duplicados" / rel(root, src)
        if simular: return f"duplicado de `{rel(root, dst)}` → `{rel(root, alvo)}`"
        alvo.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(alvo)); log(root, f"duplicado `{rel(root, src)}` → `{rel(root, alvo)}` (igual a `{rel(root, dst)}`)")
        return f"duplicado → `{rel(root, alvo)}`"
    if simular: return f"`{rel(root, src)}` → `{rel(root, dst)}`"
    dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(dst)); log(root, f"`{rel(root, src)}` → `{rel(root, dst)}`")
    return f"`{rel(root, dst)}`"

def _limpar_vazias(d: Path, parar: Path) -> None:
    if not d.exists(): return
    for p in sorted([x for x in d.rglob("*") if x.is_dir()], key=lambda x: -len(x.parts)) + [d]:
        if p == parar or not p.exists(): continue
        try:
            if all(f.name in IGN for f in p.iterdir()):
                for f in p.iterdir(): f.unlink(missing_ok=True)
                p.rmdir()
        except Exception: pass

def arquivos(d: Path) -> list[Path]:
    return [f for f in sorted(d.rglob("*")) if f.is_file() and f.name not in IGN and not f.name.startswith("~$")] if d.exists() else []

def normalizar_arvore(root: Path, d: Path, res: dict, simular: bool) -> Path:
    """Pasta de área já existente: pastas e arquivos em minúsculas, sem acento, sem número na frente. Nome igual a outro já
    existente → mescla (conteúdo igual vai para _legado/duplicados/). Devolve o caminho final da pasta."""
    for p in sorted([x for x in d.rglob("*") if x.is_dir()], key=lambda x: -len(x.parts)) + [d]:
        alvo = p.parent / slug_sem_numero(p.name)
        if alvo.name == p.name or not alvo.name: continue
        res["renomeados"].append(f"`{rel(root, p)}/` → `{rel(root, alvo)}/`")
        if simular: continue
        if alvo.exists() and not _mesmo(p, alvo):
            for f in arquivos(p): mover_arquivo(root, f, alvo / f.relative_to(p), False)
            _limpar_vazias(p, p.parent)
        else: _renomear(root, p, alvo)
        if p == d: d = alvo
    for f in arquivos(d):
        if f.name in NAO_RENOMEAR: continue
        alvo = f.with_name(nome_modelo(f.name))
        if alvo.name != f.name: res["renomeados"].append(mover_arquivo(root, f, alvo, simular))
    return d

def organizar(root: Path, simular: bool = False) -> dict:
    """1) normaliza os nomes dentro das pastas de área · 2) classifica e guarda o que está em _novos/, solto na raiz de modelos/
    ou em pasta desconhecida na raiz de modelos/ · 3) limpa pastas vazias e refaz os índices (só se algo mudou)."""
    if not simular: esqueleto(root)
    tab = tabela(root); geral = espec()["knowledge"]["modelos"]["geral"]; conhecidas = categorias_conhecidas(root)
    m = M(root); caixa = CAIXA(root); res = {"organizados": [], "geral": [], "duplicados": [], "renomeados": []}
    if not m.exists(): return res
    for x in sorted(m.iterdir()):
        if x.is_dir() and x != caixa and (x.name in conhecidas or slug_sem_numero(x.name) in conhecidas):
            normalizar_arvore(root, x, res, simular)
    fila = [(caixa, f) for f in arquivos(caixa) if not (f.parent == caixa and f.name in SISTEMA_MODELOS)]
    for x in sorted(m.iterdir()):
        if x.name in IGN or x == caixa: continue
        if x.is_file() and x.name not in SISTEMA_MODELOS: fila.append((m, x))
        elif x.is_dir() and x.name not in conhecidas and slug_sem_numero(x.name) not in conhecidas:
            fila += [(m, f) for f in arquivos(x)]
    ja = {}   # conteúdo (md5) → arquivo já guardado numa área: o mesmo modelo em duas pastas vira duplicado, não dois modelos
    for x in m.iterdir():
        if x.is_dir() and x != caixa and (x.name in conhecidas or slug_sem_numero(x.name) in conhecidas):
            for f in arquivos(x):
                if f.name not in SISTEMA_MODELOS: ja.setdefault(assinatura(f), f)
    # A área se decide pela PASTA que o advogado despejou (o agrupamento dele é mantido); arquivo solto decide sozinho.
    grupos = {}
    for base, f in fila:
        relc = f.relative_to(base); chave = relc.parts[0] if len(relc.parts) > 1 else None
        grupos.setdefault((base, chave), []).append(f)
    decisao = {}
    for (base, chave), fs in grupos.items():
        if chave is None: continue
        sc = pontuar(slug_sem_numero(chave), tab, 6.0)   # o nome da pasta pesa mais que qualquer arquivo
        for f in fs:
            c1, s1 = classificar(f.relative_to(base / chave).as_posix(), texto_de(f), tab)
            for c, v in s1.items(): sc[c] = sc.get(c, 0) + v / max(1, len(fs)) * 2
        orden = sorted(sc.items(), key=lambda x: -x[1])
        decisao[(base, chave)] = orden[0][0] if orden and (len(orden) == 1 or orden[0][1] >= 1.3 * orden[1][1]) else geral
    for base, f in fila:
        relc = f.relative_to(base); sig = assinatura(f)
        if f.name == "CLAUDE.md":   # instrução antiga para o Claude, não é modelo
            alvo = root / "_legado" / "knowledge-antigo" / relc
            if not simular: alvo.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(f), str(alvo)); log(root, f"`{rel(root, f)}` → `{rel(root, alvo)}` (instrução antiga, não é modelo)")
            res["renomeados"].append(f"`{rel(root, f)}` → `{rel(root, alvo)}`"); continue
        if sig in ja and not _mesmo(f, ja[sig]):
            alvo = root / "_legado" / "duplicados" / rel(root, f)
            if not simular:
                alvo.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(f), str(alvo)); log(root, f"duplicado `{rel(root, f)}` → `{rel(root, alvo)}` (igual a `{rel(root, ja[sig])}`)")
            res["duplicados"].append(f"`{rel(root, f)}` igual a `{rel(root, ja[sig])}` → `{rel(root, alvo)}`"); continue
        if len(relc.parts) > 1: cat = decisao[(base, relc.parts[0])]
        else: cat = classificar(relc.as_posix(), texto_de(f), tab)[0] or geral
        aliases = {a for a, _ in tab.get(cat, [])}
        vazias = PASTAS_NEUTRAS | aliases | {cat, "de", "da", "do", "das", "dos", "e", "meus", "minhas"}
        # pasta que só repete a área ("MODELOS TRABALHISTAS", "Trabalhista") some; pasta de tema ("teses-defesa-franquia") fica
        tema = [t for t in (slug_sem_numero(p) for p in relc.parts[:-1]) if t and not set(t.split("-")) <= vazias and t not in aliases]
        dst = m / cat / Path(*tema) / nome_modelo(f.name) if tema else m / cat / nome_modelo(f.name)
        r = mover_arquivo(root, f, dst, simular)
        (res["duplicados"] if r.startswith("duplicado") else res["geral" if cat == geral else "organizados"]).append(r)
        if not r.startswith("duplicado"): ja[sig] = dst
    # bases de citação: só nomes (minúsculas, sem acento, sem número na frente) — nunca muda de pasta
    for d in (K(root) / "jurisprudencia" / "proprias", K(root) / "doutrina" / "proprias", K(root) / "legislacao"):
        if d.is_dir(): normalizar_arvore(root, d, res, simular)
    if not simular:
        _limpar_vazias(caixa, caixa)
        for x in list(m.iterdir()):
            if x.is_dir() and x != caixa: _limpar_vazias(x, m)
        if any(res.values()) or not (m / "INDEX.md").exists(): indexar(root)
    return res

# ---------- índices ----------
def _descricoes_antigas(p: Path) -> dict:
    """{arquivo: descrição} do INDEX.md anterior — o que o advogado escreveu à mão sobrevive à reindexação."""
    out = {}
    for l in ler(p).splitlines():
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 3 and c[0].startswith("`"):
            d = c[2].replace("[área?] ", "")
            if d and not d.startswith("[descrever]"): out[c[0].strip("`")] = d
    return out

def indexar(root: Path) -> dict:
    m = M(root); caixa = CAIXA(root); geral = espec()["knowledge"]["modelos"]["geral"]; resumo = {}
    if not m.exists(): return resumo
    for cdir in sorted(d for d in m.iterdir() if d.is_dir() and d != caixa):
        fs = [f for f in arquivos(cdir) if not (f.parent == cdir and f.name in SISTEMA_MODELOS)]
        antigas = _descricoes_antigas(cdir / "INDEX.md")
        L = [f"# Índice — knowledge/modelos/{cdir.name}/", "", f"> Gerado em {hoje()} pelo plugin. A coluna \"O que é\" pode ser editada à mão: a próxima indexação preserva o que você escrever "
             "(o que termina em `[auto]` foi tirado do título do documento).", "",
             "| Arquivo | Tipo | O que é | Data |", "|---|---|---|---|"]
        for f in fs:
            r = f.relative_to(cdir).as_posix()
            d = antigas.get(r)
            if not d:
                tt = titulo_de(f); d = (tt + " [auto]") if tt else "[descrever]"
            if cdir.name == geral and not d.startswith("[área?]"): d = "[área?] " + d
            L.append(f"| `{r}` | {tipo_de(f.name)} | {d.replace('|', '/')} | {datetime.date.fromtimestamp(f.stat().st_mtime).isoformat()} |")
        (cdir / "INDEX.md").write_text("\n".join(L) + "\n", encoding="utf-8"); resumo[cdir.name] = len(fs)
    G = [f"# Índice geral — knowledge/modelos/ · {hoje()}", "", "| Área | Modelos | Índice |", "|---|---:|---|"]
    G += [f"| `{c}` | {n} | [{c}/INDEX.md]({c}/INDEX.md) |" for c, n in resumo.items()]
    pend = len(arquivos(caixa)) - sum(1 for f in (caixa.iterdir() if caixa.exists() else []) if f.name in SISTEMA_MODELOS)
    if pend > 0: G += ["", f"**{pend} arquivo(s) em `_novos/` esperando organização** — `/modelos organizar`."]
    if resumo.get(geral): G += ["", f"`{geral}/` = modelos cuja área o plugin não soube dizer: `/modelos mover <arquivo> <area>`."]
    (m / "INDEX.md").write_text("\n".join(G) + "\n", encoding="utf-8")
    readme_knowledge(root, resumo)
    return resumo

def contar(d: Path, exts=(".md", ".pdf", ".docx", ".json", ".txt", ".doc", ".odt")) -> int:
    return sum(1 for f in d.rglob("*") if f.is_file() and f.suffix.lower() in exts and f.name not in ("README.md", "INDEX.md")) if d.exists() else 0

def readme_knowledge(root: Path, resumo: dict | None = None) -> None:
    """knowledge/README.md é do plugin: regrava a partir do template com o índice atual."""
    if resumo is None: resumo = {d.name: len([f for f in arquivos(d) if f.name not in SISTEMA_MODELOS]) for d in sorted(M(root).iterdir()) if d.is_dir() and d != CAIXA(root)} if M(root).exists() else {}
    k = K(root); perfil = ler_json(root / "_sistema" / "perfil.json", {}) or {}
    L = ["| Base | Conteúdo |", "|---|---|",
         "| `modelos/` | " + (" · ".join(f"`{c}` {n}" for c, n in resumo.items()) or "vazio — despeje em `modelos/_novos/`") + " |",
         f"| `jurisprudencia/` | jusia {contar(k / 'jurisprudencia' / 'jusia', ('.json',))} busca(s) · próprias {contar(k / 'jurisprudencia' / 'proprias')} · súmulas embarcadas no plugin |",
         f"| `doutrina/` | jusia {contar(k / 'doutrina' / 'jusia', ('.json',))} busca(s) · próprias {contar(k / 'doutrina' / 'proprias')} |",
         f"| `legislacao/` | {contar(k / 'legislacao')} arquivo(s) |"]
    txt = render(template("knowledge/README.md"), {"TRATAMENTO": perfil.get("TRATAMENTO") or "o advogado", "INDICE_KNOWLEDGE": "\n".join(L)})
    (k / "README.md").write_text(txt, encoding="utf-8")

# ---------- comandos ----------
def importar(root: Path, origem: Path) -> int:
    ext = set(espec()["knowledge"]["modelos"]["extensoes"]); caixa = CAIXA(root); caixa.mkdir(parents=True, exist_ok=True); n = 0
    if not origem.exists(): print(f"origem não existe: {origem}"); sys.exit(2)
    try:
        origem.resolve().relative_to(M(root).resolve()); print("essa pasta já está dentro de knowledge/modelos/ — use `organizar`."); sys.exit(2)
    except ValueError: pass
    fontes = [(origem.parent, origem)] if origem.is_file() else [(origem.parent, f) for f in sorted(origem.rglob("*")) if f.is_file() and f.suffix.lower() in ext and f.name not in IGN]
    for base, f in fontes:
        dst = caixa / f.relative_to(base)
        if dst.exists() and assinatura(dst) == assinatura(f): continue
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, dst); n += 1
    log(root, f"importados {n} arquivo(s) de `{origem.name}` (cópia; original intacto)")
    return n

def mover_manual(root: Path, arquivo: str, destino: str) -> None:
    src = (root / arquivo) if not Path(arquivo).is_absolute() else Path(arquivo)
    if not src.exists(): src = M(root) / arquivo
    if not src.exists(): print(f"não achei: {arquivo}"); sys.exit(2)
    partes = [slug_sem_numero(p) for p in destino.strip("/").split("/") if p]
    if not partes: print("destino vazio — use <area> ou <area>/<tema>"); sys.exit(2)
    cat = area_por_nome(partes[0], root) or partes[0]
    print(mover_arquivo(root, src, M(root) / cat / Path(*partes[1:]) / nome_modelo(src.name), False))
    _limpar_vazias(src.parent, M(root)); indexar(root)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("acao", choices=["esqueleto", "organizar", "importar", "mover", "indexar", "ler"]); ap.add_argument("arg", nargs="*")
    ap.add_argument("--simular", action="store_true"); ap.add_argument("--resumo", action="store_true"); ap.add_argument("--json", action="store_true"); ap.add_argument("--raiz")
    a = ap.parse_args(); root = raiz(a.raiz)
    if a.acao == "esqueleto":
        f = esqueleto(root); print("criado: " + ", ".join(f) if f else "knowledge/ já completo"); return
    if a.acao == "ler":
        if not a.arg: print("uso: ler <arquivo>"); sys.exit(2)
        p = Path(a.arg[0]); p = p if p.is_absolute() or p.exists() else root / p
        print(texto_de(p, None) or f"(sem texto extraível de {p.name} — abra o arquivo)"); return
    if a.acao == "indexar":
        r = indexar(root); print("índices: " + (" · ".join(f"{c} {n}" for c, n in r.items()) or "nenhum modelo ainda")); return
    if a.acao == "mover":
        if len(a.arg) < 2: print("uso: mover <arquivo> <area>[/<tema>]"); sys.exit(2)
        mover_manual(root, a.arg[0], a.arg[1]); return
    if a.acao == "importar":
        if not a.arg: print("uso: importar <pasta ou arquivo>"); sys.exit(2)
        n = importar(root, Path(a.arg[0]).expanduser()); print(f"copiados {n} arquivo(s) para knowledge/modelos/_novos/ (originais intactos)")
    res = organizar(root, a.simular)
    if a.json: print(json.dumps(res, ensure_ascii=False, indent=2)); return
    n_org, n_ger, n_dup, n_ren = (len(res[k]) for k in ("organizados", "geral", "duplicados", "renomeados"))
    if a.resumo:
        if n_org or n_ger or n_dup or n_ren:
            print(f"modelos: {n_org} organizado(s) por área · {n_ger} em geral/ (diga a área com /modelos mover) · {n_dup} duplicado(s) → _legado/duplicados/ · {n_ren} renomeado(s)")
        return
    verbo = "seria(m)" if a.simular else "foram"
    print(f"{n_org} modelo(s) {verbo} organizado(s) por área · {n_ger} em geral/ · {n_dup} duplicado(s) · {n_ren} renomeado(s)")
    for k in ("organizados", "geral", "duplicados", "renomeados"):
        for x in res[k][:40]: print(f"  [{k}] {x}")
    if not a.simular: print("Índices: knowledge/modelos/INDEX.md e knowledge/modelos/<area>/INDEX.md · log: _sistema/modelos.log")

if __name__ == "__main__":
    main()
