const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = 9000;
const PROJECT_ROOT = path.join(__dirname, '..');
const DASHBOARD_HTML = path.join(PROJECT_ROOT, 'dashboard.html');
const GENERATE_SCRIPT = path.join(PROJECT_ROOT, 'scripts', 'generate-dashboard.sh');
const DATA_FILE = path.join(PROJECT_ROOT, 'dashboard-data.json');

// MIME types for serving files
const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.md': 'text/markdown; charset=utf-8',
    '.txt': 'text/plain',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
    // Handle CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    const url = new URL(req.url, `http://${req.headers.host}`);
    const pathname = url.pathname;

    if (pathname === '/' || pathname === '/dashboard.html') {
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
    } else if (pathname.startsWith('/api/data')) {
        // Generate fresh data and serve it
        console.log('🔄 Regenerating data...');
        exec(GENERATE_SCRIPT, { timeout: 30000 }, (error, stdout, stderr) => {
            if (error) {
                console.error(`Exec error: ${error}`);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Failed to generate data', details: stderr }));
                return;
            }

            fs.readFile(DATA_FILE, (err, content) => {
                if (err) {
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Failed to read data file' }));
                    return;
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(content);
            });
        });
    } else if (pathname.startsWith('/files/')) {
        // Serve local project files (for markdown viewing)
        // URL format: /files/path/to/file.md -> PROJECT_ROOT/path/to/file.md
        const relativePath = pathname.replace('/files/', '');
        const filePath = path.join(PROJECT_ROOT, relativePath);

        // Security: prevent directory traversal
        if (!filePath.startsWith(PROJECT_ROOT)) {
            res.writeHead(403);
            res.end('Access denied');
            return;
        }

        fs.readFile(filePath, (err, content) => {
            if (err) {
                res.writeHead(404);
                res.end(`File not found: ${relativePath}`);
                return;
            }

            const ext = path.extname(filePath).toLowerCase();
            const contentType = MIME_TYPES[ext] || 'application/octet-stream';

            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content);
        });
    } else if (pathname === '/vscode') {
        // Open file in VS Code - redirect helper
        const filePath = url.searchParams.get('path');
        if (filePath) {
            const vscodeUrl = `vscode://file${filePath}`;
            res.writeHead(302, { 'Location': vscodeUrl });
            res.end();
        } else {
            res.writeHead(400);
            res.end('Missing path parameter');
        }
    } else {
        res.writeHead(404);
        res.end('Not found');
    }
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`\n🚀 Dashboard Server running at: http://localhost:${PORT}`);
    console.log(`   - Dashboard: http://localhost:${PORT}/`);
    console.log(`   - API:       http://localhost:${PORT}/api/data`);
    console.log(`   - Files:     http://localhost:${PORT}/files/<path>`);
    console.log(`   - Tailscale: Use your Tailscale IP\n`);
});
