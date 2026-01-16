import http.server
import socketserver
import json
import os
import mimetypes

PORT = 9090
DIRECTORY = "companion/static"

# Mock Data
mock_items = [
    {"id": "1", "title": "Approve Plan", "description": "Implementation plan for Docker", "timestamp": "2026-01-16 10:00", "status": "pending"},
    {"id": "2", "title": "Run Command", "description": "sudo apt-get install tailscale", "timestamp": "2026-01-16 10:05", "status": "pending"},
]

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # API: Inbox
        if self.path == '/api/inbox':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            pending = [i for i in mock_items if i['status'] == 'pending']
            self.wfile.write(json.dumps(pending).encode())
            return
        
        # Serve Static Files
        if self.path == '/':
            self.path = '/index.html'
        
        # Serve from companion/static
        file_path = os.path.join(DIRECTORY, self.path.lstrip('/'))
        
        if os.path.exists(file_path):
            self.send_response(200)
            # Guess mime type
            ctype, _ = mimetypes.guess_type(file_path)
            self.send_header('Content-type', ctype or 'application/octet-stream')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        # API: Approve
        if self.path.startswith('/api/approve/'):
            item_id = self.path.split('/')[-1]
            found = False
            for item in mock_items:
                if item['id'] == item_id:
                    item['status'] = 'approved'
                    found = True
                    break
            
            if found:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            else:
                self.send_error(404, "Item not found")
            return

print(f"🚀 Mock Server running at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
