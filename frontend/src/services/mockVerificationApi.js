/** Talks to the InHand FastAPI backend. Keeps the same methods the Base44 pages already call. */

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

let cached = {
  sessionId: null,
  challenge: null,
  terminal: null,
};

function mapChallenge(current, last) {
  if (!current?.challenge) return null;
  const retry = current.challenge.attempt > 1;
  return {
    id: current.challenge.id,
    instruction: current.challenge.instruction,
    supportingText: retry
      ? "Try the same check again."
      : "Keep the item centered and clearly visible.",
    durationSeconds: 8,
    attempt: current.challenge.attempt,
    index: current.challenge.index,
    total: current.challenge.total,
  };
}

async function parse(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail ? JSON.stringify(data.detail) : res.statusText;
    throw new Error(detail);
  }
  return data;
}

export const verificationApi = {
  async initializeRefundSession(input = {}) {
    const product = input.product;
    const reason = input.reason || "Item issue";
    const res = await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        products: [
          {
            id: product?.id || "item",
            name: product?.name || "Product",
            reason,
            price_cents: Math.round((product?.price || 0) * 100),
          },
        ],
      }),
    });
    const data = await parse(res);
    cached = {
      sessionId: data.session_id,
      challenge: mapChallenge(data.current, data.last),
      terminal: data.terminal,
    };
    return { sessionId: data.session_id, challenge: cached.challenge };
  },

  async submitIssueDescription() {},

  async startVerification(sessionId) {
    if (cached.sessionId === sessionId && cached.challenge) return cached.challenge;
    const res = await fetch(`/api/sessions/${sessionId}`);
    const data = await parse(res);
    cached.challenge = mapChallenge(data.current, data.last);
    cached.terminal = data.terminal;
    return cached.challenge;
  },

  async submitChallengeVideo(sessionId, _challengeId, videoBlob, stills = []) {
    const body = new FormData();
    if (videoBlob && videoBlob.size) {
      body.append("video", videoBlob, "challenge.webm");
    }
    stills.filter(Boolean).forEach((blob, i) => {
      body.append("frame", blob, `frame-${i}.jpg`);
    });
    const res = await fetch(`/api/sessions/${sessionId}/recordings`, {
      method: "POST",
      body,
    });
    const data = await parse(res);
    cached.terminal = data.terminal;
    cached.challenge = mapChallenge(data.current, data.last);
    const passed = data.last?.challenge === "pass";
    const complete = data.action === "done";
    return {
      challengeId: data.current?.challenge?.id || _challengeId,
      verdict: passed ? "passed" : "failed",
      next: complete ? null : cached.challenge,
      complete,
      payment: data.terminal?.payment || null,
    };
  },

  async waitForRefundDecision() {
    await delay(1600);
    const status = cached.terminal?.payment?.status;
    return status === "full" || status === "partial" ? "approved" : "rejected";
  },
};

export const DEMO_CONFIG = { finalOutcome: "auto", reviewDelay: 1600 };
