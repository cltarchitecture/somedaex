# Somedaex

Somedaex is an app for exploratory analysis and visualization of social media data. It is intended for researchers in social science and related fields who are interested in leveraging data from social media but who lack the programming skills necessary to use existing NLP toolkits.


## Project Organization

Somedaex is an [Electron](https://www.electronjs.org/) app that uses a [Python](https://www.python.org/) backend for data processing. Its code is organized into three main sections:

* The `backend` folder contains the code for the data processing backend.
* The `main` folder contains code for the Electron app's [main process](https://www.electronjs.org/docs/latest/tutorial/process-model#the-main-process).
* The `renderer` folder contains the code for the Electron app's [renderer process](https://www.electronjs.org/docs/latest/tutorial/process-model#the-renderer-process).


## Notes

After (re)installing `mmap-io`, you must run `npx electron-rebuild`
