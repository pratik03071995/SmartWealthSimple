// web/src/components/SkylineFooter.tsx
import React from "react";
import { motion } from "framer-motion";
import {
  Info, Link as LinkIcon, ArrowRight,
  Instagram, Twitter, Facebook, Youtube
} from "lucide-react";

const GlassCard: React.FC<React.PropsWithChildren<{ className?: string }>> = ({ className = "", children }) => (
  <motion.div
    initial={{ y: 10, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
    transition={{ duration: 0.35 }}
    className={
      "rounded-3xl bg-white/85 backdrop-blur-md ring-1 ring-white/30 " +
      "shadow-xl p-5 hover:shadow-2xl transition " + className
    }
  >
    {children}
  </motion.div>
);

/**
 * Floating glossy cards over the existing background.
 * No skyline, no navy band. Fixed above the slim disclaimer.
 * Rendered only on the Advisor route by your App.tsx.
 */
export default function SkylineFooter() {
  // Adjust this if your slim disclaimer bar height changes
  const bottomOffset = 64; // px

  return (
    <div
      aria-label="SmartWealth overview"
      className="fixed inset-x-0 z-20 pointer-events-none"
      style={{ bottom: bottomOffset }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="pointer-events-auto grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* About */}
          <GlassCard>
            <div className="flex items-center gap-2 text-slate-900">
              <div className="h-9 w-9 grid place-items-center rounded-2xl bg-slate-100 ring-1 ring-slate-200">
                <Info size={18} />
              </div>
              <div className="font-semibold">About SmartWealth</div>
            </div>
            <p className="mt-3 text-sm text-slate-700">
              We’re building an AI-assisted research companion to help you learn,
              screen, and track potential multi-baggers—responsibly. Signals, not hype.
              Education first.
            </p>
            <p className="mt-3 text-xs text-slate-500">
              <b>Note:</b> Educational only, not investment advice.
            </p>
          </GlassCard>

          {/* Quick links */}
          <GlassCard>
            <div className="flex items-center gap-2 text-slate-900">
              <div className="h-9 w-9 grid place-items-center rounded-2xl bg-slate-100 ring-1 ring-slate-200">
                <LinkIcon size={18} />
              </div>
              <div className="font-semibold">Quick links</div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <a
                href="/"
                className="rounded-xl px-3 py-2 ring-1 ring-slate-200 bg-white text-slate-800 text-sm flex items-center justify-between hover:bg-slate-50"
              >
                Advisor <ArrowRight size={14} />
              </a>
              <a
                href="/earnings"
                className="rounded-xl px-3 py-2 ring-1 ring-slate-200 bg-white text-slate-800 text-sm flex items-center justify-between hover:bg-slate-50"
              >
                Earnings <ArrowRight size={14} />
              </a>
              <a
                href="/learn"
                className="rounded-xl px-3 py-2 ring-1 ring-slate-200 bg-white text-slate-800 text-sm flex items-center justify-between hover:bg-slate-50 col-span-2"
              >
                Learn — fundamentals, risk & valuation
                <ArrowRight size={14} className="ml-auto" />
              </a>
            </div>
          </GlassCard>

          {/* Follow us */}
          <GlassCard>
            <div className="flex items-center gap-2 text-slate-900">
              <div className="h-9 w-9 grid place-items-center rounded-2xl bg-slate-100 ring-1 ring-slate-200">
                <LinkIcon size={18} />
              </div>
              <div className="font-semibold">Follow us</div>
            </div>
            <p className="mt-3 text-sm text-slate-700">Placeholders for now—links coming soon.</p>
            <div className="mt-4 flex items-center gap-2">
              <button
                className="h-9 w-9 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
                aria-label="Instagram"
                title="Instagram (coming soon)"
              >
                <Instagram size={16} />
              </button>
              <button
                className="h-9 w-9 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
                aria-label="Twitter / X"
                title="Twitter / X (coming soon)"
              >
                <Twitter size={16} />
              </button>
              <button
                className="h-9 w-9 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
                aria-label="Facebook"
                title="Facebook (coming soon)"
              >
                <Facebook size={16} />
              </button>
              <button
                className="h-9 w-9 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
                aria-label="YouTube"
                title="YouTube (coming soon)"
              >
                <Youtube size={16} />
              </button>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
