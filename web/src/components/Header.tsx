import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import {
  LineChart,
  CalendarDays,
  GraduationCap,
  User,
  MessagesSquare,
  Sparkles,
} from "lucide-react";

/** Minimal pathname hook without react-router */
function usePathname() {
  const [p, setP] = useState<string>(
    typeof window !== "undefined" ? window.location.pathname || "/" : "/"
  );
  useEffect(() => {
    const onPop = () => setP(window.location.pathname || "/");
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  return p;
}

const NAV = [
  { label: "Advisor", href: "/", Icon: LineChart },
  { label: "Earnings", href: "/earnings", Icon: CalendarDays },
  { label: "Learn", href: "/learn", Icon: GraduationCap },
  { label: "Community", href: "/community", Icon: MessagesSquare }, // NEW
  { label: "Emerging", href: "/emerging", Icon: Sparkles },         // NEW
] as const;

export default function Header() {
  const pathname = usePathname();
  const prefersReducedMotion = useReducedMotion();

  const activeKey = useMemo(() => {
    if (pathname.startsWith("/earnings")) return "/earnings";
    if (pathname.startsWith("/learn")) return "/learn";
    if (pathname.startsWith("/community")) return "/community";
    if (pathname.startsWith("/emerging")) return "/emerging";
    return "/";
  }, [pathname]);

  // --- Sign-in popover (click to show; auto-hide; click-outside/Escape to close) ---
  const [showTip, setShowTip] = useState(false);
  const tipTimer = useRef<number | null>(null);
  const signInRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (!signInRef.current) return;
      if (!signInRef.current.contains(e.target as Node)) setShowTip(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setShowTip(false);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  useEffect(() => {
    if (showTip) {
      if (tipTimer.current) window.clearTimeout(tipTimer.current);
      tipTimer.current = window.setTimeout(() => setShowTip(false), 2200);
    }
    return () => {
      if (tipTimer.current) window.clearTimeout(tipTimer.current);
    };
  }, [showTip]);

  const push = (href: string) => {
    window.history.pushState({}, "", href);
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  return (
    <div className="sticky top-0 z-50">
      <div className="relative">
        {/* glossy navy bar */}
        <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800" />
        <div className="absolute inset-0 pointer-events-none">
          <div className="h-16 w-full bg-[linear-gradient(120deg,rgba(255,255,255,0.10)_0%,rgba(255,255,255,0.03)_40%,rgba(255,255,255,0)_60%)]" />
        </div>

        <header className="relative h-16 flex items-center justify-between max-w-6xl mx-auto px-4 sm:px-6">
          {/* Brand (text) */}
          <a
            className="flex items-center gap-2 select-none"
            href="/"
            onClick={(e) => {
              e.preventDefault();
              push("/");
            }}
          >
            <div className="h-8 w-8 rounded-xl bg-white/10 ring-1 ring-white/20 grid place-items-center">
              <LineChart size={18} className="text-sky-300" />
            </div>
            <div className="text-lg font-bold tracking-wide text-white">
              SmartWealth <span className="text-sky-300">AI</span>
            </div>
          </a>

          {/* Glossy slider nav */}
          <nav
            className="relative hidden md:flex items-center gap-1 px-1 py-1 rounded-2xl bg-white/10 ring-1 ring-white/15 backdrop-blur"
            aria-label="Primary"
          >
            {NAV.map(({ label, href, Icon }) => {
              const active = activeKey === href;
              return (
                <a
                  key={href}
                  href={href}
                  aria-current={active ? "page" : undefined}
                  onClick={(e) => {
                    e.preventDefault();
                    push(href);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      push(href);
                    }
                  }}
                  className="relative isolate rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
                >
                  {active && (
                    <motion.div
                      layoutId="navPill"
                      className="absolute inset-0 rounded-xl bg-white/70 shadow-lg"
                      transition={
                        prefersReducedMotion
                          ? { duration: 0 }
                          : { type: "spring", stiffness: 350, damping: 30 }
                      }
                    />
                  )}
                  <div
                    className={`relative z-10 px-4 py-2 rounded-xl flex items-center gap-2 text-sm transition ${
                      active ? "text-slate-900" : "text-slate-200 hover:text-white"
                    }`}
                  >
                    <Icon size={16} aria-hidden />
                    {label}
                  </div>
                </a>
              );
            })}
          </nav>

          {/* Sign in (click -> popover) */}
          <div ref={signInRef} className="relative">
            <button
              className="group flex items-center gap-2 px-3 py-2 rounded-xl bg-white/10 ring-1 ring-white/15 text-slate-200 hover:bg-white/15 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
              aria-haspopup="dialog"
              aria-expanded={showTip}
              onClick={() => setShowTip((s) => !s)}
            >
              <User size={16} className="opacity-90" aria-hidden />
              <span className="text-sm">Sign in</span>
            </button>

            <AnimatePresence>
              {showTip && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="absolute right-0 mt-2 px-3 py-2 rounded-xl bg-white text-slate-800 text-xs shadow-xl ring-1 ring-slate-200"
                  role="dialog"
                >
                  Work in progress — coming soon!
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </header>
      </div>
    </div>
  );
}
