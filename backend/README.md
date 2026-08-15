# Backend

FastAPI session engine. OpenAI and Stripe are isolated under `integrations/`.

```
backend/
  app.py                      # CORS, routes
  config.py                   # env
  store.py                    # in-memory sessions (swap later)
  api/routes/sessions.py      # HTTP
  models/schemas.py           # API contract
  models/session.py           # workflow state
  services/workflow.py        # products + reasons → challenge plan
  services/engine.py          # cursor: next challenge / product / done
  services/judge.py           # recording → pass/fail
  services/payments.py        # which products get refunded
  integrations/openai_client.py   # FILL IN
  integrations/stripe_client.py   # FILL IN
```

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## API

`POST /api/sessions` — start. Body: `{ "products": [{ "id", "name", "reason", "price_cents" }] }`

`GET /api/sessions/{id}` — current cursor

`POST /api/sessions/{id}/recordings` — multipart `video` file, optional form field `demo_result=pass|fail` to skip the judge while UI is built

Every response:

```json
{
  "session_id": "ses_…",
  "status": "in_progress",
  "last_result": "pass",
  "action": "show_challenge | next_challenge | next_product | done",
  "current": { "product": { "…", "index": 1, "total": 2 }, "challenge": { "instruction": "…", "index": 1, "total": 3 } },
  "terminal": null
}
```

When `action` is `done`, `current` is null and `terminal` has payment `full | partial | none`.

## Teammates

OpenAI: implement `plan_challenges` and `judge_recording` in `integrations/openai_client.py`. Do not advance the session there.

Stripe: implement `settle_refunds` in `integrations/stripe_client.py`. The engine only calls it at the terminal state, for products with `status == "refund"`.
