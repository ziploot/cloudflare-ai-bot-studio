#!/bin/bash
echo "========================================================"
echo "  ZipLoot Cloudflare AI Bot & API Studio (Automated)"
echo "========================================================"
echo ""

echo "[1/3] Installing Python dependencies..."
python3 -m pip install flask requests --quiet

echo ""
echo "[2/3] Authenticating with Cloudflare via Wrangler..."
npx -y wrangler login

echo ""
echo "[3/3] Building & Deploying Serverless AI Worker to Cloudflare..."
npx -y wrangler deploy worker.js --name cloudflare-ai-bot-studio

echo ""
echo "[SUCCESS] Cloudflare AI Worker Deployed Automatically!"
echo "Launching Local Studio & AI Chatbot Interface..."
python3 app.py
