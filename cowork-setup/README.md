# cowork-setup — organize sua pasta COWORK-OS no método Code-OS

Plugin para o Claude (Cowork) que organiza a pasta de trabalho do escritório: **um lugar por cliente**, um `STATE.md` por caso (onde o trabalho está), uma `FICHA.md` por caso (o que sabemos e o que provamos), versões antigas em `historico/`, e uma cadeia de comando que impede o Claude de "inventar" organização: **Zeus** organiza → **Gandalf** faz o brief → **Chefe** produz com o plugin da área → **Thor** confere a entrega.

O plugin traz **só a mecânica**. Identidade, voz, regras, modelos e clientes são seus — ele pergunta e registra.

## Instalar (uma vez)
1. No app do Claude: **Configurações → Plugins → Marketplaces → adicionar** o endereço deste repositório.
2. Instale **cowork-setup**. Os plugins jurídicos que você já usa continuam iguais.

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
| `/zeus contestação do caso X do cliente Y` | classifica, abre a pasta certa, faz o brief se precisar, produz com o plugin da área, confere e grava no STATE |
| `/novo-cliente "Nome"` · `/novo-projeto contencioso civel "Cliente" "Adversário nº"` | as únicas formas de criar pasta — sempre certas |
| `/gandalf` | brief + FICHA antes de qualquer peça ou contrato |
| `/entregar` | versão final na raiz do caso, anterior em `historico/`, STATE atualizado |
| `/lint-estrutura` | "tem algo fora do lugar?" |
| `/encerrar` | fecha a sessão: STATE de tudo que foi tocado, memória, tarefas |
| `/cowork-setup` de novo | auditar · atualizar (plugin novo) · reconfigurar (plugin/área nova) |

## O que ele cria
```
COWORK-OS/
├── CLAUDE.md · TASKS.md            constituição (gerada) · pendências vivas
├── identidade/00–06                 suas regras, quem você é, voz, escrita, mapa, roteamento, memória
├── clientes/<cliente>/              STATE (índice) · cadastro/ · contencioso/<area>/<caso>/ · consultivo/<area>/<doc>/ · holding/
│     cada caso: STATE.md · FICHA.md · entrada/ · pesquisas/ · historico/ · (raiz = versão vigente)
├── knowledge/<area>/ · templates/   seus modelos validados · os templates da mecânica
├── <plugin>/                        motores dos seus plugins jurídicos (ficam onde estão)
├── _sistema/                        do plugin: versão, plano, auditorias
└── _legado/                         o que veio de antes e espera sua decisão
```

## Garantias
- **Nada se move sem você aprovar o plano; nada se apaga.** Prova de integridade ao final: todo arquivo original é reencontrado (por conteúdo).
- **Rodar de novo não bagunça:** o setup é idempotente.
- **A organização é regra em código** (`espec/estrutura.json`): o verificador, o painel e a auditoria leem a mesma lei — o Claude não improvisa.
- **Pronto para o próximo passo:** quando quiser versionar com git, a estrutura já é compatível (o `historico/` vira histórico do git).

Requisitos: Claude com Cowork · Python 3 (o macOS já traz). **Passo a passo completo: [MANUAL.md](MANUAL.md).** Dúvidas: `/cowork-setup` e pergunte.
