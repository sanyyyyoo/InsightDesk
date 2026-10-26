import hashlib
import os
import json
import threading
import requests
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


LOCAL_PROVIDER = "local"
GROQ_PROVIDER = "groq"

DEFAULT_LOCAL_MODEL = "qwen3:1.7b"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


def get_provider():
    return os.getenv(
        "LLM_PROVIDER",
        LOCAL_PROVIDER
    ).lower()


def get_model_name():
    provider = get_provider()

    if provider == LOCAL_PROVIDER:
        return os.getenv(
            "LOCAL_LLM_MODEL",
            DEFAULT_LOCAL_MODEL
        )

    if provider == GROQ_PROVIDER:
        return os.getenv(
            "GROQ_MODEL",
            DEFAULT_GROQ_MODEL
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}"
    )


def _generate_local(prompt):
    model = get_model_name()

    base_url = os.getenv(
        "LOCAL_LLM_BASE_URL",
        "http://localhost:11434"
    ).rstrip("/")

    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,

            # Ask Ollama for structured JSON.
            "format": "json",

            "options": {
                "temperature": 0
            }
        },
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]


def _generate_groq(prompt, json_mode=False):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing."
        )

    client = Groq(
        api_key=api_key
    )

    model = get_model_name()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        **({"response_format": {"type": "json_object"}} if json_mode else {})
    )

    return (
        response
        .choices[0]
        .message
        .content
    )


def generate_text(prompt, json_mode=False):
    provider = get_provider()

    if provider == LOCAL_PROVIDER:
        return _generate_local(prompt)

    if provider == GROQ_PROVIDER:
        return _generate_groq(prompt, json_mode)

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}"
    )


# Decision cache: judge and re-joining answers keyed by (provider, model, prompt), so a replay of the
# same complaints gives the same decisions. Failed or malformed answers are never cached.
CACHE_PATH = os.getenv("LLM_CACHE_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                                                       "llm_decisions.jsonl"))
_cache, _cache_lock = None, threading.Lock()


def _cache_key(prompt):
    return hashlib.sha256(f"{get_provider()}|{get_model_name()}|{prompt}".encode("utf-8")).hexdigest()


def _cache_get(key):
    global _cache
    with _cache_lock:
        if _cache is None:
            _cache = {}
            if os.path.exists(CACHE_PATH):
                for line in open(CACHE_PATH, encoding="utf-8"):
                    try:
                        row = json.loads(line)
                        _cache[row["key"]] = row["answer"]
                    except (ValueError, KeyError):
                        continue
        return _cache.get(key)


def _cache_put(key, answer):
    with _cache_lock:
        _cache[key] = answer
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, "answer": answer}) + "\n")


def generate_json(prompt, cache=False):
    """JSON answer of the configured LLM (Groq JSON mode, Ollama format=json) at temperature 0.
    cache=True (judge decisions): reuse the stored answer for an identical prompt."""
    if cache and os.getenv("LLM_CACHE", "1") == "1":
        key = _cache_key(prompt)
        hit = _cache_get(key)
        if hit is not None:
            return hit
        answer = generate_json(prompt)
        _cache_put(key, answer)
        return answer

    content = generate_text(prompt, json_mode=True)

    content = (
        content
        .replace("```json", "")
        .replace("```JSON", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(content)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "LLM returned invalid JSON.\n"
            f"Provider: {get_provider()}\n"
            f"Model: {get_model_name()}\n"
            f"Response:\n{content}"
        ) from exc
def get_chat_model():
    provider = get_provider()
    model = get_model_name()

    if provider == LOCAL_PROVIDER:
        return ChatOllama(
            model=model,
            base_url=os.getenv(
                "LOCAL_LLM_BASE_URL",
                "http://localhost:11434"
            ),
            temperature=0,
        )

    if provider == GROQ_PROVIDER:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing."
            )

        return ChatGroq(
            model=model,
            api_key=api_key,
            temperature=0,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}"
    )