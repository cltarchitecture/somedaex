import { Schema } from '@apache-arrow/esnext-cjs'
import type { Component } from 'vue'


export interface TaskConstructor {

  readonly id: string
  readonly component: Component
  readonly label: string

  new(): Task
}



/**
 * A Task holds the state of a task.
 */
export abstract class Task {

  id: number
  status: string
  source: Task | null = null
  column: string | null = null
  schema: Schema | null = null

  abstract config: {}

  constructor(id = -1) {
    this.id = id
    this.status = 'invalid'
  }

  get type(): TaskConstructor {
    return this.constructor as TaskConstructor
  }

  get title(): string {
    return this.type.label
  }

  toJSON(): string {
    return JSON.stringify({
      type: this.type.id,
      ...this.config,
    })
  }

}

