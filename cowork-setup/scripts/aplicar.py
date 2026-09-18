#!/usr/bin/env python3
"""F3 — Aplicar: executa o plano APROVADO (_sistema/migracao/plano.json). Idempotente: rodar 2× = zero mudança.
NUNCA apaga arquivo: move, cria, anexa. Conflito vai para _legado/triagem/conflitos/. Log em _sistema/migracao/MIGRACAO.md.
Uso:
  python3 aplicar.py [--raiz X]        executa o plano aprovado
  python3 aplicar.py --so-render       só regenera CLAUDE.md, TASKS.md (se ausente), identidade/, knowledge/README (se ausente) a partir do perfil
  python3 aplicar.py --novo            pasta vazia: só esqueleto + templates + renders (sem plano)"""
import argparse, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

IGN = {".DS_Store"}
LOG = []

def log(msg):
    LOG.append(f"- {agora()} · {msg}"); print(msg)

def mkdir_exato(root: Path, relp: str) -> Path:
    """Cria a pasta garantindo a CAIXA exata de cada componente (APFS não distingue CLIENTES de clientes:
    se existir irmã igual ignorando caixa, renomeia em dois passos)."""
    cur = root
    for comp in Path(relp).parts:
        alvo = cur / comp
        if not alvo.exists() or alvo.name == comp:
            if not alvo.exists(): alvo.mkdir()
        try:
            real = next((f for f in cur.iterdir() if f.name.lower() == comp.lower()), None)
        except FileNotFoundError:
            real = None
        if real is not None and real.name != comp:
            tmp = cur / (comp + ".__caixa__"); real.rename(tmp); tmp.rename(cur / comp); log(f"caixa corrigida `{rel(root, cur / real.name)}` → `{rel(root, cur / comp)}`")
        cur = cur / comp
    return cur

def triagem(root: Path, rel_: str) -> Path:
    return root / "_legado" / "triagem" / "conflitos" / rel_

def mover(root: Path, de: str, para: str, mesclar=False, caso_plugin=False):
    src, dst = root / de, root / para
    if not src.exists():
        log(f"pulado (origem já não existe): `{de}` → `{para}`"); return
    if caso_plugin and src.is_dir():
        mkdir_exato(root, para); (dst / "historico").mkdir(exist_ok=True)
        for f in list(src.iterdir()):
            if f.name in IGN: f.unlink(missing_ok=True); continue
            if f.name.upper() in ("CASO.MD", "STATE.MD"):
                alvo = dst / "historico" / f"{hoje()}-{f.stem}-{Path(de).parts[0]}.md"; shutil.move(str(f), str(alvo)); log(f"movido `{de}/{f.name}` → `{rel(root, alvo)}`")
            elif f.name.upper() == "MEMORY.MD":
                anexar(root, f"{de}/{f.name}", f"{para}/_memoria-cowork.md")
            else:
                _mover_um(root, f, dst / f.name, f"{de}/{f.name}", f"{para}/{f.name}")
        _limpar_vazia(src, root); return
    if dst.exists() and (mesclar or (src.is_dir() and dst.is_dir())):
        mkdir_exato(root, para)
        for f in list(src.iterdir()):
            if f.name in IGN: f.unlink(missing_ok=True); continue
            _mover_um(root, f, dst / f.name, f"{de}/{f.name}", f"{para}/{f.name}")
        _limpar_vazia(src, root); return
    _mover_um(root, src, dst, de, para)

def _mover_um(root, src: Path, dst: Path, de: str, para: str):
    if dst.exists():
        if src.is_dir() and dst.is_dir():
            for f in list(src.iterdir()):
                if f.name in IGN: f.unlink(missing_ok=True); continue
                _mover_um(root, f, dst / f.name, f"{de}/{f.name}", f"{para}/{f.name}")
            _limpar_vazia(src, root); return
        alvo = triagem(root, de); alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(alvo)); log(f"CONFLITO: `{para}` já existia — `{de}` foi para `{rel(root, alvo)}`"); return
    mkdir_exato(root, str(Path(para).parent)); shutil.move(str(src), str(dst)); log(f"movido `{de}` → `{para}`")

def _limpar_vazia(d: Path, root: Path):
    try:
        resto = [f for f in d.iterdir() if f.name not in IGN]
        if not resto:
            for f in d.iterdir(): f.unlink(missing_ok=True)
            d.rmdir(); log(f"pasta vazia removida `{rel(root, d)}`")
    except Exception: pass

def mover_resto(root: Path, de: str, para: str):
    src, dst = root / de, root / para
    if not src.exists(): log(f"pulado (origem já não existe): resto de `{de}`"); return
    mkdir_exato(root, para)
    for f in list(src.iterdir()):
        if f.name in IGN: f.unlink(missing_ok=True); continue
        _mover_um(root, f, dst / f.name, f"{de}/{f.name}", f"{para}/{f.name}")
    _limpar_vazia(src, root)
    # sobe removendo pais vazios (CLIENTES/ antigo etc.)
    p = src.parent
    while p != root and p.exists():
        _limpar_vazia(p, root)
        if p.exists(): break
        p = p.parent

def anexar(root: Path, de: str, para: str):
    src, dst = root / de, root / para
    if not src.exists(): log(f"pulado (origem já não existe): `{de}`"); return
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(dst)); log(f"movido `{de}` → `{para}`"); return
    with dst.open("a", encoding="utf-8") as fh:
        fh.write(f"\n\n## Importado de `{de}` ({hoje()})\n\n" + ler(src).strip() + "\n")
    alvo = root / "_legado" / "anexados" / de; alvo.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(alvo))
    log(f"anexado `{de}` em `{para}` (original em `{rel(root, alvo)}`)")

# ---------- renders ----------
def vars_render(root: Path) -> dict:
    perfil = ler_json(root / "_sistema" / "perfil.json", {}) or {}
    v = {k: (", ".join(x) if isinstance(x, list) else x) for k, x in perfil.items() if not isinstance(x, dict)}
    v["DATA"] = hoje(); v["VERSAO"] = versao_plugin()
    esp = espec(); ae = areas_espec()
    motores = [d.name for d in sorted(root.iterdir()) if d.is_dir() and eh_motor(d, esp)]
    v["MOTORES"] = ", ".join(f"`{m}/`" for m in motores) or "nenhum ainda"
    v["PLUGINS"] = v.get("PLUGINS") or (", ".join(motores) or "nenhum detectado")
    local = ler_json(root / "_sistema" / "areas.json", {"areas": {}}) or {"areas": {}}
    areas = sorted(set(local.get("areas", {}).keys()) | set(a.strip() for a in str(perfil.get("AREAS", "")).replace("·", ",").split(",") if a.strip()))
    v["AREAS"] = " · ".join(f"`{a}`" for a in areas) or "(nenhuma ainda — nascem com o /novo-projeto)"
    linhas = []
    for a in areas:
        info = ae["areas"].get(a) or local["areas"].get(a, {})
        plugin = info.get("plugin"); master = info.get("master")
        instalado = plugin and any(m in plugin for m in [slug(x) for x in motores] + [x.replace("direito-", "") for x in motores])
        obs = ("[confirmar]" if info.get("confirmar") else "") + ("" if instalado or not plugin else " (plugin não detectado na pasta — rode /start-* ou o chefe usa a persona)")
        linhas.append(f"| {a} | {plugin or '— (persona do escritório)'} | {('`/' + master + '`') if master else '—'} | {obs.strip()} |")
    v["TABELA_ROTEAMENTO"] = "\n".join(linhas) or "| (nenhuma área registrada) | | | |"
    v["TABELA_APOIOS"] = "\n".join(f"| {k} | {x['plugin']} | {x['para']} |" for k, x in ae["auxiliares"].items() if not k.startswith("_"))
    leg = root / "_legado"
    mem = leg / "MEMORY-cowork.md"; v["MEMORIA_IMPORTADA"] = ler(mem).strip() or "(nada importado)"; v["ORIGEM_MEMORIA"] = "_legado/MEMORY-cowork.md" if mem.exists() else "—"
    v.setdefault("ORIGEM_REGRAS", "_legado/CLAUDE-cowork.md" if (leg / "CLAUDE-cowork.md").exists() else "entrevista")
    v.setdefault("ORIGEM_VOZ", "_legado/PERSONA-cowork.md" if (leg / "PERSONA-cowork.md").exists() else "entrevista")
    v.setdefault("ORIGEM_ESCRITA", v["ORIGEM_VOZ"])
    tk = leg / "TASKS-cowork.md"
    v["TAREFAS_IMPORTADAS"] = ("ver `_legado/TASKS-cowork.md` e trazer o que ainda está vivo" if tk.exists() else "(nenhuma pendência importada)")
    kn = root / "knowledge"; idx = []
    if kn.exists():
        for f in sorted(kn.rglob("*")):
            if f.is_file() and f.parent.name != "templates" and f.name not in ("README.md",) and f.suffix.lower() in (".md", ".docx", ".pdf", ".txt"):
                idx.append(f"| `{rel(kn, f)}` | {f.parent.name if f.parent != kn else '—'} | [REVISAR] | — |")
    v["INDICE_KNOWLEDGE"] = "\n".join(idx) or "| (vazio) | | | |"
    v["IMPORTADO_KNOWLEDGE"] = "Índice antigo em `knowledge/INDEX-cowork.md`." if (kn / "INDEX-cowork.md").exists() else "(nada)"
    for c in ("NOME", "OAB", "ESCRITORIO", "CIDADE_UF", "TRATAMENTO", "NOME_DOCUMENTO", "FERRAMENTAS", "ATUACAO", "COMO_TRABALHO", "LOCAL_PASTA",
              "PROIBICOES", "PROTOCOLOS", "POSTURA", "TOM", "VOCABULARIO", "ANTI_VOZ", "ESTRUTURA_PECA", "REGRAS_ESTILO", "FORMATACAO",
              "FERRAMENTAS_DETALHE", "PREFERENCIAS", "CONTEXTO", "ENTREGAS", "COMO_TRABALHAR"):
        if not str(v.get(c, "")).strip(): v[c] = "[A PREENCHER]"
    v.setdefault("CAMADAS_EXTRAS", ""); v.setdefault("POLOS_VETADOS", "")
    if v["POLOS_VETADOS"] and v["POLOS_VETADOS"] != "[A PREENCHER]" and not v["POLOS_VETADOS"].startswith("**"):
        v["POLOS_VETADOS"] = f"**Polos vetados:** {v['POLOS_VETADOS']}."
    return v

def render_op(root: Path, tpl: str, para: str, se_ausente=False, v=None):
    dst = root / para
    if se_ausente and dst.exists(): log(f"mantido `{para}` (já existia)"); return
    v = v or vars_render(root); txt = render(template(tpl), v)
    if dst.exists() and dst.read_text(encoding="utf-8") == txt: return
    dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(txt, encoding="utf-8"); log(f"gerado `{para}`")

def copiar_templates(root: Path):
    d = root / "knowledge" / "templates"; d.mkdir(parents=True, exist_ok=True)
    for f in (TEMPLATES / "knowledge" / "templates").iterdir():
        if not (d / f.name).exists(): shutil.copy(f, d / f.name); log(f"template `{rel(root, d / f.name)}`")

def state_cliente(root: Path, para: str, nome: str):
    base = mkdir_exato(root, para); mkdir_exato(root, f"{para}/cadastro/documentos")
    st = base / "STATE.md"
    if not st.exists():
        t = template_bancada(root, "STATE-cliente.template.md").replace("<Cliente>", nome).replace("AAAA-MM-DD", hoje())
        t = "\n".join(l for l in t.splitlines() if not l.startswith("| `contencioso/<area>/")) + "\n"
        t = t.replace("1 linha, SEMPRE preenchida (do cliente como um todo).", f"Revisar os projetos migrados (tabela acima), dizer quais estão vivos e completar o cadastro (migrado em {hoje()}).")
        t = t.replace("## Histórico\n", f"## Histórico\n{hoje()} · pasta organizada pelo cowork-setup (migração)\n")
        st.write_text(t, encoding="utf-8"); log(f"criado `{para}/STATE.md`")
    cad = base / "cadastro" / "CADASTRO.md"
    if not cad.exists():
        cad.write_text(template_bancada(root, "CADASTRO.template.md").replace("<Cliente>", nome).replace("AAAA-MM-DD", hoje()), encoding="utf-8"); log(f"criado `{para}/cadastro/CADASTRO.md`")

def state_projeto(root: Path, para: str, cliente: str, tipo: str, area: str, projeto: str, tier: str, state_antigo=None):
    d = mkdir_exato(root, para); st = d / "STATE.md"
    if not st.exists():
        import re as _re
        m = _re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", projeto + " " + ler(root / state_antigo) if state_antigo else projeto)
        ref = m.group(0) if m else ("(sem processo)" if tipo != "contencioso" else "<a preencher>")
        t = (template_bancada(root, "STATE.template.md")
             .replace("<Cliente> × <Adversário | Documento | Família>", f"{cliente} × {projeto}")
             .replace("- Tipo: Contencioso | Consultivo | Holding · Área: <área> · Ref/Nº processo: <…>", f"- Tipo: {tipo.capitalize()} · Área: {area} · Ref/Nº processo: {ref}")
             .replace("@chefe (área <área>) · Plugin: <plugin> · Tier: T0–T3", f"@chefe (área {area}) · Plugin: ver identidade/05 · Tier: {tier}")
             .replace("AAAA-MM-DD", hoje()))
        if state_antigo:
            ant = f"historico/{Path(state_antigo).name}"
            t = t.replace("O que é, em 3 linhas. Partes. Pedido. Resultado esperado.", f"Migrado em {hoje()}: o STATE anterior está em `{ant}`. Preencher a partir dele (Gandalf) quando o caso for tocado.")
            t = t.replace("1 linha, SEMPRE preenchida.", f"Ler `{ant}` e preencher Demanda · Fase atual · Próximo passo (caso migrado em {hoje()}).")
            t = t.replace("**1 linha por entrega** — AAAA-MM-DD · o que foi feito · arquivo", f"**1 linha por entrega**\n{hoje()} · migrado do Cowork OS anterior; STATE antigo em historico/")
        st.write_text(t, encoding="utf-8"); log(f"criado `{para}/STATE.md`")
    if tier in ("T2", "T3") and not (d / "FICHA.md").exists():
        (d / "FICHA.md").write_text(template_bancada(root, "FICHA.template.md").replace("<Cliente> × <Adversário | Documento | Família>", f"{cliente} × {projeto}"), encoding="utf-8"); log(f"criado `{para}/FICHA.md`")
    for sub in ("entrada", "pesquisas"):
        (d / sub).mkdir(exist_ok=True)

def reindexar(root: Path):
    """Garante que todo projeto conste na tabela 'Projetos abertos' do STATE do cliente."""
    for cli in sorted((root / "clientes").glob("*/")):
        idx = cli / "STATE.md"
        if not idx.exists(): continue
        txt = ler(idx); marca = "|---|---|---|---|---|"; novas = []
        for st in sorted(cli.glob("*/*/*/STATE.md")) + ([cli / "holding" / "STATE.md"] if (cli / "holding" / "STATE.md").exists() else []):
            p = st.parent; r = rel(cli, p); partes = r.split("/")
            if f"`{r}/`" in txt: continue
            tipo_area = f"{partes[0]}/{partes[1]}" if len(partes) >= 3 else "holding"
            novas.append(f"| `{r}/` | {tipo_area} | migrado | {proximo_passo(st)[:60]} | {hoje()} |")
        if novas and marca in txt:
            txt = txt.replace(marca, marca + "\n" + "\n".join(novas), 1); idx.write_text(txt, encoding="utf-8"); log(f"índice `{rel(root, idx)}`: +{len(novas)} projeto(s)")

def chave(o): return f"{o['tipo']}|{o.get('de','')}|{o.get('para','')}"

def executar(root: Path, plano: dict):
    v = None; pj = sistema(root) / "migracao" / "aplicado.json"; feitos = ler_json(pj, {}) or {}
    origens = set()
    for o in plano["ops"]:
        t = o["tipo"]; st = o.get("status", "pronto")
        if st == "pendente": log(f"PENDENTE (sem resposta) — não executado: {o['id']} `{o.get('de','')}`"); continue
        if st == "manter": log(f"mantido no lugar: `{o.get('de','')}`"); continue
        if t in ("mover", "mover_resto", "anexar") and chave(o) in feitos: continue   # já executada em rodada anterior
        if o.get("de"): origens.add(o["de"])
        if t == "mkdir": mkdir_exato(root, o["para"])
        elif t == "mover": mover(root, o["de"], o["para"], o.get("mesclar", False), o.get("caso_plugin", False))
        elif t == "mover_resto": mover_resto(root, o["de"], o["para"])
        elif t == "anexar": anexar(root, o["de"], o["para"])
        elif t == "state_cliente": state_cliente(root, o["para"], o["nome"])
        elif t == "state_projeto": state_projeto(root, o["para"], o["cliente"], o["tipo_projeto"], o["area"], o["projeto"], o.get("tier", "T2"), o.get("state_antigo"))
        elif t == "registrar_area": registrar_area(root, o["area"], "migracao")
        elif t == "templates": copiar_templates(root)
        elif t == "copiar":
            dst = root / o["para"]
            if not (o.get("se_ausente") and dst.exists()): shutil.copy(TEMPLATES / o["template"], dst); log(f"copiado `{o['para']}`")
        elif t == "render":
            if v is None: v = vars_render(root)
            render_op(root, o["template"], o["para"], o.get("se_ausente", False), v)
        elif t == "versao": (root / o["para"]).write_text(o["valor"] + "\n", encoding="utf-8")
        if t in ("mover", "mover_resto", "anexar"): feitos[chave(o)] = agora()
    gravar_json(pj, feitos)
    # varredura: pastas antigas que ficaram vazias (só ancestrais de origens do plano)
    esp = espec()
    for de in sorted(origens, key=lambda x: -len(x)):
        p = (root / de).parent
        while p != root and p.exists():
            if p.name == "casos" or eh_motor(p, esp) or p.name in esp["raiz"]["pastas"]: break   # motor e esqueleto ficam
            try:
                if any(f.name not in IGN for f in p.iterdir()): break
                for f in p.iterdir(): f.unlink(missing_ok=True)
                p.rmdir(); log(f"pasta vazia removida `{rel(root, p)}`")
            except Exception: break
            p = p.parent
    reindexar(root)

def arquivos_perdidos(root: Path) -> list:
    """Cada arquivo do censo (nome + tamanho) precisa existir em algum lugar da pasta (moveu, não sumiu)."""
    censo = ler_json(root / "_sistema" / "censo.json", {}) or {}
    atuais = {}
    for f in root.rglob("*"):
        if f.is_file() and f.name not in IGN and "_sistema" not in f.parts:
            k = assinatura(f); atuais[k] = atuais.get(k, 0) + 1
    perdidos = []
    for item in censo.get("arquivos_lista", []):
        relp, k = item[0], item[2] if len(item) > 2 else f"{Path(item[0]).name}:{item[1]}"
        if atuais.get(k, 0) > 0: atuais[k] -= 1
        else: perdidos.append(relp)
    return perdidos

def atualizar_roteamento(root: Path, v=None):
    """Regera só a tabela entre <!-- roteamento:inicio --> e <!-- roteamento:fim --> de identidade/05 (o resto é do advogado)."""
    p = root / "identidade" / "05-ROTEAMENTO-PLUGINS.md"
    if not p.exists(): return
    v = v or vars_render(root); t = ler(p); ini, fim = "<!-- roteamento:inicio", "<!-- roteamento:fim -->"
    if ini not in t or fim not in t: return
    a = t.index(ini); a = t.index("\n", a) + 1; b = t.index(fim)
    novo = "| Área | Plugin instalado | Skill-mestre | Observação |\n|---|---|---|---|\n" + v["TABELA_ROTEAMENTO"] + "\n"
    if t[a:b] != novo: p.write_text(t[:a] + novo + t[b:], encoding="utf-8"); log("tabela de roteamento atualizada em identidade/05")

def so_render(root: Path, forcar=False):
    """Setup: gera tudo. Depois: identidade/ e knowledge/README são do advogado (só se ausentes); CLAUDE.md, _sistema/README e a tabela de 05 são do plugin."""
    v = vars_render(root)
    render_op(root, "CLAUDE.md", "CLAUDE.md", v=v); render_op(root, "TASKS.md", "TASKS.md", se_ausente=True, v=v)
    for f in espec()["identidade"]["arquivos"]:
        render_op(root, f"identidade/{f}", f"identidade/{f}", se_ausente=not forcar, v=v)
    atualizar_roteamento(root, v)
    render_op(root, "knowledge/README.md", "knowledge/README.md", se_ausente=True, v=v)
    render_op(root, "_sistema/README.md", "_sistema/README.md", v=v)
    (root / "_sistema" / "versao").write_text(versao_plugin() + "\n", encoding="utf-8")

def novo(root: Path):
    for d in espec()["raiz"]["pastas"] + ["_legado"]: (root / d).mkdir(exist_ok=True)
    copiar_templates(root)
    if not (root / ".gitignore").exists(): shutil.copy(TEMPLATES / "gitignore", root / ".gitignore")
    so_render(root)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raiz"); ap.add_argument("--so-render", action="store_true"); ap.add_argument("--novo", action="store_true")
    ap.add_argument("--forcar", action="store_true", help="com --so-render: regera também identidade/ (sobrescreve edições manuais!)")
    ap.add_argument("--roteamento", action="store_true", help="só a tabela de identidade/05 (área nova / plugin novo)")
    a = ap.parse_args(); root = raiz(a.raiz); sistema(root)
    if a.roteamento: atualizar_roteamento(root); return
    if a.so_render: so_render(root, a.forcar)
    elif a.novo: novo(root)
    else:
        plano = ler_json(root / "_sistema" / "migracao" / "plano.json")
        if not plano: print("Sem plano — rode censo.py e planejar.py."); sys.exit(2)
        if not plano.get("aprovado"): print("Plano NÃO aprovado — responda as perguntas e rode planejar.py --aprovar."); sys.exit(1)
        executar(root, plano)
        perdidos = arquivos_perdidos(root)
        log(f"prova de integridade: {len(perdidos)} arquivo(s) original(is) não reencontrado(s)" + (" — " + "; ".join(perdidos[:5]) if perdidos else " ✓"))
    mig = sistema(root) / "migracao"; mig.mkdir(exist_ok=True)
    with (mig / "MIGRACAO.md").open("a", encoding="utf-8") as fh:
        fh.write(f"\n## Rodada {agora()} · plugin {versao_plugin()}\n" + "\n".join(LOG) + "\n")
    print(f"Log: _sistema/migracao/MIGRACAO.md ({len(LOG)} linhas)")

if __name__ == "__main__":
    main()
