# Frontend

Customer UI for the live verification. React + Vite + Tailwind.

Product story: [`README.md`](../README.md) · API / pipeline / Stripe: [`backend/README.md`](../backend/README.md)

Pick a product, describe the issue, complete the camera challenges. Frames go to the API; a verified session settles a returnless refund.

Catalog: Wireless Headphones ($129), Portable Charger ($49), Phone Case ($29).

```bash
# terminal 1
cd backend && source ../.venv/bin/activate && uvicorn app:app --reload --port 8000

# terminal 2
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 — allow the camera. Vite proxies `/api/sessions` to port 8000.

Swagger and debug mode (engine + Stripe test path) live at http://127.0.0.1:8000/docs.
