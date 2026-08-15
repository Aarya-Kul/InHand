/** API contract for the UI teammate. Replace App.tsx; keep using these helpers. */

export type ProductIn = {
  id: string;
  name: string;
  reason: string;
  price_cents?: number;
  sku?: string;
};

export type SessionResponse = {
  session_id: string;
  status: "in_progress" | "done";
  last_result: "pass" | "fail" | null;
  action: "show_challenge" | "next_challenge" | "next_product" | "done";
  current: {
    product: {
      id: string;
      name: string;
      reason: string;
      index: number;
      total: number;
      price_cents: number;
    };
    challenge: {
      id: string;
      instruction: string;
      index: number;
      total: number;
    };
  } | null;
  terminal: {
    payment: {
      status: "full" | "partial" | "none";
      refunded_cents: number;
      provider_ref: string | null;
      message: string;
    };
    products: {
      id: string;
      name: string;
      refunded: boolean;
      passed_challenges: number;
      total_challenges: number;
      price_cents: number;
    }[];
  } | null;
};

export async function startSession(products: ProductIn[]): Promise<SessionResponse> {
  const res = await fetch("/api/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ products }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionResponse> {
  const res = await fetch(`/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/** Send the camera recording. demoResult is only for backend testing without OpenAI. */
export async function submitRecording(
  sessionId: string,
  video?: Blob,
  demoResult?: "pass" | "fail",
): Promise<SessionResponse> {
  const body = new FormData();
  if (video) body.append("video", video, "challenge.webm");
  if (demoResult) body.append("demo_result", demoResult);
  const res = await fetch(`/api/sessions/${sessionId}/recordings`, {
    method: "POST",
    body,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
