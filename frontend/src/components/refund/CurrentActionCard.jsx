import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, CircleAlert, LoaderCircle } from "lucide-react";

export default function CurrentActionCard({ challenge, state }) {
  const checking = state === "CHALLENGE_UPLOADING" || state === "CHALLENGE_REVIEWING";
  const passed = state === "CHALLENGE_PASSED";
  const failed = state === "CHALLENGE_FAILED";
  const content = checking ? { title: "Checking this video…", detail: "This usually takes a moment.", icon: <LoaderCircle className="animate-spin text-primary" size={19} strokeWidth={1.8}/> } : passed ? { title: "Check complete", detail: "Verified successfully.", icon: <CheckCircle2 className="text-emerald-600" size={19} strokeWidth={1.8}/> } : failed ? { title: "Check not verified", detail: "We’ll continue with another check.", icon: <CircleAlert className="text-amber-600" size={19} strokeWidth={1.8}/> } : { title: challenge?.instruction || "Preparing verification…", detail: challenge?.supportingText || "", icon: null };
  return <div className="min-h-[102px] rounded-[22px] border border-white/50 bg-white/90 px-5 py-[18px] shadow-[0_12px_32px_rgba(20,20,20,0.08)] backdrop-blur-xl">
    <AnimatePresence mode="wait">
      <motion.div key={checking ? "checking" : passed ? "passed" : failed ? "failed" : challenge?.id || "preparing"} initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: 0.2 }}>
        <div className="flex items-start gap-3">{content.icon && <span className="mt-0.5 shrink-0">{content.icon}</span>}<div><p className="text-[18px] font-semibold leading-snug tracking-[-0.01em] text-foreground">{content.title}</p>{content.detail && <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{content.detail}</p>}</div></div>
      </motion.div>
    </AnimatePresence>
  </div>;
}