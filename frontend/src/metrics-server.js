const express = require('express');
const client = require('prom-client');
const app = express();

// Create registry
const register = new client.Registry();

// Add default metrics
client.collectDefaultMetrics({ register });

// Custom metrics (optional)
const httpRequestCounter = new client.Counter({
  name: 'http_requests_total',
  help: 'Count of HTTP requests',
  labelNames: ['method', 'route', 'status'],
  registers: [register]
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// Start server
app.listen(8001, '0.0.0.0', () => {
  console.log('Metrics server listening on port 8001');
});