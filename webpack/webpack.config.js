const makeConfig = require('sc-recipe-staticresources');
const CopyWebpackPlugin = require('copy-webpack-plugin');


module.exports = makeConfig(
  //name
  'collective.cover',

  //shortName
  'cover',

  //path
  `${__dirname}/../src/collective/cover/browser/static`,

  //publicPath
  '++resource++collective.cover/',

  //callback
  function(config, options) {
    config.entry.unshift(
      './app/img/dot.png',
      './app/img/frontpage_icon.png',
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
  },
);
