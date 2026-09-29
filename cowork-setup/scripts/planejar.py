#!/usr/bin/env python3
"""F2 — Plano: censo × espec → _sistema/migracao/plano.json + PLANO.md (dry-run). NÃO move nada.
Uso:
  python3 planejar.py [--raiz X]                 gera/regenera o plano (mantém respostas já dadas)
  python3 planejar.py --responder q-03 "civel"   registra a resposta de uma pergunta e regenera
  python3 planejar.py --aprovar                  marca aprovado (exige todas as perguntas respondidas)
  python3 planejar.py --aprovar --resto-legado   perguntas sem resposta vão para _legado/triagem/
Perguntas têm id estável (derivado do caminho) — sobrevivem à regeneração."""
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

NUM_PROC = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

def sugerir_area(nome: str, root: Path):
    a = area_por_nome(nome, root)
    if a: return a
    n = slug(nome)
    for area, info in areas_espec()["areas"].items():
        for alias in [area] + info.get("nomes", []):
            if slug(alias) and slug(alias) in n.split("-"): return area
    return None

class Plano:
    def __init__(self, root, censo, anterior):
        self.root, self.censo = root, censo
        self.ops, self.perguntas = [], []
        self.respostas = {q["id"]: q.get("resposta") for q in (anterior or {}).get("perguntas", []) if q.get("resposta")}
        self.n = 0
    def op(self, tipo, **kw):
        self.n += 1; o = {"id": f"op-{self.n:03d}", "tipo": tipo}; o.update(kw); self.ops.append(o); return o
    def pergunta(self, chave, sobre, texto, sugestao, opcoes=None):
        qid = "q:" + chave
        q = {"id": qid, "sobre": sobre, "pergunta": texto, "sugestao": sugestao, "opcoes": opcoes or [], "resposta": self.respostas.get(qid)}
        self.perguntas.append(q); return q
    def mover(self, de, para, motivo, pergunta=None):
        o = self.op("mover", de=de, para=para, motivo=motivo)
        if pergunta: o["depende"] = pergunta["id"]
        return o

def gerar(root: Path, censo: dict, anterior: dict | None) -> dict:
    esp = espec(); P = Plano(root, censo, anterior); hoje_ = hoje()
    lg = esp["legado_antigo"]; rp = {slug(k): v for k, v in lg["raiz_pastas"].items()}
    areas_detectadas = set()
    # --- esqueleto novo
    for d in esp["raiz"]["pastas"] + ["_legado"]:
        P.op("mkdir", para=d)
    # --- identidade / arquivos de raiz antigos
    for nome in censo["identidade_legado"]:
        alvo = {"claude.md": "CLAUDE-cowork.md", "cloud.md": "CLAUDE-cowork.md", "persona.md": "PERSONA-cowork.md",
                "memory.md": "MEMORY-cowork.md", "tasks.md": "TASKS-cowork.md"}.get(nome.lower(), nome)
        P.mover(nome, f"_legado/{alvo}", "arquivo de identidade antigo: conteúdo é importado para identidade/ na entrevista; original preservado")
    # --- pastas de raiz antigas
    for item in censo["raiz_itens"]:
        if item.get("classe") != "legado-pasta": continue
        dest = item["destino"]; nome = item["nome"]
        if dest == "clientes":
            for c in censo["clientes_legado"]:
                planejar_cliente(P, c, nome, areas_detectadas, root, hoje_)
        elif dest == "knowledge":
            k = censo["knowledge_legado"]
            planejar_knowledge(P, nome, k["subpastas"], k.get("soltos", k.get("index", [])))
        elif dest == "identidade":
            P.mover(nome, "_legado/identidade-cowork", "identidade antiga preservada; a nova nasce da entrevista")
        elif dest == "timbrado":
            P.mover(nome, "timbrado", "modelos → timbrado/")
    # --- motores: casos com dado de cliente
    for m in censo["motores"]:
        area = area_por_nome(m["nome"], root) or {"direito-familia": "familia", "direito-medico": "medico", "marca-inpi": "marcas-inpi",
                                                 "tributario-societario": "tributario"}.get(m["nome"], m["nome"])
        for c in m["casos"]:
            if c["arquivos"] == 0: continue
            cli = proximo_cliente(c["slug"], censo)
            sug = f"clientes/{cli or c['slug']}/contencioso/{area}/{c['slug']}"
            q = P.pergunta(f"{m['nome']}/casos/{c['pasta']}", f"{m['nome']}/casos/{c['pasta']}",
                           f"Este caso do plugin {m['nome']} é de qual cliente e vai para onde? (o motor não guarda dado nominativo)",
                           sug, ["<caminho clientes/…>", "manter", "legado"])
            oo = P.mover(f"{m['nome']}/casos/{c['pasta']}", "{Q}", "dado de cliente sai do motor; CASO.md/MEMORY.md viram historico/ e _memoria-cowork.md do projeto", q); oo["caso_plugin"] = True; oo["mesclar"] = True
    # --- desconhecidos na raiz
    for d in censo["desconhecidos"]:
        nome = d.rstrip("/")
        q = P.pergunta(nome, nome, "Não reconheci este item. Para onde vai?", f"_legado/triagem/{nome}",
                       ["<caminho>", "legado", "manter"])
        P.mover(nome, "{Q}", "item não reconhecido", q)
    # --- renders e templates
    for t in ("CLAUDE.md", "TASKS.md"):
        P.op("render", template=t, para=t, motivo="gerado do perfil (entrevista)")
    for f in esp["identidade"]["arquivos"]:
        P.op("render", template=f"identidade/{f}", para=f"identidade/{f}", motivo="gerado do perfil; conteúdo do escritório")
    P.op("render", template="_sistema/README.md", para="_sistema/README.md", motivo="explica a pasta do plugin")
    P.op("copiar", template="gitignore", para=".gitignore", motivo="dormente — só age se um dia virar git", se_ausente=True)
    P.op("templates", para="_sistema/templates", motivo="modelos da mecânica: STATE / STATE-cliente / FICHA / CADASTRO (do plugin)")
    P.op("knowledge", para="knowledge", motivo="modelos/ (organiza por área o que veio da base antiga) · jurisprudencia/ · doutrina/ · legislacao/ · índices")
    P.op("plugins", para="_sistema/plugins.json", motivo="acopla os plugins instalados (nenhum é obrigatório)")
    for a in sorted(areas_detectadas):
        P.op("registrar_area", area=a)
    P.op("versao", para="_sistema/versao", valor=versao_plugin())
    pend = [q for q in P.perguntas if not q.get("resposta")]
    return {"data": agora(), "modo": censo["modo"], "versao_plugin": versao_plugin(), "aprovado": False,
            "arquivos_antes": censo["arquivos_total"], "perguntas": P.perguntas, "pendentes": len(pend), "ops": P.ops}

INDICES_ANTIGOS = ("readme", "index", "indice", "claude", "_kb", "leia-me", "leiame")

def _sem(s: str, prefixos: tuple) -> str:
    for pre in prefixos:
        if s.startswith(pre) and len(s) > len(pre): return s[len(pre):]
    return s

def destino_knowledge(sub: str) -> tuple[str, str]:
    """(destino, motivo) de uma pasta que estava na raiz da base de conhecimento antiga."""
    s = slug_sem_numero(sub)
    if s in ("templates", "template"): return f"_legado/knowledge-templates-1.0", "modelos da mecânica da 1.0 (STATE/FICHA/CADASTRO): agora vivem em _sistema/templates/ (do plugin); o que você personalizou fica aqui para comparar"
    if "jurisprud" in s or s in ("acordaos", "sentencas", "decisoes", "precedentes"):
        return f"knowledge/jurisprudencia/proprias/{_sem(s, ('jurisprudencia-', 'jurisprudencias-'))}", "jurisprudência do escritório → jurisprudencia/proprias/ (nível 1 se tiver a cópia dos autos)"
    if "doutrin" in s: return f"knowledge/doutrina/proprias/{_sem(s, ('doutrina-', 'doutrinas-'))}", "doutrina do escritório → doutrina/proprias/"
    if "legisla" in s or s in ("normas", "leis", "codigos"):
        return f"knowledge/legislacao/{_sem(s, ('legislacao-', 'legislacoes-'))}", "normas → legislacao/<tema>/"
    if "sumula" in s: return f"knowledge/jurisprudencia/proprias/{s}", "súmulas guardadas pelo escritório (o repertório oficial já vem no plugin)"
    return f"knowledge/modelos/_novos/{sub}", "modelos → knowledge/modelos/_novos/: o plugin organiza por área e renomeia em minúsculas logo depois de mover"

def planejar_knowledge(P, base: str, subpastas: list, soltos: list, pular=()):
    for sub in subpastas:
        if sub in pular: continue
        d, motivo = destino_knowledge(sub)
        o = P.mover(f"{base}/{sub}", d, motivo); o["mesclar"] = True
    for f in soltos:
        if f in pular: continue
        if slug(Path(f).stem).startswith(INDICES_ANTIGOS):
            P.mover(f"{base}/{f}", f"_legado/knowledge-antigo/{f}", "índice/regras da base antiga preservados; o índice novo é gerado (knowledge/README.md e modelos/INDEX.md)")
        else:
            P.mover(f"{base}/{f}", f"knowledge/modelos/_novos/{f}", "modelo solto → organizado por área logo depois de mover")

def gerar_atualizacao(root: Path, censo: dict, anterior: dict | None) -> dict:
    """Bancada JÁ organizada por versão anterior (Trilha D): só a mecânica muda — identidade/, clientes/ e motores ficam como estão."""
    P = Plano(root, censo, anterior); esp = espec()
    k = censo.get("knowledge_atual") or {}
    novas = set(esp["knowledge"]["pastas"])
    planejar_knowledge(P, "knowledge", [s for s in k.get("subpastas", []) if s not in novas],
                       [f for f in k.get("soltos", []) if f != "README.md"])
    if k.get("readme_antigo"):
        P.mover("knowledge/README.md", "_legado/knowledge-antigo/README-1.0.md", "o README da 1.0 era um índice escrito à mão; o novo é gerado pelo plugin (o antigo fica para consulta)")
    P.op("templates", para="_sistema/templates", motivo="modelos da mecânica passam de knowledge/templates/ para _sistema/templates/ (do plugin)")
    P.op("knowledge", para="knowledge", motivo="modelos/ organizado por área + jurisprudencia/ · doutrina/ · legislacao/ + índices")
    P.op("render", template="CLAUDE.md", para="CLAUDE.md", motivo="constituição da bancada (do plugin) na versão nova")
    P.op("render", template="_sistema/README.md", para="_sistema/README.md", motivo="explica a pasta do plugin")
    P.op("mapa", para="identidade/04-MAPA-DE-CONTEXTO.md", motivo="só as 2 linhas que a 1.0 escreveu sobre knowledge/ (o resto do arquivo é seu)")
    P.op("plugins", para="_sistema/plugins.json", motivo="acopla os plugins instalados (nenhum é obrigatório)")
    P.op("roteamento", para="identidade/05-ROTEAMENTO-PLUGINS.md", motivo="só a tabela entre os marcadores (o resto do arquivo é seu)")
    P.op("versao", para="_sistema/versao", valor=versao_plugin())
    pend = [q for q in P.perguntas if not q.get("resposta")]
    return {"data": agora(), "modo": "atualizar", "de_versao": censo.get("versao_instalada"), "versao_plugin": versao_plugin(), "aprovado": False,
            "arquivos_antes": censo["arquivos_total"], "perguntas": P.perguntas, "pendentes": len(pend), "ops": P.ops}

def proximo_cliente(s: str, censo: dict):
    cands = [c["slug"] for c in censo["clientes_legado"]] + [c["slug"] for c in censo["clientes_novo"]]
    for c in cands:
        if c == s or c.startswith(s) or s.startswith(c): return c
    return None

def planejar_cliente(P: Plano, c: dict, pasta_clientes: str, areas: set, root: Path, hoje_: str):
    base = f"clientes/{c['slug']}"; orig = f"{pasta_clientes}/{c['pasta']}"
    P.op("mkdir", para=base); P.op("mkdir", para=f"{base}/cadastro/documentos")
    P.op("state_cliente", para=base, nome=c["nome"], motivo="STATE.md (índice) + cadastro/CADASTRO.md com o que se vê")
    for f in c["arquivos_soltos"]:
        P.mover(f"{orig}/{f}", f"{base}/cadastro/documentos/{f}", "arquivo solto do cliente → cadastro/documentos/")
    for k in ("state", "memory"):
        if c.get(k):
            P.op("anexar", de=f"{orig}/{c[k]}", para=f"{base}/_memoria-cowork.md", motivo="STATE/memory do nível do cliente → memória a absorver no índice (lint avisa LEGADO)")
    for t in c["tipos"]:
        tipo = t["tipo"]; torig = f"{orig}/{t['pasta']}"
        if tipo == "holding":
            P.mover(torig, f"{base}/holding", "holding do cliente → clientes/<x>/holding/ (nomenclatura livre, espelho do Drive)")
            P.op("state_projeto", para=f"{base}/holding", cliente=c["nome"], tipo_projeto="holding", area="holding", projeto=f"Holding {c['nome']}", tier="T3", motivo="STATE.md + FICHA.md da holding",
                 state_antigo=(f"{base}/holding/{t['projetos'][0]['detalhe']['state']}" if t["projetos"] and t["projetos"][0]["detalhe"]["state"] else None))
            areas.add("holding"); continue
        for p in t["projetos"]:
            porig = f"{torig}/{p['pasta']}"; det = p["detalhe"]
            # área
            if p["area_conhecida"]:
                area = p["area"]; qa = None
            else:
                sug = sugerir_area(p["pasta"].split("/")[0], root) or sugerir_area(det["pasta"], root) or "empresarial"
                qa = P.pergunta(f"area:{porig}", porig, "Qual a área deste projeto? (slug: civel, trabalhista, familia, tributario, empresarial…)", sug)
                area = "{QA}"
            if qa is None: areas.add(area)
            # nome do projeto
            if p.get("nivel") == 1 and p["area_conhecida"]:
                # a pasta da área É o caso: precisa de nome (adversário + nº processo)
                txt = ler(root / porig / det["state"]) if det["state"] else ""
                m = NUM_PROC.search(txt); sug = f"caso-{m.group(0)}" if m else f"caso-{area}-1"
                qn = P.pergunta(f"nome:{porig}", porig, "Esta pasta de área é um caso só. Nome da pasta do projeto (adversário + nº do processo, em slug)?", sug)
                proj = "{QN}"
            else:
                qn = None; proj = det["slug"]
            dest = f"{base}/{tipo}/{area}/{proj}"
            o = P.op("mkdir", para=dest); deps = [q["id"] for q in (qa, qn) if q]
            if deps: o["depende"] = deps
            # conteúdo
            for sp in det["subpastas"]:
                sdest = sp["destino"]
                if sdest is None: sdest = slug(sp["nome"])
                para = dest if sdest == "." else f"{dest}/{sdest}"
                oo = P.mover(f"{porig}/{sp['nome']}", para, "subpasta do caso → anatomia (entrada/ · raiz = vigente · pesquisas/)")
                oo["mesclar"] = True
                if deps: oo["depende"] = deps
            if det["state"]:
                oo = P.mover(f"{porig}/{det['state']}", f"{dest}/historico/{hoje_}-STATE-cowork.md", "STATE antigo preservado em historico/; o novo nasce do template")
                if deps: oo["depende"] = deps
            if det["memory"]:
                oo = P.op("anexar", de=f"{porig}/{det['memory']}", para=f"{dest}/_memoria-cowork.md", motivo="memory.md do caso → a absorver em Decisões fixadas (lint avisa LEGADO)")
                if deps: oo["depende"] = deps
            if det["claude"]:
                oo = P.op("anexar", de=f"{porig}/{det['claude']}", para=f"{dest}/_memoria-cowork.md", motivo="CLAUDE.md do caso → a absorver")
                if deps: oo["depende"] = deps
            oo = P.op("mover_resto", de=porig, para=dest, motivo="arquivos soltos do caso → raiz do projeto (vigente); versões antigas: /entregar leva a historico/")
            if deps: oo["depende"] = deps
            oo = P.op("state_projeto", para=dest, cliente=c["nome"], tipo_projeto=tipo, area=area, projeto=(proj if not qn else "{QN}"), tier="T2", motivo="STATE.md + FICHA.md do template; o STATE antigo fica em historico/",
                      state_antigo=(f"{dest}/historico/{hoje_}-STATE-cowork.md" if det["state"] else None))
            if deps: oo["depende"] = deps
        if t["arquivos_soltos"]:
            q = P.pergunta(f"soltos:{torig}", torig, f"Há {t['arquivos_soltos']} arquivo(s) solto(s) em {t['pasta']}/ (não estão em pasta de caso). Para onde vão?",
                           f"_legado/triagem/{torig}", ["<caminho clientes/…>", "legado"])
            P.op("mover_resto", de=torig, para="{Q}", motivo="arquivos soltos no nível do tipo", depende=q["id"])
    for o in c["outros"]:
        oorig = f"{orig}/{o['pasta']}"
        q = P.pergunta(f"outro:{oorig}", oorig, f"Pasta fora do padrão ({o['arquivos']} arquivos). Para onde vai? (cadastro/documentos, um projeto, ou legado)",
                       f"_legado/triagem/{oorig}", ["<caminho>", "legado", f"{base}/cadastro/documentos/{slug(o['pasta'])}"])
        P.mover(oorig, "{Q}", "pasta fora do padrão no cliente", q)

def resolver(plano: dict) -> dict:
    """Substitui {Q}/{QA}/{QN} pelas respostas; ops sem resposta ficam 'pendente'."""
    resp = {q["id"]: q.get("resposta") for q in plano["perguntas"]}
    for o in plano["ops"]:
        deps = o.get("depende"); deps = [deps] if isinstance(deps, str) else (deps or [])
        faltam = [d for d in deps if not resp.get(d)]
        o["status"] = "pendente" if faltam else "pronto"
        if faltam: continue
        for campo in ("de", "para", "area", "projeto", "state_antigo"):
            v = o.get(campo)
            if not isinstance(v, str): continue
            for d in deps:
                r = resp[d]
                if r == "legado": r = f"_legado/triagem/{o.get('de', o.get('para'))}"
                if r == "manter": o["status"] = "manter"; continue
                tag = "{QA}" if d.startswith("q:area:") else "{QN}" if d.startswith("q:nome:") else "{Q}"
                v = v.replace(tag, r)
            o[campo] = v
    return plano

def escrever_md(root: Path, plano: dict) -> None:
    L = [f"# PLANO DE ORGANIZAÇÃO — {root.name} · {plano['data']} · modo {plano['modo'].upper()}", "",
         f"> Nada foi movido ainda. Este é o de→para que o `/cowork-setup` vai executar depois que {'' if plano['aprovado'] else 'você '}aprovar.",
         f"> Arquivos hoje: **{plano['arquivos_antes']}**. Nada é apagado: o que não tem lugar vai para `_legado/triagem/`.", ""]
    pend = [q for q in plano["perguntas"] if not q.get("resposta")]
    if plano["perguntas"]:
        L += [f"## Perguntas ({len(pend)} pendente(s) de {len(plano['perguntas'])})", "", "| # | Sobre | Pergunta | Sugestão | Resposta |", "|---|---|---|---|---|"]
        for i, q in enumerate(plano["perguntas"], 1):
            L.append(f"| {i} | `{q['sobre']}` | {q['pergunta']} | `{q['sugestao']}` | {('**' + q['resposta'] + '**') if q.get('resposta') else '—'} |")
        L.append("")
    L += ["## De → Para", "", "| Op | Ação | De | Para | Motivo | Status |", "|---|---|---|---|---|---|"]
    for o in plano["ops"]:
        if o["tipo"] in ("mkdir", "versao", "registrar_area", "templates", "knowledge", "plugins", "mapa", "roteamento"): continue
        L.append(f"| {o['id']} | {o['tipo']} | `{o.get('de','')}` | `{o.get('para','')}` | {o.get('motivo','')} | {o.get('status','')} |")
    L += ["", "## O que será criado", ""]
    for o in plano["ops"]:
        if o["tipo"] == "mkdir": L.append(f"- pasta `{o['para']}/`")
        elif o["tipo"] == "state_cliente": L.append(f"- `{o['para']}/STATE.md` + `cadastro/CADASTRO.md` ({o['nome']})")
        elif o["tipo"] == "state_projeto": L.append(f"- `{o['para']}/STATE.md`" + (" + FICHA.md" if o.get("tier") in ("T2", "T3") else "") + f" ({o['tipo_projeto']}/{o['area']})")
        elif o["tipo"] == "registrar_area": L.append(f"- área registrada: `{o['area']}`")
        elif o["tipo"] == "templates": L.append(f"- `{o['para']}/` (4 modelos da mecânica)")
        elif o["tipo"] == "knowledge": L.append("- `knowledge/modelos/<area>/` (modelos canônicos organizados por área, com INDEX.md) · `jurisprudencia/` · `doutrina/` · `legislacao/`")
        elif o["tipo"] == "plugins": L.append("- `_sistema/plugins.json` (plugins acoplados — nenhum é obrigatório)")
        elif o["tipo"] == "versao": L.append(f"- `{o['para']}` = {o['valor']}")
    L += ["", f"**Aprovado:** {'sim' if plano['aprovado'] else 'não — responda as perguntas e aprove'}", ""]
    (sistema(root) / "migracao").mkdir(exist_ok=True)
    (root / "_sistema" / "migracao" / "PLANO.md").write_text("\n".join(L), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raiz"); ap.add_argument("--responder", nargs=2, metavar=("ID", "RESPOSTA"))
    ap.add_argument("--aprovar", action="store_true"); ap.add_argument("--resto-legado", action="store_true")
    a = ap.parse_args(); root = raiz(a.raiz)
    censo = ler_json(root / "_sistema" / "censo.json")
    if not censo: print("Sem _sistema/censo.json — rode censo.py primeiro."); sys.exit(2)
    pj = root / "_sistema" / "migracao" / "plano.json"; anterior = ler_json(pj)
    if a.responder and anterior:
        for q in anterior["perguntas"]:
            if q["id"] == a.responder[0] or q["id"].endswith(a.responder[0]) or str(anterior["perguntas"].index(q) + 1) == a.responder[0]:
                q["resposta"] = a.responder[1]
    plano = gerar_atualizacao(root, censo, anterior) if censo.get("modo") == "organizado" else gerar(root, censo, anterior)
    if a.aprovar:
        pend = [q for q in plano["perguntas"] if not q.get("resposta")]
        if pend and not a.resto_legado:
            print(f"Não aprovado: {len(pend)} pergunta(s) sem resposta. Responda (--responder) ou use --resto-legado."); sys.exit(1)
        for q in pend: q["resposta"] = "legado"
        plano["aprovado"] = True
    plano = resolver(plano); plano["pendentes"] = sum(1 for o in plano["ops"] if o.get("status") == "pendente")
    gravar_json(pj, plano); escrever_md(root, plano)
    print(f"Plano: {len(plano['ops'])} operações · {len(plano['perguntas'])} pergunta(s), {sum(1 for q in plano['perguntas'] if not q.get('resposta'))} pendente(s) · aprovado: {plano['aprovado']}")
    print("Leia: _sistema/migracao/PLANO.md")

if __name__ == "__main__":
    main()
