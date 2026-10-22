export type CasoDir = string

declare module 'claude-code' {
  interface PluginState {
    dossie: { caso: CasoDir }
  }
}
