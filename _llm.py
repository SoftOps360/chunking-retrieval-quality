"""Shared LLM client + helpers (same as every episode: openai SDK -> Groq's free,
OpenAI-compatible endpoint). Swap base_url + model for OpenAI or a local Ollama."""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
MODEL = "openai/gpt-oss-120b"   # if this errors, check console.groq.com/docs/models


def ask(prompt, system=None):
    """One prompt in, the reply text out."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=MODEL, messages=messages)
    return resp.choices[0].message.content


def ask_json(prompt, system=None):
    """Force valid JSON and parse it. (JSON mode needs the word 'JSON' in the messages.)"""
    sys_msg = (system or "") + "\nRespond with valid JSON only."
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": prompt},
    ]
    resp = client.chat.completions.create(
        model=MODEL, messages=messages, response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)
