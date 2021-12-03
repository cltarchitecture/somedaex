# Electron Main Process

The [main process](https://www.electronjs.org/docs/latest/tutorial/process-model#the-main-process) is responsible for window management, file access, and native UI components. It also manages the Python data processing backend when run in production mode.


## Building

The main process uses [esbuild](https://esbuild.github.io/) to compile its [TypeScript](https://www.typescriptlang.org/) source code to plain JavaScript. To initiate a build, run:

```
$ npm run build
```

Once the build is complete, you can start the Electron app by running:
```
$ npm start
```


## Code Quality

The main process is configured for linting and automatic code formatting with [JavaScript Standard Style](https://standardjs.com/). To lint and format the Typescript sources, run:
```
$ npm run standard
```

Esbuild does not perform type checking when compiling Typescript to plain JavaScript. Your editor should perform type checking automatically, but you can also do it manually by running:
```
$ npm run typecheck
```


## Notes

The main process depends on `@raygun-nickj/mmap-io`, which contains a platform-native Node modules written in C++. After installing or reinstalling this package, you may need to run `npx electron-rebuild` to ensure that the native module is compiled for the same version of Node as is used internally by Electron.
