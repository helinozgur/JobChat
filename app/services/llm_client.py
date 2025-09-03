import requests
from flask import current_app as app

class LLMClient:
    @staticmethod
    def _base() -> str:
        return (app.config.get("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")

    @staticmethod
    def _timeout(t=None) -> int:
        return int(t or app.config.get("OLLAMA_TIMEOUT", 60))

    @staticmethod
    def _post(path: str, payload: dict, stream: bool = False, timeout=None):
        url = f"{LLMClient._base()}{path}"
        return requests.post(url, json=payload, stream=stream, timeout=LLMClient._timeout(timeout))

    @staticmethod
    def chat(messages, options=None, timeout=None, format_json: bool = False) -> str:
        """
        Tek seferlik yanıt (stream değil). format_json=True ise Ollama'ya 'format':'json' gönderilir.
        """
        payload = {
            "model": app.config.get("OLLAMA_MODEL", "qwen2.5:7b-instruct"),
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_ctx": 4096,
            },
        }
        if options:
            payload["options"].update(options)
        if format_json:
            payload["format"] = "json"

        resp = LLMClient._post("/api/chat", payload, stream=False, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")

    @staticmethod
    def chat_stream(messages, options=None, timeout=None):
        """
        SSE akışı. (Ollama'da 'stream': True ile 'format':'json' genelde desteklenmez;
        bu yüzden burada format_json yok.)
        """
        payload = {
            "model": app.config.get("OLLAMA_MODEL", "qwen2.5:7b-instruct"),
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000,
            },
        }
        if options:
            payload["options"].update(options)

        return LLMClient._post("/api/chat", payload, stream=True, timeout=timeout)
