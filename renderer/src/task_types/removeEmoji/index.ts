import vueComponent from './RemoveEmoji.vue'
import { Task } from '../../lib/task'

enum ReplacementMode {
  ReplaceWithName = 'name',
  ReplaceWithString = 'string',
  Remove = 'remove'
}

export interface RemoveEmojiConfig {
  column: string
  mode: ReplacementMode
  replacement: string
}

export default class RemoveEmoji extends Task {
  static readonly id = 'removeEmoji'
  static readonly label = 'Remove emoji from text'
  static readonly component = vueComponent

  config: RemoveEmojiConfig = {
    column: '',
    mode: ReplacementMode.ReplaceWithName,
    replacement: ''
  }

  get title (): string {
    const column = this.config.column || 'a column'
    switch (this.config.mode) {
      case ReplacementMode.Remove:
        return `Remove emoji from ${column}`
      case ReplacementMode.ReplaceWithName:
        return `Replace emoji in ${column} with their names`
      case ReplacementMode.ReplaceWithString:
        return `Replace emoji in ${column} with "${this.config.replacement}"`
    }
  }
}
