# _sistema/ — do plugin `cowork-setup`. Não editar à mão.

| Arquivo | O que é |
|---|---|
| `versao` | versão da organização instalada (o `/cowork-setup` compara com a do plugin para oferecer "atualizar") |
| `areas.json` | áreas registradas nesta bancada (cresce quando `/novo-projeto` cria área nova) |
| `censo.json` | inventário da pasta na última rodada |
| `perfil.json` | respostas da entrevista (identidade, plugins, módulos) — usado para regenerar `identidade/` e `CLAUDE.md` |
| `plugins.json` | plugins acoplados (área · skill-mestre · Corte) — refeito a cada abertura; nenhum é obrigatório |
| `templates/` | modelos da mecânica: `STATE`, `STATE-cliente`, `FICHA`, `CADASTRO` (os de peça/contrato ficam em `knowledge/modelos/`) |
| `modelos.log` | cada modelo organizado, renomeado ou separado como duplicado (o mapa de desfazer de `knowledge/modelos/`) |
| `migracao/PLANO.md` · `plano.json` | o de→para aprovado antes de mover qualquer coisa |
| `migracao/MIGRACAO.md` | log do que foi movido/criado (é o mapa de desfazer) |
| `migracao/AUDITORIA-AAAA-MM-DD.md` | as verificações de ponta a ponta, PASS/FAIL |
| `.sessao` | carimbo da sessão atual (hook SessionStart) — usado pelo hook Stop |
