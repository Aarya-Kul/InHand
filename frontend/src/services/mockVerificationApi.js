export const DEMO_CONFIG = { finalOutcome: "auto", reviewDelay: 1600 };

const challenges = [
  { id: "full-item", instruction: "Show the entire pair of headphones.", supportingText: "Keep the item centered and clearly visible.", durationSeconds: 6 },
  { id: "damage-closeup", instruction: "Move closer to the cracked right ear cup.", supportingText: "Hold the damaged area steady for a moment.", durationSeconds: 6 },
  { id: "rotate-label", instruction: "Slowly rotate the headphones and show the product label.", supportingText: "Keep the label in focus as you move.", durationSeconds: 6 },
];

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const createId = () => `refund-${Date.now()}`;

export const verificationApi = {
  async initializeRefundSession() { return { sessionId: createId() }; },
  async submitIssueDescription() { await delay(200); },
  async startVerification() { await delay(350); return challenges[0]; },
  async submitChallengeVideo(sessionId, challengeId, videoBlob) {
    await delay(DEMO_CONFIG.reviewDelay);
    const index = challenges.findIndex((challenge) => challenge.id === challengeId);
    return { challengeId, verdict: "passed", next: challenges[index + 1] || null, complete: index === challenges.length - 1, videoSize: videoBlob?.size || 0 };
  },
  async waitForRefundDecision() {
    await delay(3800);
    return DEMO_CONFIG.finalOutcome === "auto" ? "approved" : DEMO_CONFIG.finalOutcome;
  },
};