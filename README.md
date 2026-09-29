# PocketSmart AI

PocketSmart AI turns a spending limit into a practical starter plan for home updates, gatherings, and jewelry. This project includes a responsive browser interface, a FastAPI service, SQLite accounts and plan history, and optional multimodal Gemini guidance for jewelry outfit photos.

## What is included

- Home, party, and jewelry planners with input validation and budget estimates.
- Registration, sign-in, bearer tokens, sign-out, account session details, and per-user recommendation history.
- Optional Gemini guidance. Without an API key, deterministic sample recommendations still work.
- Marketplace search links for Amazon, Flipkart, IKEA, Zomato, Swiggy, and Google Maps.
- Interactive API documentation at `/docs`.

The project notes mention both Flask and FastAPI. The detailed backend milestones specify FastAPI and explicit route schemas, so this implementation uses FastAPI. Marketplace results are curated examples with search links, not live inventory, scraped listings, or verified quotes; live merchant APIs require separate credentials and integrations.

## Requirements

- Python 3.11 or newer
- Visual Studio Code and its Python extension
- Optional: a Gemini API key from Google AI Studio for generated planning notes and outfit-image analysis

## Set up in VS Code on Windows

1. Open the `PocketSmart AI` project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

4. Install the dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Create your local environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

   Set `SECRET_KEY` in `.env` to a long random value. For Gemini, paste your Google AI Studio key as `GEMINI_API_KEY`. Keep `.env` private; it is excluded from Git. The default model is `gemini-3.8-flash`; change `GEMINI_MODEL` if your account uses another available model.

6. In VS Code, select the `.venv` interpreter with **Ctrl+Shift+P → Python: Select Interpreter**.
7. Start the app:

   ```powershell
   python -m uvicorn app.main:app --reload
   ```

8. Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Create an account, then choose a planner. API docs are at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

For debugging, use **Run and Debug → PocketSmart AI (FastAPI)** or press **F5** after installing the recommended Python extension.

The first run creates `pocketsmart.db` in the project folder. Do not commit this database if it contains real user data.

## Run and verify

With the virtual environment active, run the automated checks:

```powershell
python -m pytest -q
```

You can also check the running service at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health). It reports whether a Gemini API key is configured.

For a manual check, register, try each planner with a small budget, review a result, and open **My plans**. Try jewelry with and without a JPG, PNG, or WEBP outfit photo. Without a Gemini key, the deterministic sample plans are used. With a key, Gemini adds a personalized note and may use the image to comment on visible colors and style.

## Main routes

| Route | Purpose |
| --- | --- |
| `POST /register`, `POST /login`, `POST /logout`, `POST /token` | Account creation and token sign-in |
| `GET /session-info`, `GET /session-data` | Current session and saved-plan count |
| `POST /generate-home` | Create a home plan (JSON) |
| `POST /generate-party` | Create an event plan (JSON) |
| `POST /generate-jewelry` | Create a jewelry plan (multipart form, optional image) |
| `GET /history` | List the signed-in user's recent plans |
| `GET /recommendations-details/{id}` | Retrieve one saved plan |
| `GET /health`, `GET /startup` | Application readiness details |

Protected routes expect `Authorization: Bearer <access_token>`. The browser stores the token in local storage and clears it at sign-out. For a deployed service, use HTTPS, set a private `SECRET_KEY`, configure allowed CORS origins, and review token storage/session policy for your environment.

## Project layout

```text
app/
  main.py                 FastAPI app and page routes
  config.py               Environment settings
  database.py             SQLite setup
  security.py             Password hashing and JWT handling
  schemas.py              Validated request/response models
  routes/                 Account, planner, and history endpoints
  services/               Gemini integration and sample catalog
  templates/index.html    Responsive planner interface
  static/                 Browser JavaScript and CSS
tests/                    API and flow checks
.vscode/                  Python interpreter and F5 launch settings
requirements.txt
.env.example
```
