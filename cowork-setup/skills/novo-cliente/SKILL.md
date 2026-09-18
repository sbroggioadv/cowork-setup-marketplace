---
name: novo-cliente
description: Cria a pasta canônica de um cliente novo na bancada (clientes/<slug>/ com STATE.md índice, cadastro/CADASTRO.md e cadastro/documentos/). Use quando o advogado disser /novo-cliente, "abre pasta do cliente X", "cadastra o cliente X", "cria uma pasta para o cliente X", ou quando Zeus encontrar cliente sem pasta.
---

# /novo-cliente "<Nome do Cliente>"

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/novo_cliente.py" "<Nome do Cliente>"
```
Cria `clientes/<slug>/` (minúsculas, hífen, sem acento) com `STATE.md` (índice) + `cadastro/CADASTRO.md` + `cadastro/documentos/`. Nunca crie a pasta à mão. Depois: preencha o `CADASTRO.md` com o que o advogado já tem (razão social, CNPJ/CPF, representante, contato, honorários, procuração) — pergunte o que faltar para T≥2; documentos que valem para o cliente inteiro (cartão CNPJ, contrato social, procuração geral) vão em `cadastro/documentos/`. Caso concreto → `/novo-projeto`.

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
