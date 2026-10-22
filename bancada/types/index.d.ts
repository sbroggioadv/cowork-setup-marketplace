export type CasoDir = string
export type Desfazer = { raiz: string; antes: string; depois: string; texto: string }

declare module 'claude-code' {
  interface PluginState {
    bancada: { caso: CasoDir; desfazer: Desfazer | null }
  }
}
