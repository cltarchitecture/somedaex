import {
  ChildProcess,
  execFile,
  ExecFileOptions,
  spawn,
  SpawnOptions
} from 'child_process'
import { promisify } from 'util'


const PIPENV = "pipenv"
const execFilePromise = promisify(execFile)


export class Pipenv {

  #path: string

  constructor(path: string) {
    this.#path = path
  }

  async #exec(cmd: string[], options: ExecFileOptions = {}) {
    return execFilePromise(PIPENV, cmd, {
      cwd: this.#path,
      ...options,
    })
  }

  async isInitialized() {
    return this.#exec(["--venv"]).then(() => true).catch((err) => {
      if (err.code === 1) {
        return false
      }
      throw err
    })
  }

  async getVenvPath() {
    return this.#exec(["--venv"]).then(({stdout}) => stdout.trim())
  }


  // async init() {
  //    this.#exec(["--three"]).then(() => this
  //      const venv_path = stdout.trim()
  //    })
  // }

  async install() {
    return this.#exec(["install"])
  }

  async remove() {
    this.#exec(["--rm"])
  }

  async run(cmd: string[], options: ExecFileOptions = {}) {
    return this.#exec(["run", ...cmd], options)
  }

  spawn(cmd: string[], options: SpawnOptions = {}): ChildProcess {
    return spawn(PIPENV, ["run", ...cmd], {
      cwd: this.#path,
      ...options,
    })
  }

}
