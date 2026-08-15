# InHand

Verify it while it's InHand.

Hackathon app: customer picks products, explains the refund, then completes a live camera challenge per product. The backend owns the workflow (plan → judge each take → retry/advance → refund).

## Tech stack

| Layer | What |
|---|---|
| API | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| Vision / LLM | OpenAI `gpt-4o` structured outputs (`ChallengePlan`, `JudgeVerdict`) |
| Frames | OpenCV: video/image → 3 JPEGs (OpenAI does not take raw video) |
| Payments | Stripe placeholder in `integrations/stripe_client.py` |
| Session store | In-memory dict (lost on process restart / `--reload`) |
| Frontend | React 19 + Vite + TypeScript (`frontend/src/api.ts` is the contract) |
| UI source | Base44/Figma screens copied into `frontend/src` — no Base44 runtime |

**Demo limits (per product)**

- Planner proposes 4 challenge kinds (`pose`, `interact`, `identify`, `inspect`); we **run 3** (`pose` + `interact` + `inspect`)
- One retry on fail (`retry_challenge`)
- Two fails in a row → product failed, skip remaining challenges
- Max **4 takes** per product (blocks fail–pass loops)
- All planned challenges that ran must pass to refund that item
- Failed verification is not fraud — it means no returnless refund

**Env** (`backend/.env` or `backend/env`, gitignored)

```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
STRIPE_SECRET_KEY=
JUDGE_MODE=placeholder
PRODUCT_PASS_MODE=all
MAX_CHALLENGES=3
MAX_TAKES_PER_PRODUCT=4
MAX_CONSECUTIVE_FAILS=2
CORS_ORIGINS=*
```

If `OPENAI_API_KEY` is set, session start calls the planner and recordings without `demo_result` call the vision judge.

## Who owns what

| Path | Owner |
|---|---|
| `backend/services/` `backend/api/` | workflow / session engine |
| `backend/skills/` | OpenAI prompts + output schemas |
| `backend/integrations/openai_client.py` | OpenAI HTTP calls |
| `backend/integrations/stripe_client.py` | Stripe teammate |
| `frontend/src/` except `api.ts` | UI teammate (Figma / Base44 port) |
| `frontend/src/api.ts` | shared contract — do not break the response shape |

## Run locally

Backend (from repo root, venv may already exist at `./.venv`):

```bash
cd backend
source ../.venv/bin/activate   # or: python -m venv ../.venv && pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health
- Swagger: http://127.0.0.1:8000/docs

`--reload` **wipes sessions** (in-memory). After a code save, create a new session.

Frontend (phone-friendly with `--host`):

```bash
cd frontend
npm install
npm run dev
```

http://127.0.0.1:5173 — placeholder Demo pass/fail until Base44 screens land.

## Usage

### Customer flow (what the UI calls)

1. `POST /api/sessions` with products + refund reasons → first challenge
2. Show `current.challenge.instruction` (and `attempt` if 2)
3. `POST /api/sessions/{id}/recordings` with the camera `video` file
4. Banner `last`, then switch on `action`
5. Repeat until `done`; show `terminal.payment.status`: `full` | `partial` | `none`

### Actions the UI must handle

| `action` | Meaning |
|---|---|
| `show_challenge` | First challenge (session just created) |
| `retry_challenge` | Same instruction, second try (`attempt: 2`) |
| `next_challenge` | Next instruction on this product |
| `next_product` | This item is finished; first challenge of the next item |
| `done` | Session over; read `terminal` |

`last.challenge` is pass/fail for the take you just sent. `last.product` is set only when that item is finished.

A session is **exhausted** at `done`. Start a new `POST /api/sessions` to test another path. IDs do not survive server restart.

### Try the API (Swagger or curl)

Create a session:

```bash
curl -s -X POST 'http://127.0.0.1:8000/api/sessions' \
  -H 'Content-Type: application/json' \
  -d '{"products":[{"id":"sku_headphones","name":"AeroPods headphones","reason":"left hinge cracked","price_cents":29900}]}'
```

Copy `session_id`. Each recording uses the **same** id (do not create a new session per challenge).

Skip the camera (engine only):

```bash
curl -s -X POST "http://127.0.0.1:8000/api/sessions/SESSION_ID/recordings" -F 'demo_result=pass'
```

Use `demo_result=fail` to test retry / product fail. `demo_result` **does not** call the vision model.

Hit the OpenAI judge (no `demo_result`):

```bash
curl -s -X POST "http://127.0.0.1:8000/api/sessions/SESSION_ID/recordings" \
  -F 'video=@/path/to/headphones.jpg'
```

Walk a full demo without Swagger:

```bash
cd backend
python scripts/simulate.py
python scripts/simulate.py --fail-second
python scripts/simulate.py --video ~/photo.jpg
```

JSON body for `POST /api/sessions` must be valid JSON (closing `}` included) or Swagger returns 422.

## Flow (engine)

```
products + reasons
        ↓
OpenAI planner → 3 challenges (pose, interact, inspect)
        ↓
customer recording
        ↓
judge (OpenAI vision, or demo_result)
        ↓
pass  → next challenge
fail  → retry same challenge once
fail ×2 in a row → fail product, skip rest
4 takes without finishing → fail product
        ↓
all products done → Stripe placeholder → full | partial | none
```

---

## Product / UX

### The problem

When a customer reports that a product arrived damaged, the merchant usually has no way of physically inspecting the item unless it is shipped back.

Today, merchants typically have to rely on:

* customer-uploaded photos or videos
* written descriptions
* manual support review
* account and order history
* physically returning the product for inspection

This creates a tradeoff.

Trusting the customer is faster, but creates more fraud risk.

Returning the product provides stronger verification, but adds shipping, handling, inspection, and waiting time for both the merchant and the customer.

Generative AI also makes static visual evidence increasingly difficult to trust.

The question we are trying to solve is not simply:

> "Is this photo fake?"

It is:

> **"What is physically true about this product right now?"**

---

### The idea

InHand applies the idea of **liveness verification to physical products**.

Instead of only analyzing evidence that the customer chooses to upload, InHand asks the customer to respond to unpredictable instructions during a live camera session.

For example:

> Rotate the headphones clockwise.

> Cover the right earcup with two fingers.

> Show the serial number.

> Move the camera around the damaged hinge.

The challenges are presented after the verification session begins.

This gives the merchant a way to gather new evidence about whether:

* the product is physically present
* the same product remains present throughout the session
* it matches the expected product
* identifying information matches where available
* the customer can perform the requested physical interaction
* the reported damage or condition can be observed

---

### Customer experience

The experience should feel like a faster way to resolve a legitimate refund, not like an accusation.

The intended message is:

> **Show us the item for a few seconds so we can resolve your refund faster.**

Not:

> "Prove that you are not committing fraud."

The ideal customer flow is:

**1. Select the product**

The customer chooses the product they are requesting a refund for.

**2. Explain the issue**

The customer describes why they are requesting the refund.

Example:

> "The left hinge arrived cracked."

**3. Start live verification**

InHand opens the camera and explains that the customer will complete a few short product checks.

**4. Complete the challenges**

The customer follows one instruction at a time.

The interface should make each instruction:

* short
* easy to understand
* visually clear
* possible to complete on a phone
* easy to retry when necessary

**5. Receive the result**

After the challenges are completed, the customer receives a clear outcome.

Possible states include:

* Verified
* Partially verified
* Unable to verify

For the hackathon implementation, these map into the refund result generated by the existing backend workflow.

---

### UX principles

#### Keep it fast

The live verification should feel significantly easier than packaging and returning an item.

#### One instruction at a time

Customers should never have to remember several challenges at once.

#### Explain why the camera is needed

Users should understand that the verification helps the merchant resolve the claim faster.

#### Do not treat failure as fraud

A customer may fail a challenge because of poor lighting, camera quality, confusion, accessibility needs, or technical issues.

A failed challenge should only be treated as a verification signal.

#### Give clear feedback

The interface should communicate when:

* the object is visible
* the challenge is being recorded
* the action was recognized
* another attempt is required
* the verification is complete

#### Design mobile first

The customer is expected to hold and manipulate a physical product while using the camera, so the experience should require as little tapping and navigation as possible.

---

### Merchant value

InHand is not designed to replace a merchant's refund policy.

It provides additional physical evidence before the merchant makes a decision.

The goal is to help merchants make faster decisions while potentially reducing:

* unnecessary return shipments
* manual review
* fraudulent claims
* warehouse inspection
* customer waiting time

The first use case is especially relevant for **returnless refunds**, where a merchant may prefer to refund the customer without requiring the item to be shipped back.

---

### Design hypothesis

Our main product hypothesis for the hackathon is:

> **A short, unpredictable live camera challenge can provide stronger evidence of a product's physical presence and condition than a customer-selected photo alone.**

The prototype should make this idea understandable without requiring the user to understand the underlying computer vision or verification technology.

The experience should simply feel like:

**Claim**

↓

**Verify**

↓

**Resolve**

---

### Hackathon UX scope

For the hackathon, the design should stay focused on one complete customer journey:

**Choose product**

↓

**Explain refund reason**

↓

**Start verification**

↓

**Complete challenge**

↓

**Continue through remaining challenges/products**

↓

**See refund result**

The goal is not to design every possible return or fraud workflow.

The goal is to make the core InHand interaction feel simple, trustworthy, and immediately understandable.

---

### Future product direction

The hackathon focuses on damaged-item claims and refunds, but the same verification experience could eventually support other situations where software needs to understand the state of a physical object.

Examples include:

* warranties
* resale marketplaces
* rentals
* insurance claims
* logistics
* equipment verification

The broader product idea is:

> **Verify it while it's InHand.**

