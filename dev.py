#!/usr/bin/env python3
"""Local dev server: serves public/ and handles POST /api/generate"""
import http.server, json, os, urllib.request, urllib.error

PORT = 3000
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='public', **kwargs)

    def do_POST(self):
        if self.path != '/api/generate':
            self.send_error(404)
            return

        if not API_KEY:
            self._json(500, {'error': 'Set ANTHROPIC_API_KEY env var before running.'})
            return

        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        prompt = body.get('prompt', '')
        if not prompt:
            self._json(400, {'error': 'Missing prompt.'})
            return

        payload = json.dumps({
            'model': 'claude-sonnet-4-6',
            'max_tokens': 8192,
            'stream': True,
            'system': 'You are a JSON API. Output only raw valid JSON. Never use markdown, backticks, or any text outside the JSON object. Your entire response must be a single JSON object starting with { and ending with }.',
            'messages': [{'role': 'user', 'content': prompt}],
        }).encode()

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': API_KEY,
                'anthropic-version': '2023-06-01',
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                buffer = b''
                while True:
                    chunk = resp.read(256)
                    if not chunk:
                        break
                    buffer += chunk
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        line = line.decode('utf-8', errors='replace').strip()
                        if not line.startswith('data: '):
                            continue
                        data = line[6:].strip()
                        if data == '[DONE]':
                            continue
                        try:
                            event = json.loads(data)
                            if (event.get('type') == 'content_block_delta'
                                    and event.get('delta', {}).get('type') == 'text_delta'):
                                self.wfile.write(event['delta']['text'].encode())
                                self.wfile.flush()
                        except Exception:
                            pass

        except urllib.error.HTTPError as e:
            detail = e.read().decode()
            self._json(e.code, {'error': f'Anthropic API error: {e.code}', 'detail': detail})

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args)

print(f'Dev server → http://localhost:{PORT}')
print('Set ANTHROPIC_API_KEY in your environment if not already set.')
http.server.HTTPServer(('', PORT), Handler).serve_forever()
