---
name: entregar
description: Fecha um entregável na bancada COWORK-OS - confere o selo de Thor no STATE.md, arquiva a versão anterior em historico/ (regra 10 sem git), grava a versão final na raiz do projeto, atualiza Fase/Próximo passo/Histórico e o índice do cliente, e diz o que o advogado faz fora da bancada. Use quando o advogado disser /entregar, "fecha essa peça", "gera a versão final", "entrega o contrato".
---

# /entregar <caminho do projeto> [arquivo]

1. Leia o `STATE.md` do projeto. Sem `Thor: ok` em `## Gates` (T≥1) → pare e acione `/zeus` (Thor); não entregue.
2. **Versão anterior:** se já existe arquivo com o mesmo nome na raiz do projeto, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/historico.py" <arquivo>` **antes** de gravar a nova. A raiz só tem a vigente.
3. **Formato:** peça processual e contrato saem em `.docx` (se houver `timbrado/`, use o modelo de lá; senão, o `.docx` simples) com o `.md` equivalente ao lado; e-mail/WhatsApp em `.md`. Nome sem espaço, sem acento, com data: `contestacao-banco-x-2026-09-18.docx`. Rascunho que estava em `<plugin>/casos/` vem para a raiz do projeto; o que fica lá não pode ter dado nominativo.
4. Atualize `STATE.md`: `## Fase atual` (marque a etapa) · `## Próximo passo` (nunca vazio — se acabou: "arquivar após protocolo/assinatura") · `## Histórico` (data · entregue · arquivo). Atualize a linha do projeto em `clientes/<x>/STATE.md`. Protocolado? `<peça>-protocolo.pdf` ao lado e data/número no Histórico.
5. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint.py" --cliente <slug>` sem erro.
6. Diga em 4 linhas: caminho do arquivo · o que Thor selou · próximo passo · o que ele faz fora da bancada (protocolar / enviar ao cliente / assinar / lançar prazo no sistema de processos).

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
