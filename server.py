import http.server
import socketserver
import os
import json

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='app', **kwargs)

    def do_GET(self):
        if self.path == '/marcos':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            files = [f for f in os.listdir('marcos') if os.path.isfile(os.path.join('marcos', f))]
            self.wfile.write(json.dumps(files).encode())
        elif self.path == '/stickers':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            files = [f for f in os.listdir('stickers') if os.path.isfile(os.path.join('stickers', f))]
            self.wfile.write(json.dumps(files).encode())
        elif self.path.startswith('/marcos/') or self.path.startswith('/stickers/'):
             # Serve files from marcos and stickers directories
            if self.path.startswith('/marcos/'):
                path = os.path.join('marcos', os.path.basename(self.path))
            else: # /stickers/
                path = os.path.join('stickers', os.path.basename(self.path))

            if os.path.isfile(path):
                try:
                    with open(path, 'rb') as f:
                        self.send_response(200)
                        if path.endswith('.png'):
                            self.send_header('Content-type', 'image/png')
                        elif path.endswith('.jpg') or path.endswith('.jpeg'):
                            self.send_header('Content-type', 'image/jpeg')
                        else:
                             self.send_header('Content-type', self.guess_type(path))
                        self.end_headers()
                        self.wfile.write(f.read())
                except Exception as e:
                    self.send_error(500, f'Error reading file: {e}')
            else:
                self.send_error(404, 'File not found')
        else:
            # Serve app files
            super().do_GET()


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor iniciado en http://localhost:{PORT}")
    print("Para detener el servidor, presiona Ctrl+C")
    httpd.serve_forever()
