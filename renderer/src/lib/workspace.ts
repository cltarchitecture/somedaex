import { reactive, watch } from 'vue'
import { Backend, TaskCreationParams } from './backend'
import { Task, TaskConstructor } from './task'

import { Table } from '@apache-arrow/esnext-cjs'

export class Workspace {

  readonly pipeline: {[id: string]: Task} = reactive({})
  readonly backend: Backend
  readonly events: EventSource

  #newestTask: Task | null = null

  #watchers = {}


  constructor() {
    this.backend = new Backend('http://localhost:8080/')
    this.events = this.backend.getEvents()

    this.events.addEventListener('message', (event) => {
      const e = JSON.parse(event.data)
      console.log(e)

      const task = this.pipeline[e.task]
      if (!task) {
        console.warn('Dropping event for unknown task', e)
        return
      }

      if (e.event == 'status') {
        const task = this.pipeline[e.task]
        task.status = e.value
      }

      if (e.event == 'schema') {
        const task = this.pipeline[e.task]
        if (e.value == null) {
          task.schema = null
        } else {
          const buffer = Buffer.from(e.value, 'base64')
          task.schema = Table.from(buffer).schema
        }
      }
    })
  }

  addTask(type: TaskConstructor) {
    const task = reactive(new type())
    const params: TaskCreationParams = {
      type: type.id,
      ...task.config,
    }

    if (this.#newestTask) {
      task.source = this.#newestTask
      params.source = this.#newestTask.id
    }

    this.backend.createTask(params).then((resp) => {
      task.id = resp.id
      this.pipeline[task.id] = task

      this.#watchers[task.id] = watch(
        () => {return {source: task.source?.id, ...task.config}},
        (newConfig) => {this.backend.updateTask(task.id, newConfig)},
        {deep: true}
      )

      this.#newestTask = task
    })
  }

  deleteTask(task: Task) {
    this.backend.deleteTask(task.id).then(() => {
      delete this.pipeline[task.id]
      this.#watchers[task.id]()
      delete this.#watchers[task.id]

      if (this.#newestTask == task) {
        this.#newestTask = null
      }
    })
  }

}
