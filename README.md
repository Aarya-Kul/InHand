# InHand

Verify it while it's InHand.

Hackathon app: customer picks products, explains the refund, then completes a live camera challenge per product. The backend owns the workflow (product → challenge → next → refund).

## Who owns what

| Path | Owner |
|---|---|
| `backend/services/` `backend/api/` | workflow / session engine |
| `backend/integrations/openai_client.py` | OpenAI teammate |
| `backend/integrations/stripe_client.py` | Stripe teammate |
| `frontend/src/` except `api.ts` | UI teammate (Figma / Base44 port) |
| `frontend/src/api.ts` | shared contract — do not break the response shape |

## Run locally

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --port 8000
```

Frontend (phone-friendly on the same Wi-Fi via `--host`):

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173 — placeholder UI can walk a session with Demo pass / Demo fail. API docs: http://127.0.0.1:8000/docs

## Flow

1. UI `POST /api/sessions` with `{ products: [{ id, name, reason, price_cents }] }`
2. Backend plans challenges per product (OpenAI placeholder today)
3. Response includes `current` = first product, first challenge — UI shows that
4. UI uploads a recording to `POST /api/sessions/{id}/recordings`
5. Backend judges pass/fail, then returns one of:
   - `next_challenge` — same product, next instruction
   - `next_product` — first challenge of the next product
   - `done` — `terminal.payment.status` is `full` | `partial` | `none` and Stripe placeholder has run
6. UI renders that screen and repeats until `done`

A product is refunded if **all** of its challenges passed (`PRODUCT_PASS_MODE=all`). Failed challenges still advance; they just count against the refund.
