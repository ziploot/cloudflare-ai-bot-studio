/**
 * ZipLoot Cloudflare Workers AI API Gateway & Chatbot
 * Deploy to Cloudflare Workers ($0/month, 10,000 free daily neurons)
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // OpenAI-Compatible Chat Endpoint
    if (url.pathname === "/v1/chat/completions" && request.method === "POST") {
      try {
        const body = await request.json();
        const messages = body.messages || [{ role: "user", content: body.prompt || "Hello" }];
        const model = body.model || "@cf/meta/llama-3.3-70b-instruct-fp8-fast";

        const response = await env.AI.run(model, { messages });
        
        return new Response(JSON.stringify({
          id: "chatcmpl-" + Date.now(),
          object: "chat.completion",
          created: Math.floor(Date.now() / 1000),
          model: model,
          choices: [{
            index: 0,
            message: { role: "assistant", content: response.response },
            finish_reason: "stop"
          }]
        }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: corsHeaders });
      }
    }

    // Default Status Page
    return new Response(JSON.stringify({
      status: "online",
      engine: "ZipLoot Cloudflare Workers AI Gateway v1.0",
      models: [
        "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
        "@cf/black-forest-labs/flux-1-schnell"
      ]
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
};
