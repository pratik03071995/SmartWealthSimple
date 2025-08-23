import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import Header from "./components/Header";
import SideRailNav from "./components/SideRailNav";
import SmartWealthNeonWizard from "./components/SmartWealthNeonWizard";
import EarningsCalendar from "./components/EarningsCalendar";

function PageTransition({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[radial-gradient(1200px_600px_at_10%_-10%,#ecfeff_0%,transparent_60%),radial-gradient(900px_500px_at_90%_-20%,#fff7ed_0%,transparent_60%),linear-gradient(#f8fafc,#f1f5f9)]">
        <Header />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 flex gap-6">
          {/* Left rail (desktop) */}
          <aside className="hidden md:block">
            <SideRailNav />
          </aside>

          {/* Top tabs (mobile) */}
          <nav className="md:hidden w-full mb-4 -mt-2">
            <div className="bg-white/90 backdrop-blur ring-1 ring-slate-200 rounded-2xl p-1 flex">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `flex-1 text-center py-2 text-sm rounded-xl ${
                    isActive ? "bg-sky-100 text-sky-700" : "text-slate-700"
                  }`
                }
              >
                Advisor
              </NavLink>
              <NavLink
                to="/earnings"
                className={({ isActive }) =>
                  `flex-1 text-center py-2 text-sm rounded-xl ${
                    isActive ? "bg-sky-100 text-sky-700" : "text-slate-700"
                  }`
                }
              >
                Earnings
              </NavLink>
            </div>
          </nav>

          {/* Page content */}
          <main className="flex-1">
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
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
