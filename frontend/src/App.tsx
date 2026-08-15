import { useState } from "react";
import { startSession, submitRecording, type SessionResponse } from "./api";

const SAMPLE = [
  {
    id: "sku_headphones",
    name: "AeroPods",
    reason: "Left hinge cracked",
    price_cents: 29900,
  },
  {
    id: "sku_keyboard",
    name: "KeyLine 75",
    reason: "Spacebar stuck",
    price_cents: 14900,
  },
];

/** Placeholder smoke UI so the backend can be demoed. Replace this file with Figma/Base44 screens. */
export default function App() {
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function begin() {
    setBusy(true);
    setError(null);
    try {
      setSession(await startSession(SAMPLE));
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  async function send(demoResult: "pass" | "fail") {
    if (!session) return;
    setBusy(true);
    setError(null);
    try {
      setSession(await submitRecording(session.session_id, undefined, demoResult));
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ fontFamily: "sans-serif", maxWidth: 520, margin: "2rem auto", padding: 16 }}>
      <p style={{ color: "#666", fontSize: 13 }}>UI placeholder — swap this page, keep src/api.ts</p>
      <h1>InHand</h1>
      {!session && (
        <button disabled={busy} onClick={begin}>
          Start return with sample products
        </button>
      )}
      {session?.current && (
        <section>
          <p>
            Product {session.current.product.index}/{session.current.product.total}:{" "}
            <strong>{session.current.product.name}</strong>
          </p>
          <p>{session.current.product.reason}</p>
          <p>
            Challenge {session.current.challenge.index}/{session.current.challenge.total}
          </p>
          <h2>{session.current.challenge.instruction}</h2>
          {session.last && (
            <p>
              Challenge: <strong>{session.last.challenge}</strong>
              {session.last.reason ? ` — ${session.last.reason}` : ""}
              {session.last.product
                ? ` · Product ${session.last.completed_product?.name}: ${session.last.product}`
                : ""}
            </p>
          )}
          <p>Action: {session.action}</p>
          <button disabled={busy} onClick={() => send("pass")}>
            Demo pass
          </button>{" "}
          <button disabled={busy} onClick={() => send("fail")}>
            Demo fail
          </button>
        </section>
      )}
      {session?.terminal && (
        <section>
          <h2>Payment {session.terminal.payment.status}</h2>
          <p>{session.terminal.payment.message}</p>
          <ul>
            {session.terminal.products.map((p) => (
              <li key={p.id}>
                {p.name}: {p.refunded ? "refund" : "return item"} ({p.passed_challenges}/
                {p.total_challenges})
              </li>
            ))}
          </ul>
        </section>
      )}
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </main>
  );
}
