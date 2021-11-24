import { ChildProcess } from 'child_process'
import path from 'path'
import { dialog, BrowserWindow, BrowserWindowConstructorOptions } from 'electron'
import { merge } from 'merge-anything'
import { Pipenv } from './pipenv'

const BACKEND_DIR = path.join(__dirname, '../../backend')
const PYTHON_ENV = new Pipenv(BACKEND_DIR)

const DEFAULT_WINDOW_OPTIONS: BrowserWindowConstructorOptions = {
  width: 1280,
  height: 640,
  show: false,
  webPreferences: {
    nodeIntegration: true,
    contextIsolation: false,
    preload: path.join(__dirname, 'preload.js'),
    // additionalArguments: [] -- appended to renderer's process.argv
  }
}



export class Workspace {

  static #instances: Workspace[] = []

  #backend: ChildProcess | null = null;
  #window: BrowserWindow;


  constructor(windowOptions: BrowserWindowConstructorOptions = {}) {
    const options = merge(DEFAULT_WINDOW_OPTIONS, windowOptions)
    this.#window = new BrowserWindow(options)
    this.#window.once('ready-to-show', () => {
      this.#window.show()
    })

    Workspace.#instances.push(this)
  }

  get backend() {
    return this.#backend
  }

  get window() {
    return this.#window
  }

  // check() {

  //   const d = path.join(BACKEND_DIR, '..')

  //   execFile("pipenv", ["--venv"], {cwd: d}, (error, stdout, stderr) => {
  //     console.log(error, stdout, stderr)
  //   })
  // }

  start() {
    this.#backend = PYTHON_ENV.spawn(["python", "main.py", "-l", "28223"], {stdio: 'inherit'})


    // spawn("pipenv", ["run", "python", "main.py", "-l", "28223"], {
    //   cwd: BACKEND_DIR,
    //   stdio: 'inherit'
    // })

    this.#backend.on('error', (err) => {
      dialog.showMessageBox(this.#window, {message: `Unable to start backend process: ${err}`, type: 'error'})
    })

    this.#backend.on('exit', (code, signal) => {
      dialog.showMessageBox(this.#window, {message: `Backend process exited with code ${code} and ${signal}.`, type: 'error'})
    })
  }

  close() {
    this.#window.close()
    this.stop()
  }

  stop() {
    if (this.#backend) {
      this.#backend.kill()
      this.#backend = null
    }
  }

  static stopAll() {
    Workspace.#instances.forEach((w) => w.stop())
  }

}

