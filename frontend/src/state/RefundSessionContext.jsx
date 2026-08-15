import React, { createContext, useContext, useMemo, useState } from "react";
import { verificationApi } from "@/services/mockVerificationApi";

const products = [
  { id: "headphones", name: "Wireless Headphones", variant: "Black", quantity: 1, price: 129, icon: "headphones" },
  { id: "charger", name: "Portable Charger", variant: "10,000 mAh", quantity: 1, price: 49, icon: "battery" },
  { id: "case", name: "Phone Case", variant: "Clear", quantity: 1, price: 29, icon: "phone" },
];
const defaultState = () => ({ sessionId: null, selectedProduct: products[0], issueDescription: "", inputMode: "voice", completedChallenges: [], currentChallenge: null, finalDecision: null });
const RefundSessionContext = createContext(null);

export function RefundSessionProvider({ children }) {
  const [session, setSession] = useState(defaultState);
  const value = useMemo(() => ({
    ...session, products, merchant: { name: "Example Electronics", order: "Order #10482", date: "August 15, 2026" },
    selectProduct: (selectedProduct) => setSession((s) => ({ ...s, selectedProduct })),
    setIssue: (issueDescription, inputMode) => setSession((s) => ({ ...s, issueDescription, inputMode: inputMode || s.inputMode })),
    setChallenge: (currentChallenge) => setSession((s) => ({ ...s, currentChallenge })),
    completeChallenge: (item) => setSession((s) => ({ ...s, completedChallenges: [...s.completedChallenges, item] })),
    setDecision: (finalDecision) => setSession((s) => ({ ...s, finalDecision })),
    ensureSession: async () => { if (session.sessionId) return session.sessionId; const data = await verificationApi.initializeRefundSession(); setSession((s) => ({ ...s, sessionId: data.sessionId })); return data.sessionId; },
    resetSession: () => setSession(defaultState()),
  }), [session]);
  return <RefundSessionContext.Provider value={value}>{children}</RefundSessionContext.Provider>;
}
export const useRefundSession = () => useContext(RefundSessionContext);