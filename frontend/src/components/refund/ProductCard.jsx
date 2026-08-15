import { Check } from "lucide-react";
import { Image } from "@/components/ui/image";

const productImages = {
  headphones: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=160&q=80",
  charger: "https://images.unsplash.com/photo-1640872005860-8a21cb5b05be?auto=format&fit=crop&w=160&q=80",
  case: "https://images.unsplash.com/photo-1774320391374-ec34fc98553d?auto=format&fit=crop&w=160&q=80",
};
export default function ProductCard({ product, selected, onSelect, compact = false }) {
  const imageUrl = productImages[product.id];
  return <button onClick={onSelect} className={`refund-surface flex w-full items-center gap-3.5 p-4 text-left transition duration-200 ${selected ? "border-primary bg-accent" : "hover:border-input"} ${compact ? "pointer-events-none" : "active:scale-[.99]"}`}>
    <Image src={imageUrl} alt={product.name} className="h-16 w-16 shrink-0 rounded-xl bg-secondary" fittingType="fill"/><div className="min-w-0 flex-1"><p className="truncate text-base font-semibold tracking-[-0.01em] text-foreground">{product.name}</p><p className="mt-1 text-[13px] text-muted-foreground">{product.variant} · Qty {product.quantity}</p><p className="mt-1.5 text-[15px] font-semibold text-foreground">${product.price.toFixed(2)}</p></div>
    {!compact && <span className={`grid h-5 w-5 place-items-center rounded-full border transition ${selected ? "border-primary bg-primary text-primary-foreground" : "border-input bg-card"}`}>{selected && <Check size={12} strokeWidth={2.5}/>}</span>}
  </button>;
}