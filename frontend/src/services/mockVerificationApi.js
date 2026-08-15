export const DEMO_CONFIG = { finalOutcome: "auto", reviewDelay: 1600 };

const challengesByProduct = {
  headphones: [
    {
      id: "full-item",
      instruction: "Show the entire pair of headphones.",
      supportingText: "Keep the item centered and clearly visible.",
      durationSeconds: 6,
    },
    {
      id: "damage-closeup",
      instruction: "Move closer to the cracked right ear cup.",
      supportingText: "Hold the damaged area steady for a moment.",
      durationSeconds: 6,
    },
    {
      id: "rotate-label",
      instruction: "Slowly rotate the headphones and show the product label.",
      supportingText: "Keep the label in focus as you move.",
      durationSeconds: 6,
    },
  ],
  charger: [
    {
      id: "full-item",
      instruction: "Show the entire portable charger.",
      supportingText: "Keep the item centered and clearly visible.",
      durationSeconds: 6,
    },
    {
      id: "damage-closeup",
      instruction: "Move closer to the damaged charging port.",
      supportingText: "Hold the damaged area steady for a moment.",
      durationSeconds: 6,
    },
    {
      id: "rotate-label",
      instruction:
        "Slowly rotate the portable charger and show the product label.",
      supportingText: "Keep the label in focus as you move.",
      durationSeconds: 6,
    },
  ],
  case: [
    {
      id: "full-item",
      instruction: "Show the entire phone case.",
      supportingText: "Keep the item centered and clearly visible.",
      durationSeconds: 6,
    },
    {
      id: "damage-closeup",
      instruction: "Move closer to the stain on the phone case.",
      supportingText: "Hold the damaged area steady for a moment.",
      durationSeconds: 6,
    },
    {
      id: "rotate-label",
      instruction: "Slowly rotate the phone case and show the product label.",
      supportingText: "Keep the label in focus as you move.",
      durationSeconds: 6,
    },
  ],
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const createId = () => `refund-${Date.now()}`;
let challengeAttempts = {};
let challenges = challengesByProduct.headphones;

export const verificationApi = {
  async initializeRefundSession() {
    challengeAttempts = {};
    return { sessionId: createId() };
  },
  async submitIssueDescription() {
    await delay(200);
  },
  async startVerification(sessionId, productId) {
    await delay(350);
    challenges =
      challengesByProduct[productId] || challengesByProduct.headphones;
    return challenges[0];
  },
  async submitChallengeVideo(sessionId, challengeId, videoBlob) {
    await delay(DEMO_CONFIG.reviewDelay);
    const index = challenges.findIndex(
      (challenge) => challenge.id === challengeId,
    );
    const attempt = (challengeAttempts[challengeId] || 0) + 1;
    challengeAttempts[challengeId] = attempt;
    const retry = challengeId === "damage-closeup" && attempt === 1;
    return {
      challengeId,
      verdict: retry ? "failed" : "passed",
      next: retry ? challenges[index] : challenges[index + 1] || null,
      complete: !retry && index === challenges.length - 1,
      videoSize: videoBlob?.size || 0,
    };
  },

  async waitForRefundDecision() {
    await delay(3800);
    return DEMO_CONFIG.finalOutcome === "auto"
      ? "approved"
      : DEMO_CONFIG.finalOutcome;
  },
};
