const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = 9000;
const PROJECT_ROOT = path.join(__dirname, '..');
const DASHBOARD_HTML = path.join(PROJECT_ROOT, 'dashboard.html');
const GENERATE_SCRIPT = path.join(PROJECT_ROOT, 'scripts', 'generate-dashboard.sh');
const DATA_FILE = path.join(PROJECT_ROOT, 'dashboard-data.json');

const server = http.createServer((req, res) => {
    // Handle CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    if (req.url === '/' || req.url === '/dashboard.html') {
        // Serve the HTML file
        fs.readFile(DASHBOARD_HTML, (err, content) => {
            if (err) {
                res.writeHead(500);
                res.end('Error loading dashboard.html');
                return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(content);
        });
    } else if (req.url.startsWith('/api/data')) {
        // Generate fresh data and serve it
        console.log('🔄 Regenerating data...');
        exec(GENERATE_SCRIPT, (error, stdout, stderr) => {
            if (error) {
                console.error(`Exec error: ${error}`);
                res.writeHead(500);
                res.end(JSON.stringify({ error: 'Failed to generate data' }));
                return;
            }

            // Read the generated JSON file
            fs.readFile(DATA_FILE, (err, content) => {
                if (err) {
                    res.writeHead(500);
                    res.end(JSON.stringify({ error: 'Failed to read data file' }));
                    return;
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(content);
            });
        });
    } else {
        res.writeHead(404);
        res.end('Not found');
    }
});

server.listen(PORT, () => {
    console.log(`\n🚀 Dashboard Server running at: http://localhost:${PORT}`);
    console.log(`   - Dashboard: http://localhost:${PORT}/`);
    console.log(`   - API:       http://localhost:${PORT}/api/data`);
    console.log(`   - Tailscale: Use your Tailscale IP (100.104.238.110)\n`);
});
