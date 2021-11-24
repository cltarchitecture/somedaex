export interface TaskCreationParams {
  type: string
  [key: string]: any
}

export class Backend {

  baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  getEvents(): EventSource {
    // return new Promise((resolve, reject) => {
    return new EventSource(this.baseUrl)
      // eventSource.onopen = () => {
      //   resolve(eventSource)
      // }
      // eventSource.onerror = (args) => {
      //   reject(args)
      // }
    // })
  }

  async createTask(params: TaskCreationParams): Promise<{id: number, type: string}> {
    return fetch(this.baseUrl, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(params),
    }).then(async (response) => {
      if (response.ok) {
        return response.json()
      } else {
        const error = await response.text()
        console.error(error)
      }
    })
  }

  async updateTask(id: number, updates: {}): Promise<{}> {
    return fetch(this.baseUrl + id, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(updates),
    }).then(async (response) => {

      if (response.ok) {
        return response.json()
      } else {
        const error = await response.text()
        console.error(error)
      }
    })
  }

  async deleteTask(id: number): Promise<void> {
    return fetch(this.baseUrl + id, {
      method: 'DELETE'
    }).then(async (response) => {
      if (!response.ok) {
        const error = await response.text()
        console.error(error)
      }
    })
  }

}

