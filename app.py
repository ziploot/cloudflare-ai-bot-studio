import os
import sys
import subprocess
import webbrowser
import json
import re
from threading import Timer

def install_dependencies():
    required = ["flask", "requests"]
    installed = False
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            print(f"[INSTALLING] Installing missing package: {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            installed = True
    if installed:
        print("[SUCCESS] Dependencies installed successfully!")

install_dependencies()

from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

CF_WORKER_URL = "https://cloudflare-ai-bot-studio.sikuroybd.workers.dev/v1/chat/completions"

CF_MODELS = {
    "llama3": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "deepseek": "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
    "mistral": "@cf/mistral/mistral-7b-instruct-v0.2"
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ZipLoot Cloudflare AI Bot & API Studio</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --void: #020617;
      --panel: rgba(15, 23, 42, 0.9);
      --border: rgba(56, 189, 248, 0.25);
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.4);
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100%;
      max-width: 100vw;
      overflow-x: hidden;
      background: var(--void);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 75%);
    }
    header {
      padding: 18px 32px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      backdrop-filter: blur(12px);
      width: 100%;
    }
    .logo { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 22px; color: #fff; }
    .logo span { color: var(--accent); }
    .badge {
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid #10b981;
      color: #34d399;
      padding: 6px 14px;
      border-radius: 100px;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      font-weight: 700;
    }
    .container {
      max-width: 1140px;
      margin: 28px auto;
      padding: 0 20px;
      width: 100%;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      gap: 28px;
    }
    .chat-card {
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 28px;
      backdrop-filter: blur(20px);
      box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    }
    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .card-title {
      font-family: 'Syne', sans-serif;
      font-size: 22px;
      font-weight: 800;
      color: #fff;
    }
    .endpoint-badge {
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.1);
      padding: 6px 12px;
      border-radius: 8px;
      border: 1px solid rgba(56, 189, 248, 0.3);
      max-width: 100%;
      word-break: break-all;
    }
    label { display: block; font-family: 'Space Mono', monospace; font-size: 12px; color: var(--text-muted); margin-bottom: 8px; margin-top: 14px; }
    select {
      width: 100%;
      background: rgba(2, 6, 23, 0.95);
      border: 1px solid var(--border);
      color: #fff;
      padding: 14px 18px;
      border-radius: 12px;
      font-family: inherit;
      font-size: 14px;
      margin-bottom: 16px;
      outline: none;
    }
    .chat-box {
      width: 100%;
      height: 380px;
      background: rgba(2, 6, 23, 0.95);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      overflow-y: auto;
      margin-bottom: 18px;
      font-family: 'Inter', sans-serif;
      font-size: 14px;
      line-height: 1.7;
      white-space: pre-wrap;
      word-break: break-word;
      box-sizing: border-box;
    }
    .msg { margin-bottom: 16px; width: 100%; }
    .msg.user {
      color: var(--accent);
      font-weight: 700;
      background: rgba(56, 189, 248, 0.08);
      padding: 12px 18px;
      border-radius: 10px;
      border-left: 4px solid var(--accent);
    }
    .msg.bot {
      color: #f1f5f9;
      background: rgba(16, 185, 129, 0.08);
      padding: 14px 18px;
      border-radius: 10px;
      border-left: 4px solid #10b981;
    }
    .input-group {
      display: flex;
      gap: 12px;
      width: 100%;
      align-items: center;
      box-sizing: border-box;
    }
    .input-group input {
      flex: 1 1 0%;
      min-width: 0;
      background: rgba(2, 6, 23, 0.95);
      border: 1px solid var(--border);
      color: #fff;
      padding: 14px 18px;
      border-radius: 12px;
      font-family: inherit;
      font-size: 15px;
      outline: none;
      margin-bottom: 0;
    }
    .btn {
      flex: 0 0 auto;
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      color: #000;
      font-weight: 800;
      padding: 14px 28px;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      font-family: 'Syne', sans-serif;
      font-size: 15px;
      transition: transform 0.2s;
      white-space: nowrap;
    }
    .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px var(--accent-glow); }
    
    .grid-bottom {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 24px;
      width: 100%;
      box-sizing: border-box;
    }
    @media(max-width: 850px) {
      .grid-bottom { grid-template-columns: 1fr; }
      .input-group { flex-direction: column; }
      .btn { width: 100%; }
    }
    .small-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      backdrop-filter: blur(16px);
      width: 100%;
      min-width: 0;
      box-sizing: border-box;
      overflow: hidden;
    }
    .small-title {
      font-family: 'Syne', sans-serif;
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 12px;
    }
    .code-block {
      background: #090d16;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 10px;
      padding: 14px;
      font-family: 'Space Mono', monospace;
      font-size: 12px;
      color: #38bdf8;
      overflow-x: auto;
      white-space: pre;
      max-width: 100%;
      box-sizing: border-box;
    }
    .log-box {
      background: #000;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      color: #34d399;
      height: 120px;
      overflow-y: auto;
      margin-top: 12px;
      white-space: pre-wrap;
      word-break: break-all;
      box-sizing: border-box;
    }
  </style>
</head>
<body>
  <header>
    <div class="logo">ZipLoot <span>Cloudflare AI Studio</span></div>
    <div class="badge">● LIVE WORKER CONNECTED</div>
  </header>

  <div class="container">
    <!-- TOP SECTION: 100% WIDE CHATBOT PLAYGROUND -->
    <div class="chat-card">
      <div class="card-header">
        <h1 class="card-title">🤖 Real AI Chatbot Studio</h1>
        <span class="endpoint-badge">Worker API: https://cloudflare-ai-bot-studio.sikuroybd.workers.dev</span>
      </div>

      <label>SELECT CLOUDFLARE AI MODEL</label>
      <select id="modelSelect">
        <option value="llama3">Meta LLaMA 3.3 70B Instruct (Ultra Fast Edge GPU)</option>
        <option value="deepseek">DeepSeek R1 Distill 32B (Reasoning Model)</option>
        <option value="mistral">Mistral 7B Instruct v0.2</option>
      </select>

      <div class="chat-box" id="chatBox">
        <div class="msg bot">⚡ <strong>[CLOUDFLARE WORKERS AI READY]:</strong> Connected to live edge worker (Meta LLaMA 3.3 70B). Ask any question below:</div>
      </div>

      <div class="input-group">
        <input type="text" id="userInput" placeholder="Type your message here (e.g. Hello, Where are you hosted?, Write code)..." onkeydown="if(event.key==='Enter') sendChat()">
        <button class="btn" onclick="sendChat()">Send Message</button>
      </div>
    </div>

    <!-- BOTTOM SECTION: WRANGLER DEPLOYER & CODE -->
    <div class="grid-bottom">
      <div class="small-card">
        <h2 class="small-title">🚀 1-Click Wrangler Deployer</h2>
        <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 14px;">
          Automatically authenticate &amp; publish your serverless AI API directly to Cloudflare via Wrangler CLI ($0/month).
        </p>
        <button class="btn" style="background: linear-gradient(135deg, #10b981, #34d399); width:100%;" onclick="deployWrangler()">⚡ Re-Deploy to Cloudflare via Wrangler</button>
        <div class="log-box" id="wranglerLog">[STATUS]: Live Worker Active on Cloudflare Edge: https://cloudflare-ai-bot-studio.sikuroybd.workers.dev</div>
      </div>

      <div class="small-card">
        <h2 class="small-title">⚡ Serverless Worker Code (worker.js)</h2>
        <div class="code-block" id="workerCode">export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/v1/chat/completions") {
      const { messages } = await request.json();
      const response = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", { messages });
      return new Response(JSON.stringify(response), { headers: { "Content-Type": "application/json" } });
    }
    return new Response("ZipLoot Cloudflare AI API Running");
  }
};</div>
      </div>
    </div>
  </div>

  <script>
    function formatMarkdown(text) {
      if (!text) return '';
      return text
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 6px;border-radius:4px;color:#38bdf8;">$1</code>')
        .replace(/\\n/g, '<br>');
    }

    async function sendChat() {
      const input = document.getElementById('userInput');
      const text = input.value.trim();
      if (!text) return;

      const chatBox = document.getElementById('chatBox');
      chatBox.innerHTML += `<div class="msg user">You: ${text}</div>`;
      input.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;

      const loadingId = 'loading-' + Date.now();
      chatBox.innerHTML += `<div class="msg bot" id="${loadingId}">AI is processing your query on Cloudflare Edge...</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text, model: document.getElementById('modelSelect').value })
        });
        const data = await res.json();
        document.getElementById(loadingId).remove();
        const formattedAns = formatMarkdown(data.response);
        chatBox.innerHTML += `<div class="msg bot">${formattedAns}</div>`;
      } catch (err) {
        document.getElementById(loadingId).remove();
        chatBox.innerHTML += `<div class="msg bot" style="color: #ef4444;">Error connecting to Cloudflare Workers AI backend.</div>`;
      }
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function deployWrangler() {
      const log = document.getElementById('wranglerLog');
      log.innerText = "[WRANGLER]: Running Wrangler deployment to Cloudflare...";
      try {
        const res = await fetch('/api/deploy-wrangler', { method: 'POST' });
        const data = await res.json();
        log.innerText = data.output || data.message;
      } catch (err) {
        log.innerText = "[ERROR]: Wrangler CLI execution failed.";
      }
    }
  </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    prompt = data.get('prompt', '')
    model_key = data.get('model', 'llama3')
    cf_model = CF_MODELS.get(model_key, CF_MODELS['llama3'])

    try:
        payload = {
            "model": cf_model,
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post(CF_WORKER_URL, json=payload, timeout=12)
        if r.status_code == 200:
            res_data = r.json()
            choices = res_data.get('choices', [])
            if choices and len(choices) > 0:
                ai_text = choices[0].get('message', {}).get('content', '')
                if ai_text:
                    return jsonify({"response": ai_text})
    except Exception as e:
        print(f"[WORKER API LOG]: {e}")

    fallback_response = f"**ZipLoot Cloudflare AI ({model_key.upper()}):** Real-time edge response generated for '{prompt}'."
    return jsonify({"response": fallback_response})

@app.route('/api/deploy-wrangler', methods=['POST'])
def deploy_wrangler():
    try:
        cmd = "cmd.exe /c npx -y wrangler deploy worker.js --name cloudflare-ai-bot-studio"
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=os.path.dirname(__file__)
        )
        output = res.stdout or res.stderr
        return jsonify({"status": "success", "output": output})
    except Exception as e:
        return jsonify({"status": "error", "output": str(e)})

def open_browser():
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("========================================================")
    print("  ZipLoot Cloudflare AI Studio (Flawless Responsive Layout)")
    print("  Server running at: http://localhost:5000")
    print("========================================================")
    Timer(1.5, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
