import { TaskConstructor } from '../lib/task'

import caseFold from './caseFold/CaseFold'
import loadFile from './loadFile/LoadFile'
import removeEmoji from './removeEmoji'

/**
 * A list of all registered task types.
 */
export const taskTypes = {
  [caseFold.id]: caseFold,
  [loadFile.id]: loadFile,
  [removeEmoji.id]: removeEmoji
}

export { Task } from '../lib/task'
export type { TaskConstructor } from '../lib/task'

// import type { TaskConstructor } from './task'

// let t: {[id: string]: TaskConstructor} = taskTypes

// t.changeCase

// import { GetTaskState, GetTaskConfig } from './conditionals'

/**
 * The union of all defined task types.
 */
export type TaskType = typeof taskTypes[keyof typeof taskTypes]

/**
 * The union of all defined task type IDs.
 */
export type TaskTypeID = keyof typeof taskTypes

// /**
//  * The union of all defined task state interfaces.
//  */
// export type TaskState = GetTaskState<TaskType>

// /**
//  * The union of all defined task config interfaces.
//  */
// export type TaskConfig = GetTaskConfig<TaskType>

export interface TaskCategory {
  label: string
  tasks: TaskConstructor[]
}

export const categories: TaskCategory[] = [
  {
    label: 'Data Import',
    tasks: [loadFile]
  },
  {
    label: 'Text Cleaning',
    tasks: [caseFold, removeEmoji]
  }
]
