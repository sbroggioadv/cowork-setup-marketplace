# cowork-setup — organize sua pasta COWORK-OS no método Code-OS

Plugin gratuito para o Claude (Cowork ou Code) que organiza a pasta de trabalho do escritório: **um lugar por cliente**, um `STATE.md` por caso (onde o trabalho está), uma `FICHA.md` por caso (o que sabemos e o que provamos), versões antigas em `historico/`, os seus **modelos canônicos por área** em `knowledge/modelos/` (é deles que toda peça parte), bases de jurisprudência, doutrina e legislação com nível de citação, e uma cadeia de comando que impede o Claude de "inventar": **Zeus** organiza → **Gandalf** faz o brief → **Chefe** produz a partir do seu modelo → **Corte** revisa o mérito, fora do contexto de quem escreveu → **Thor** confere a entrega.

**Nenhum plugin é obrigatório.** Ele acopla os plugins jurídicos que você tiver instalados — um, vários ou nenhum.

O plugin traz **só a mecânica**. Identidade, voz, regras, modelos e clientes são seus — ele pergunta e registra.

## Instalar (uma vez)
1. No app do Claude: **Configurações → Plugins → Marketplaces → adicionar** o endereço deste repositório.
2. Instale **cowork-setup**. Os plugins jurídicos que você já usa continuam iguais (e as pastas deles continuam na raiz, onde eles as procuram).

## Organizar (uma vez por pasta)
1. Abra o Cowork na sua pasta **COWORK-OS** (a que já usa, ou uma nova).
2. No Finder, duplique a pasta (⌘D) — é o seu backup.
3. No chat: `/cowork-setup`. Ele conta o que encontrou, faz a entrevista (quem você é, áreas, voz, regras), mostra o **plano** do que vai para onde e **só move depois que você aprovar**. Nada é apagado: o que não tem lugar vai para `_legado/triagem/` para você decidir.
4. Cole o bloco que ele gera em **Configurações → Preferências Pessoais**.
5. Feche e reabra a pasta. O painel de abertura passa a aparecer sozinho.

## Usar (todo dia)
| Você diz | O que acontece |
|---|---|
| `/comecar` (ou reabrir a pasta) | painel: pendências, casos com próximo passo, estado da estrutura |
| `/zeus contestação do caso X do cliente Y` | classifica, confere conflito de interesses, abre a pasta certa, faz o brief se precisar, produz a partir do seu modelo (com o plugin da área, se houver), passa pela Corte e pelo Thor e grava no STATE |
| arrastar modelos para `knowledge/modelos/_novos/` · `/modelos` | organiza sozinho por área, nomes em minúsculas, índice por área |
| `/jurisprudencia` | pesquisa (Jus IA), súmulas e temas embarcados, doutrina e legislação — sempre com nível de citação |
| `/me-ajuda` | qualquer dúvida sobre a bancada |
| `/novo-cliente "Nome"` · `/novo-projeto contencioso civel "Cliente" "Adversário nº"` | as únicas formas de criar pasta — sempre certas |
| `/gandalf` | brief + FICHA antes de qualquer peça ou contrato |
| `/entregar` | versão final na raiz do caso, anterior em `historico/`, STATE atualizado |
| `/lint-estrutura` | "tem algo fora do lugar?" |
| `/encerrar` | fecha a sessão: STATE de tudo que foi tocado, memória, tarefas |
| `/cowork-setup` de novo | auditar · atualizar (versão nova do plugin) · plugins (instalou ou removeu) · reconfigurar |

## O que ele cria
```
COWORK-OS/
├── CLAUDE.md · TASKS.md            constituição (gerada) · pendências vivas
├── identidade/00–06                 suas regras, quem você é, voz, escrita, mapa, roteamento, memória
├── clientes/<cliente>/              STATE (índice) · cadastro/ · contencioso/<area>/<caso>/ · consultivo/<area>/<doc>/ · holding/
│     cada caso: STATE.md · FICHA.md · entrada/ · pesquisas/ · historico/ · (raiz = versão vigente)
├── knowledge/modelos/<area>/        seus modelos canônicos (+ honorarios · procuracoes · notificacoes · geral) · _novos/ = caixa de entrada
├── knowledge/jurisprudencia · doutrina · legislacao   bases de citação, com nível
├── <plugin>/                        pastas dos seus plugins jurídicos (na raiz, onde eles as procuram)
├── _sistema/                        do plugin: versão, plugins acoplados, templates (STATE · FICHA · CADASTRO), plano, auditorias
└── _legado/                         o que veio de antes e espera sua decisão
```

## Garantias
- **Nada se move sem você aprovar o plano; nada se apaga.** Prova de integridade ao final: todo arquivo original é reencontrado (por conteúdo). A única organização automática é a da caixa `knowledge/modelos/_novos/` — despejar ali é o pedido; cada movimento fica em `_sistema/modelos.log` e duplicado vai para `_legado/duplicados/`.
- **Rodar de novo não bagunça:** o setup é idempotente.
- **A organização é regra em código** (`espec/estrutura.json`): o verificador, o painel e a auditoria leem a mesma lei — o Claude não improvisa.
- **Pronto para o próximo passo:** quando quiser versionar com git, a estrutura já é compatível (o `historico/` vira histórico do git).

Requisitos: Claude (Cowork ou Code) · Python 3 (o macOS já traz; no Windows, python.org). Súmulas e temas do STF, STJ, TST, TJSP, TRT-15, CJF e FONAJE vêm embarcados (retrato datado — conferir vigência antes de citar). **Passo a passo completo: [MANUAL.md](MANUAL.md).** Dúvidas: `/cowork-setup` e pergunte.
