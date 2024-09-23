const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
	host: 'localhost',
	port: 5000,
	proxy: {
	  '^/api': {
		target: process.env.VUE_APP_SERVER_URL,
		changeOrigin: true,
	  },
	}
  }
})
