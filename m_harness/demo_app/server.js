const express = require('express');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3000;
const CSP_PROFILE = process.env.CSP_PROFILE || 'baseline';
const LAB_HOST = process.env.LAB_HOST || 'http://assets.demo.local';

// CSP profiles
const cspProfiles = {
  baseline: {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'"],
    "img-src": ["'self'"],
    "connect-src": ["'self'"]
  },
  allow_inline: {
    "default-src": ["'self'"],
    "script-src": ["'self'", "'unsafe-inline'"],
    "style-src": ["'self'"],
    "img-src": ["'self'"],
    "connect-src": ["'self'"]
  },
  allow_blob: {
    "default-src": ["'self'"],
    "script-src": ["'self'", "blob:"],
    "style-src": ["'self'"],
    "img-src": ["'self'"],
    "connect-src": ["'self'"]
  },
  allow_lab_host_wildcard: {
    "default-src": ["'self'"],
    // Allow inline and the asset host
    "script-src": ["'self'", "'unsafe-inline'", `${LAB_HOST}`, `${LAB_HOST}:*`],
    "style-src": ["'self'"],
    "img-src": ["'self'", `${LAB_HOST}`],
    "connect-src": ["'self'", `${LAB_HOST}`]
  }
};


const selected = cspProfiles[CSP_PROFILE] || cspProfiles['baseline'];

app.use(helmet({
  contentSecurityPolicy: {
    useDefaults: false,
    directives: selected
  }
}));

app.use(express.static('public'));

app.get('/', (req, res) => {
  res.send(`
<!doctype html>
<html>
<head><meta charset="utf-8"/><title>PG Demo App</title></head>
<body>
  <h1>PG Demo App</h1>
  <p>Profile: <code>${CSP_PROFILE}</code></p>
  <div id="injection-root"></div>
</body>
</html>`);
});

app.get('/login', (req, res) => res.send('<h1>Login</h1>'));
app.get('/account', (req, res) => res.send('<h1>Account</h1>'));
app.get('/api/secret', (req, res) => res.json({ secret: "redacted" }));

app.listen(PORT, () => console.log(`[demo] listening on http://localhost:${PORT} CSP=${CSP_PROFILE}`));
