import json
import os
from flask import current_app


SYSTEM_PROMPT = """You are a comic script writer. Convert the user's story into a structured comic script.
Return ONLY valid JSON with this shape:
{
  "title": "string",
  "scenes": [
    {
      "scene_number": 1,
      "setting": "string",
      "panels": [
        {
          "panel_number": 1,
          "description": "string",
          "characters": ["string"],
          "dialogue": [{"character": "string", "line": "string"}],
          "narration": "string"
        }
      ]
    }
  ]
}
No markdown, no code fences, no extra text."""


class GeminiError(Exception):
    pass


def _client():
    key = current_app.config.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise GeminiError("GEMINI_API_KEY not configured")
    model = current_app.config.get("GEMINI_MODEL") or os.environ.get("GEMINI_MODEL")
    if not model:
        raise GeminiError("GEMINI_MODEL not configured")
    from google import genai
    return genai.Client(api_key=key), model


def generate(story):
    client, model = _client()
    user_prompt = (
        f"Title: {story['title']}\n"
        f"Content: {story['content']}\n"
        f"Character gender: {story.get('character_gender') or 'unspecified'}\n"
        f"Target audience: {story.get('target_audience') or 'general'}\n"
        f"Desired length: {story.get('desired_length') or 'medium'}\n"
        f"Language: {story.get('language') or 'English'}\n"
    )
    try:
        resp = client.models.generate_content(
            model=model,
            contents=SYSTEM_PROMPT + "\n\n" + user_prompt,
        )
    except Exception as e:
        raise GeminiError(str(e))

    text = getattr(resp, "text", None)
    if not text:
        raise GeminiError("Empty response from Gemini")

    # parse JSON
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        raise GeminiError("Invalid JSON from Gemini")

    if not isinstance(data, dict) or "scenes" not in data:
        raise GeminiError("Malformed script structure")

    # usage
    usage = getattr(resp, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
    output_tokens = getattr(usage, "candidates_token_count", None) if usage else None

    return data, input_tokens, output_tokens