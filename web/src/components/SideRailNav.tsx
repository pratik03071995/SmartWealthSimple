import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import { LineChart, CalendarDays, BarChart3 } from "lucide-react";
import { useMemo } from "react";

const items = [
  { to: "/", label: "Advisor", icon: LineChart, exact: true },
  { to: "/scoring", label: "Stock Scoring", icon: BarChart3 },
  { to: "/earnings", label: "Earnings", icon: CalendarDays },
];

export default function SideRailNav() {
  return (
    <div className="sticky top-[5rem]">
      <nav className="w-44">
        <ul className="relative bg-white/90 backdrop-blur ring-1 ring-slate-200 rounded-2xl p-2 shadow-sm">
          {items.map(({ to, label, icon: Icon, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact as any}
              className={({ isActive }) =>
                `group relative flex items-center gap-2 px-3 py-2 rounded-xl transition ${
                  isActive ? "text-sky-700" : "text-slate-700 hover:text-slate-900"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.span
                      layoutId="rail-active"
                      className="absolute inset-0 rounded-xl bg-sky-50 ring-1 ring-sky-200"
                      transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    />
                  )}
                  <Icon className="relative z-10" size={18} />
                  <span className="relative z-10 text-sm font-medium">{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </ul>
      </nav>
    </div>
  );
}
