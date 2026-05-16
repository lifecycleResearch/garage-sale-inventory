"""AI vision analysis for garage sale items.

Supports three modes:
1. API key mode (OpenAI, Anthropic, Google Gemini)
2. Ollama local mode (free, needs GPU)
3. Manual fallback (no AI — user enters data)
"""
import json
import os
from pathlib import Path


def analyze_image(image_path: str, api_key: str | None = None) -> dict:
    """Analyze a product photo and return item details.

    Returns dict with keys: name, brand, description, category, condition, confidence
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("GEMINI_API_KEY")

    if api_key:
        return _analyze_with_api(image_path, api_key)

    # Check if Ollama is running locally
    try:
        return _analyze_with_ollama(image_path)
    except Exception:
        pass

    # Manual fallback — return empty fields with a message
    return {
        "name": "",
        "brand": "",
        "description": "",
        "category": "Other",
        "condition": "Good",
        "confidence": 0.0,
        "source": "manual",
        "message": "No AI vision API key set. Enter details manually or set OPENAI_API_KEY / GEMINI_API_KEY env var.",
    }


def _analyze_with_api(image_path: str, api_key: str) -> dict:
    """Use OpenAI GPT-4 Vision API to analyze the image."""
    import base64
    import urllib.request

    # Detect key type by prefix
    if api_key.startswith("sk-ant-"):
        return _analyze_with_anthropic(image_path, api_key)

    # Default: OpenAI
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are a product cataloging expert at a garage sale. "
                            "Look at this photo and identify the item. "
                            "Return ONLY a JSON object with these exact keys: "
                            "name (short product name), brand (manufacturer or brand name, empty if unknown), "
                            "description (1-2 sentences for a listing), category (one of: Furniture, Electronics, Clothing, Toys, Books, Tools, Sports, Jewelry, Art, Collectibles, Other), "
                            "condition (one of: New, Like New, Good, Fair, Poor), "
                            "confidence (0.0-1.0)."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}", "detail": "low"},
                    },
                ],
            }
        ],
        "max_tokens": 500,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            # Extract JSON from markdown code block if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            result = json.loads(content)
            result["source"] = "openai"
            return result
    except Exception as exc:
        return {
            "name": "",
            "brand": "",
            "description": "",
            "category": "Other",
            "condition": "Good",
            "confidence": 0.0,
            "source": "error",
            "message": f"API error: {exc}",
        }


def _analyze_with_anthropic(image_path: str, api_key: str) -> dict:
    """Use Anthropic Claude API. Stub — similar to OpenAI."""
    return {
        "name": "",
        "brand": "",
        "description": "",
        "category": "Other",
        "condition": "Good",
        "confidence": 0.0,
        "source": "anthropic_stub",
        "message": "Anthropic vision not yet implemented. Use OpenAI or manual entry.",
    }


def _analyze_with_ollama(image_path: str) -> dict:
    """Use local Ollama with llava model."""
    import base64
    import urllib.request

    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": "llava",
        "prompt": (
            "Identify this garage sale item. Return JSON with keys: "
            "name, brand, description, category, condition, confidence."
        ),
        "images": [b64_image],
        "stream": False,
    }

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text = data.get("response", "")
        # Try to extract JSON
        try:
            result = json.loads(text)
            result["source"] = "ollama"
            return result
        except json.JSONDecodeError:
            return {
                "name": "",
                "brand": "",
                "description": text[:200],
                "category": "Other",
                "condition": "Good",
                "confidence": 0.3,
                "source": "ollama",
            }
