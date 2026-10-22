import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Desfazer } from '../types'

// Bancada v0.1 — painel lateral do caso desta conversa (só leitura; as ações
// apenas escrevem o pedido na caixa de mensagem). Fonte da verdade: STATE.md,
// FICHA.md e TASKS.md da bancada; o mod nunca grava nada.

const PANE = 'bancada'
const caso = atom({ plugin: 'bancada', key: 'caso' } as const, '')
const desfazer = atom({ plugin: 'bancada', key: 'desfazer' } as const, null as Desfazer | null)

// Paleta: um significado por cor (ver bancada-mods/DESENHO.md).
const AZUL = 'suggestion' // agora / ação indicada
const VERDE = 'success' // feito, provado
const AMBAR = 'warning' // atenção, sai do escritório
const VERMELHO = 'error' // bloqueio, vencido, pendência
const LARANJA = 'claude' // olhar do adversário
const ROXO = 'merged' // olhar do juiz
const APAGADO = 'inactive' // ainda não existe

// Fundo tingido dos botões (o app não pinta o texto dentro de Button):
// hex com transparência, legível no tema claro e no escuro.
const TINTA: Record<string, string> = {
  [LARANJA]: '#D85A3030',
  [ROXO]: '#7F77DD38',
  [AZUL]: '#378ADD2E',
  [AMBAR]: '#EF9F2740',
  [VERMELHO]: '#E24B4A24',
  [VERDE]: '#25D36638', // verde do WhatsApp
}

// No terminal, transparência não existe: o fundo vem das chaves de tema
// (seguem o tema claro/escuro da pessoa) e só onde há uma tinta suave.
const fundo = (surface: string, cor: string): string | undefined =>
  surface === 'terminal' ? (cor === VERMELHO ? 'diffRemovedDimmed' : undefined) : TINTA[cor]

type Etapa = { nome: string; cor: string; tracejado: boolean; atual: boolean }
type Pendencia = { texto: string; doCaso: boolean; linha: string }
type Snap = { brief: boolean; corte: string; thor: string; feitas: number; total: number; entregue: boolean }
type Registro = { ts: string; caso: string; eventos: string[]; snap: Snap }
type Modelo = {
  dir: string
  cliente: string
  projeto: string
  area: string
  tier: string
  ref: string
  aberto: string
  etapasFeitas: number
  etapasTotal: number
  etapaAtual: string
  trilha: Etapa[]
  proximo: string
  prazo: { texto: string; dias: number | undefined } | undefined
  fatos: { confirmados: number; relatados: number; lacunas: number } | undefined
  provas: { tem: number; parcial: number; falta: number } | undefined
  entrada: number
  pendCaso: string[]
  snap: Snap
  agenda: { quando: string; oque: string; levar: string; dias: number } | undefined
  temFicha: boolean
}

// ---------- leitura do markdown ----------

const secao = (md: string, titulo: string): string => {
  const ini = md.search(new RegExp(`^## ${titulo}`, 'm'))
  if (ini < 0) return ''
  const resto = md.slice(ini).split('\n').slice(1).join('\n')
  const fim = resto.search(/^## /m)
  return (fim < 0 ? resto : resto.slice(0, fim)).trim()
}

const subsecao = (md: string, titulo: string): string => {
  const ini = md.search(new RegExp(`^### ${titulo}`, 'm'))
  if (ini < 0) return ''
  const resto = md.slice(ini).split('\n').slice(1).join('\n')
  const fim = resto.search(/^##/m)
  return fim < 0 ? resto : resto.slice(0, fim)
}

const limpa = (s: string): string =>
  s.replace(/\*\*|`|\[\[|\]\]/g, '').replace(/\s+/g, ' ').trim()

const corta = (s: string, n: number): string =>
  s.length > n ? `${s.slice(0, n - 1).replace(/[\s.,;:]+$/, '')}…` : s

const contaItens = (bloco: string): number =>
  bloco.split('\n').filter(l => /^\s*(- |\d+\. )/.test(l) && !/<fato>|<o que falta>/.test(l)).length

const diasAte = (ddmmaaaa: string): number | undefined => {
  const m = ddmmaaaa.match(/(\d{2})\/(\d{2})\/(\d{4})/)
  if (!m) return undefined
  const alvo = Date.UTC(Number(m[3]), Number(m[2]) - 1, Number(m[1]))
  const hoje = new Date()
  const base = Date.UTC(hoje.getFullYear(), hoje.getMonth(), hoje.getDate())
  return Math.round((alvo - base) / 86400000)
}

// Próximo compromisso da "## Agenda do caso" da FICHA (data de hoje em diante).
const proximaAgenda = (ficha: string): Modelo['agenda'] => {
  const linhas = secao(ficha, 'Agenda do caso')
    .split('\n')
    .filter(l => /^\|\s*\d{4}-\d{2}-\d{2}/.test(l))
    .map(l => l.split('|').slice(1, -1).map(c => limpa(c)))
  const futuros = linhas
    .map(c => {
      const [a, m, d] = (c[0] ?? '').split('-')
      return { c, dias: diasAte(`${d}/${m}/${a}`) ?? -1 }
    })
    .filter(x => x.dias >= 0)
    .sort((x, y) => x.dias - y.dias)
  const p = futuros[0]
  if (!p) return undefined
  const [a, m, d] = (p.c[0] ?? '').split('-')
  const hora = /\d{1,2}:\d{2}/.test(p.c[1] ?? '') ? ` ${p.c[1]}` : ''
  return {
    quando: `${d}/${m}${hora}`,
    oque: corta([p.c[2], p.c[3]].filter(Boolean).join(' · '), 80),
    levar: corta(p.c[4] ?? '', 80),
    dias: p.dias,
  }
}

const estadoGate = (linha: string): 'ok' | 'ajustar' | 'nenhum' => {
  if (!linha) return 'nenhum'
  const t = linha.toLowerCase()
  if (/devolvid|ajustar|reprovad/.test(t)) return 'ajustar'
  if (/\bok\b|aprovad|liberad/.test(t)) return 'ok'
  return 'nenhum'
}

const raizDe = (dir: string): string => {
  const m = dir.match(/^(.*?)\/(clientes|holding|mentorias)\//)
  return m?.[1] ?? dir
}

// Caminho de arquivo tocado → pasta do projeto (onde mora o STATE.md do caso).
const projetoDe = (p: string): string | undefined => {
  const m = p.match(/^(.*?\/)(clientes|holding|mentorias)\/(.*)$/)
  if (!m) return undefined
  const seg = (m[3] ?? "").split('/')
  const base = `${m[1]}${m[2]}`
  if (m[2] === 'clientes' && seg.length >= 5 && /^(contencioso|consultivo)$/.test(seg[1] ?? ""))
    return `${base}/${seg.slice(0, 4).join('/')}`
  if (m[2] === 'holding' && seg.length >= 2) return `${base}/${seg[0]}`
  if (m[2] === 'mentorias' && seg.length >= 3) return `${base}/${seg.slice(0, 2).join('/')}`
  return undefined
}

const montaModelo = async ($: any, dir: string): Promise<Modelo | undefined> => {
  const state: string = await $.fs.read(`${dir}/STATE.md`).catch(() => '')
  if (!state) return undefined
  const ficha: string = await $.fs.read(`${dir}/FICHA.md`).catch(() => '')

  const titulo = state.match(/^# STATE — (.+)$/m)?.[1] ?? dir.split('/').pop() ?? ''
  const [cliente, projeto = ''] = titulo.split(' × ')
  const area = state.match(/Área:\s*([^·\n]+)/)?.[1]?.trim() ?? ''
  const tier = state.match(/Tier:\s*\**(T\d)/)?.[1] ?? ''
  const ref = limpa(state.match(/Ref\/Nº processo:\s*([^·\n]+)/)?.[1] ?? '')
  const aberto = state.match(/Aberto em:\s*([\d-]+)/)?.[1] ?? ''

  const fase = secao(state, 'Fase atual').split('\n').filter(l => /^- \[[ xX]\]/.test(l))
  const feitas = fase.filter(l => /^- \[[xX]\]/.test(l)).length
  const pendente = fase.find(l => /^- \[ \]/.test(l)) ?? ''
  const etapaAtual = limpa(pendente.replace(/^- \[ \]\s*(etapa \d+\s*—\s*)?/, ''))

  const gates = secao(state, 'Gates').split('\n')
  const corte = estadoGate(gates.find(l => /^Corte/i.test(l)) ?? '')
  const thor = estadoGate(gates.find(l => /^Thor/i.test(l)) ?? '')
  const rodadaCorte = (gates.find(l => /^Corte/i.test(l)) ?? '').match(/(\d+) rodadas?/)?.[1]
  const brief = secao(state, 'Demanda').replace(/<[^>]+>/g, '').trim().length > 20
  const entregue = fase.length > 0 && feitas === fase.length

  const passos: Array<[string, boolean, boolean]> = [
    ['Brief', brief, false],
    ['Redação', corte !== 'nenhum', false],
    [`Corte${rodadaCorte ? ` r${rodadaCorte}` : ''}`, corte === 'ok', corte === 'ajustar'],
    ['Thor', thor === 'ok', thor === 'ajustar'],
    ['Entrega', entregue, false],
  ]
  const iAtual = passos.findIndex(([, feito]) => !feito)
  const trilha: Etapa[] = passos.map(([nome, feito, devolvido], i) => ({
    nome,
    cor: devolvido ? AMBAR : feito ? VERDE : i === iAtual ? AZUL : APAGADO,
    tracejado: !feito && !devolvido && i !== iAtual,
    atual: i === iAtual,
  }))

  const proximo = corta(limpa(secao(state, 'Próximo passo')), 320)

  const linhaPrazo = state.match(/^Prazo:\s*(.+)$/m)?.[1] ?? ''
  const prazo = linhaPrazo
    ? { texto: corta(limpa(linhaPrazo), 90), dias: diasAte(linhaPrazo) }
    : undefined

  const fatosBloco = secao(ficha, 'Fatos')
  const fatos = ficha
    ? {
        confirmados: contaItens(subsecao(fatosBloco, 'Confirmados')),
        relatados: contaItens(subsecao(fatosBloco, 'Relatados')),
        lacunas: contaItens(subsecao(fatosBloco, 'Lacunas')),
      }
    : undefined

  const linhas = secao(ficha, 'Matriz de provas')
    .split('\n')
    .filter(l => l.startsWith('|') && !/^\|\s*-/.test(l) && !/Status\s*\|/.test(l) && !/…/.test(l))
  const status = linhas.map(l => (l.split('|').filter(Boolean).pop() ?? '').toLowerCase())
  const provas = linhas.length
    ? {
        tem: status.filter(s => /^\s*tem/.test(s)).length,
        parcial: status.filter(s => /parcial/.test(s)).length,
        falta: status.filter(s => /falta|pedir/.test(s) && !/parcial/.test(s)).length,
      }
    : undefined

  const lista = await $.fs.list(`${dir}/entrada`).catch(() => [])
  const nomes = new Set<string>(
    lista
      .filter((f: { kind: string; name: string }) => f.kind === 'file' && !f.name.startsWith('.'))
      .map((f: { name: string }) => f.name.replace(/\.[^.]+$/, '')),
  )

  const pendCaso = secao(state, 'Pendências do Doc')
    .split('\n')
    .filter(l => /^- /.test(l))
    .map(l => corta(limpa(l.slice(2)).split(':')[0] ?? '', 70))
    .slice(0, 4)

  return {
    dir,
    cliente: limpa(cliente ?? ''),
    projeto: limpa(projeto),
    area,
    tier,
    ref,
    aberto,
    etapasFeitas: feitas,
    etapasTotal: fase.length,
    etapaAtual,
    trilha,
    proximo,
    prazo,
    fatos,
    provas,
    entrada: nomes.size,
    pendCaso,
    snap: { brief, corte, thor, feitas, total: fase.length, entregue },
    agenda: proximaAgenda(ficha),
    temFicha: Boolean(ficha),
  }
}

const pendenciasTasks = async ($: any, raiz: string, m: Modelo | undefined): Promise<Pendencia[]> => {
  const tasks: string = await $.fs.read(`${raiz}/TASKS.md`).catch(() => '')
  if (!tasks) return []
  const out: Pendencia[] = []
  let ignorar = false
  const slug = m?.dir.match(/\/(?:clientes|holding|mentorias)\/([^/]+)/)?.[1] ?? '#'
  const nome = (m?.cliente ?? '#').toLowerCase()
  for (const l of tasks.split('\n')) {
    if (l.startsWith('## ')) ignorar = /Feito|Um dia/i.test(l)
    if (ignorar || !/^- \[ \]/.test(l)) continue
    const negrito = l.match(/\*\*(.+?)\*\*/)?.[1]
    const texto = corta(limpa(negrito ?? l.replace(/^- \[ \]\s*/, '').split(' — ')[0] ?? '').replace(/:$/, ''), 90)
    const baixo = l.toLowerCase()
    out.push({ texto, doCaso: baixo.includes(slug) || baixo.includes(nome), linha: l })
  }
  return [...out.filter(p => p.doCaso), ...out.filter(p => !p.doCaso)]
}


// ---------- registro de pedidos (.bancada/pedidos.jsonl, na raiz da bancada) ----------
// Uma linha por mudança no STATE.md do caso: brief, Corte, Thor, etapa, entrega.
// O STATE.md continua sendo a fonte da verdade; o registro só guarda o "quando".

const REGISTRO = '.bancada/pedidos.jsonl'

const lerRegistro = async ($: any, raiz: string): Promise<Registro[]> => {
  const txt: string = await $.fs.read(`${raiz}/${REGISTRO}`).catch(() => '')
  return txt
    .split('\n')
    .filter(Boolean)
    .flatMap(l => {
      try {
        return [JSON.parse(l) as Registro]
      } catch {
        return []
      }
    })
}

const relativo = (raiz: string, dir: string): string => dir.slice(raiz.length + 1)

const mudancas = (antes: Snap | undefined, agora: Snap): string[] => {
  if (!antes) return ['registro iniciado']
  const ev: string[] = []
  if (!antes.brief && agora.brief) ev.push('brief escrito')
  if (antes.corte !== agora.corte)
    ev.push(agora.corte === 'ok' ? 'Corte aprovou' : agora.corte === 'ajustar' ? 'Corte pediu ajuste' : 'Corte reaberta')
  if (antes.thor !== agora.thor)
    ev.push(agora.thor === 'ok' ? 'Thor aprovou' : agora.thor === 'ajustar' ? 'Thor devolveu' : 'Thor reaberto')
  if (agora.feitas > antes.feitas) ev.push(`etapa ${agora.feitas} de ${agora.total} concluída`)
  if (agora.total > antes.total) ev.push(`${agora.total - antes.total} etapa(s) nova(s)`)
  if (!antes.entregue && agora.entregue) ev.push('entregue')
  return ev
}

const registrar = async ($: any, m: Modelo): Promise<void> => {
  const raiz = raizDe(m.dir)
  const rel = relativo(raiz, m.dir)
  const todos = await lerRegistro($, raiz)
  const ultimo = [...todos].reverse().find(r => r.caso === rel)
  const ev = mudancas(ultimo?.snap, m.snap)
  if (!ev.length) return
  const linha: Registro = { ts: new Date().toISOString(), caso: rel, eventos: ev, snap: m.snap }
  const atual: string = await $.fs.read(`${raiz}/${REGISTRO}`).catch(() => '')
  await $.fs.write(`${raiz}/${REGISTRO}`, `${atual}${atual && !atual.endsWith('\n') ? '\n' : ''}${JSON.stringify(linha)}\n`)
}

const quando = (iso: string): string => {
  const d = new Date(iso)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${p(d.getDate())}/${p(d.getMonth() + 1)} ${p(d.getHours())}:${p(d.getMinutes())}`
}

const duracao = (desde: string): string => {
  const min = Math.max(0, Math.round((Date.now() - new Date(desde).getTime()) / 60000))
  const d = Math.floor(min / 1440)
  const h = Math.floor((min % 1440) / 60)
  return d ? `${d}d ${h}h` : h ? `${h}h ${min % 60}min` : `${min}min`
}

// ---------- pendências do TASKS.md: concluir (vai para "Feito" com data) e desfazer ----------

const concluirTarefa = async ($: any, raiz: string, p: Pendencia): Promise<void> => {
  const antes: string = await $.fs.read(`${raiz}/TASKS.md`).catch(() => '')
  const linhas = antes.split('\n')
  const i = linhas.indexOf(p.linha)
  const iFeito = linhas.findIndex(l => /^## Feito/.test(l))
  if (i < 0 || iFeito < 0) {
    $.ui.toast('Não achei a pendência ou a seção "Feito" no TASKS.md; nada mudou.')
    return
  }
  const d = new Date()
  const hoje = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  const feita = `${p.linha.replace(/^- \[ \]/, '- [x]')} ✓ ${hoje}`
  linhas.splice(i, 1)
  const destino = linhas.findIndex(l => /^## Feito/.test(l))
  linhas.splice(destino + 1, 0, feita)
  const depois = linhas.join('\n')
  await $.fs.write(`${raiz}/TASKS.md`, depois)
  await update($, desfazer, () => ({ raiz, antes, depois, texto: p.texto }))
  $.ui.invalidate('ui.render')
}

const desfazerUltima = async ($: any): Promise<void> => {
  const u = await read($, desfazer)
  if (!u) return
  const atual: string = await $.fs.read(`${u.raiz}/TASKS.md`).catch(() => '')
  if (atual !== u.depois) {
    $.ui.toast('O TASKS.md mudou depois do check; desfaça à mão.')
  } else {
    await $.fs.write(`${u.raiz}/TASKS.md`, u.antes)
  }
  await update($, desfazer, () => null)
  $.ui.invalidate('ui.render')
}

// ---------- ações: só escrevem o pedido na caixa de mensagem ----------

const pedidos = (m: Modelo | undefined): Array<{ k: string; rotulo: string; cor: string; texto: string }> => {
  const nome = m ? `caso ${m.cliente} × ${m.projeto}` : 'caso desta conversa'
  const doCaso = `do ${nome}`
  const noCaso = `no ${nome}`
  const d = new Date()
  const hoje = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  return [
    { k: 'juris', rotulo: 'Juris', cor: 'text', texto: `Pesquise jurisprudência para a tese ${doCaso} e grave em pesquisas/ com o nível de cada citação.` },
    { k: 'corte', rotulo: 'Corte', cor: 'text', texto: `Rode a Corte R1-R4 no entregável atual ${doCaso}.` },
    { k: 'thor', rotulo: 'Thor', cor: 'text', texto: `Submeta o entregável atual ${doCaso} ao Thor.` },
    { k: 'adv', rotulo: 'Adversário', cor: LARANJA, texto: [
      `Faça a análise adversarial ${doCaso} (voz da parte contrária, método do prisma-julgador-os; se o plugin estiver instalado, use a skill voz-da-parte-contraria).`,
      'Leia o entregável atual, a FICHA e entrada/ como um advogado adversário competente: "se esta peça chegasse contra o meu cliente, por onde eu a desmontaria?". Ataque só onde há vulnerabilidade real.',
      'Cubra as 5 frentes: (1) contradições exploráveis, entre afirmações ou com documento juntado; (2) fundamento fraco ou sem subsunção aos fatos; (3) precedente contrário; (4) pedidos vulneráveis; (5) preliminares prováveis.',
      'Cada achado: trecho atacável · linha de ataque · lastro. Precedente contrário só se já validado em pesquisas/ (número + trecho da ementa); sem isso, rotule "linha de ataque provável, sem precedente coletado" e sugira a busca. Nunca complete julgado, relator ou número de memória.',
      'Só mérito (integridade do documento é do blindagem-peticao-os). Aponte vulnerabilidade, nunca desfecho. Não reescreva a peça.',
      `Grave em pesquisas/${hoje}-analise-adversarial.md.`,
    ].join('\n') },
    { k: 'juiz', rotulo: 'Juiz', cor: ROXO, texto: [
      `Faça a análise do juiz ${noCaso} (voz do magistrado, método do prisma-julgador-os; se o plugin estiver instalado, use a skill voz-do-magistrado).`,
      'Abra com o rótulo fixo: "Leitura simulada com base no padrão público coletado — não é manifestação do magistrado, nem previsão de decisão." Leia o padrão do órgão no exercício da função, nunca a pessoa física do juiz.',
      'Sem perfil do órgão nem precedentes validados em pesquisas/, diga na primeira linha: "Sem dado coletado deste órgão — leitura de julgador diligente genérico." e não cite precedente.',
      'Saída em 3 blocos, cada ponto com lastro (fato confirmado da FICHA, precedente validado com número + trecho, ou dispositivo): (1) o que tenderia a estranhar ou rejeitar; (2) trechos que pedem reforço e o fundamento que preencheria o gap; (3) o que já está alinhado.',
      'Fato só relatado ou lacuna da FICHA conta como fragilidade de prova. Nunca afirme "este juízo rejeita X" sem lastro coletado; nunca preveja resultado; não reescreva a peça.',
      `Grave em pesquisas/${hoje}-analise-do-juiz.md.`,
    ].join('\n') },
    { k: 'docx', rotulo: '.docx', cor: AZUL, texto: `Gere o .docx timbrado do entregável atual ${doCaso} (/entregar).` },
    { k: 'pdf', rotulo: 'PDF', cor: AZUL, texto: `Gere o PDF timbrado do entregável atual ${doCaso} (só com selo de Thor).` },
    { k: 'wa', rotulo: 'WhatsApp', cor: VERDE, texto: `Rascunhe a mensagem de WhatsApp ao cliente ${doCaso}: ache o contato no CADASTRO.md (ou na FICHA), mostre a prévia e só envie quando eu disser "enviar".` },
    { k: 'drive', rotulo: 'Drive', cor: AMBAR, texto: `Suba ao Drive os entregáveis ${doCaso} (/subir-drive).` },
  ]
}

const casoDoArgumento = async ($: any, arg: string): Promise<string | undefined> => {
  const raiz: string = await $.session.root().catch(() => $.session.cwd())
  const abs = arg.startsWith('/') ? arg : `${raiz}/${arg.replace(/^\.\//, '').replace(/\/$/, '')}`
  const dir = abs.endsWith('/STATE.md') ? abs.slice(0, -9) : abs
  return (await $.fs.exists(`${dir}/STATE.md`)) ? dir : undefined
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'bancada',
      description: 'Abre a Bancada; com um caminho, fixa o caso desta conversa',
      argumentHint: '[clientes/<cliente>/<tipo>/<area>/<projeto>]',
    })
    void $.ui.open({ id: PANE, title: 'Bancada' })
    return next(e)
  })

  on('command.run', { command: 'bancada' }, async ($, e) => {
    const arg = e.args.trim()
    if (arg) {
      const dir = await casoDoArgumento($, arg)
      if (!dir) return { text: `Não achei STATE.md em ${arg}.` }
      await update($, caso, () => dir)
    }
    await $.ui.open({ id: PANE, title: 'Bancada' })
    const atual = await read($, caso)
    return { text: atual ? `Bancada aberta no caso ${atual.split('/').slice(-3).join('/')}.` : 'Bancada aberta (sem caso nesta conversa ainda).' }
  })

  // O caso da conversa é o projeto cujo arquivo a conversa leu ou editou por último.
  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    const tool = (e as { tool?: string }).tool ?? ''
    const p = (e as { file_path?: unknown }).file_path
    if (typeof p === 'string' && /^(Read|Edit|Write|MultiEdit)$/.test(tool)) {
      const dir = projetoDe(p)
      if (dir && dir !== (await read($, caso)) && (await $.fs.exists(`${dir}/STATE.md`)))
        await update($, caso, () => dir)
      else if (dir) $.ui.invalidate('ui.render')
      if (dir && (p.endsWith('/STATE.md') || tool === 'Read')) {
        const m = await montaModelo($, dir).catch(() => undefined)
        if (m) await registrar($, m).catch(() => undefined)
      }
    }
    return ran
  })

  on('turn.complete', async ($, e, next) => {
    $.ui.invalidate('ui.render')
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const dir = await read($, caso)
    const m = dir ? await montaModelo($, dir) : undefined
    const raiz = dir ? raizDe(dir) : await $.session.root().catch(() => $.session.cwd())
    const pend = await pendenciasTasks($, raiz, m)
    const ultimoCheck = await read($, desfazer)
    const meus = m ? (await lerRegistro($, raiz)).filter(r => r.caso === relativo(raiz, m.dir)) : []
    const iEntrega = meus.map(r => r.eventos.includes('entregue')).lastIndexOf(true)
    const inicioPedido = meus[iEntrega + 1]?.ts
    const preenche = (texto: string) => () => void $.prompt.fill({ text: texto })

    const Cartao = (p: { cor?: string; borda?: string; children?: any; k: string }) => (
      <Box key={p.k} flexDirection="column" borderStyle={p.borda ?? 'round'} borderColor={p.cor ?? 'subtle'} paddingX={1} marginBottom={1}>
        {p.children}
      </Box>
    )

    const acoes = pedidos(m)
    const botao = (a: (typeof acoes)[number]) => (
      <Box key={`b-${a.k}`} borderStyle="round" borderColor={a.cor === 'text' ? 'subtle' : a.cor} backgroundColor={fundo(e.surface, a.cor)} paddingX={1}>
        <Button key={a.k} plain onPress={preenche(a.texto)}>
          <Text color={a.cor}>{a.rotulo}</Text>
        </Button>
      </Box>
    )
    const grupo = (rotulo: string, cor: string, ks: string[]) => (
      <Box key={`g-${rotulo}`} flexDirection="column" marginTop={1}>
        <Text color={cor} dimColor={cor === 'text'}>{rotulo}</Text>
        <Box flexDirection="row" flexWrap="wrap" columnGap={1}>
          {acoes.filter(a => ks.includes(a.k)).map(botao)}
        </Box>
      </Box>
    )

    const prazoCor = (d: number | undefined) =>
      d === undefined ? 'subtle' : d <= 0 ? VERMELHO : d <= 5 ? AMBAR : 'subtle'

    return (
      <Box flexDirection="column" width={e.props.bodyColumns}>
        {!m && (
          <Cartao k="vazio" borda="dashed" cor={APAGADO}>
            <Text weight="medium">Nenhum caso nesta conversa</Text>
            <Text dimColor>Abra ou edite o STATE.md de um projeto, ou use /bancada clientes/…/projeto.</Text>
          </Cartao>
        )}

        {m && (
          <Cartao k="caso">
            <Box flexDirection="row" justifyContent="space-between">
              <Text dimColor>Caso desta conversa</Text>
              <Text dimColor>{[m.area, m.tier].filter(Boolean).join(' · ')}</Text>
            </Box>
            <Text weight="semibold">{m.cliente}</Text>
            <Text dimColor>{[m.projeto, m.ref && !/sem processo/i.test(m.ref) ? m.ref : ''].filter(Boolean).join(' · ')}</Text>
            <Box flexDirection="row">
              <Button key="abrir-dossie" plain onPress={preenche('/dossie')}>
                <Text color={AZUL}>Dossiê do caso ↵</Text>
              </Button>
            </Box>
          </Cartao>
        )}

        {m && (
          <Cartao k="trilha">
            <Box flexDirection="row" justifyContent="space-between">
              <Text dimColor>{m.aberto ? `Aberto em ${m.aberto.split('-').reverse().join('/')}` : 'Pedido'}</Text>
              <Text dimColor>{m.etapasTotal ? `${m.etapasFeitas} de ${m.etapasTotal} etapas` : ''}</Text>
            </Box>
            <Box flexDirection="row" columnGap={1} flexWrap="wrap">
              {m.trilha.map(t => (
                <Box key={t.nome} borderStyle={t.tracejado ? 'dashed' : t.atual ? 'bold' : 'round'} borderColor={t.cor} paddingX={1}>
                  <Text color={t.cor}>{t.cor === VERDE ? `✓ ${t.nome}` : t.nome}</Text>
                </Box>
              ))}
            </Box>
            {m.etapaAtual && <Text dimColor>Agora: {corta(m.etapaAtual, 110)}</Text>}
            {inicioPedido && (
              <Text color={AZUL}>Pedido em curso há {duracao(inicioPedido)} · desde {quando(inicioPedido)}</Text>
            )}
            {meus.slice(-3).reverse().map(r => (
              <Text key={`r-${r.ts}`} dimColor>{quando(r.ts)} · {r.eventos.join(' · ')}</Text>
            ))}
          </Cartao>
        )}

        {m && m.proximo && (
          <Cartao k="proximo" borda="bold" cor={AZUL}>
            <Text color={AZUL}>→ Próximo passo</Text>
            <Text>{m.proximo}</Text>
            <Button key="continuar" variant="primary" onPress={preenche(`Retome o caso ${m.cliente} × ${m.projeto} a partir do Próximo passo do STATE.md.`)}>
              Continuar daqui ↵
            </Button>
          </Cartao>
        )}

        {m && (m.fatos || m.provas) && (
          <Cartao k="ficha">
            <Box flexDirection="row" justifyContent="space-between">
              <Text dimColor>O que sabemos (FICHA)</Text>
              <Text dimColor>entrada/ · {m.entrada} docs</Text>
            </Box>
            {m.fatos && (
              <Box flexDirection="row" columnGap={2}>
                <Text color={VERDE}>{m.fatos.confirmados} confirmados</Text>
                <Text color={AMBAR}>{m.fatos.relatados} relatados</Text>
                <Text color={VERMELHO}>{m.fatos.lacunas} lacunas</Text>
              </Box>
            )}
            {m.provas && (
              <Box flexDirection="row" columnGap={2}>
                <Text dimColor>Provas:</Text>
                <Text color={VERDE}>{m.provas.tem} tem</Text>
                <Text color={AMBAR}>{m.provas.parcial} parcial</Text>
                <Text color={VERMELHO}>{m.provas.falta} falta</Text>
              </Box>
            )}
          </Cartao>
        )}

        <Cartao k="acoes">
          <Text dimColor>Ações · escrevem o pedido; você dá Enter</Text>
          {grupo('Ler e auditar', 'text', ['juris', 'corte', 'thor'])}
          {grupo('O outro lado', 'text', ['adv', 'juiz'])}
          {grupo('Produzir', AZUL, ['docx', 'pdf'])}
          {grupo('Sai do escritório', AMBAR, ['wa', 'drive'])}
        </Cartao>

        {m && m.prazo && (
          <Cartao k="prazo" cor={prazoCor(m.prazo.dias)}>
            <Box flexDirection="row" justifyContent="space-between">
              <Text color={prazoCor(m.prazo.dias)}>Prazo do caso</Text>
              <Text color={prazoCor(m.prazo.dias)} weight="semibold">
                {m.prazo.dias === undefined ? '' : m.prazo.dias < 0 ? `vencido ${-m.prazo.dias}d` : m.prazo.dias === 0 ? 'hoje' : `${m.prazo.dias} dias`}
              </Text>
            </Box>
            <Text color={prazoCor(m.prazo.dias)}>{m.prazo.texto}</Text>
          </Cartao>
        )}

        {m && m.agenda && (
          <Cartao k="agenda" cor={prazoCor(m.agenda.dias)}>
            <Box flexDirection="row" justifyContent="space-between">
              <Text color={prazoCor(m.agenda.dias)}>Próximo compromisso</Text>
              <Text color={prazoCor(m.agenda.dias)} weight="semibold">
                {m.agenda.dias === 0 ? 'hoje' : `${m.agenda.dias} dias`}
              </Text>
            </Box>
            <Text>{m.agenda.quando} · {m.agenda.oque}</Text>
            {m.agenda.levar && <Text dimColor>Levar: {m.agenda.levar}</Text>}
          </Cartao>
        )}
        {m && !m.agenda && m.temFicha && (
          <Cartao k="agenda" borda="dashed" cor={APAGADO}>
            <Text color={APAGADO}>Sem audiência, perícia ou reunião na Agenda do caso (FICHA)</Text>
          </Cartao>
        )}

        <Box key="pend" flexDirection="column" borderStyle="bold" borderColor={VERMELHO} backgroundColor={fundo(e.surface, VERMELHO)} paddingX={1}>
          <Box flexDirection="row" justifyContent="space-between">
            <Text color={VERMELHO} weight="semibold">⚠ Pendências em aberto · TASKS.md</Text>
            <Text color={VERMELHO} weight="semibold">{pend.length + (m?.pendCaso.length ?? 0)}</Text>
          </Box>
          {m && m.pendCaso.length > 0 && <Text color={VERMELHO} dimColor>deste caso (STATE.md)</Text>}
          {m?.pendCaso.map(p => (
            <Text key={`c-${p}`} color={VERMELHO}>▌ {p}</Text>
          ))}
          {pend.filter(p => p.doCaso).map((p, i) => (
            <Box key={`t-${i}`} flexDirection="row" columnGap={1}>
              <Button key={`ok-t-${i}`} plain onPress={() => void concluirTarefa($, raiz, p)}>☐</Button>
              <Text color={VERMELHO}>{p.texto}</Text>
            </Box>
          ))}
          {pend.some(p => !p.doCaso) && <Text color={VERMELHO} dimColor>outros casos</Text>}
          {pend.filter(p => !p.doCaso).slice(0, 8).map((p, i) => (
            <Box key={`o-${i}`} flexDirection="row" columnGap={1}>
              <Button key={`ok-o-${i}`} plain onPress={() => void concluirTarefa($, raiz, p)}>☐</Button>
              <Text dimColor>{p.texto}</Text>
            </Box>
          ))}
          {pend.filter(p => !p.doCaso).length > 8 && (
            <Text dimColor>… e mais {pend.filter(p => !p.doCaso).length - 8}</Text>
          )}
          {ultimoCheck && (
            <Box flexDirection="row" columnGap={1}>
              <Text color={VERDE}>✓ {corta(ultimoCheck.texto, 50)} foi para "Feito"</Text>
              <Button key="desfazer" onPress={() => void desfazerUltima($)}>Desfazer</Button>
            </Box>
          )}
          <Button key="anotar" plain onPress={preenche(`Anote no TASKS.md, em "## Ativas" e no formato do arquivo, esta pendência${m ? ` do caso ${m.cliente} × ${m.projeto}` : ''}: `)}>
            + anotar pendência
          </Button>
        </Box>
      </Box>
    )
  })
}
