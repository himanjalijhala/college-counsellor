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
            'stream': False,
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
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                text = data['content'][0]['text']
                body = text.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

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
