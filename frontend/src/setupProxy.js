const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy all API calls to backend
  app.use(
    ['/api', '/health', '/analyze', '/update_analysis', '/clear_context'],
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug'
    })
  );
};