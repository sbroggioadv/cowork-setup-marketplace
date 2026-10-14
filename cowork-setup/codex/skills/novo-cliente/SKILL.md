---
name: novo-cliente
description: "Cria a pasta canônica de um cliente novo na bancada (clientes/<slug>/ com STATE.md índice, cadastro/CADASTRO.md e cadastro/documentos/). Use quando o advogado disser $novo-cliente, \"abre pasta do cliente X\", \"cadastra o cliente X\", \"cria uma pasta para o cliente X\", ou quando Zeus encontrar cliente sem pasta."
metadata:
  short-description: "Cria a pasta canônica de um cliente novo na bancada (clientes/<slug>/ com STATE.md índice, cadastro/CADASTRO.md e cad…"
---

> **Codex.** Versão para o Codex da skill `novo-cliente` do plugin `cowork-setup` v1.1.4 — gerada do mesmo texto da versão do Claude (não editar).
> - **`<plugin>`** = a pasta do plugin: `../../..` a partir da pasta deste SKILL.md (a que tem `scripts/`, `espec/` e `templates/`). Use o caminho absoluto dela nos comandos abaixo e rode-os **a partir da raiz da pasta COWORK-OS**.
> - Comandos da bancada no Codex começam com `$` (`$zeus` · nome completo `$cowork-setup:zeus`); skill de outro plugin: `$<plugin>:<skill>`. Textos da bancada (CLAUDE.md = AGENTS.md, identidade/) escrevem `/x`: leia como `$x`.
> - "Agente `X`" = o subagente `X` desta bancada (`.codex/agents/X.toml`). Ao chamá-lo, passe no pedido o caminho absoluto de `<plugin>` — ele não o recebe sozinho. Sem `.codex/agents/` na pasta (ou o setup avisou que não conseguiu gravá-la — o sandbox do Codex protege `.codex/`): rode `python3 "<plugin>/scripts/aplicar.py" --agentes-codex` **pedindo execução fora do sandbox** (o Codex mostra o pedido ao advogado; explique em uma linha que é só para gravar os 5 agentes da bancada) e depois abra uma sessão nova; a pasta precisa estar marcada como confiável no Codex para ele ler os agentes.

# $novo-cliente "<Nome do Cliente>"

```bash
python3 "<plugin>/scripts/novo_cliente.py" "<Nome do Cliente>"
```
Cria `clientes/<slug>/` (minúsculas, hífen, sem acento) com `STATE.md` (índice) + `cadastro/CADASTRO.md` + `cadastro/documentos/`. Nunca crie a pasta à mão. Depois: preencha o `CADASTRO.md` com o que o advogado já tem (razão social, CNPJ/CPF, representante, contato, honorários, procuração) — pergunte o que faltar para T≥2; documentos que valem para o cliente inteiro (cartão CNPJ, contrato social, procuração geral) vão em `cadastro/documentos/`. Caso concreto → `$novo-projeto`.

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
