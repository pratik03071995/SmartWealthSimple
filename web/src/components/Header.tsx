import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LineChart, CalendarDays, GraduationCap, User, Sparkles, Users, BarChart3 } from "lucide-react";

/** Minimal pathname hook without react-router */
function usePathname() {
  const [p, setP] = useState<string>(window.location.pathname || "/");
  useEffect(() => {
    const onPop = () => setP(window.location.pathname || "/");
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  return p;
}

type NavItem = { label: string; href: string; Icon: React.ComponentType<{ size?: number | string }> };

const NAV: NavItem[] = [
  { label: "Advisor",    href: "/",          Icon: LineChart },
  { label: "Sectors",    href: "/sectors",   Icon: BarChart3 },
  { label: "Scoring",    href: "/scoring",   Icon: BarChart3 },
  { label: "Emerging",   href: "/emerging",  Icon: Sparkles   },
  { label: "Earnings",   href: "/earnings",  Icon: CalendarDays },
  { label: "Community",  href: "/community", Icon: Users      },
  { label: "Learn",      href: "/learn",     Icon: GraduationCap },
];

export default function Header() {
  const pathname = usePathname();
  const activeKey = useMemo(() => {
    if (pathname.startsWith("/sectors"))   return "/sectors";
    if (pathname.startsWith("/scoring"))   return "/scoring";
    if (pathname.startsWith("/emerging"))  return "/emerging";
    if (pathname.startsWith("/earnings"))  return "/earnings";
    if (pathname.startsWith("/community")) return "/community";
    if (pathname.startsWith("/learn"))     return "/learn";
    return "/";
  }, [pathname]);

  // --- Sign-in popover (click to show; auto-hide; click-outside to close) ---
  const [showTip, setShowTip] = useState(false);
  const tipTimer = useRef<number | null>(null);
  const signInRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (!signInRef.current) return;
      if (!signInRef.current.contains(e.target as Node)) setShowTip(false);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
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
        <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800" />
        <div className="absolute inset-0 pointer-events-none">
          <div className="h-16 w-full bg-[linear-gradient(120deg,rgba(255,255,255,0.10)_0%,rgba(255,255,255,0.03)_40%,rgba(255,255,255,0)_60%)]" />
        </div>

        <header className="relative h-16 flex items-center justify-between max-w-6xl mx-auto px-4 sm:px-6">
          {/* Brand */}
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

          {/* Desktop glossy slider nav */}
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
                  onClick={(e) => {
                    e.preventDefault();
                    push(href);
                  }}
                  className="relative isolate"
                >
                  {active && (
                    <motion.div
                      layoutId="navPill"
                      className="absolute inset-0 rounded-xl bg-white/70 shadow-lg"
                      transition={{ type: "spring", stiffness: 350, damping: 30 }}
                    />
                  )}
                  <div
                    className={`relative z-10 px-4 py-2 rounded-xl flex items-center gap-2 text-sm transition ${
                      active ? "text-slate-900" : "text-slate-200 hover:text-white"
                    }`}
                  >
                    <Icon size={16} />
                    {label}
                  </div>
                </a>
              );
            })}
          </nav>

          {/* Sign in (click -> popover) */}
          <div ref={signInRef} className="relative">
            <button
              className="group flex items-center gap-2 px-3 py-2 rounded-xl bg-white/10 ring-1 ring-white/15 text-slate-200 hover:bg-white/15 transition"
              aria-haspopup="dialog"
              aria-expanded={showTip}
              onClick={() => setShowTip((s) => !s)}
            >
              <User size={16} className="opacity-90" />
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

        {/* Mobile scrollable pills */}
        <div className="relative md:hidden max-w-6xl mx-auto px-4 sm:px-6 pb-2">
          <div className="flex gap-2 overflow-x-auto no-scrollbar -mx-1 px-1">
            {NAV.map(({ label, href, Icon }) => {
              const active = activeKey === href;
              return (
                <button
                  key={href}
                  onClick={() => push(href)}
                  className={`shrink-0 inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm ring-1 transition
                    ${active
                      ? "bg-white text-slate-900 ring-white/60 shadow"
                      : "bg-white/10 text-slate-200 ring-white/15 hover:bg-white/15"}`}
                  aria-current={active ? "page" : undefined}
                >
                  <Icon size={16} />
                  {label}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
