---
name: entregar
description: "Fecha um entregável na bancada COWORK-OS - confere o selo de Thor no STATE.md, arquiva a versão anterior em historico/ (regra 10 sem git), grava a versão final na raiz do projeto, atualiza Fase/Próximo passo/Histórico e o índice do cliente, e diz o que o advogado faz fora da bancada. Use quando o advogado disser $entregar, \"fecha essa peça\", \"gera a versão final\", \"entrega o contrato\"."
metadata:
  short-description: "Fecha um entregável na bancada COWORK-OS"
---

> **Codex.** Versão para o Codex da skill `entregar` do plugin `cowork-setup` v1.1.7 — gerada do mesmo texto da versão do Claude (não editar).
> - **`<plugin>`** = a pasta do plugin: `../../..` a partir da pasta deste SKILL.md (a que tem `scripts/`, `espec/` e `templates/`). Use o caminho absoluto dela nos comandos abaixo e rode-os **a partir da raiz da pasta COWORK-OS**.
> - Comandos da bancada no Codex começam com `$` (`$zeus` · nome completo `$cowork-setup:zeus`); skill de outro plugin: `$<plugin>:<skill>`. Textos da bancada (CLAUDE.md = AGENTS.md, identidade/) escrevem `/x`: leia como `$x`.
> - "Agente `X`" = o subagente `X` desta bancada (`.codex/agents/X.toml`). Ao chamá-lo, passe no pedido o caminho absoluto de `<plugin>` — ele não o recebe sozinho. Sem `.codex/agents/` na pasta (ou o setup avisou que não conseguiu gravá-la — o sandbox do Codex protege `.codex/`): rode `python3 "<plugin>/scripts/aplicar.py" --agentes-codex` **pedindo execução fora do sandbox** (o Codex mostra o pedido ao advogado; explique em uma linha que é só para gravar os 5 agentes da bancada) e depois abra uma sessão nova; a pasta precisa estar marcada como confiável no Codex para ele ler os agentes.

# $entregar <caminho do projeto> [arquivo]

1. Leia o `STATE.md` do projeto. Sem `Thor: ok` em `## Gates` (T≥1) → pare e acione `$zeus` (Corte + Thor); não entregue. O `CORTE-R1-R4-<data>.md` da rodada fica na raiz do projeto.
2. **Versão anterior:** se já existe arquivo com o mesmo nome na raiz do projeto, `python3 "<plugin>/scripts/historico.py" <arquivo>` **antes** de gravar a nova. A raiz só tem a vigente.
3. **Formato:** peça processual e contrato saem em `.docx` (se houver `timbrado/`, use o modelo de lá; senão, o `.docx` simples) com o `.md` equivalente ao lado; e-mail/WhatsApp em `.md`. Nome sem espaço, sem acento, com data: `contestacao-banco-x-2026-09-18.docx`. Rascunho que estava em `<plugin>/casos/` vem para a raiz do projeto; o que fica lá não pode ter dado nominativo.
4. Atualize `STATE.md`: `## Fase atual` (marque a etapa) · `## Próximo passo` (nunca vazio — se acabou: "arquivar após protocolo/assinatura") · `## Histórico` (data · entregue · arquivo). Atualize a linha do projeto em `clientes/<x>/STATE.md`. Protocolado? `<peça>-protocolo.pdf` ao lado e data/número no Histórico.
5. `python3 "<plugin>/scripts/lint.py" --cliente <slug>` sem erro.
6. Diga em 4 linhas: caminho do arquivo · o que Thor selou · próximo passo · o que ele faz fora da bancada (protocolar / enviar ao cliente / assinar / lançar prazo no sistema de processos).

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
