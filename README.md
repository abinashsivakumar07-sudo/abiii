# Carrier Assistant — Flask + Gemini

A domain-specific **Carrier Assistant** chatbot built with Flask and the Google Gemini API.

## Features

- No login or registration.
- Temporary, per-browser/device Flask session chat history.
- Gemini is instructed to answer only mobile-carrier/telecom questions.
- Configuration is centralized in `config.py`.
- Gemini API key can be supplied through `.env` or `config.py`.
- Responsive UI for mobile, tablet, laptop and desktop.
- Customizable title, domain, prompt, welcome message, colors and UI style.
- Render + Gunicorn deployment.
- Configurable `PORT` through the environment.

## Project structure

```text
carrier-assistant/
├── app.py
├── config.py
├── .env
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

## 1. Get a Gemini API key

Create a Gemini API key from Google AI Studio, then put it in `.env`:

```env
GEMINI_API_KEY=your_api_key_here
FLASK_SECRET_KEY=use-a-long-random-secret
```

Do not commit a real API key to GitHub.

If you prefer, set `GEMINI_API_KEY` directly in `config.py`, although `.env` is recommended.

## 2. Install

Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Run locally

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

You can also run Gunicorn on Linux/Render:

```bash
gunicorn app:app
```

The application reads `PORT` from the environment and defaults to `5000` locally.

## 4. Customize for another chatbot

Edit only `config.py` for the main chatbot identity:

- `TITLE`
- `DOMAIN`
- `WELCOME_MESSAGE`
- `SYSTEM_PROMPT`
- `UI_STYLE`
- `PRIMARY_COLOR`
- `ACCENT_COLOR`
- `BG_COLOR`
- `SURFACE_COLOR`
- `TEXT_COLOR`
- `MUTED_COLOR`
- `PORT`

For a different domain, rewrite `SYSTEM_PROMPT` so the allowed scope exactly matches the new domain.

### Example titles

- Cricket Assistant
- Tech Support Assistant
- Study Assistant
- Food & Nutrition Assistant
- Travel Assistant

For each title, change the logo/visual details in `templates/index.html` if you want a different design, while keeping the same Flask backend.

## 5. How session privacy works

There is no login system.

Each browser/device gets its own Flask session cookie. The temporary conversation history is stored in that session, not in a shared global Python variable. The server sends only that session's history to Gemini.

Important deployment note: use a strong `FLASK_SECRET_KEY`.

This implementation does not intentionally persist chat messages in a database. A browser session is temporary and can disappear when the session expires or is cleared.

For multiple Render instances/workers, production-grade shared session storage would require a server-side session store such as Redis. This starter keeps the architecture simple and avoids a database.

## 6. Render deployment

Push the project to GitHub with these files in the repository root:

```text
app.py
config.py
requirements.txt
README.md
templates/index.html
```

In Render, create a **Web Service** and set:

**Build Command**
```bash
pip install -r requirements.txt
```

**Start Command**
```bash
gunicorn app:app
```

Add environment variables in Render:

```text
GEMINI_API_KEY = your_real_key
FLASK_SECRET_KEY = a_long_random_secret
```

Render supplies the `PORT` environment variable automatically; the app reads it through `config.py`.

## Troubleshooting

### `Could not open requirements file`

Make sure `requirements.txt` is in the repository root, at the same level as `app.py`:

```text
repo/
├── app.py
├── config.py
├── requirements.txt
└── templates/
    └── index.html
```

Then commit and push the file before redeploying.

### Gemini API key missing

Check that `.env` exists locally and contains:

```env
GEMINI_API_KEY=your_api_key_here
```

On Render, add the key under Environment Variables instead of uploading `.env`.

### Model unavailable

If your Gemini account/project does not expose the configured model, change `GEMINI_MODEL` in `config.py` to a Gemini model available to your API account.

## Security notes

- Never publish a real Gemini API key in GitHub.
- Use a strong `FLASK_SECRET_KEY` in production.
- This is not an account system; there is no user authentication.
- Do not put sensitive personal information into the chatbot.
