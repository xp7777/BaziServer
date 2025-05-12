const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
    devServer: {
        proxy: {
            '/api': {
                target: 'http://localhost:5000',
                changeOrigin: true
            }
        }
    },
    lintOnSave: false,  // 禁用保存时的lint
    transpileDependencies: true,
    configureWebpack: {
        performance: {
            hints: false  // 禁用性能提示
        },
        plugins: [
            new webpack.DefinePlugin({
                __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
                __VUE_PROD_DEVTOOLS__: JSON.stringify(false),
                __VUE_OPTIONS_API__: JSON.stringify(true)
            })
        ]
    },
    // 定义页面标题
    chainWebpack: config => {
        config.plugin('html').tap(args => {
            args[0].title = '八字命理AI人生指导系统';
            return args;
        });
    }
})