# Backend

Session engine, multimodal verification pipeline, and Stripe test settlement.

Product story and how the pieces fit: [`README.md`](../README.md) · customer UI: [`frontend/README.md`](../frontend/README.md)

```
backend/
  app.py                         # CORS, routes
  config.py                      # env
  store.py                       # in-memory sessions (demo)
  api/routes/sessions.py         # HTTP
  models/schemas.py              # API contract
  models/session.py              # workflow state
  services/workflow.py           # claim → challenge plan
  services/engine.py             # cursor: next / retry / done
  services/judge.py              # take → attestation
  services/payments.py           # which products refund
  skills/                        # planner + grader contracts
  integrations/                  # model client, frame sample, Stripe
  scripts/simulate.py            # debug walk: engine + Stripe
```

```bash
source ../.venv/bin/activate
uvicorn app:app --reload --port 8000
```

**Swagger:** http://127.0.0.1:8000/docs

## API

`POST /api/sessions` — `{ "products": [{ "id", "name", "reason", "price_cents" }] }`

`GET /api/sessions/{id}`

`POST /api/sessions/{id}/recordings` — multipart `frame` stills (up to 8) and optional `video`. Live mode runs the multimodal network. Debug mode (Swagger or `python scripts/simulate.py`) walks the engine through to Stripe test settlement.

When `action` is `done`, `terminal.payment` is `full | partial | none` with `refunded_cents` and `provider_ref`. Confirm refunds in the Stripe test dashboard (Test mode ON).

Sessions are in-memory for the demo. Restart the process and start a new verification.
