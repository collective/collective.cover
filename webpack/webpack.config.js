const CopyWebpackPlugin = require('copy-webpack-plugin');
// const childProcess = require('child_process');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
// const HtmlWebpackPlugin = require('html-webpack-plugin');
const SpritesmithPlugin = require('webpack-spritesmith');


const path = `${__dirname}/../src/collective/cover/static`;

// https://github.com/alleyinteractive/webpack-git-hash/issues/10
// const gitCmd = 'git rev-list -1 HEAD -- `pwd`'
// const gitHash = childProcess.execSync(gitCmd).toString().substring(0, 7);
// childProcess.execSync(`rm -f ${path}/cover-*`);


module.exports = {
  entry: [
    './app/img/dot.png',
    './app/img/tile-banner.png',
    './app/img/tile-basic.png',
    './app/img/tile-calendar.png',
    './app/img/tile-carousel.png',
    './app/img/tile-collection.png',
    './app/img/tile-contentbody.png',
    './app/img/tile-embed.png',
    './app/img/tile-file.png',
    './app/img/tile-generic.png',
    './app/img/tile-list.png',
    './app/img/tile-pfg.png',
    './app/img/tile-richtext.png',
    './app/cover.scss',
    './app/cover.js',
  ],
  output: {
    filename: 'cover.js',
    // filename: `cover-${gitHash}.js`,
    library: 'cover',
    libraryExport: 'default',
    libraryTarget: 'umd',
    path: path,
    pathinfo: true,
    publicPath: '++resource++collective.cover/',
  },
  module: {
    rules: [{
      test: /\.js$/,
      exclude: /(\/node_modules\/|test\.js$|\.spec\.js$)/,
      use: 'babel-loader',
    }, {
      test: /\.scss$/,
      use: ExtractTextPlugin.extract({
        fallback: 'style-loader',
        use: [
          'css-loader',
          'postcss-loader',
          'sass-loader'
        ]
      }),
    }, {
      test: /.*\.(gif|png|jpe?g)$/i,
      use: [
        {
          loader: 'file-loader',
          options: {
            name: '[path][name].[ext]',
            context: 'app/',
          }
        },
        {
          loader: 'image-webpack-loader',
          query: {
            mozjpeg: {
              progressive: true,
            },
            pngquant: {
              quality: '65-90',
              speed: 4,
            },
            gifsicle: {
              interlaced: false,
            },
            optipng: {
              optimizationLevel: 7,
            }
          }
        }
      ]
    }, {
      test: /\.svg/,
      exclude: /node_modules/,
      use: 'svg-url-loader',
    }]
  },
  devtool: 'source-map',
  plugins: [
    new CopyWebpackPlugin([{
      from: 'app/galleria/*',
      to: 'galleria',
      flatten: true
    }]),
    new ExtractTextPlugin({
      filename: 'cover.css',
      // filename: `cover-${gitHash}.css`,
      allChunks: true
    }),
    // new HtmlWebpackPlugin({
    //   filename: 'index.html',
    //   template: 'app/index.html',
    // }),
    new SpritesmithPlugin({
      src: {
        cwd: 'app/sprite',
        glob: '*.png',
      },
      target: {
        image: 'app/img/sprite.png',
        css: 'app/scss/_sprite.scss',
      },
      apiOptions: {
        cssImageRef: './img/sprite.png',
      }
    }),
  ]
}
