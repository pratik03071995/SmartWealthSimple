import React from "react";
import { motion } from "framer-motion";
import {
  DollarSign, PiggyBank, TrendingUp, TrendingDown,
  LineChart, Coins, Banknote
} from "lucide-react";

/**
 * Light, animated finance icons for the home canvas.
 * Tuned a bit darker (≈35% opacity) so they read without feeling busy.
 */
export default function OrnamentBackdrop() {
  // helper for floaty drift
  const drift = (delay = 0) => ({
    initial: { y: 0, opacity: 0 },
    animate: { y: [0, -8, 0], opacity: [0, 1, 1] },
    transition: {
      duration: 6,
      delay,
      repeat: Infinity,
      ease: "easeInOut",
    },
  });

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* soft color glows (also nudged darker) */}
      <motion.div
        className="absolute w-[42rem] h-[42rem] rounded-full blur-3xl"
        style={{ left: "-8%", top: "-10%", background: "radial-gradient(closest-side, rgba(125,211,252,0.45), transparent 70%)" }}
        {...drift(0)}
      />
      <motion.div
        className="absolute w-[36rem] h-[36rem] rounded-full blur-3xl"
        style={{ right: "-6%", top: "5%", background: "radial-gradient(closest-side, rgba(196,181,253,0.40), transparent 70%)" }}
        {...drift(1.2)}
      />
      <motion.div
        className="absolute w-[44rem] h-[44rem] rounded-full blur-3xl"
        style={{ left: "20%", bottom: "-18%", background: "radial-gradient(closest-side, rgba(110,231,183,0.40), transparent 70%)" }}
        {...drift(2)}
      />

      {/* ornaments – bumped from /20–/25 to /35 */}
      <motion.div className="absolute text-sky-500/35" style={{ left: "8%", top: "16%" }} {...drift(0.2)}>
        <DollarSign size={34} />
      </motion.div>

      <motion.div className="absolute text-violet-500/35" style={{ left: "22%", top: "10%" }} {...drift(0.6)}>
        <LineChart size={40} />
      </motion.div>

      <motion.div className="absolute text-teal-500/35" style={{ left: "34%", top: "18%" }} {...drift(0.9)}>
        <Coins size={30} />
      </motion.div>

      <motion.div className="absolute text-slate-500/35" style={{ left: "12%", top: "54%" }} {...drift(1.1)}>
        <Banknote size={38} />
      </motion.div>

      <motion.div className="absolute text-emerald-500/35" style={{ left: "52%", top: "14%" }} {...drift(0.4)}>
        <TrendingUp size={36} />
      </motion.div>

      <motion.div className="absolute text-rose-500/35" style={{ left: "76%", top: "20%" }} {...drift(0.7)}>
        <TrendingDown size={32} />
      </motion.div>

      <motion.div className="absolute text-sky-500/35" style={{ left: "68%", top: "10%" }} {...drift(1.0)}>
        <DollarSign size={28} />
      </motion.div>

      <motion.div className="absolute text-violet-500/35" style={{ left: "86%", top: "16%" }} {...drift(1.3)}>
        <Coins size={26} />
      </motion.div>

      <motion.div className="absolute text-amber-500/35" style={{ left: "60%", top: "56%" }} {...drift(0.5)}>
        <PiggyBank size={40} />
      </motion.div>

      {/* a few lower-canvas accents */}
      <motion.div className="absolute text-slate-500/35" style={{ left: "30%", bottom: "14%" }} {...drift(0.8)}>
        <Banknote size={30} />
      </motion.div>
      <motion.div className="absolute text-sky-500/35" style={{ left: "48%", bottom: "12%" }} {...drift(1.1)}>
        <DollarSign size={26} />
      </motion.div>
      <motion.div className="absolute text-emerald-500/35" style={{ left: "72%", bottom: "16%" }} {...drift(1.4)}>
        <TrendingUp size={28} />
      </motion.div>
    </div>
  );
}
