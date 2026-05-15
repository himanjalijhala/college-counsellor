export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405, headers: { 'Content-Type': 'application/json' },
    });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'Server configuration error: missing API key.' }), {
      status: 500, headers: { 'Content-Type': 'application/json' },
    });
  }

  const { prompt } = await req.json().catch(() => ({}));
  if (!prompt) {
    return new Response(JSON.stringify({ error: 'Missing prompt in request body.' }), {
      status: 400, headers: { 'Content-Type': 'application/json' },
    });
  }

  const upstream = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: 8192,
      stream: true,
      system:
        'You are a JSON API. Output only raw valid JSON. Never use markdown, backticks, or any text outside the JSON object. Your entire response must be a single JSON object starting with { and ending with }.',
      messages: [{ role: 'user', content: prompt }],
    }),
  });

  if (!upstream.ok) {
    const errorText = await upstream.text();
    return new Response(
      JSON.stringify({ error: `Anthropic API error: ${upstream.status}`, detail: errorText }),
      { status: upstream.status, headers: { 'Content-Type': 'application/json' } },
    );
  }

  // Pipe the Anthropic SSE stream directly to the client.
  // The browser parses the SSE events to extract text.
  return new Response(upstream.body, {
    headers: { 'Content-Type': 'text/event-stream; charset=utf-8' },
  });
}
