import { useNavigate } from "react-router-dom";
import { CircleCheckBig, CircleX } from "lucide-react";
import { motion } from "framer-motion";
import PageShell from "@/components/refund/PageShell";
import MerchantHeader from "@/components/refund/MerchantHeader";
import ProductCard from "@/components/refund/ProductCard";
import { PrimaryButton, SecondaryButton } from "@/components/refund/Buttons";
import { useRefundSession } from "@/state/RefundSessionContext";
export default function ResultPage() {
  const navigate = useNavigate();
  const { finalDecision, selectedProduct, resetSession } = useRefundSession();
  if (!finalDecision || !selectedProduct) {
    navigate("/");
    return null;
  }
  const approved = finalDecision === "approved";
  const exit = () => {
    resetSession();
    navigate("/");
  };
  return (
    <PageShell>
      <MerchantHeader context="Refund request" />
      <div className="pt-14 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.26 }}
          className={`mx-auto grid h-16 w-16 place-items-center rounded-full ${approved ? "bg-emerald-50 text-emerald-700" : "bg-accent text-primary"}`}
        >
          {approved ? (
            <CircleCheckBig size={32} strokeWidth={1.8} />
          ) : (
            <CircleX size={30} strokeWidth={1.7} />
          )}
        </motion.div>
        <h1 className="mt-6 text-[28px] font-semibold leading-[34px] tracking-[-0.02em] text-foreground">
          {approved ? "Refund approved" : "We couldn’t verify this refund"}
        </h1>
        <p className="mx-auto mt-3 max-w-sm text-base leading-6 text-muted-foreground">
          {approved
            ? "Your refund request has been verified."
            : "We weren’t able to verify this refund request using the information provided."}
        </p>
      </div>
      <div className="mt-10">
        <ProductCard product={selectedProduct} compact />
        <div className="refund-surface mt-4 p-4">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Refund amount</span>
            <strong className="font-semibold text-foreground">
              ${selectedProduct.price.toFixed(2)}
            </strong>
          </div>
          {approved && (
            <>
              <div className="my-4 h-px bg-border" />
              <p className="text-sm text-muted-foreground">Refund method</p>
              <p className="mt-1 text-sm font-medium text-foreground">
                Original payment method
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                Bank account ending in XXXX 4821
              </p>
              <p className="mt-2 text-xs text-muted-foreground hidden">
                Refund timing depends on your payment provider.
              </p>
            </>
          )}
        </div>
      </div>
      <div className="mt-auto pt-8">
        {approved ? (
          <PrimaryButton onClick={exit}>Done</PrimaryButton>
        ) : (
          <>
            <PrimaryButton onClick={exit}>Try again</PrimaryButton>
            <SecondaryButton onClick={exit} className="mt-3 w-full">
              Exit
            </SecondaryButton>
          </>
        )}
      </div>
    </PageShell>
  );
}
