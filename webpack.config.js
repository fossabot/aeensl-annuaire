const webpack = require('webpack');
const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  context: path.resolve(__dirname, 'assets/src'),
  entry: {
    app: './index.js'
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ExtractTextPlugin.extract({
          use: 'css-loader?importLoaders=1!postcss-loader'
        }),
      },
      {
        test: /\.(png|jpg)$/,
        loader: 'url-loader?name=./img/[name].[ext]&limit=8192',
      },
      {
        test: /\.(woff|woff2|ttf|eot|svg)(\?v=[a-z0-9]\.[a-z0-9]\.[a-z0-9])?$/,
        use: 'file-loader?name=./fonts/[name]-[hash].[ext]'
      },
    ]
  },
  output: {
    path: path.resolve(__dirname, 'assets/dist'),
    filename: "./index.js"
  },
  plugins: [
    new ExtractTextPlugin('[name].bundle.css'),
  ],
};
