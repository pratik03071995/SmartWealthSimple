import React, { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import Header from "./components/Header";
import Footer from "./components/Footer";
import OrnamentBackdrop from "./components/OrnamentBackdrop";
import SmartWealthNeonWizard from "./components/SmartWealthNeonWizard";
import EarningsCalendar from "./components/EarningsCalendar";
import LearnHub from "./components/LearnHub";
import CommunityWIP from "./components/CommunityWIP";     // NEW
import EmergingStocks from "./components/EmergingStocks"; // NEW
import SkylineFooter from "./components/SkylineFooter";   // (you already have this)

/** Minimal pathname hook */
function usePathname() {
  const [p, setP] = useState<string>(window.location.pathname || "/");
  useEffect(() => {
    const onPop = () => setP(window.location.pathname || "/");
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  return p;
}

type Route = { path: string; key: string; title: string; element: React.ReactNode };

const ROUTES: Route[] = [
  { path: "/",          key: "advisor",   title: "Advisor",   element: <SmartWealthNeonWizard /> },
  { path: "/earnings",  key: "earnings",  title: "Earnings",  element: <EarningsCalendar /> },
  { path: "/learn",     key: "learn",     title: "Learn",     element: <LearnHub /> },
  { path: "/community", key: "community", title: "Community", element: <CommunityWIP /> },     // NEW
  { path: "/emerging",  key: "emerging",  title: "Emerging",  element: <EmergingStocks /> },   // NEW
];

export default function App() {
  const pathname = usePathname();

  const activeRoute = useMemo<Route>(() => {
    if (pathname.startsWith("/earnings"))  return ROUTES[1];
    if (pathname.startsWith("/learn"))     return ROUTES[2];
    if (pathname.startsWith("/community")) return ROUTES[3];
    if (pathname.startsWith("/emerging"))  return ROUTES[4];
    return ROUTES[0];
  }, [pathname]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [activeRoute.key]);

  return (
    <div className="min-h-screen text-slate-900 pb-16">
      {/* Soft light background (pushed back a layer) */}
      <div className="fixed inset-0 -z-20 pointer-events-none">
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(1200px 600px at 10% -10%, #ecfeff 0%, transparent 60%)," +
              "radial-gradient(900px 500px at 90% -20%, #fff7ed 0%, transparent 60%)," +
              "linear-gradient(#f8fafc, #f1f5f9)",
          }}
        />
      </div>

      {/* Ornaments above background, below content */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <OrnamentBackdrop />
      </div>


      <Header />

      <main className="relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeRoute.key}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
          >
            {activeRoute.element}
          </motion.div>
        </AnimatePresence>

        {/* Show the large skyline footer ONLY on the Advisor (/) */}
        {activeRoute.key === "advisor" && <SkylineFooter />}
      </main>

      <Footer />
    </div>
  );
}
