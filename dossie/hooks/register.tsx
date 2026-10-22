import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

// Dossiê do caso v0.1 — painel de consulta: o que se sabe do caso desta conversa.
// Só leitura, sem botões que executam. Lê STATE.md, FICHA.md, o CADASTRO.md do
// cliente e a raiz do projeto; nunca grava nada. Funciona sozinho ou ao lado da Bancada.

const PANE = 'dossie'
const caso = atom({ plugin: 'dossie', key: 'caso' } as const, '')

// Mesma paleta da Bancada (bancada-mods/DESENHO.md): um significado por cor.
const AZUL = 'suggestion' // em curso
const VERDE = 'success' // provado, concluído
const AMBAR = 'warning' // atenção, só relato, a decidir
const VERMELHO = 'error' // lacuna, bloqueio
const ROXO = 'merged' // decisão fixada: não muda sem avisar
const APAGADO = 'inactive' // ainda não existe

// App: tinta translúcida; terminal: só chaves de tema (sem transparência).
const TINTA: Record<string, string> = { [ROXO]: '#7F77DD24' }
const fundo = (surface: string, cor: string): string | undefined =>
  surface === 'terminal' ? undefined : TINTA[cor]

type Decisao = { data: string; quem: string; texto: string; aDecidir: boolean }
type Marco = { data: string; fato: string; cor: string }
type Parte = { rotulo: string; texto: string }
type Peca = { nome: string; status: string; cor: string; data: string; maisRecente: boolean }
type Dossie = {
  cliente: string
  projeto: string
  area: string
  tier: string
  decisoes: Decisao[]
  cronologia: Marco[]
  partes: Parte[]
  valor: string
  valorNota: { texto: string; atrasado: boolean } | undefined
  conflito: string
  honorarios: string
  hon: { contratado: number; recebido: number; aVencer: number; vencido: number; em: string } | undefined
  pecas: Peca[]
}

// ---------- leitura do markdown ----------

const secao = (md: string, titulo: string): string => {
  const ini = md.search(new RegExp(`^## ${titulo}`, 'm'))
  if (ini < 0) return ''
  const resto = md.slice(ini).split('\n').slice(1).join('\n')
  const fim = resto.search(/^## /m)
  return (fim < 0 ? resto : resto.slice(0, fim)).trim()
}

const limpa = (s: string): string =>
  s.replace(/\*\*|`|\[\[|\]\]/g, '').replace(/\s+/g, ' ').trim()

const corta = (s: string, n: number): string =>
  s.length > n ? `${s.slice(0, n - 1).replace(/[\s.,;:]+$/, '')}…` : s

const semDocumentos = (s: string): string =>
  s.replace(/\s*\((?:CPF|CNPJ|RG|OAB|CRECI)[^)]*\)/gi, '').replace(/\s{2,}/g, ' ')

const dataBR = (iso: string): string => {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})/)
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso
}

const corDoStatus = (status: string): string => {
  const t = status.toLowerCase()
  if (/lacuna|falta/.test(t) && !/confirmad/.test(t)) return VERMELHO
  if (/relatad|lacuna/.test(t)) return AMBAR
  if (/confirmad|tem\b/.test(t)) return VERDE
  return 'subtle'
}

// Caminho de arquivo tocado → pasta do projeto (mesma regra da Bancada).
const projetoDe = (p: string): string | undefined => {
  const m = p.match(/^(.*?\/)(clientes|holding|mentorias)\/(.*)$/)
  if (!m) return undefined
  const seg = (m[3] ?? '').split('/')
  const base = `${m[1]}${m[2]}`
  if (m[2] === 'clientes' && seg.length >= 5 && /^(contencioso|consultivo)$/.test(seg[1] ?? ''))
    return `${base}/${seg.slice(0, 4).join('/')}`
  if (m[2] === 'holding' && seg.length >= 2) return `${base}/${seg[0]}`
  if (m[2] === 'mentorias' && seg.length >= 3) return `${base}/${seg.slice(0, 2).join('/')}`
  return undefined
}

const reais = (s: string | undefined): number => {
  const m = (s ?? '').match(/R\$\s*([\d.]+(?:,\d{1,2})?)/)
  return m ? Number((m[1] ?? '0').replace(/\./g, '').replace(',', '.')) : 0
}

const brl = (n: number): string =>
  `R$ ${n.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`

const diasDesde = (iso: string): number | undefined => {
  const m = iso.match(/(\d{4})-(\d{2})-(\d{2})/)
  if (!m) return undefined
  return Math.floor((Date.now() - new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])).getTime()) / 86400000)
}

const cadastroDe = (dir: string): string | undefined => {
  const m = dir.match(/^(.*?\/clientes\/[^/]+)\//)
  return m ? `${m[1]}/cadastro/CADASTRO.md` : undefined
}

const ehEntregavel = (nome: string): boolean =>
  /\.(docx|md|pdf|xlsx|html)$/i.test(nome) &&
  !/^(STATE|FICHA|CLAUDE)\.md$/i.test(nome) &&
  !/^CORTE-R1-R4/i.test(nome) &&
  !/-protocolo\.pdf$/i.test(nome)

const montaDossie = async ($: any, dir: string): Promise<Dossie | undefined> => {
  const state: string = await $.fs.read(`${dir}/STATE.md`).catch(() => '')
  if (!state) return undefined
  const ficha: string = await $.fs.read(`${dir}/FICHA.md`).catch(() => '')
  const cad = cadastroDe(dir)
  const cadastro: string = cad ? await $.fs.read(cad).catch(() => '') : ''

  const titulo = state.match(/^# STATE — (.+)$/m)?.[1] ?? dir.split('/').pop() ?? ''
  const [cliente, projeto = ''] = titulo.split(' × ')

  const decisoes: Decisao[] = secao(state, 'Decisões fixadas')
    .split('\n')
    .filter(l => /^- /.test(l))
    .map(l => {
      const cab = l.match(/^- (\d{4}-\d{2}-\d{2})\s*(?:\(([^)]*)\))?:?\s*(.*)$/)
      const texto = limpa(cab?.[3] ?? l.slice(2))
      return {
        data: cab?.[1] ? dataBR(cab[1]) : '',
        quem: limpa(cab?.[2] ?? '').split(/[,;]/)[0] ?? '',
        texto: corta(texto, 150),
        aDecidir: /recomenda[çc][ãa]o|ainda n[ãa]o decidid|\[decidir\]/i.test(l),
      }
    })

  const cronologia: Marco[] = secao(ficha, 'Cronologia')
    .split('\n')
    .filter(l => l.startsWith('|') && !/^\|\s*-/.test(l) && !/^\|\s*Data\s*\|/i.test(l) && !/…/.test(l))
    .map(l => {
      const c = l.split('|').slice(1, -1).map(x => limpa(x))
      return { data: c[0] ?? '', fato: corta(c[1] ?? '', 110), cor: corDoStatus(c[c.length - 1] ?? '') }
    })

  const blocoPartes = secao(ficha, 'Partes e foro')
  const partes: Parte[] = blocoPartes
    .split('\n')
    .filter(l => /^- [^:]{2,40}:/.test(l) && !/^- Valor d/i.test(l))
    .map(l => {
      const i = l.indexOf(':')
      return { rotulo: limpa(l.slice(2, i)), texto: corta(semDocumentos(limpa(l.slice(i + 1))), 120) }
    })

  // Modelo novo: "Valor da causa ou do negócio: R$ X · índice: Y · data-base: AAAA-MM-DD"; antigo: "Valor do negócio: R$ X".
  const linhaValor = `${blocoPartes}\n${state}`
    .split('\n')
    .find(l => /Valor d[ao] (?:causa|neg[óo]cio)/i.test(l) && /R\$\s*\d/.test(l))
  const mValor = linhaValor?.match(/Valor d[ao] (causa ou do neg[óo]cio|causa|neg[óo]cio):\s*(R\$\s*[\d.,]+)/i)
  const valor = mValor
    ? `${/ou do/i.test(mValor[1] ?? '') ? 'Causa ou negócio' : /causa/i.test(mValor[1] ?? '') ? 'Causa' : 'Negócio'}: ${mValor[2]}`
    : ''
  const indice = limpa(linhaValor?.match(/índice:\s*([^·\n]+)/i)?.[1] ?? '')
  const base = linhaValor?.match(/data-base:\s*(\d{4}-\d{2}-\d{2})/i)?.[1]
  const idade = base ? diasDesde(base) : undefined
  const valorNota =
    mValor && (indice || base) && !/</.test(indice)
      ? {
          texto: [indice, base ? `data-base ${dataBR(base)}` : ''].filter(Boolean).join(' · ') + (idade !== undefined && idade > 30 ? ` · ${idade} dias atrás` : ''),
          atrasado: idade !== undefined && idade > 30,
        }
      : undefined

  const conflito = limpa(state.match(/^.*conflito de interesses.*$/im)?.[0] ?? '')

  const vinculo = secao(cadastro, 'Vínculo com o escritório')
  const linhaHon = vinculo.split('\n').find(l => /honor[áa]rios/i.test(l)) ?? ''
  const honorarios = /<[^>]+>|Modalidade:\s*mensal \| por demanda \| êxito/i.test(linhaHon) || !linhaHon
    ? ''
    : corta(limpa(linhaHon.replace(/^- /, '')), 120)

  const linhaPago = vinculo.split('\n').find(l => /^- Honorários \(atualizar/i.test(l)) ?? ''
  const pega = (rotulo: string) => linhaPago.match(new RegExp(`${rotulo}\\s*(R\\$\\s*[\\d.,]+)`, 'i'))?.[1]
  const hon = pega('contratado') || pega('recebido')
    ? {
        contratado: reais(pega('contratado')),
        recebido: reais(pega('recebido')),
        aVencer: reais(pega('a vencer')),
        vencido: reais(pega('vencido')),
        em: dataBR(linhaPago.match(/atualizado em\s*(\d{4}-\d{2}-\d{2})/i)?.[1] ?? ''),
      }
    : undefined

  const lista: Array<{ name: string; kind: string; mtimeMs: number }> = await $.fs.list(dir).catch(() => [])
  const arquivos = lista.filter(f => f.kind === 'file')
  const nomes = new Set(arquivos.map(f => f.name))
  const porTronco = new Map<string, { nome: string; mtime: number; exts: Set<string> }>()
  for (const f of arquivos.filter(f => ehEntregavel(f.name))) {
    const tronco = f.name.replace(/\.[^.]+$/, '')
    const ext = f.name.slice(tronco.length + 1).toLowerCase()
    const atual = porTronco.get(tronco) ?? { nome: tronco, mtime: 0, exts: new Set<string>() }
    atual.exts.add(ext)
    atual.mtime = Math.max(atual.mtime, f.mtimeMs)
    porTronco.set(tronco, atual)
  }
  const ordenadas = [...porTronco.values()].sort((a, b) => b.mtime - a.mtime)
  const pecas: Peca[] = ordenadas.slice(0, 8).map((p, i) => {
    const protocolada = nomes.has(`${p.nome}-protocolo.pdf`)
    const final = p.exts.has('docx') || p.exts.has('pdf')
    const d = new Date(p.mtime)
    return {
      nome: corta(p.nome.replace(/[_-]+/g, ' '), 60),
      status: protocolada ? 'protocolada' : final ? `gerada (.${p.exts.has('docx') ? 'docx' : 'pdf'})` : 'rascunho .md',
      cor: protocolada ? VERDE : i === 0 ? AZUL : final ? 'text' : APAGADO,
      data: `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}`,
      maisRecente: i === 0,
    }
  })

  return {
    cliente: limpa(cliente ?? ''),
    projeto: limpa(projeto),
    area: state.match(/Área:\s*([^·\n]+)/)?.[1]?.trim() ?? '',
    tier: state.match(/Tier:\s*\**(T\d)/)?.[1] ?? '',
    decisoes,
    cronologia,
    partes,
    valor,
    valorNota,
    conflito,
    honorarios,
    hon,
    pecas,
  }
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
      name: 'dossie',
      description: 'Abre o Dossiê do caso; com um caminho, fixa o caso',
      argumentHint: '[clientes/<cliente>/<tipo>/<area>/<projeto>]',
    })
    void $.ui.open({ id: PANE, title: 'Dossiê do caso' })
    return next(e)
  })

  on('command.run', { command: 'dossie' }, async ($, e) => {
    const arg = e.args.trim()
    if (arg) {
      const dir = await casoDoArgumento($, arg)
      if (!dir) return { text: `Não achei STATE.md em ${arg}.` }
      await update($, caso, () => dir)
    }
    await $.ui.open({ id: PANE, title: 'Dossiê do caso' })
    const atual = await read($, caso)
    return { text: atual ? `Dossiê aberto no caso ${atual.split('/').slice(-3).join('/')}.` : 'Dossiê aberto (sem caso nesta conversa ainda).' }
  })

  // Mesmo critério da Bancada: o caso é o projeto cujo arquivo a conversa leu ou editou por último.
  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    const tool = (e as { tool?: string }).tool ?? ''
    const p = (e as { file_path?: unknown }).file_path
    if (typeof p === 'string' && /^(Read|Edit|Write|MultiEdit)$/.test(tool)) {
      const dir = projetoDe(p)
      if (dir && dir !== (await read($, caso)) && (await $.fs.exists(`${dir}/STATE.md`)))
        await update($, caso, () => dir)
      else if (dir) $.ui.invalidate('ui.render')
    }
    return ran
  })

  on('turn.complete', async ($, e, next) => {
    $.ui.invalidate('ui.render')
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const dir = await read($, caso)
    const d = dir ? await montaDossie($, dir) : undefined

    const Cartao = (p: { k: string; titulo: string; fonte?: string; cor?: string; borda?: string; children?: any }) => (
      <Box key={p.k} flexDirection="column" borderStyle={p.borda ?? 'round'} borderColor={p.cor ?? 'subtle'} backgroundColor={p.cor ? fundo(e.surface, p.cor) : undefined} paddingX={1} marginBottom={1}>
        <Box flexDirection="row" justifyContent="space-between">
          <Text color={p.cor && p.cor !== 'subtle' && p.cor !== APAGADO ? p.cor : undefined} dimColor={!p.cor || p.cor === 'subtle' || p.cor === APAGADO}>{p.titulo}</Text>
          {p.fonte ? <Text dimColor>{p.fonte}</Text> : null}
        </Box>
        {p.children}
      </Box>
    )

    if (!d)
      return (
        <Box flexDirection="column" width={e.props.bodyColumns}>
          <Cartao k="vazio" titulo="Nenhum caso nesta conversa" borda="dashed" cor={APAGADO}>
            <Text dimColor>Abra o STATE.md ou a FICHA.md de um projeto, ou use /dossie clientes/…/projeto.</Text>
          </Cartao>
        </Box>
      )

    return (
      <Box flexDirection="column" width={e.props.bodyColumns}>
        <Box key="cab" flexDirection="column" paddingX={1} marginBottom={1}>
          <Box flexDirection="row" justifyContent="space-between">
            <Text weight="semibold">{d.cliente}</Text>
            <Text dimColor>{[d.area, d.tier].filter(Boolean).join(' · ')}</Text>
          </Box>
          <Text dimColor>{d.projeto}</Text>
        </Box>

        <Cartao k="decisoes" titulo="🔒 Decisões fixadas · não mudam sem avisar" fonte="STATE.md" cor={ROXO} borda="bold">
          {d.decisoes.length === 0 && <Text dimColor>Nenhuma decisão fixada ainda.</Text>}
          {d.decisoes.map((x, i) => (
            <Box key={`d-${i}`} flexDirection="column" marginTop={i ? 1 : 0}>
              <Text color={x.aDecidir ? AMBAR : ROXO}>
                {x.aDecidir ? '◇' : '🔒'} {[x.data, x.quem].filter(Boolean).join(' · ')}{x.aDecidir ? ' · a decidir' : ''}
              </Text>
              <Text>{x.texto}</Text>
            </Box>
          ))}
        </Cartao>

        <Cartao k="crono" titulo="Cronologia" fonte="FICHA.md">
          {d.cronologia.length === 0 && <Text dimColor>FICHA sem cronologia.</Text>}
          {d.cronologia.map((x, i) => (
            <Box key={`c-${i}`} flexDirection="row" columnGap={1}>
              <Text color={x.cor}>●</Text>
              <Text dimColor>{x.data}</Text>
              <Text>{x.fato}</Text>
            </Box>
          ))}
          <Box flexDirection="row" columnGap={2} marginTop={d.cronologia.length ? 1 : 0}>
            <Text color={VERDE}>● com prova</Text>
            <Text color={AMBAR}>● só relato</Text>
            <Text color={VERMELHO}>● lacuna</Text>
          </Box>
        </Cartao>

        <Cartao k="partes" titulo="Partes e foro" fonte="FICHA.md">
          {d.partes.length === 0 && <Text dimColor>FICHA sem a seção "Partes e foro".</Text>}
          {d.partes.map((x, i) => (
            <Box key={`p-${i}`} flexDirection="column">
              <Text dimColor>{x.rotulo}</Text>
              <Text>{x.texto}</Text>
            </Box>
          ))}
          <Box marginTop={1}>
            {d.conflito ? (
              <Text color={/sem coincid|sem conflito|nenhum/i.test(d.conflito) ? VERDE : AMBAR}>{corta(d.conflito, 110)}</Text>
            ) : (
              <Box borderStyle="dashed" borderColor={APAGADO} paddingX={1}>
                <Text color={APAGADO}>Checagem de conflito de interesses não registrada no STATE.md</Text>
              </Box>
            )}
          </Box>
        </Cartao>

        <Box key="valores" flexDirection="row" columnGap={1}>
          <Box flexDirection="column" flexGrow={1} borderStyle={d.valor ? 'round' : 'dashed'} borderColor={d.valor ? 'subtle' : APAGADO} paddingX={1} marginBottom={1}>
            <Text dimColor>Valor</Text>
            {d.valor ? <Text weight="semibold">{d.valor}</Text> : <Text color={APAGADO}>sem campo de valor</Text>}
            {d.valorNota && <Text color={d.valorNota.atrasado ? AMBAR : undefined} dimColor={!d.valorNota.atrasado}>{d.valorNota.texto}</Text>}
          </Box>
          <Box flexDirection="column" flexGrow={1} borderStyle={d.honorarios || d.hon ? 'round' : 'dashed'} borderColor={d.honorarios || d.hon ? 'subtle' : APAGADO} paddingX={1} marginBottom={1}>
            <Text dimColor>Honorários</Text>
            {d.honorarios ? <Text>{d.honorarios}</Text> : !d.hon && <Text color={APAGADO}>CADASTRO sem contrato de honorários</Text>}
            {d.hon && (() => {
              const total = d.hon.recebido + d.hon.aVencer + d.hon.vencido || 1
              const n = (v: number) => (v > 0 ? Math.max(1, Math.round((v / total) * 20)) : 0)
              return (
                <Box flexDirection="column">
                  <Box flexDirection="row">
                    <Text color={VERDE}>{'█'.repeat(n(d.hon.recebido))}</Text>
                    <Text color={AMBAR}>{'█'.repeat(n(d.hon.aVencer))}</Text>
                    <Text color={VERMELHO}>{'█'.repeat(n(d.hon.vencido))}</Text>
                  </Box>
                  <Text color={VERDE}>recebido {brl(d.hon.recebido)}</Text>
                  <Text color={AMBAR}>a vencer {brl(d.hon.aVencer)}</Text>
                  <Text color={VERMELHO}>vencido {brl(d.hon.vencido)}</Text>
                  {d.hon.em && <Text dimColor>atualizado em {d.hon.em}</Text>}
                </Box>
              )
            })()}
          </Box>
        </Box>

        <Cartao k="pecas" titulo="Peças do caso" fonte="raiz do projeto">
          {d.pecas.length === 0 && <Text dimColor>Nenhuma peça na raiz do projeto ainda.</Text>}
          {d.pecas.map((x, i) => (
            <Box key={`pc-${i}`} flexDirection="row" justifyContent="space-between" columnGap={1}>
              <Text>{x.nome}</Text>
              <Text color={x.cor}>{x.maisRecente ? `${x.status} · mais recente` : x.status} · {x.data}</Text>
            </Box>
          ))}
        </Cartao>
      </Box>
    )
  })
}
