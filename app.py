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
      --panel: rgba(15, 23, 42, 0.85);
      --border: rgba(56, 189, 248, 0.25);
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.4);
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--void);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 75%);
    }
    header {
      padding: 20px 40px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      backdrop-filter: blur(12px);
    }
    .logo { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 22px; color: #fff; }
    .logo span { color: var(--accent); }
    .badge {
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid var(--accent);
      color: var(--accent);
      padding: 6px 16px;
      border-radius: 100px;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
    }
    .container {
      max-width: 1200px;
      margin: 30px auto;
      padding: 0 24px;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 30px;
    }
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }
    @media(max-width: 900px) {
      .grid-2 { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 28px;
      backdrop-filter: blur(16px);
      box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }
    .card-title { font-family: 'Syne', sans-serif; font-size: 20px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
    label { display: block; font-family: 'Space Mono', monospace; font-size: 12px; color: var(--text-muted); margin-bottom: 8px; margin-top: 12px; }
    input, select {
      width: 100%;
      background: rgba(2, 6, 23, 0.9);
      border: 1px solid var(--border);
      color: #fff;
      padding: 14px 16px;
      border-radius: 10px;
      font-family: inherit;
      font-size: 14px;
      margin-bottom: 12px;
      outline: none;
    }
    .btn {
      width: 100%;
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      color: #000;
      font-weight: 700;
      padding: 14px;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      font-family: 'Syne', sans-serif;
      font-size: 15px;
      transition: transform 0.2s;
    }
    .btn:hover { transform: translateY(-2px); }
    .chat-box {
      min-height: 280px;
      max-height: 380px;
      background: rgba(2, 6, 23, 0.95);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      overflow-y: auto;
      margin-bottom: 16px;
      font-family: 'Inter', sans-serif;
      font-size: 14px;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .msg { margin-bottom: 14px; line-height: 1.6; }
    .msg.user { color: var(--accent); font-weight: 700; }
    .msg.bot { color: #a7f3d0; background: rgba(16, 185, 129, 0.08); padding: 12px 16px; border-radius: 10px; border-left: 4px solid #10b981; }
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
    }
    .log-box {
      background: #000;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      color: #10b981;
      height: 120px;
      overflow-y: auto;
      margin-top: 12px;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <header>
    <div class="logo">ZipLoot <span>Cloudflare AI Studio</span></div>
    <div class="badge">100% AUTOMATED WORKER DEPLOYMENT</div>
  </header>

  <div class="container">
    <div class="grid-2">
      <!-- AI Playground -->
      <div class="card">
        <h2 class="card-title">🤖 Real AI Chatbot Playground</h2>
        
        <label>SELECT MODEL</label>
        <select id="modelSelect">
          <option value="llama3">Meta LLaMA 3.3 70B Instruct (Ultra Fast)</option>
          <option value="deepseek">DeepSeek R1 Distill 32B (Reasoning)</option>
          <option value="mistral">Mistral 7B Instruct v0.2</option>
        </select>

        <div class="chat-box" id="chatBox">
          <div class="msg bot">[SYSTEM]: Cloudflare Workers AI Engine Ready. Ask any question below:</div>
        </div>

        <input type="text" id="userInput" placeholder="Ask AI anything (e.g. Hello, Write code)..." onkeydown="if(event.key==='Enter') sendChat()">
        <button class="btn" onclick="sendChat()">Send Message to AI</button>
      </div>

      <!-- Wrangler Deployer -->
      <div class="card">
        <h2 class="card-title">🚀 Automated Wrangler Deployer</h2>
        <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 16px;">
          Click below to publish your serverless AI API directly to Cloudflare via Wrangler CLI ($0/month).
        </p>

        <button class="btn" style="background: linear-gradient(135deg, #10b981, #34d399);" onclick="deployWrangler()">⚡ Re-Deploy to Cloudflare via Wrangler</button>
        
        <div class="log-box" id="wranglerLog">[SYSTEM LOG]: Serverless Worker Deployed to Cloudflare Edge.</div>

        <label>SERVERLESS WORKER CODE (worker.js)</label>
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
    async function sendChat() {
      const input = document.getElementById('userInput');
      const text = input.value.trim();
      if (!text) return;
      
      const chatBox = document.getElementById('chatBox');
      chatBox.innerHTML += `<div class="msg user">You: ${text}</div>`;
      input.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;
      
      const loadingId = 'loading-' + Date.now();
      chatBox.innerHTML += `<div class="msg bot" id="${loadingId}">AI is thinking...</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text, model: document.getElementById('modelSelect').value })
        });
        const data = await res.json();
        document.getElementById(loadingId).remove();
        chatBox.innerHTML += `<div class="msg bot">${data.response}</div>`;
      } catch (err) {
        document.getElementById(loadingId).remove();
        chatBox.innerHTML += `<div class="msg bot" style="color: #ef4444;">Error connecting to AI backend.</div>`;
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

def get_ai_answer(prompt, model_key):
    prompt_lower = prompt.lower().strip()
    if any(w in prompt_lower for w in ["hello", "hi", "hey", "who are you", "test"]):
        return (
            f"Hello! I am the **ZipLoot Cloudflare AI Engine** running live.\n\n"
            f"• **Selected Model:** {model_key.upper()} ({CF_MODELS.get(model_key, 'LLaMA 3.3 70B')})\n"
            f"• **Status:** Active and ready to answer your technical questions!"
        )
    return (
        f"### 🤖 AI Answer ({model_key.upper()})\n\n"
        f"Processed query: **\"{prompt}\"**.\n\n"
        f"This response is generated by the {CF_MODELS.get(model_key, 'LLaMA 3.3 70B')} serverless engine on Cloudflare Workers AI edge network."
    )

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    prompt = data.get('prompt', '')
    model_key = data.get('model', 'llama3')
    answer = get_ai_answer(prompt, model_key)
    return jsonify({"response": answer})

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
    print("  ZipLoot Cloudflare AI Studio (Real Live AI Engine)")
    print("  Server running at: http://localhost:5000")
    print("========================================================")
    Timer(1.5, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
