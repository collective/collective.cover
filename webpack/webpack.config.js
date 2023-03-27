const makeConfig = require('sc-recipe-staticresources');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');


module.exports = makeConfig(
  //name
  'collective.cover',

  //shortName
  'cover',

  //path
  `${__dirname}/../src/collective/cover/browser/static`,

  //publicPath
  '++plone++collective.cover/',

  //callback
  function(config, options) {
    config.entry.unshift(
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
      './app/img/tile-richtext.png',
    );
    config.plugins.push(
      new CopyWebpackPlugin([{
        from: 'app/galleria/*',
        to: 'galleria',
        flatten: true
      }]),
    );

    // We need two entries, to generate two output files. One for viewlet
    // loaded only on Cover type and one for icon viewlet, which is loaded on
    // all content types.
    config.entry = {
      cover: config.entry,
      icons: ['./icons/icons.scss'],
    };
    config.output.filename = `[name]-${options.gitHash}.js`
    config.plugins = config.plugins.map(plugin => {
      if (plugin.filename === `${options.shortName}-${options.gitHash}.css`) {
        plugin.filename=`[name]-${options.gitHash}.css`;
      }
      return plugin
    });
    config.plugins.push(
      new HtmlWebpackPlugin({
        inject: false,
        filename: 'icons.pt',
        template: 'icons/icons.pt',
        publicPath: options.publicPath,
      })
    );
  },
);
