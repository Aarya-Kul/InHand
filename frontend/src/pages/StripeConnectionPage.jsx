import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Check } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import MerchantHeader from "@/components/refund/MerchantHeader";
import PageShell from "@/components/refund/PageShell";
import { useRefundSession } from "@/state/RefundSessionContext";

export default function StripeConnectionPage() {
  const navigate = useNavigate();
  const { selectedProduct } = useRefundSession();
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!selectedProduct) {
      navigate("/");
      return;
    }

    const connectionTimer = window.setTimeout(() => setConnected(true), 1800);
    const resultTimer = window.setTimeout(() => navigate("/result"), 3000);

    return () => {
      clearTimeout(connectionTimer);
      clearTimeout(resultTimer);
    };
  }, [navigate, selectedProduct]);

  return (
    <PageShell>
      <MerchantHeader />
      <div className="flex flex-1 flex-col items-center justify-center pb-16 text-center">
        <div className="relative grid h-28 w-28 place-items-center">
          <div
            className={`absolute inset-0 rounded-full border ${connected ? "border-emerald-200" : "animate-[spin_3s_linear_infinite] border-[#635bff]/30 border-t-[#635bff]"}`}
          />
          <motion.div
            animate={{ scale: connected ? [1, 1.06, 1] : [1, 0.96, 1] }}
            transition={{
              duration: connected ? 0.42 : 1.5,
              repeat: connected ? 0 : Infinity,
            }}
            className="grid h-14 w-14 place-items-center rounded-[18px] bg-[#635bff] shadow-[0_8px_18px_rgba(99,91,255,0.22)]"
            aria-label="Stripe"
          >
            <span className="text-[17px] font-bold tracking-[-0.08em] text-white">
              stripe
            </span>
          </motion.div>
          <AnimatePresence>
            {connected && (
              <motion.span
                initial={{ opacity: 0, scale: 0.6 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute -bottom-1 -right-1 grid h-7 w-7 place-items-center rounded-full border-2 border-card bg-emerald-600 text-white"
              >
                <Check size={15} strokeWidth={2.8} />
              </motion.span>
            )}
          </AnimatePresence>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={connected ? "connected" : "connecting"}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.22 }}
          >
            <h1 className="mt-9 text-2xl font-semibold tracking-[-0.02em] text-foreground">
              {connected
                ? "Stripe account connected"
                : "Connecting your Stripe account"}
            </h1>
            <p className="mx-auto mt-3 max-w-xs text-base leading-6 text-muted-foreground">
              {connected
                ? "Your original payment method is ready for this refund."
                : "Securely linking your original payment method."}
            </p>
          </motion.div>
        </AnimatePresence>

        <div className="mt-9 flex items-center gap-2 text-sm font-medium text-primary">
          <span
            className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-600" : "animate-pulse bg-primary"}`}
          />
          {connected ? "Connected securely" : "Connecting securely…"}
        </div>
      </div>
      <p className="pb-2 text-center text-xs text-muted-foreground">
        Your payment details stay protected.
      </p>
    </PageShell>
  );
}
