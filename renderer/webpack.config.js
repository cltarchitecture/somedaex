const path = require('path')
const { DefinePlugin } = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { VueLoaderPlugin } = require('vue-loader')

const isProduction = process.env.NODE_ENV === 'production'

/**
 * @type {import('webpack').Configuration}
 */
const config = {
  mode: isProduction ? 'production' : 'development',
  target: 'electron-renderer',
  entry: {
    renderer: path.join(__dirname, './src/index.ts')
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'build')
  },
  resolve: {
    extensions: ['.ts', '...']
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.ts$/,
        loader: 'ts-loader',
        options: {
          instance: 'main',
          configFile: path.join(__dirname, 'tsconfig.json'),
          appendTsSuffixTo: [/\.vue$/]
        },
        exclude: /node_modules/
      },
      {
        test: /\.vue$/,
        use: 'vue-loader'
      }
    ]
  },
  plugins: [
    new DefinePlugin({
      __VUE_OPTIONS_API__: true,
      __VUE_PROD_DEVTOOLS__: false
    }),
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: path.join(__dirname, 'src/index.html'),
      filename: 'index.html'
    })
  ]
}

if (config.mode === 'development') {
  config.devtool = 'cheap-source-map'
  config.devServer = {
    port: 9000
  }
}

module.exports = config
