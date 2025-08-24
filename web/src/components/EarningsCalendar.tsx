import React, { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  addMonths, subMonths, startOfMonth, endOfMonth,
  startOfWeek, endOfWeek, addDays, format, isSameDay, isSameMonth
} from "date-fns";
import { ChevronLeft, ChevronRight } from "lucide-react";

type EarnEvent = {
  ticker: string;
  name: string;
  date: string;   // ISO date (YYYY-MM-DD)
  time?: string;  // "16:00"
  logoUrl?: string;
};

const CARD = "bg-white border border-slate-200 rounded-3xl shadow-xl";

export default function EarningsCalendar() {
  const [current, setCurrent] = useState<Date>(startOfMonth(new Date()));
  const [events, setEvents] = useState<EarnEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState<Date | null>(null);
  const [filter, setFilter] = useState<string[]>([]); // tickers filter

  const ym = format(current, "yyyy-MM");

  useEffect(() => {
    setLoading(true);
    fetch(`/api/earnings?month=${ym}`)
      .then(r => r.json())
      .then((data: EarnEvent[]) => setEvents(data || []))
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, [ym]);

  const days = useMemo(() => {
    const start = startOfWeek(startOfMonth(current), { weekStartsOn: 0 });
    const end = endOfWeek(endOfMonth(current), { weekStartsOn: 0 });
    const arr: Date[] = [];
    for (let d = start; d <= end; d = addDays(d, 1)) arr.push(d);
    return arr;
  }, [current]);

  const uniqTickers = useMemo(
    () => Array.from(new Set(events.map(e => e.ticker))).sort(),
    [events]
  );

  const eventsByDay = useMemo(() => {
    const map = new Map<string, EarnEvent[]>();
    for (const ev of events) {
      if (filter.length && !filter.includes(ev.ticker)) continue;
      (map.get(ev.date) || map.set(ev.date, []).get(ev.date))!.push(ev);
    }
    return map;
  }, [events, filter]);

  return (
    <div className="min-h-[calc(100vh-64px)] text-slate-900 flex items-start justify-center pb-16">
      <div className="w-full max-w-6xl px-4 sm:px-6 mt-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button
              className="h-10 w-10 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
              onClick={() => setCurrent(d => subMonths(d, 1))}
              aria-label="Previous month"
            >
              <ChevronLeft />
            </button>
            <div className="text-xl font-semibold">
              {format(current, "MMMM yyyy")}
            </div>
            <button
              className="h-10 w-10 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
              onClick={() => setCurrent(d => addMonths(d, 1))}
              aria-label="Next month"
            >
              <ChevronRight />
            </button>
          </div>

          {/* Filters (tickers) */}
          <div className="flex flex-wrap gap-2">
            {uniqTickers.map(t => {
              const on = filter.includes(t);
              return (
                <button
                  key={t}
                  onClick={() =>
                    on ? setFilter(filter.filter(x => x !== t)) : setFilter([...filter, t])
                  }
                  className={`px-3 py-1.5 rounded-full text-sm ring-1 transition ${
                    on
                      ? "bg-sky-100 text-sky-700 ring-sky-200"
                      : "bg-white text-slate-700 ring-slate-200 hover:bg-slate-50"
                  }`}
                >
                  {t}
                </button>
              );
            })}
            {filter.length > 0 && (
              <button
                className="px-3 py-1.5 rounded-full text-sm bg-slate-100 text-slate-700 ring-1 ring-slate-200"
                onClick={() => setFilter([])}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Calendar */}
        <motion.div
          key={format(current, "yyyy-MM")}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className={`${CARD} p-4`}
        >
          {/* Weekday headers */}
          <div className="grid grid-cols-7 gap-2 px-1 pb-2 text-xs font-medium text-slate-500">
            {["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].map(d => (
              <div key={d} className="text-center">{d}</div>
            ))}
          </div>

          {/* Grid */}
          <div className="grid grid-cols-7 gap-2">
            {days.map((day, i) => {
              const dateStr = format(day, "yyyy-MM-dd");
              const evts = eventsByDay.get(dateStr) || [];
              const muted = !isSameMonth(day, current);
              const today = isSameDay(day, new Date());
              return (
                <motion.button
                  key={dateStr + i}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setSelectedDay(day)}
                  className={`h-28 rounded-xl p-2 text-left ring-1 transition ${
                    muted ? "bg-slate-50 ring-slate-100 text-slate-400"
                          : "bg-white ring-slate-200 hover:bg-slate-50"
                  } ${today ? "outline outline-2 outline-sky-300" : ""}`}
                >
                  <div className="text-xs font-medium">{format(day, "d")}</div>
                  <div className="mt-1 space-y-1">
                    {evts.slice(0, 3).map((e, idx) => (
                      <motion.div
                        key={e.ticker + idx}
                        initial={{ opacity: 0, x: 8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.25, delay: idx * 0.03 }}
                        className="flex items-center gap-2 rounded-lg bg-slate-100 px-2 py-1"
                      >
                        {e.logoUrl ? (
                          <img src={e.logoUrl} className="h-4 w-4 rounded" />
                        ) : (
                          <div className="h-4 w-4 rounded bg-slate-300" />
                        )}
                        <span className="text-[11px] font-semibold text-slate-700">{e.ticker}</span>
                        {e.time && <span className="text-[10px] text-slate-500">{e.time}</span>}
                      </motion.div>
                    ))}
                    {evts.length > 3 && (
                      <div className="text-[11px] text-slate-500">+{evts.length - 3} more</div>
                    )}
                  </div>
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        {/* Drawer for selected day */}
        <AnimatePresence>
          {selectedDay && (
            <motion.div
              className="fixed inset-0 z-40 grid place-items-end bg-black/20"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedDay(null)}
            >
              <motion.div
                initial={{ y: 40, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 40, opacity: 0 }}
                transition={{ type: "spring", stiffness: 140, damping: 18 }}
                className="w-full max-w-xl bg-white rounded-t-3xl p-6 shadow-2xl"
                onClick={e => e.stopPropagation()}
              >
                <div className="text-lg font-semibold mb-2">
                  {format(selectedDay, "EEEE, MMM d")}
                </div>
                <div className="space-y-3">
                  {(eventsByDay.get(format(selectedDay, "yyyy-MM-dd")) || []).map((e, i) => (
                    <motion.div
                      key={e.ticker + i}
                      className="flex items-center gap-3 p-3 rounded-2xl ring-1 ring-slate-200 bg-slate-50"
                      initial={{ opacity: 0, x: 12 }}
                      animate={{ opacity: 1, x: 0 }}
                    >
                      {e.logoUrl ? (
                        <img src={e.logoUrl} className="h-8 w-8 rounded bg-white ring-1 ring-slate-200" />
                      ) : (
                        <div className="h-8 w-8 rounded bg-slate-300" />
                      )}
                      <div className="flex-1">
                        <div className="font-semibold">{e.ticker} — {e.name}</div>
                        <div className="text-sm text-slate-600">{e.time ? `Time: ${e.time}` : "Time: TBA"}</div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {loading && (
          <div className="fixed inset-x-0 bottom-4 flex justify-center">
            <div className="px-3 py-2 text-sm rounded-full bg-white shadow ring-1 ring-slate-200">
              Loading earnings…
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
