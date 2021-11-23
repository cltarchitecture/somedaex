import vueComponent from './LoadFile.vue'
import { Task } from '../../lib/task'

export interface LoadFileConfig {
  path: string
  format: string | null
}

export default class LoadFile extends Task {
  static readonly id = 'loadFile'
  static readonly label = 'Load data from a file'
  static readonly component = vueComponent

  config: LoadFileConfig = {
    path: '',
    format: null
  }
}
