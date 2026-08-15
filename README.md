# InHand

**Your CAPTCHA for physical products.**

Verify it while it's InHand.

InHand is liveness verification for physical goods. A customer spends about twenty seconds on live camera challenges generated from *this* product and *this* claim. Merchants get proof. Honest customers get their money back — no box, no label, no drop-off, no waiting.

Returns and damaged-item claims are the wedge. The company is a **verification layer between software and the physical world**.

| | Docs |
|---|---|
| Live UI + camera | [`frontend/README.md`](frontend/README.md) |
| Session engine, pipeline, Stripe | [`backend/README.md`](backend/README.md) |
| This page | Product story, how to run it, how to embed it |

---

## Both sides lose today

**Merchant.** Refund requests pile up. Photos of “damage.” Returned boxes. Support tickets.

> *They’re asking for a refund, but how am I supposed to know what’s actually wrong with the product from one photo? I want to trust my customers, but my margins are already tight. I can’t afford to get every refund wrong.*

```
MERCHANT POV
Fraud · Manual review · Return costs
```

**Customer.** They open the package. Wrong item. Or the hinge is already cracked.

> *They literally sent me the wrong product. Now I have to find a box, print a label, drop it off, and wait days for my refund? I don’t want to do all of that.*

```
CUSTOMER POV
Package it · Ship it · Wait
```

Merchants need proof. Honest customers want their money back. Generative AI is making static photos easier than ever to fake.

**Nearly $850B in U.S. merchandise returns every year.** NRF puts 2025 returns at $849.9B (19.3% of online sales) and estimates 9% are fraudulent. Stripe estimates ~$100B lost globally to refund abuse. Optoro: processing a return can cost 20–39% of the item and about 2× outbound labor.

```
TRUST THE CUSTOMER          RETURN THE PRODUCT
fast + cheap                expensive + slow
fraud exposure              physical verification
```

InHand is the third option: **verify it remotely, then decide whether it even needs to move.**

Face recognition needed liveness because recognizing Alice's face did not prove Alice was present. We apply the same idea to objects.

| Object recognition | InHand |
|---|---|
| “Does this look like the headphones?” | “Are they actually here, the correct pair, and actually damaged?” |

Don't classify a customer-selected photo as fake. Ask the physical world a question they could not have prepared for.

---

## The live check

Instead of another upload, InHand generates **unpredictable live challenges** after the session starts, from the product and the claim.

```
What went wrong?
Left hinge arrived cracked.
```

1. Rotate the headphones clockwise until the logo faces us.
2. Cover the right earcup (while still holding them).
3. Show the serial number, if this product has one.
4. Show us the damaged hinge.

As they go, the merchant sees structured facts — not a “fake image: 82%” score:

```
PRODUCT PRESENT     Verified
SAME OBJECT         Verified
SERIAL MATCH        Verified
DAMAGE              Verified

INHAND VERIFIED
Refund approved. No return required.
```

We verify the product is physically present, stays consistent through the session, matches the order, and shows the condition being claimed.

**Verified claims refund immediately.** If InHand is unsure, the claim goes to **review** — it does not automatically accuse the customer.

In this demo: Wireless Headphones ($129), Portable Charger ($49), Phone Case ($29). We run three checks (`pose`, `interact`, `inspect`). Inspect is written from their words — stain → the stain.

---

## Better for merchants. Better for customers.

| Merchant | Customer |
|---|---|
| Return avoided, claim closed | Refund received, product still in hand |
| Less fraud, less manual work | No box, label, drop-off, or waiting |
| Safer returnless refunds | Feels like help, not an interrogation |

UPS research: 86% of consumers surveyed prefer no-box, no-label returns with instant refunds. Happy Returns: in-person Return Bar verification cuts fraud ≥85% vs mail-in. That validates physical checks. InHand moves the checkpoint **upstream** — before a truck rolls.

```
TODAY                         INHAND

Customer                      Customer
   ↓                             ↓
ship / drop-off               LIVE VERIFICATION
   ↓                             ↓
warehouse look                decision
   ↓                             ├── refund now / keep item
refund                           └── ship only if necessary
```

Sometimes the right reverse-logistics decision is **no logistics**.

InHand is also a neutral record at the moment the return begins (`T1` condition vs warehouse `T2`). Transit damage, a wrong original shipment, or a later swap all become comparable — software that does not automatically side with either party.

---

## Shopify, and a city that already moves too many boxes

Built to sit in **existing Shopify and DTC commerce workflows**: damaged-item claim → Verify with InHand → Verified | Inconclusive → the merchant’s policy. A few hundred lines of TypeScript. No native app. See [Merchant integration](#merchant-integration).

New York is not the company. It makes the benefit obvious. ~2.5 million package deliveries a day (2024). For someone in an apartment: why ship a low-value damaged item across the city so somebody else can look at it?

Verify it while it's InHand. Move only the goods that actually need to move.

---

## Bigger than returns

```
RETURNS → WARRANTIES → RESALE → RENTALS → INSURANCE
        → equipment financing → logistics / custody
```

Returns are where we start. InHand can become the verification layer between software and the physical world.

```
inhand.prove_present()
inhand.prove_identity()
inhand.prove_condition()
inhand.prove_function()
inhand.prove_possession()
inhand.prove_transfer()
```

Mid-market retailers already know *how risky this customer is*. InHand answers *what is physically true about this item?* Complementary signals — an input to their refund engine, not a replacement.

---

## The verification pipeline

The live video feed is processed through a **single, end-to-end native multimodal neural network**, trained jointly across time-series text, vision, and audio frames. The model extracts semantic meaning and grades the authenticity of each challenge.

```
claim + product
        ↓
challenge planner          (what to ask *this* item, *this* defect)
        ↓
live capture               (~8s, eight frames across the take)
        ↓
multimodal network         (vision + instruction + claim, jointly)
        ↓
structured attestation     present / same object / condition
        ↓
session engine             retry once · next challenge · or settle
        ↓
payment                    returnless refund when the item verifies
```

Not an image-fake classifier. It scores the **requested physical response**: named side to camera, fingers on the named part while the item is held, claimed defect in close-up. Extra gripping fingers are expected.

Policy: one retry, two consecutive misses fail the *item* (not the person), cap of four takes, all planned checks must pass to refund that SKU. Stripe test settlement returns `terminal.payment`: `full` | `partial` | `none`, plus `refunded_cents` and a provider reference.

Details: [`backend/README.md`](backend/README.md).

---

## Run it right now

Two terminals. Full notes in [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md).

```bash
# API  —  see backend/README.md
cd backend
source ../.venv/bin/activate
uvicorn app:app --reload --port 8000
```

```bash
# camera UI  —  see frontend/README.md
cd frontend
npm install
npm run dev
```

| | |
|---|---|
| Live UI | http://localhost:5173 |
| API | http://127.0.0.1:8000 |
| **Swagger** | http://127.0.0.1:8000/docs |
| Health | http://127.0.0.1:8000/health |

Pick a product, describe what went wrong, allow the camera. Vite proxies `/api/sessions` to the API. Demo sessions live in memory — restart the API and start a new verification.

### Swagger and debug mode

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) is the contract.

**Live pipeline** — `POST /api/sessions`, then `POST /api/sessions/{id}/recordings` with `frame` stills. Plan → observe → attest.

**Debug mode** — same routes, no camera: walk the session engine and **Stripe test settlement** until `action` is `done`. Read `terminal.payment` (`re_…` / `pi_…`). Confirm in the [Stripe test dashboard](https://dashboard.stripe.com/test/payments) with Test mode ON.

```bash
cd backend && python scripts/simulate.py
```

```
POST /api/sessions     { "products": [{ "id", "name", "reason", "price_cents" }] }
GET  /api/sessions/{id}
POST /api/sessions/{id}/recordings     frame[] stills · optional video
```

`action`: `show_challenge` → `retry_challenge` | `next_challenge` | `next_product` → `done`.

---

## Merchant integration

A small TypeScript or JavaScript client: start a session, show one instruction, send frames, follow `action`, refund from `terminal.payment`. Drops into a DTC returns page, a Shopify theme app block / customer-account extension, or any refund button.

```ts
const API = "https://your-inhand-host";

export async function startCheck(product: {
  id: string;
  name: string;
  reason: string;
  price_cents: number;
}) {
  const res = await fetch(`${API}/api/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ products: [product] }),
  });
  return res.json();
}

export async function submitFrames(sessionId: string, frames: Blob[]) {
  const body = new FormData();
  frames.forEach((blob, i) => body.append("frame", blob, `frame-${i}.jpg`));
  const res = await fetch(`${API}/api/sessions/${sessionId}/recordings`, {
    method: "POST",
    body,
  });
  return res.json();
}
```

```
Damaged-item claim → Verify with InHand → Verified | Inconclusive → existing policy
```

---

## Why this is not another detector

**Not an AI-fraud score.** Active challenge–response. False positives should not accuse real customers.

**Not C2PA.** File provenance does not prove this is the correct item, this order, this defect, or possession *now*.

**Not capture-auth alone.** A trusted camera is useful underneath. The product is: specify the claim → unpredictable challenge → live response → structured attestation.

---

## Edge cases (design constraints)

**Real-time generative video?** Adversarial, like biometric liveness. Changing challenges, temporal continuity, device signals, depth/parallax, identifiers, risk models. Not magical proof — make fabrication much harder than a fake photo.

**Camera pointed at a screen?** Interaction, motion, parallax, reflection/screen signals, secure capture.

**Two identical products?** Strongest id available (serial, IMEI, VIN, QR, NFC). Report verification *strength*.

**$20 shirt, no serial?** Category/SKU and visible condition — no unique-item claim. Start with rigid, serialized goods.

**Internal failure?** Function challenges: power on, button, LED, error code, Bluetooth.

**Bad light, unsure model, accessibility?** Verified / Inconclusive / Manual review. Never equate a miss with fraud.

**Why not FaceTime support?** Human inspection does not scale. This is a machine-executable protocol.

---

## Extensions

**Robust vision** on the same capture: tracking and re-id, SKU embeddings, serial OCR, flow/depth liveness, replay detectors, damage segmentation. They raise the cost of beating the protocol; they do not replace it.

**Reinforcement learning on real outcomes.** Each session is `object × claim × challenge × response × outcome`. Policies learn which challenges work per product class, what legitimate motion looks like, and which defects can be confirmed remotely. Reward is downstream truth: refund that stood, inspection that agreed, chargeback that didn't.

Distribution: Shopify and retailers → returns platforms → payments → 3PLs → warranties, insurers, marketplaces.

The long-term company is not “AI for returns.” It is an **API for establishing physical truth remotely**.

---

## The pitch

Nearly $850 billion of merchandise comes back in the U.S. every year. Ecommerce still verifies physical claims with photos and expensive reverse logistics. Generative AI made those photos cheap to fake. Honest customers still wait days.

InHand is the CAPTCHA for physical products. Twenty seconds of unpredictable live challenges. Presence, identity, condition. Instant returnless refunds when it checks out. Review when it doesn’t — never an automatic accusation.

Returns are the start. The layer is for any system that needs to know a physical thing exists and is in the state someone claims.

**InHand — Verify it while it's InHand.**  
CAPTCHA for physical products.
