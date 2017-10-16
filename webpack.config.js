var path = require('path');
var webpack = require('webpack');

module.exports = {
    entry: './app/static/index.js',
    output: {
        path: path.resolve(__dirname, './app/static'),
        filename: 'bundle.js',
        publicPath: '/app/static'
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use:
                [
                    'style-loader',
                    'css-loader'
                ]
            },
            { test: /\.(png|woff|woff2|eot|ttf|svg)$/,
              loader: 'url-loader?limit=100000' }
        ]
    },
    plugins:
        [
            new webpack.ProvidePlugin({
                $: 'jquery',
                jQuery: 'jquery'
            }),
            new webpack.optimize.UglifyJsPlugin({
                //...
            })
        ]
};
