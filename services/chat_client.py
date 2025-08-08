# /mnt/data/chat_client.py  (services/chat_client.py in your tree)
import json
import urllib.request
import urllib.error

class ChatClient:
    """
    Thin HTTP client for Microservice A (chat logging + filtering).

    Expected Microservice A API (example):
      POST /filter
      body: {"username": "...", "message": "..."}
      resp: {"allowed": true/false, "filtered_text": "string", "reason": "string or null"}

    Adjust base_url or route names as needed to match your teammate's service.
    """
    def __init__(self, base_url: str = "http://localhost:7004", timeout: float = 0.5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def filter_and_log(self, username: str, message: str) -> dict:
        url = f"{self.base_url}/filter"
        payload = {"username": username, "message": message}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                parsed = json.loads(raw) or {}
                # normalize expected keys with type safety
                allowed = bool(parsed.get("allowed", True))
                filtered_text = parsed.get("filtered_text", message)
                if not isinstance(filtered_text, str):
                    filtered_text = str(filtered_text)
                reason = parsed.get("reason")
                return {"allowed": allowed, "filtered_text": filtered_text, "reason": reason}
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
            # Fallback: allow but mark as (unverified) so the UI still works offline
            return {
                "allowed": True,
                "filtered_text": message,
                "reason": f"microservice_unreachable: {e}",
            }
