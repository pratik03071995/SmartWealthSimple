import React from "react";
import { motion } from "framer-motion";
import {
  DollarSign,
  PiggyBank,
  TrendingUp,
  Shield,
  Banknote,
  CandlestickChart,
} from "lucide-react";

/** Deterministic pseudo-random so SSR/CSR match on Vercel */
function prand(i: number) {
  let x = (i + 1) * 1103515245 + 12345;
  x = (x >> 16) & 0x7fff;
  return x / 0x7fff;
}

type IconType = React.ComponentType<{ size?: number | string; className?: string }>;
const ICONS: IconType[] = [DollarSign, PiggyBank, TrendingUp, Shield, Banknote, CandlestickChart];

/**
 * Subtle floating finance icons behind the content.
 * If you want them a touch darker/lighter, tweak baseOpacity.
 */
export default function OrnamentBackdrop({
  count = 18,
  baseOpacity = 0.18,   // slightly darker per your request
  maxSize = 28,
  maxDrift = 12,
}: {
  count?: number;
  baseOpacity?: number;
  maxSize?: number;
  maxDrift?: number;
}) {
  const items = Array.from({ length: count }, (_, i) => {
    const r1 = prand(i * 3 + 1);
    const r2 = prand(i * 3 + 2);
    const r3 = prand(i * 3 + 3);
    const left = 5 + r1 * 90;    // 5%..95%
    const top = -5 + r2 * 110;   // -5%..105% (some bleed outside)
    const Icon = ICONS[i % ICONS.length];
    const size = 14 + Math.round(r3 * (maxSize - 14));
    const delay = (i % 6) * 0.15 + r2 * 0.2;
    const duration = 4 + (i % 4) * 0.6;
    return { i, left, top, Icon, size, delay, duration };
  });

  return (
    <div
      aria-hidden
      className="absolute inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    >
      {items.map(({ i, left, top, Icon, size, delay, duration }) => (
        <motion.div
          key={i}
          initial={{ y: 0, opacity: 0 }}
          animate={{ y: [0, -maxDrift, 0], opacity: baseOpacity }}
          transition={{ duration, delay, repeat: Infinity, ease: "easeInOut" }}
          style={{
            position: "absolute",
            left: `${left}%`,
            top: `${top}%`,
            lineHeight: 0,
            color: "rgb(100 116 139)", // slate-500-ish
            filter: "drop-shadow(0 1px 2px rgba(0,0,0,0.06))",
          }}
        >
          <Icon size={size} />
        </motion.div>
      ))}
    </div>
  );
}
