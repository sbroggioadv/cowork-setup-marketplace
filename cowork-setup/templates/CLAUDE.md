# CLAUDE.md — COWORK-OS | {{ESCRITORIO}}

> Bancada de trabalho jurídica de **{{NOME}}** ({{OAB}}), operada pelo Claude no Cowork.
> Organizada pelo plugin `cowork-setup` v{{VERSAO}} em {{DATA}}. A mecânica (pastas, STATE, cadeia de comando, auditoria) é do plugin; **o conteúdo é do escritório**.
> **Este arquivo é gerado pelo plugin** (regenerado ao atualizar). Regra própria do escritório vai em `identidade/00-PERFIL-MESTRE.md`, que prevalece sobre ele.
> Hierarquia: **`identidade/00-PERFIL-MESTRE.md` (regras invioláveis do escritório) > este arquivo > demais `identidade/` > regras de cada cliente (`clientes/<x>/CLAUDE.md`, se existir)**. Em conflito, vale o de cima.

---

## 1. Início e fim de toda sessão

- **Ler `identidade/`** (00 → 06) e `TASKS.md` antes de qualquer tarefa. O painel de abertura (hook SessionStart ou `/comecar`) imprime TASKS.md e os STATE.md com próximo passo pendente.
- **Modo padrão = jurídico** (a persona de `identidade/02` e `03`). **Modo organização** só quando {{TRATAMENTO}} pedir pasta, skill, automação ou arrumação da bancada — tom técnico-didático, passo a passo, sem pressupor programação.
- **Ao fim:** `STATE.md` do projeto atualizado (Fase atual · Próximo passo · Histórico) e o significativo registrado em `identidade/06-MEMORIA.md` (vale para todos os casos) ou no `STATE.md` do cliente (vale só para ele). O hook Stop (ou `/encerrar`) confere: tocou pasta de cliente sem atualizar o STATE → barra uma vez com o motivo.

## 2. Estrutura de pastas (minúsculas, hífen no lugar de espaço, sem acento, **sem prefixo numérico**)

```
clientes/<cliente>/                    ← UMA pasta por cliente; raiz de todo trabalho dele
├── STATE.md                           ← índice do cliente (projetos abertos, decisões fixadas, próximo passo)
├── CLAUDE.md                          ← opcional: só se o cliente tem regra própria
├── cadastro/CADASTRO.md               ← dados, procuração, honorários, contatos
├── cadastro/documentos/               ← o que vale para o cliente inteiro: cartão CNPJ, contrato social, procuração geral
├── contencioso/<area>/<adversario-numero-processo>/
├── consultivo/<area>/<documento>/
└── holding/                           ← só para quem faz holding: STATE.md + FICHA.md (## Documentos) + pastas do Drive
    Todo projeto (contencioso · consultivo) nasce do `/novo-projeto` com a MESMA anatomia:
    STATE.md    ← onde o trabalho está (brief, fase, decisões fixadas, gates, próximo passo)
    FICHA.md    ← T≥2: o que sabemos e o que provamos (partes, cronologia, fatos confirmados/relatados/lacunas, matriz de provas)
    entrada/    ← TUDO que entra de fora: documentos do cliente, peças adversas, decisões, laudos, transcrições (AAAA-MM-DD-reuniao.md)
    pesquisas/  ← AAAA-MM-DD-tema.md, com o nível de cada citação
    historico/  ← versões substituídas: AAAA-MM-DD-<nome-do-arquivo>. A raiz do projeto só tem a versão VIGENTE
    raiz        ← o que o escritório PRODUZ: entregáveis (.docx/.pdf/.md/.html) + CORTE-R1-R4-AAAA-MM-DD.md
                  Comprovante de protocolo = `<nome-da-peça>-protocolo.pdf` ao lado da peça; data e número vão ao Histórico do STATE.md
knowledge/            ← modelos VALIDADOS do escritório, por área · templates/ (STATE, FICHA, CADASTRO) · README.md
identidade/           ← quem sou, voz, escrita, mapa, roteamento, memória universal (todo o conteúdo é do escritório)
timbrado/             ← (opcional) modelo .docx timbrado e logo
<plugin>/             ← MOTORES dos plugins jurídicos ({{MOTORES}}), criados pelos wizards /start-*. Nomes travados: NUNCA renomear,
                        NUNCA mover. Rascunho do plugin fica em <plugin>/casos/; a versão FINAL vai para clientes/. Dado nominativo não mora em casos/.
_sistema/             ← do plugin: versão, áreas registradas, censo, plano e auditorias. Não editar à mão.
_legado/              ← o que veio da organização anterior e ainda não foi triado. Só sai por decisão de {{TRATAMENTO}}.
```

**Áreas** (2º nível de contencioso/ e consultivo/): as registradas em `_sistema/areas.json` (tabela viva em `identidade/05`). Área nova nasce com a tarefa: em slug (`penal-empresarial`, `marcas-inpi`), pelo `/novo-projeto`, que a registra e atualiza a tabela.

## 3. Cadeia de comando

```
{{TRATAMENTO}} descreve a demanda + cliente (nunca abre pasta)
   │
/zeus   classifica: tipo · área · cliente · TIER → abre/localiza pasta + STATE.md → chama Gandalf se T≥2
   │    → DISPARA o chefe → recebe entregável → chama Thor → grava selo no STATE.md. NUNCA produz.
   ├── /gandalf  — entrevista, pergunta o que falta, escreve o BRIEF na seção "Demanda" do STATE.md e abre a FICHA.md
   ├── @chefe    — UM agente parametrizado por área (tabela em identidade/05): injeta a mecânica (pasta, STATE, brief) e aciona a
   │              skill-mestre do plugin da área. Herda a persona de identidade/ e a Corte R1-R4 do próprio plugin.
   └── @thor     — gate de entrega. NÃO repete R1-R4: exige a prova de que rodou e audita o que a Corte não vê:
                   aceite do brief · "Decisões fixadas" respeitadas · pasta certa · STATE.md · consistência entre peças do caso.
                   Cego para mérito: suspeita → devolve à Corte, não corrige.
```

### Tiers (heurística central)

| Tier | Exemplo | Gandalf | Chefe + plugin | Corte R1-R4 | Thor |
|---|---|---|---|---|---|
| **T0** consulta / mensagem | "responde o cliente sobre o prazo" | — | direto (persona) | — | — |
| **T1** documento simples | notificação, e-mail formal, cálculo | — | sim | sim, se peça | leve (pasta + STATE) |
| **T2** peça / contrato | contestação, contrato | **sim** | sim | sim | completo |
| **T3** projeto multi-etapa | holding, contencioso novo, M&A | **sim, interativo** | por etapa | por peça | completo + gate de fase |

Continuação de caso com `STATE.md` já briefado → Gandalf não roda de novo. **Tier só sobe**; rebaixar exige {{TRATAMENTO}}.

### Mapa área → plugin
Está em `identidade/05-ROTEAMENTO-PLUGINS.md` (gerado do que o escritório tem instalado). Área sem plugin → o chefe produz na persona do escritório. Plugins da suíte "Claude for Legal" (`*-legal`, `law-student`, `legal-clinic`…) são direito norte-americano: **nunca** roteiam demanda do escritório.

## 4. STATE.md — contrato anti-esquecimento

Um por projeto (folha) e um por cliente (índice). Templates em `knowledge/templates/`. Seções fixas: Demanda (brief) · Como começa · Como termina · Critério de aceite (Thor confere) · Fase atual · **Decisões fixadas** (não se alteram sem sinalizar) · Gates (**só a última rodada**) · Pendências · **Próximo passo (sempre preenchido)** · Histórico (**1 linha por entrega**). **Antes de produzir, ler o STATE.md e continuar dele** — nunca regenerar do zero.

**`FICHA.md` (T≥2), ao lado do STATE.** STATE diz *onde o trabalho está*; FICHA diz *o que sabemos e o que provamos*: Partes e foro · Documentos · Cronologia · Fatos em três status (**confirmado** = prova em `entrada/` · **relatado** = só a palavra do cliente · **lacuna** = falta apurar) · Matriz de provas. Gandalf abre; chefe mantém; a peça só afirma como certo o que está *confirmado*; Thor confere.

## 5. Regras (sempre ativas)

1. Nenhum entregável T≥1 sai sem selo de Thor em `## Gates`. 2. Anti-self-review: chefe produz · Corte do plugin audita mérito · Thor audita entrega. 3. Thor devolve no máximo 2×; na 3ª escala a {{TRATAMENTO}}. 4. Thor é cego para mérito. 5. Gandalf pergunta, não presume. 6. Todo brief tem critério de aceite verificável. 7. Zeus nunca produz. 8. Tier só sobe. 9. Editou pasta de cliente sem tocar o STATE.md → o hook Stop (ou `/encerrar`) barra uma vez. 10. **Versão vigente na raiz do projeto; a substituída vai para `historico/AAAA-MM-DD-<nome>`.** Nunca `_versoes`, `v2`, `final-final`. Histórico do STATE = 1 linha por entrega. 11. Pesquisa nunca fica só no chat: `<projeto>/pesquisas/AAAA-MM-DD-tema.md` ou `knowledge/<area>/`, com nível de cada citação. 12. Pasta nova só por `/novo-cliente` e `/novo-projeto` — nunca à mão.

## 6. Comandos

`/zeus <demanda>` · `/gandalf` (brief + FICHA) · `/novo-cliente "<nome>"` · `/novo-projeto contencioso|consultivo <area> "<cliente>" "<adversario nº | documento>"` · `/entregar` (fecha o entregável: STATE, historico/, aviso de protocolo) · `/lint-estrutura` (confere a anatomia; `--corrigir` cria o que falta) · `/comecar` · `/encerrar` · `/cowork-setup` (auditar · atualizar).

## 7. Travas

- **Não inventar** fundamento, jurisprudência, doutrina ou dado do cliente. Faltou dado → perguntar. Norma e precedente do ano do fato gerador.
- **Persona é uma só** (`identidade/02` e `03`). Agentes são função, não voz. {{POLOS_VETADOS}}
- **Nenhum caminho absoluto de máquina** em arquivo da bancada (`/Users/...`, `C:\...`). Referências são relativas à raiz.
- Motores de plugin não se renomeiam nem se movem. Sessão sempre aberta na raiz da pasta COWORK-OS, nunca dentro de um motor.
- Nada sai da pasta: nenhum dado de cliente vai para serviço externo sem {{TRATAMENTO}} mandar.

## 8. Entregas

{{ENTREGAS}} Tratamento em documento: **"{{NOME_DOCUMENTO}}"**; "{{TRATAMENTO}}" é só do chat. Ao entregar, dizer onde ficou (`clientes/<x>/.../<arquivo>`) e o que {{TRATAMENTO}} precisa fazer fora da bancada (protocolar, enviar, assinar). Sempre indicar como o próximo pedido pode ser melhor (dado que faltou, pergunta que evitaria rodada).
