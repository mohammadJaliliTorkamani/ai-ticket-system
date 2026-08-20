# Ticketifier

Ticketifier is a single-page LLM request workbench for backend developers. Enter an OpenAI API key and message, wait for the response, then inspect the sanitized REST lifecycle across the browser, Ticketifier API, and OpenAI Responses API.

Ticketifier is open-source software created by [MJalili.com](https://mjalili.com). Source repository: [MJaliliT/ai-ticket-system](https://github.com/MJaliliT/ai-ticket-system).

**Live demo:** [ticketifier.mjalili.com](https://ticketifier.mjalili.com)

## Repository safety

Documentation and examples use placeholders only. Never commit or paste an API key, `.env` file, VPS IP address, SSH username, private key, host fingerprint, registry token, or other deployment credential. Keep production values in protected environment files or repository secrets. The public project and source-code URLs above are intentional and are not deployment credentials.

## Product behavior

- No registration, login, cookies, sessions, database, queue, or application accounts
- OpenAI API keys are accepted for one HTTPS request, held only in memory, never stored, and cleared from the browser form after submission
- Authorization values are always represented as `[REDACTED]` in the REST transcript
- The interface reports latency, model, token usage, request IDs, HTTP status, headers, request bodies, response bodies, loading, validation, quota, authentication, and upstream errors
- Requests are limited by IP, message length, model allowlist, timeout, retry count, and maximum output tokens

## Architecture

```text
Browser -> host Nginx/TLS -> loopback web gateway -> FastAPI -> OpenAI Responses API
```

The browser sends the API key only to Ticketifier over HTTPS. The backend uses it for one OpenAI request and does not log or persist it. Production has two stateless, non-root containers: `gateway` and `api`.

## Local development

```bash
cp .env.example .env
python -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --reload
cd web
npm ci --ignore-scripts
npm run dev
```

Open `http://127.0.0.1:5173`.

## Quality checks

```bash
ruff check .
pytest --cov=app
pip-audit -r requirements.txt
cd web
npm run lint
npm test
npm run build
npm audit --omit=dev --audit-level=high
```

## API

`POST /api/respond`

```json
{
  "api_key": "<YOUR_OPENAI_API_KEY>",
  "message": "Explain idempotency keys.",
  "model": "gpt-5-mini"
}
```

The response contains the model output, latency, usage, local/provider request IDs, and four sanitized transcript entries. Development documentation is at `/api/docs`; production documentation is disabled.

- `GET /api/health/live`
- `GET /api/health/ready`

See [deployment](docs/DEPLOYMENT.md), [operations](docs/OPERATIONS.md), and [security](docs/SECURITY.md).
