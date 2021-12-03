# Electron Renderer Process

The [renderer process](https://www.electronjs.org/docs/latest/tutorial/process-model#the-renderer-process) manages the UI inside the application's main window. It communicates with the backend process via HTTP and with the main process through Electron's [IPC service](https://www.electronjs.org/docs/latest/api/ipc-renderer).

## Building

The renderer process uses [Webpack](https://webpack.js.org/) to bundle its source code and other assets. To initiate a build, run:

```
$ npm run build
```


## Running the Dev Server

During development, you can use the [Webpack Dev Server](https://webpack.js.org/guides/development/#using-webpack-dev-server) to automatically rebuild the bundle as source files are changed. To start the dev server, simply run:

```
$ npm start
```


## Code Quality

The renderer process is configured for linting and automatic code formatting with [JavaScript Standard Style](https://standardjs.com/). To lint and format the source code, run:
```
$ npm run standard
```
