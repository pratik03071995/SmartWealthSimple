import { motion } from "framer-motion";
import {
  Sparkles,
  DollarSign,
  TrendingUp,
  PiggyBank,
  BarChart3,
  Coins,
} from "lucide-react";

function HdrIcon({
  children,
  label,
}: {
  children: React.ReactNode;
  label: string;
}) {
  return (
    <motion.div
      aria-label={label}
      className="h-8 w-8 grid place-items-center rounded-lg bg-white/10 ring-1 ring-white/15"
      whileHover={{ y: -2, scale: 1.05 }}
      whileTap={{ scale: 0.96 }}
      transition={{ type: "spring", stiffness: 260, damping: 18 }}
    >
      {children}
    </motion.div>
  );
}

export default function Header() {
  return (
    <header className="sticky top-0 z-40">
      {/* Dark navy gradient strip */}
      <div className="bg-gradient-to-r from-[#0b1e36] via-[#0a2342] to-[#0b1e36] text-white shadow-[0_6px_18px_rgba(2,6,23,.12)]">
        {/* Bar content (aligned with page container) */}
        <motion.div
          initial={{ y: -18, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.42, ease: "easeOut" }}
          className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between"
        >
          {/* LEFT: brand (no title animation) */}
          <div className="flex items-center gap-2">
            <motion.div
              initial={{ rotate: -10, scale: 0.9, opacity: 0 }}
              animate={{ rotate: 0, scale: 1, opacity: 1 }}
              transition={{ type: "spring", stiffness: 260, damping: 18, delay: 0.08 }}
              className="h-8 w-8 grid place-items-center rounded-lg bg-white/10 ring-1 ring-white/15"
            >
              <Sparkles size={16} className="text-sky-300" />
            </motion.div>

            <div className="leading-tight">
              <div className="font-semibold tracking-wide text-white text-xl md:text-2xl">
                SmartWealth AI
              </div>
              <div className="text-[11px] md:text-[12px] text-white/70">
                Find tomorrow’s compounders
              </div>
            </div>
          </div>

          {/* RIGHT: finance icons */}
          <div className="hidden sm:flex items-center gap-2">
            <HdrIcon label="Dollars">
              <DollarSign size={16} className="text-emerald-300" />
            </HdrIcon>
            <HdrIcon label="Trend">
              <TrendingUp size={16} className="text-sky-300" />
            </HdrIcon>
            <HdrIcon label="Piggy bank">
              <PiggyBank size={16} className="text-teal-300" />
            </HdrIcon>
            <HdrIcon label="Analytics">
              <BarChart3 size={16} className="text-cyan-300" />
            </HdrIcon>
            <HdrIcon label="Coins">
              <Coins size={16} className="text-amber-300" />
            </HdrIcon>
          </div>
        </motion.div>

        {/* Two-sided underline (kept) */}
        <div className="relative h-[2px] overflow-hidden">
          <motion.div
            className="absolute left-0 top-0 h-px w-1/2 bg-gradient-to-r from-sky-400 via-teal-400 to-emerald-400"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.22 }}
            style={{ transformOrigin: "left" }}
          />
          <motion.div
            className="absolute right-0 top-0 h-px w-1/2 bg-gradient-to-l from-sky-400 via-teal-400 to-emerald-400"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.22 }}
            style={{ transformOrigin: "right" }}
          />
        </div>
      </div>
    </header>
  );
}
