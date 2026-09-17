import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from google import genai
from google.genai import types
import config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

API_KEY = os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env or configure it in app.py.")

client = genai.Client(api_key=API_KEY)

def get_history():
    return session.get("chat_history", [])

@app.route("/")
def index():
    return render_template("index.html", config=config)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    if len(message) > config.MAX_MESSAGE_LENGTH:
        return jsonify({"error": "Message is too long."}), 400

    history = get_history()
    history.append({"role": "user", "text": message})

    # Keep temporary history bounded.
    history = history[-config.MAX_HISTORY_MESSAGES:]

    contents = []
    for item in history:
        role = "user" if item["role"] == "user" else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=item["text"])]
        ))

    try:
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=config.SYSTEM_PROMPT,
                temperature=config.TEMPERATURE,
                max_output_tokens=config.MAX_OUTPUT_TOKENS,
            ),
        )
        reply = (response.text or "").strip()
        if not reply:
            raise RuntimeError("Gemini returned an empty response.")

        history.append({"role": "assistant", "text": reply})
        session["chat_history"] = history[-config.MAX_HISTORY_MESSAGES:]
        session.modified = True

        return jsonify({"reply": reply})
    except Exception as exc:
        # Don't expose API/provider internals to the browser.
        print("Chat error:", repr(exc))
        return jsonify({"error": "Sorry, I couldn't process that message right now."}), 500

@app.post("/clear")
def clear():
    session.pop("chat_history", None)
    return jsonify({"ok": True})

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=False)
