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
  skills/planner.py           # challenge-plan prompt + schema
  skills/judge.py             # pass/fail prompt + schema
  skills/schemas.py           # exact JSON objects OpenAI must return
  integrations/openai_client.py
  integrations/frames.py      # video → 3 JPEGs for vision
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

`demo_result` skips OpenAI vision. Omit it and attach `video` to run the judge.

### Session rules

- In-memory only: gone on uvicorn restart or `--reload`
- `done` sessions are exhausted; create a new session to test another path
- Pass → `next_challenge` (or finish the product)
- First fail → `retry_challenge` (same instruction, `attempt: 2`)
- Two fails in a row → fail the product, skip remaining challenges
- Max 4 takes per product

Every recording response includes `last` so the UI can flash pass/fail, then follow `action`:

```json
{
  "action": "next_challenge",
  "last": {
    "challenge": "pass",
    "reason": "logo facing camera",
    "product": null,
    "completed_product": null
  },
  "current": { "challenge": { "instruction": "…" } }
}
```

When the product’s last challenge is judged:

```json
{
  "action": "next_product",
  "last": {
    "challenge": "fail",
    "reason": "damage not visible",
    "product": "fail",
    "completed_product": { "name": "AeroPods", "refunded": false, "passed_challenges": 2, "total_challenges": 3 }
  },
  "current": { "product": { "name": "KeyLine" }, "challenge": { "instruction": "…" } }
}
```

`last.product` is only set on `next_product` or `done` (the item you just finished). `last.challenge` is always the recording you just sent.

When `action` is `done`, `current` is null and `terminal` has payment `full | partial | none`.

## Teammates

OpenAI: put `OPENAI_API_KEY` in `.env`. Prompts and output shapes are in `skills/` — edit those, not the session engine. With no key, planning uses the fallback challenges and the judge auto-passes (smoke demo). With a key, the planner returns `ChallengePlan` and the judge returns `JudgeVerdict` via structured outputs.

Stripe: implement `settle_refunds` in `integrations/stripe_client.py`. The engine only calls it at the terminal state, for products with `status == "refund"`.
