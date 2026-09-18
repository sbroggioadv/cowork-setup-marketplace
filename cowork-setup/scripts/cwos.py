"""Biblioteca comum do plugin cowork-setup (importada pelos demais scripts).
Python 3 puro, sem dependência externa. Nunca usa caminho absoluto fixo: a raiz da bancada é o diretório
de trabalho (ou --raiz / COWORK_OS_RAIZ); a raiz do plugin é descoberta a partir deste arquivo."""
from __future__ import annotations
import json, os, re, sys, unicodedata, datetime
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
ESPEC_DIR = PLUGIN / "espec"
TEMPLATES = PLUGIN / "templates"

def versao_plugin() -> str:
    return (ESPEC_DIR / "VERSAO").read_text(encoding="utf-8").strip()

def espec() -> dict:
    return json.loads((ESPEC_DIR / "estrutura.json").read_text(encoding="utf-8"))

def areas_espec() -> dict:
    return json.loads((ESPEC_DIR / "areas.json").read_text(encoding="utf-8"))

def raiz(arg: str | None = None) -> Path:
    """Raiz da bancada: --raiz > $COWORK_OS_RAIZ > $CLAUDE_PROJECT_DIR > cwd."""
    for cand in (arg, os.environ.get("COWORK_OS_RAIZ"), os.environ.get("CLAUDE_PROJECT_DIR"), os.getcwd()):
        if cand:
            return Path(cand).expanduser().resolve()
    return Path.cwd().resolve()

def sistema(root: Path) -> Path:
    d = root / "_sistema"; d.mkdir(exist_ok=True); return d

def hoje() -> str:
    return datetime.date.today().isoformat()

def agora() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def slug(name: str) -> str:
    """'Clínica Mansur Jacob' -> 'clinica-mansur-jacob'. Mantém '_' inicial (pastas de sistema)."""
    lead = "_" if name.startswith("_") else ""
    s = unicodedata.normalize("NFKD", name.lstrip("_")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9.\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return lead + s

def ler_json(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def gravar_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def ler(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

def render(texto: str, vars: dict) -> str:
    """Substitui {{CHAVE}}; chave ausente fica como está (a auditoria acusa)."""
    return PLACEHOLDER.sub(lambda m: str(vars.get(m.group(1), m.group(0))), texto)

def template(rel: str) -> str:
    return (TEMPLATES / rel).read_text(encoding="utf-8")

def template_bancada(root: Path, nome: str) -> str:
    """Template de STATE/FICHA/CADASTRO: o da bancada (knowledge/templates) se existir, senão o do plugin."""
    p = root / "knowledge" / "templates" / nome
    return p.read_text(encoding="utf-8") if p.exists() else template("knowledge/templates/" + nome)

def area_por_nome(nome: str, root: Path | None = None) -> str | None:
    """'Cível' -> 'civel'. Consulta a lista do plugin + a lista local da bancada (_sistema/areas.json)."""
    n = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower().strip()
    tabelas = [areas_espec().get("areas", {})]
    if root is not None:
        local = ler_json(root / "_sistema" / "areas.json", {}) or {}
        tabelas.append(local.get("areas", {}))
    for tab in tabelas:
        for a, info in tab.items():
            nomes = [a] + [unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower() for x in info.get("nomes", [])]
            if n in nomes or slug(nome) == a:
                return a
    return None

def registrar_area(root: Path, area: str, origem: str = "novo-projeto") -> bool:
    """Registra a área em _sistema/areas.json. Devolve True se era nova (quem chama atualiza a tabela de roteamento)."""
    p = root / "_sistema" / "areas.json"
    local = ler_json(p, {"areas": {}}) or {"areas": {}}
    local.setdefault("areas", {})
    if area in local["areas"]: return False
    local["areas"][area] = {"nomes": [area], "registrada_em": hoje(), "por": origem}
    gravar_json(p, local); return True

def proximo_passo(state_md: Path) -> str:
    linhas = ler(state_md).splitlines()
    for i, l in enumerate(linhas):
        t = l.strip().lower()
        if t.startswith("## próximo passo") or t.startswith("## proximo passo"):
            for m in linhas[i + 1:i + 4]:
                if m.strip() and not m.startswith("#"):
                    return m.strip()
            return "(vazio)"
    return "(sem seção)"

def tier_de(state_md: Path) -> str:
    m = re.search(r"Tier:\s*\**(T[0-3])", ler(state_md))
    return m.group(1) if m else "?"

def eh_motor(d: Path, esp: dict | None = None) -> bool:
    esp = esp or espec()
    if not d.is_dir():
        return False
    if d.name in esp["motores"]["conhecidos"]:
        return True
    return any((d / m).exists() for m in esp["motores"]["marcadores"])

def cru(state_md: Path) -> bool:
    """STATE ainda com texto do template (nunca preenchido)."""
    t = ler(state_md)
    return ("1 linha, SEMPRE preenchida" in t) or ("<Cliente>" in t) or ("O que é, em 3 linhas" in t)

def rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)

def assinatura(f: Path) -> str:
    """Identidade do conteúdo (md5) — sobrevive a renomeação. Arquivo > 64 MB usa nome+tamanho."""
    import hashlib
    try:
        st = f.stat()
        if st.st_size > 64 * 1024 * 1024: return f"{f.name}:{st.st_size}"
        h = hashlib.md5()
        with f.open("rb") as fh:
            for bloco in iter(lambda: fh.read(1 << 20), b""): h.update(bloco)
        return h.hexdigest()
    except Exception:
        return f"{f.name}:?"

def contar_arquivos(d: Path, ignorar=(".DS_Store",)) -> int:
    return sum(1 for f in d.rglob("*") if f.is_file() and f.name not in ignorar and "__pycache__" not in f.parts)
