import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

async def _ollama(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        })
        r.raise_for_status()
        return r.json().get("response", "")

async def _openai(prompt: str) -> str:
    # Minimal HTTP call to OpenAI-style Responses API is intentionally not hard-coded here
    # to avoid breaking changes. If you want OpenAI, adapt this function to your org's standard client.
    # For now we fall back to Ollama if OPENAI_API_KEY is absent.
    return await _ollama(prompt)

async def generate(prompt: str) -> str:
    if OPENAI_API_KEY:
        return await _openai(prompt)
    return await _ollama(prompt)
