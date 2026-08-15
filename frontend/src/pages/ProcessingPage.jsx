import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PageShell from "@/components/refund/PageShell";
import MerchantHeader from "@/components/refund/MerchantHeader";
import ProcessingAnimation from "@/components/refund/ProcessingAnimation";
import { verificationApi } from "@/services/mockVerificationApi";
import { useRefundSession } from "@/state/RefundSessionContext";
const messages = [
  "Reviewing product details…",
  "Checking verification clips…",
  "Finalizing refund decision…",
];
export default function ProcessingPage() {
  const navigate = useNavigate();
  const { selectedProduct, setDecision } = useRefundSession();
  const [message, setMessage] = useState(messages[0]);
  useEffect(() => {
    if (!selectedProduct) {
      navigate("/");
      return;
    }
    const timer = setInterval(
      () =>
        setMessage(
          (current) =>
            messages[(messages.indexOf(current) + 1) % messages.length],
        ),
      1150,
    );
    verificationApi.waitForRefundDecision().then((decision) => {
      setDecision(decision);
      navigate("/stripe-connection");
    });
    return () => clearInterval(timer);
  }, [navigate, selectedProduct, setDecision]);
  return (
    <PageShell>
      <MerchantHeader />
      <div className="flex flex-1 flex-col items-center justify-center pb-16 text-center">
        <ProcessingAnimation />
        <h1 className="mt-9 text-2xl font-semibold tracking-[-0.02em] text-foreground">
          Reviewing your refund request
        </h1>
        <p className="mt-3 max-w-xs text-base leading-6 text-muted-foreground">
          We’re checking the information you provided.
        </p>
        <p className="mt-9 text-sm font-medium text-primary">{message}</p>
      </div>
      <p className="pb-2 text-center text-xs text-muted-foreground">
        No need to refresh this page.
      </p>
    </PageShell>
  );
}
