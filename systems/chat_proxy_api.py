
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os

app = Flask(__name__)
CORS(app)

# Basic profanity list; can be extended via environment variable CHAT_BADWORDS (comma-separated)
DEFAULT_BAD_WORDS = [
    "shit", "fuck", "bitch", "asshole", "bastard", "dick", "pussy", "cunt",
    "motherfucker", "fucker", "fucking", "faggot", "slut", "whore", "nigger", "nigga"
]

def load_bad_words():
    extra = os.getenv("CHAT_BADWORDS", "")
    words = [w.strip().lower() for w in extra.split(",") if w.strip()]
    base = set(w.lower() for w in DEFAULT_BAD_WORDS)
    base.update(words)
    return sorted(base)

BAD_WORDS = load_bad_words()

# precompile a regex that matches whole words from the list (case-insensitive)
# words like "ass" are excluded by default to reduce false positives; add deliberately via env if needed
bad_word_pattern = re.compile(r"\b(" + "|".join(map(re.escape, BAD_WORDS)) + r")\b", re.IGNORECASE)

@app.get("/health")
def health():
    return {"ok": True, "bad_words": len(BAD_WORDS)}

def filter_text(message: str):
    """
    Return (allowed: bool, filtered_text: str, reason: str|None)
    Blocks if any bad word is found; filtered_text has stars for bad words.
    """
    if not isinstance(message, str):
        return True, "", "invalid_message_type"
    found = bad_word_pattern.search(message or "")
    if not found:
        return True, message, None

    # replace each match with same-length asterisks
    def repl(m):
        return "*" * (m.end() - m.start())

    censored = bad_word_pattern.sub(repl, message)
    return False, censored, "profanity"

@app.post("/filter")
def filter_endpoint():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"allowed": True, "filtered_text": "", "reason": "invalid_json"}), 200

    username = data.get("username") or data.get("user_name") or "Player"
    message = data.get("message") or data.get("text") or ""
    allowed, filtered_text, reason = filter_text(message)

    # Always loggable structure; the client should trust "allowed" and display accordingly
    payload = {
        "allowed": bool(allowed),
        "filtered_text": str(filtered_text),
        "reason": reason,
        "username": username,
    }
    return jsonify(payload), 200

if __name__ == "__main__":
    # Default port 7004 to match client expectation
    app.run(host="0.0.0.0", port=7004, debug=True)
