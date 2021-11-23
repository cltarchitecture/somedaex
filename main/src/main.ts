import { app, BrowserWindow, dialog, ipcMain } from 'electron'
import installExtension, { VUEJS3_DEVTOOLS } from 'electron-devtools-installer'
import process from 'process'

import { Workspace } from './lib/workspace'

// const backend = new Backend("../backend")

ipcMain.handle('showOpenDialog', (event, options) => {
  const window = BrowserWindow.fromWebContents(event.sender)
  if (window != null) {
    return dialog.showOpenDialog(window, options)
  }
})

ipcMain.handle('showSaveDialog', (event, options) => {
  const window = BrowserWindow.fromWebContents(event.sender)
  if (window != null) {
    return dialog.showSaveDialog(window, options)
  }
})

ipcMain.handle('showMessageBox', (event, options) => {
  const window = BrowserWindow.fromWebContents(event.sender)
  if (window != null) {
    return dialog.showMessageBox(window, options)
  }
})

// Chromium disables SharedArrayBuffer by default
app.commandLine.appendSwitch('enable-features', 'SharedArrayBuffer')

app.on('ready', () => {
  installExtension(VUEJS3_DEVTOOLS).then((name) => {
    console.log(`Added extension: ${name}`)
  }).catch((err) => {
    console.error('Unable to install Vue Devtools:', err)
  })

  const workspace = new Workspace()
  // workspace.start()

  if (process.env.NODE_ENV === 'production') {
    workspace.window.loadFile('../../renderer/build/index.html')
  } else {
    workspace.window.loadURL('http://localhost:9000/index.html', {
      extraHeaders: 'Cross-Origin-Embedder-Policy: require-corp\nCross-Origin-Opener-Policy: same-origin'
    })
    workspace.window.webContents.openDevTools()
  }
})

app.on('will-quit', () => Workspace.stopAll())
app.on('quit', () => Workspace.stopAll())

app.on('window-all-closed', () => {
  app.quit()
})
