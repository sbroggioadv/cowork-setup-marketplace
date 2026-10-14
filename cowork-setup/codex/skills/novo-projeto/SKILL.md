---
name: novo-projeto
description: "Cria a pasta de um projeto (contencioso, consultivo ou holding) dentro do cliente, com STATE.md do template (e FICHA.md em T≥2), entrada/ e pesquisas/, registro no índice do cliente e da área (área nova é registrada e entra na tabela de roteamento). Use quando o advogado disser $novo-projeto, \"abre o caso X do cliente Y\", \"novo contrato para Y\", \"cria a pasta do processo\", \"inicia a holding de Z\", ou quando Zeus precisar de pasta de projeto."
metadata:
  short-description: "Cria a pasta de um projeto (contencioso, consultivo ou holding) dentro do cliente, com STATE.md do template (e FICHA.…"
---

> **Codex.** Versão para o Codex da skill `novo-projeto` do plugin `cowork-setup` v1.1.4 — gerada do mesmo texto da versão do Claude (não editar).
> - **`<plugin>`** = a pasta do plugin: `../../..` a partir da pasta deste SKILL.md (a que tem `scripts/`, `espec/` e `templates/`). Use o caminho absoluto dela nos comandos abaixo e rode-os **a partir da raiz da pasta COWORK-OS**.
> - Comandos da bancada no Codex começam com `$` (`$zeus` · nome completo `$cowork-setup:zeus`); skill de outro plugin: `$<plugin>:<skill>`. Textos da bancada (CLAUDE.md = AGENTS.md, identidade/) escrevem `/x`: leia como `$x`.
> - "Agente `X`" = o subagente `X` desta bancada (`.codex/agents/X.toml`). Ao chamá-lo, passe no pedido o caminho absoluto de `<plugin>` — ele não o recebe sozinho. Sem `.codex/agents/` na pasta (ou o setup avisou que não conseguiu gravá-la — o sandbox do Codex protege `.codex/`): rode `python3 "<plugin>/scripts/aplicar.py" --agentes-codex` **pedindo execução fora do sandbox** (o Codex mostra o pedido ao advogado; explique em uma linha que é só para gravar os 5 agentes da bancada) e depois abra uma sessão nova; a pasta precisa estar marcada como confiável no Codex para ele ler os agentes.

# $novo-projeto <tipo> <area> "<Cliente>" "<Projeto>"

- **contencioso:** `<Projeto>` = "Adversário nº-do-processo" (ex.: `"Banco X 0001234-56.2026.8.26.0576"`).
- **consultivo:** `<Projeto>` = nome do documento (ex.: `"Contrato de Parceria Comercial"`).
- **holding:** área é ignorada (`-`); cria `clientes/<cliente>/holding/` (nomenclatura livre dentro, espelho do Drive se houver).

```bash
python3 "<plugin>/scripts/novo_projeto.py" <tipo> <area> "<Cliente>" "<Projeto>" --tier T2
```
Área: use a registrada (`_sistema/areas.json`, tabela em `identidade/05`) ou crie uma nova em slug (`penal-empresarial`, `marcas-inpi`) — o script registra e atualiza a tabela. O cliente precisa existir (`$novo-cliente` antes). Todo projeto nasce com `STATE.md` + `entrada/` + `pesquisas/` (+ `FICHA.md` em T≥2, que Gandalf preenche). `entrada/` recebe tudo que vem de fora; a raiz recebe o que o escritório produz; `historico/` recebe versão substituída. Nenhuma pasta com prefixo numérico. Depois: T≥2 → `$gandalf`.

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
