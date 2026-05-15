# College Counsellor Engine

A free, personalised college guidance tool for students — powered by Claude AI.

## Project Structure

```
college-counsellor/
├── api/
│   └── generate.js       ← Vercel serverless function (proxies Anthropic API)
├── public/
│   └── index.html        ← The full frontend (no API key UI)
├── vercel.json           ← Vercel config
└── README.md
```

## Deploy to Vercel (5 minutes)

### Step 1 — Push to GitHub
Create a new GitHub repo and push this folder:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/college-counsellor.git
git push -u origin main
```

### Step 2 — Import on Vercel
1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import your GitHub repo
3. Leave all build settings as default (Vercel auto-detects)
4. Click **Deploy**

### Step 3 — Add your Anthropic API Key (critical)
1. In your Vercel project → **Settings** → **Environment Variables**
2. Add a new variable:
   - **Name:** `ANTHROPIC_API_KEY`
   - **Value:** `sk-ant-api03-...` (your key from console.anthropic.com)
   - **Environment:** Production, Preview, Development ✓ all three
3. Click **Save**
4. Go to **Deployments** → click the three dots on your latest deploy → **Redeploy**

Your site is now live and free for anyone to use — no API key needed on their end.

## How it works

```
Browser (student fills form)
        ↓  POST /api/generate  { prompt: "..." }
Vercel Serverless Function  (api/generate.js)
        ↓  injects ANTHROPIC_API_KEY from env
Anthropic API  →  JSON response
        ↓
Browser renders the personalised guide
```

The API key **never touches the browser**. Students just open the URL and go.

## Cost estimate
Each guide generation uses ~4,000 output tokens on claude-sonnet-4.
At current Anthropic pricing that's roughly **₹3–5 per guide**.
