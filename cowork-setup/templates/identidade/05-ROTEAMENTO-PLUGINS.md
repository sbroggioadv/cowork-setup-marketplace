# 05 — ROTEAMENTO DE PLUGINS

> Qual plugin cobre qual demanda, e para onde vai o resultado. O roteamento é do **Zeus**; o plugin entra pelo **chefe** da área. Gerado em {{DATA}} a partir do que está instalado; atualize quando instalar plugin novo (`/cowork-setup` → atualizar).

## Como funciona
1. Zeus classifica a demanda (tipo · área · cliente · tier) e abre/localiza a pasta.
2. O chefe da área injeta a mecânica (pasta, STATE, brief) e aciona a **skill-mestre** do plugin.
3. O plugin produz na persona de `identidade/` e audita com a própria Corte R1-R4.
4. O resultado FINAL vai para `clientes/<x>/…`; o rascunho do plugin pode ficar em `<plugin>/casos/` (sem dado nominativo).
5. Thor confere a entrega e Zeus grava o selo no STATE.

## Mapa — área → plugin (skill-mestre) → destino
<!-- roteamento:inicio (tabela mantida pelo plugin — o resto do arquivo é seu) -->
| Área | Plugin instalado | Skill-mestre | Observação |
|---|---|---|---|
{{TABELA_ROTEAMENTO}}
<!-- roteamento:fim -->

Área sem plugin → o chefe produz direto na persona do escritório. `[confirmar]` = nome da skill não verificado: o chefe tenta; se não existir, cai para a persona.

## Apoios (qualquer chefe aciona)
| Apoio | Plugin | Para |
|---|---|---|
{{TABELA_APOIOS}}

## Trava
A suíte "Claude for Legal" (`legal`, `corporate-legal`, `ip-legal`, `legal-clinic`, `product-legal`, `ai-governance-legal`, `law-student`…) é direito norte-americano. **Nunca** roteia demanda do escritório; só sob pedido nominal de {{TRATAMENTO}}, para estudo.
