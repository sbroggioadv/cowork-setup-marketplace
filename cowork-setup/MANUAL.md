# Manual do `cowork-setup` — instalar, montar do zero, organizar o que já existe, atualizar

> Versão 1.0.1 · Para quem usa o Claude (Cowork ou Claude Code) numa pasta chamada **COWORK-OS**, no **Mac ou no Windows**. Você não precisa saber o que é terminal, script ou repositório: tudo acontece no chat, por perguntas e respostas.

## 0. O que é, em 3 linhas

O plugin organiza a sua pasta de trabalho no **método Code-OS**: uma pasta por cliente, um `STATE.md` por caso (onde o trabalho está), uma `FICHA.md` por caso (o que sabemos e o que provamos), versões antigas em `historico/`, e uma cadeia de comando que impede o Claude de improvisar organização: **Zeus** organiza → **Gandalf** faz o brief → **Chefe** produz com o plugin da área → **Thor** confere a entrega.

**O que ele não faz:** não apaga arquivo (nunca), não move nada sem você aprovar o plano, não traz conteúdo de terceiros — identidade, voz, regras, modelos e clientes são seus; o plugin só traz a mecânica.

## 1. Antes de começar

| Precisa de | Como saber |
|---|---|
| App Claude com Cowork (ou Claude Code) | você já usa |
| Python 3 | **Mac:** já vem instalado. **Windows:** baixe em python.org e, na instalação, marque **"Add python.exe to PATH"**. Para conferir: abra o Terminal (Mac) ou o Prompt de Comando (Windows) e digite `python3 --version` (Mac) ou `python --version` (Windows). |
| A pasta **COWORK-OS** | a que você já usa, ou uma nova e vazia |
| Seus plugins jurídicos (`trabalhista-adv-os`, `holding-architect`…) | opcionais — o plugin reconhece os que estiverem instalados |

Pasta na nuvem? Deixe-a sempre baixada, senão o Claude pode não enxergar arquivos que só existem na nuvem: **iCloud** (Mac) → botão direito → Manter baixado · **OneDrive** (Windows) → botão direito → Sempre manter neste dispositivo · **Google Drive** → botão direito → Disponível off-line.

## 2. Instalar (uma vez, 2 minutos)

**No app Claude (Cowork):**
1. Configurações → **Plugins** → **Marketplaces** → **Adicionar** → cole:
   `https://github.com/sbroggioadv/cowork-setup-marketplace`
2. Na lista de plugins, instale **cowork-setup**.
3. Conferir: abra qualquer pasta no Cowork e digite `/cow` — devem aparecer `cowork-setup:cowork-setup`, `cowork-setup:zeus`, etc.

**No Claude Code (terminal), se você usa:**
```bash
claude plugin marketplace add https://github.com/sbroggioadv/cowork-setup-marketplace
claude plugin install cowork-setup@cowork-setup-marketplace
```

Os comandos aparecem com o prefixo do plugin (`/cowork-setup:zeus`). Quando não houver outro plugin com comando de mesmo nome, o atalho curto (`/zeus`) também funciona.

## 3. Montar do zero (pasta nova e vazia)

1. Crie a pasta `COWORK-OS` (Mac: Finder → Nova Pasta · Windows: Explorador → Nova pasta) e abra-a no Cowork.
2. Digite **`/cowork-setup`**. Ele detecta "pasta vazia" → modo **NOVO**.
3. Responda a **entrevista** (6 blocos, um por vez):
   1. quem você é — nome, OAB, escritório, cidade, como quer ser chamado, nome que assina;
   2. atuação — áreas, polos que nunca atua (ex.: "trabalhista só pela empresa"), ferramentas, onde a pasta está;
   3. voz e escrita — postura, tom, vocabulário, o que nunca soa como você, estrutura de peça, formatação;
   4. regras invioláveis — o que nunca se faz, o que sempre se confere;
   5. módulos — tem modelo `.docx` timbrado? quer pasta de súmulas? faz holding?;
   6. memória e tarefas — preferências e pendências que valem para todos os casos.
4. Ele cria a estrutura (seção 8), roda a **auditoria** (13 verificações) e mostra o resultado.
5. Cole o bloco que ele gera em **Configurações → Preferências Pessoais**.
6. Feche e reabra a pasta. O painel de abertura passa a aparecer sozinho.
7. Primeiro cliente: `/novo-cliente "Nome"`. Primeira demanda: `/zeus <o que precisa>`.

Tempo: 15 a 25 minutos, quase todo na entrevista.

## 4. Organizar uma pasta que já existe (migrar)

É o caso de quem já tem o COWORK-OS com `CLIENTES/`, `PERSONA.md`, `MEMORY.md`, `BASE DE CONHECIMENTO/` e as pastas dos plugins.

1. Abra a pasta no Cowork e digite **`/cowork-setup`**. Ele faz o **censo** (não muda nada) e resume: quantos clientes, quantos casos, o que não reconheceu, quais plugins tem.
2. **Backup** — ele pede: duplique a pasta (Mac: selecione no Finder → ⌘D · Windows: botão direito → Copiar, depois Colar na mesma pasta) e responda "sim". Sem isso ele não continua.
3. **Entrevista** — igual à seção 3, mas pré-preenchida com o que ele leu no seu `PERSONA.md`, `CLAUDE.md` e `MEMORY.md` antigos. Você confirma ou corrige.
4. **Plano** — ele mostra o de→para de cada pasta e arquivo e faz **perguntas** só sobre o que não conseguiu decidir sozinho:
   - "qual a área deste caso?" (quando a pasta não diz — ex.: `CONSULTIVO/Contrato X`);
   - "nome da pasta do caso?" (quando a pasta da área é o próprio caso — ex.: `CONTENCIOSO/Cível/STATE.md`); ele sugere `adversario-numero-do-processo`;
   - "este caso do plugin trabalhista é de qual cliente?" (dado de cliente dentro de `trabalhista/casos/`);
   - "para onde vai isto?" (arquivo ou pasta fora do padrão). Responda com um destino, ou `legado` (vai para `_legado/triagem/` para você decidir depois), ou `manter`.
   Depois, **aprove**. Nada foi movido até aqui.
5. **Aplicar** — ele move, cria os `STATE.md`/`FICHA.md`/`CADASTRO.md`, gera a identidade e prova a integridade: **todo arquivo original é reencontrado** (por conteúdo). Se algo não fechar, ele para e mostra.
6. **Casos vivos** — ele lista os casos migrados e pergunta quais estão vivos; nesses, preenche Demanda, Fase atual, Decisões fixadas e Próximo passo a partir do STATE antigo (que fica em `historico/`), marcando `[REVISAR]`.
7. **Auditoria** — 13 verificações; corrige sozinho o que é mecânico; o que sobra vira lista para você (`_legado/triagem/`, memórias a absorver).
8. Cole o bloco em **Preferências Pessoais**, feche e reabra a pasta.

O que muda na sua pasta antiga:

| Antes | Depois |
|---|---|
| `CLAUDE.md`, `PERSONA.md`, `MEMORY.md` na raiz | `identidade/00–06` (conteúdo preservado; originais em `_legado/`) |
| `BASE DE CONHECIMENTO/` | `knowledge/` |
| `CLIENTES/Nome/CONSULTIVO/Documento/STATE.md` | `clientes/nome/consultivo/<area>/documento/STATE.md` (+ FICHA, entrada/, pesquisas/, historico/) |
| `CONTENCIOSO/Cível/{Documentos cliente, Peças Finais}` | `contencioso/civel/<caso>/{entrada/, raiz}` |
| `memory.md` do caso | `_memoria-cowork.md` ao lado do STATE, até ser absorvido |
| `trabalhista/casos/<cliente>/` | o caso vai para `clientes/…`; a pasta do plugin fica |
| o que ele não reconheceu | `_legado/triagem/` |

## 5. Atualizar (saiu versão nova do plugin)

1. No app: Configurações → Plugins → **cowork-setup** → atualizar (ou reinstalar).
2. Ao abrir a pasta, o painel avisa: "Plugin v1.x > organização v1.0: rode /cowork-setup → atualizar".
3. Digite `/cowork-setup` e escolha **atualizar**. Ele regenera só o que é do plugin (`CLAUDE.md`, `_sistema/`, a tabela de roteamento em `identidade/05`) e roda a auditoria. **Não toca** no que é seu (`identidade/01–04` e `06`, `knowledge/`, clientes).

## 6. Auditar e reconfigurar

- **Auditar** (a qualquer hora): `/cowork-setup` → auditar. Relatório em `_sistema/migracao/AUDITORIA-<data>.md`. FAIL = ele corrige ou diz o que fazer; AVISO = lista de trabalho sua.
- **Reconfigurar** (instalou plugin jurídico novo, mudou de área, mudou o nome do escritório): `/cowork-setup` → reconfigurar. Ele pergunta só o que mudou e atualiza a tabela de roteamento. Regerar a identidade inteira só se você mandar — sobrescreve o que você editou à mão.

## 7. As skills, uma a uma

| Comando | Quando usar | O que faz | O que produz | O que NÃO faz |
|---|---|---|---|---|
| **`/cowork-setup`** | primeira vez; plugin atualizado; "tem algo errado?" | detecta o modo (novo · migrar · auditar · atualizar · reconfigurar) e conduz as fases: censo → entrevista → plano → aplicar → auditoria | a estrutura da seção 8 + relatórios em `_sistema/` | mover sem aprovação; apagar; inventar dado seu |
| **`/comecar`** | ao abrir a pasta (ou quando o painel automático não apareceu) | lê `identidade/` e `TASKS.md`; imprime pendências, casos com próximo passo e o estado da estrutura | painel de abertura | produzir |
| **`/zeus`** | **toda demanda de cliente**: "contestação do X", "contrato para Y", "responde o cliente Z" | classifica (tipo · área · cliente · tier), acha ou cria a pasta, chama Gandalf se precisar de brief, dispara o Chefe (plugin da área), submete a Thor, grava os gates no STATE | o entregável na pasta do caso + STATE atualizado | redigir ele mesmo; pular Thor |
| **`/gandalf`** | antes de qualquer peça ou contrato (T≥2) | entrevista você e escreve o brief no STATE (Demanda · Como começa · Como termina · Critério de aceite) e abre a FICHA (partes, cronologia, fatos confirmados/relatados/lacunas, matriz de provas) | STATE briefado + FICHA | presumir dado que falta |
| **`/novo-cliente "Nome"`** | cliente novo | cria `clientes/nome/` com STATE (índice), `cadastro/CADASTRO.md`, `cadastro/documentos/` | a pasta do cliente | criar caso (isso é `/novo-projeto`) |
| **`/novo-projeto <tipo> <area> "Cliente" "Caso"`** | caso novo (contencioso · consultivo · holding) | cria a pasta do caso com STATE (+ FICHA em T≥2), `entrada/`, `pesquisas/`; registra no índice do cliente; área nova é registrada e entra na tabela de roteamento | a pasta do caso | pasta com número na frente; nome com acento |
| **`/entregar`** | fechar um entregável | confere o selo de Thor; manda a versão anterior para `historico/`; grava a final na raiz do caso; atualiza STATE e índice; diz o que você faz fora da bancada | versão final + STATE fechado | entregar sem Thor (T≥1) |
| **`/lint-estrutura`** | "tem algo fora do lugar?" | confere a pasta contra a lei do plugin; corrige o que só adiciona (FICHA, entrada/, pesquisas/); lista o que depende de você | relatório E/A | mover conteúdo seu sem perguntar |
| **`/encerrar`** | fim da sessão | garante STATE atualizado em todo caso tocado; registra o significativo na memória (`identidade/06`) ou no cliente; atualiza `TASKS.md`; roda o verificador | sessão fechada sem esquecimento | — |

**Os agentes** (você não os chama; Zeus chama): **Gandalf** (brief), **Chefe** (produz na sua persona com o plugin da área e roda a Corte R1-R4 do plugin), **Thor** (gate de entrega: critério de aceite, decisões fixadas, pasta certa, STATE, versões, polos vetados, consistência — cego para mérito; devolve no máximo 2 vezes, na 3ª escala a você).

**Tiers:** T0 consulta/mensagem (resposta direta) · T1 documento simples (Chefe + Thor leve) · T2 peça/contrato (Gandalf + Chefe + Corte + Thor) · T3 projeto multi-etapa (tudo, por etapa). Tier só sobe.

## 8. O que o plugin cria na pasta — e de quem é cada coisa

> Mapa visual (as cinco camadas, o que há dentro de um caso, a cadeia de comando): página "A pasta em um olhar" do `MANUAL.pdf`, ou a página web do manual.

```
COWORK-OS/
├── CLAUDE.md · TASKS.md               constituição (do plugin, regenerada) · pendências (suas)
├── identidade/
│   ├── 00-PERFIL-MESTRE.md            SUAS regras invioláveis — prevalecem sobre tudo
│   ├── 01 quem-sou · 02 voz · 03 escrita · 04 mapa · 06 memória   seus (gerados uma vez, depois você edita)
│   └── 05-ROTEAMENTO-PLUGINS.md       tabela área→plugin (do plugin, entre marcadores); o resto do arquivo é seu
├── clientes/<cliente>/
│   ├── STATE.md · cadastro/CADASTRO.md · cadastro/documentos/
│   ├── contencioso/<area>/<adversario-numero>/   STATE · FICHA · entrada/ · pesquisas/ · historico/ · raiz = vigente
│   ├── consultivo/<area>/<documento>/            idem
│   └── holding/                                  só para quem faz
├── knowledge/<area>/ · templates/     seus modelos validados · os templates da mecânica
├── <plugin>/                          motores dos seus plugins jurídicos (ficam onde estão; não renomear)
├── _sistema/                          do plugin: versão, áreas, plano, auditorias — não editar
└── _legado/                           o que veio de antes e espera sua decisão
```

Regras de nome: pastas em minúsculas, hífen no lugar de espaço, sem acento, sem número na frente. Pasta nova só por `/novo-cliente` e `/novo-projeto`.

## 9. A rotina (a cronologia de todo dia)

1. Abrir a pasta → painel (ou `/comecar`).
2. Demanda de cliente → `/zeus …` (ele chama Gandalf, Chefe e Thor sozinho).
3. Fechar entregável → `/entregar`.
4. Fim → `/encerrar`.

Se você mexer numa pasta de cliente e tentar encerrar sem atualizar o STATE, o plugin barra uma vez e diz qual caso ficou sem próximo passo.

## 10. Problemas comuns

| Sintoma | O que fazer |
|---|---|
| "python3 não encontrado" | Mac: abra o Terminal e digite `python3` — o sistema oferece instalar. Windows: instale de python.org com "Add python.exe to PATH" e reabra o app; o plugin usa `python` ou `py` quando `python3` não existe. Enquanto isso ele segue em modo checklist (só verifica, não move). |
| Arquivos "na nuvem" (ícone de nuvem ao lado do arquivo) | botão direito na pasta → Manter baixado (iCloud) · Sempre manter neste dispositivo (OneDrive) · Disponível off-line (Google Drive), antes de aprovar o plano |
| Painel de abertura não aparece | feche e reabra a pasta; se persistir, `/comecar` faz o mesmo |
| Dois clientes que são o mesmo (`Maria Oliveira` e `MARIA OLIVEIRA ME`) | no plano, responda a pergunta de destino dos dois com o mesmo caminho — ele une |
| Plugin jurídico "não detectado" na tabela de roteamento | rode o `/start-*` daquele plugin na pasta; depois `/cowork-setup` → reconfigurar |
| Comandos aparecem como `/cowork-setup:zeus` | é o prefixo do plugin; o atalho `/zeus` funciona quando não há conflito |
| Quero desfazer | nada foi apagado: `_sistema/migracao/MIGRACAO.md` lista cada movimento; a cópia que você fez no passo do backup é a volta |

## 11. Preferências Pessoais

No fim do setup o plugin imprime um bloco ("Quem sou · Minha bancada · Como trabalhar comigo"). Cole em **Configurações → Preferências Pessoais** do Claude, substituindo o antigo. É o que faz o Claude ler `CLAUDE.md` e `identidade/` antes de qualquer tarefa mesmo em sessões novas.

## 12. Versões

- A versão da organização instalada está em `_sistema/versao`; a do plugin, no app. O painel de abertura avisa quando diferem.
- Histórico do plugin e melhorias: `github.com/sbroggioadv/cowork-setup-marketplace`.
