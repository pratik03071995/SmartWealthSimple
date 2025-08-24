// web/src/App.tsx
import React from "react";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";

import SmartWealthNeonWizard from "./components/SmartWealthNeonWizard";
import EarningsCalendar from "./components/EarningsCalendar";
import LearnHub from "./components/LearnHub";

import { Banknote, LineChart, CalendarDays, GraduationCap } from "lucide-react";

function Header() {
  const linkBase =
    "px-3 py-2 rounded-xl text-sm transition ring-1 focus:outline-none focus:ring-2 focus:ring-sky-400/60";
  const linkInactive = "text-slate-200/80 ring-slate-800 hover:bg-slate-800/60 hover:text-white";
  const linkActive = "bg-slate-800 text-white ring-slate-700";

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur border-b border-slate-800">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="h-14 flex items-center gap-4">
          {/* Brand (left-aligned, white, no animation) */}
          <NavLink to="/" className="group flex items-center gap-2 select-none" aria-label="SmartWealth AI Home">
            <span className="h-7 w-7 grid place-items-center rounded-lg bg-slate-800 ring-1 ring-slate-700">
              <Banknote size={16} className="text-emerald-300" />
            </span>
            <span className="text-base sm:text-lg font-bold text-white tracking-tight">
              SmartWealth AI
            </span>
          </NavLink>

          {/* Nav */}
          <nav className="flex items-center gap-2">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkInactive} flex items-center gap-1.5`
              }
            >
              <LineChart size={14} />
              <span>Advisor</span>
            </NavLink>

            <NavLink
              to="/earnings"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkInactive} flex items-center gap-1.5`
              }
            >
              <CalendarDays size={14} />
              <span>Earnings</span>
            </NavLink>

            <NavLink
              to="/learn"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkInactive} flex items-center gap-1.5`
              }
            >
              <GraduationCap size={14} />
              <span>Learn</span>
            </NavLink>
          </nav>
        </div>
      </div>
    </header>
  );
}

function PageTransition({ children }: { children: React.ReactNode }) {
  // Subtle page transition on route change (title itself is not animated)
  return (
    <motion.main
      key={useLocation().pathname}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
      className="min-h-[calc(100vh-56px)]"
    >
      {children}
    </motion.main>
  );
}

function AppRoutes() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        <Route
          path="/"
          element={
            <PageTransition>
              <SmartWealthNeonWizard />
            </PageTransition>
          }
        />
        <Route
          path="/earnings"
          element={
            <PageTransition>
              <EarningsCalendar />
            </PageTransition>
          }
        />
        <Route
          path="/learn"
          element={
            <PageTransition>
              <LearnHub />
            </PageTransition>
          }
        />
        {/* Fallback: redirect unknown routes to Advisor */}
        <Route
          path="*"
          element={
            <PageTransition>
              <SmartWealthNeonWizard />
            </PageTransition>
          }
        />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <Header />
        <AppRoutes />
      </div>
    </BrowserRouter>
  );
}
