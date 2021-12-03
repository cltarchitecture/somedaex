# Somedaex

Somedaex is an app for exploratory analysis and visualization of social media data. It is intended for researchers in social science and related fields who are interested in leveraging data from social media but who lack the programming skills necessary to use existing NLP toolkits.


## Project Organization

Somedaex is an [Electron](https://www.electronjs.org/) app that uses a [Python](https://www.python.org/) backend for data processing. Its code is organized into three main packages:

* The `backend` folder contains the code for the data processing backend.
* The `main` folder contains code for the Electron app's [main process](https://www.electronjs.org/docs/latest/tutorial/process-model#the-main-process).
* The `renderer` folder contains the code for the Electron app's [renderer process](https://www.electronjs.org/docs/latest/tutorial/process-model#the-renderer-process).

Each of these folders contains a README with more information about its package.


## Setting Up for Development

To set up a development environment for Somedaex, first ensure that the following dependencies are installed:

* [Node.js](https://nodejs.org/en/) version 16
* [NPM](https://www.npmjs.com/) version 7 or higher
* [Python](https://www.python.org/) version 3.9 or higher
* [Poetry](https://python-poetry.org/)

Next, set up a Python virtual environment by running:
```
$ cd backend
$ poetry install
```

Finally, install the required Node modules:
```
$ npm install
```

## Running in Development Mode

To start the backend process:
```
$ cd backend
$ poetry run python scripts/run_server.py
```

To start the Webpack dev server for the renderer process:
```
$ npm start -w renderer
```

To build and run the main process:
```
$ npm run build -w main
$ npm start -w main
```
