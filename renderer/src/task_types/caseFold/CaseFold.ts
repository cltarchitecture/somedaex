import vueComponent from './CaseFold.vue'
import { Task } from '../../lib/task'

export interface CaseFoldConfig {
  column: string
}

export default class CaseFold extends Task {
  static readonly id = 'caseFold'
  static readonly label = 'Normalize the case of text'
  static readonly component = vueComponent

  config: CaseFoldConfig = {
    column: ''
  }

  get title (): string {
    const column = this.config.column || 'a column'
    return `Normalize ${column} to lower case`
  }
}
