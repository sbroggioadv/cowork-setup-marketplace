# 05 — ROTEAMENTO DE PLUGINS

> Qual plugin cobre qual demanda, e para onde vai o resultado. O roteamento é do **Zeus**; o plugin entra pelo **chefe** da área. Gerado em {{DATA}} a partir do que está instalado; atualize quando instalar plugin novo (`/cowork-setup` → atualizar).

## Como funciona
1. Zeus classifica a demanda (tipo · área · cliente · tier) e abre/localiza a pasta.
2. O chefe da área injeta a mecânica (pasta, STATE, brief) e aciona a **skill-mestre** do plugin.
3. O plugin produz na persona de `identidade/`, a partir do modelo canônico de `knowledge/modelos/<area>/`; o agente corte audita o mérito com a Corte do plugin (ou a genérica da bancada).
4. O resultado FINAL vai para `clientes/<x>/…`; o rascunho do plugin pode ficar em `<plugin>/casos/` (sem dado nominativo).
5. Thor confere a entrega e Zeus grava o selo no STATE.

## Mapa — área → plugin (skill-mestre) → destino
<!-- roteamento:inicio (tabela mantida pelo plugin — o resto do arquivo é seu) -->
| Área | Plugin | Skill-mestre | Corte R1-R4 | Observação |
|---|---|---|---|---|
{{TABELA_ROTEAMENTO}}
<!-- roteamento:fim -->

**Nenhum plugin é obrigatório.** Área sem plugin → o chefe produz direto na persona do escritório a partir de `knowledge/modelos/<area>/`, e a Corte usa o checklist R1-R4 da bancada. Instalou ou removeu plugin → `/cowork-setup` → plugins (a tabela se refaz sozinha).

## Apoios instalados (qualquer chefe aciona)
| Plugin | Skill-mestre | Tipo |
|---|---|---|
{{TABELA_APOIOS}}

## Trava
A suíte "Claude for Legal" (`legal`, `corporate-legal`, `ip-legal`, `legal-clinic`, `product-legal`, `ai-governance-legal`, `law-student`…) é direito norte-americano. **Nunca** roteia demanda do escritório; só sob pedido nominal de {{TRATAMENTO}}, para estudo.
