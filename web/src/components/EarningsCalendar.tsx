import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { addDays, addWeeks, format, startOfWeek, isSameDay } from "date-fns";
import {
  ChevronLeft, ChevronRight, Loader2,
  Sparkles, TrendingUp, Info, Calendar as CalIcon
} from "lucide-react";
import { API_BASE_URL } from '../config';

type EarnEvent = {
  ticker: string;
  name: string;
  date: string;       // "YYYY-MM-DD"
  time?: string | null;
  logoUrl?: string | null;
  epsEstimate?: number | null;
  epsReported?: number | null;
  surprisePct?: number | null;
  currency?: string | null;
};

type EarnDetail = {
  ticker: string;
  name: string;
  logoUrl?: string | null;
  last?: { date?: string; time?: string | null; epsEstimate?: number | null; epsReported?: number | null; surprisePct?: number | null };
  next?: { date?: string; time?: string | null; epsEstimate?: number | null; low?: number | null; high?: number | null };
  history?: Array<{ date: string; epsEstimate?: number | null; epsReported?: number | null; surprisePct?: number | null }>;
};

const CARD = "bg-white border border-slate-200 rounded-3xl shadow-xl";

/* ---------- First-visit fun-fact overlay (only once per mount) ---------- */
const FUN_FACTS = [
  "Guidance often moves stocks more than headline EPS.",
  "Surprise = Reported EPS − Estimate (as %).",
  "Revenue growth + margins tell a deeper story than EPS alone.",
  "Moats matter: brand, network effects, scale, switching costs.",
  "Operating leverage: costs scale slower than revenue — margins expand.",
  "Compounding > market timing over long horizons.",
];
const FIRST_LOAD_MS = 5000;

function LoadingOverlay({ show, factSeed }: { show: boolean; factSeed: number }) {
  const [idx, setIdx] = useState(factSeed % FUN_FACTS.length);
  useEffect(() => { if (show) setIdx(factSeed % FUN_FACTS.length); }, [show, factSeed]);
  useEffect(() => {
    if (!show) return;
    const iv = setInterval(() => setIdx(i => (i + 1) % FUN_FACTS.length), 2000);
    return () => clearInterval(iv);
  }, [show]);

  return (
    <AnimatePresence>
      {show && (
        <motion.div className="fixed inset-0 z-40 grid place-items-center bg-white/80 backdrop-blur-sm"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
            {[0,1,2].map(i=>(
              <motion.div key={i} className="absolute w-[420px] h-[420px] rounded-full blur-3xl"
                style={{
                  left: `${15 + i*30}%`, top: `${10 + i*25}%`,
                  background: i===0
                    ? "radial-gradient(200px 200px at 30% 30%, #e0f2fe 0%, transparent 60%)"
                    : i===1
                    ? "radial-gradient(220px 220px at 70% 40%, #ffedd5 0%, transparent 60%)"
                    : "radial-gradient(240px 240px at 50% 70%, #e9d5ff 0%, transparent 60%)",
                }}
                animate={{ scale:[1,1.06,1], opacity:[0.7,1,0.7] }}
                transition={{ duration: 4+i, repeat: Infinity, ease:"easeInOut" }}
              />
            ))}
          </div>

          <motion.div
            className="w-[92%] max-w-xl bg-white rounded-3xl shadow-2xl ring-1 ring-slate-200 p-6 text-center"
            initial={{ y:14, opacity:0 }} animate={{ y:0, opacity:1 }} exit={{ y:8, opacity:0 }}
            transition={{ type:"spring", stiffness:140, damping:18 }}
            aria-busy="true" aria-live="polite"
          >
            <div className="flex items-center justify-center gap-2 mb-2">
              <div className="h-10 w-10 rounded-2xl bg-slate-100 grid place-items-center ring-1 ring-slate-200">
                <Loader2 className="animate-spin" size={20} />
              </div>
              <div className="text-lg font-semibold text-slate-800">Loading earnings calendar…</div>
            </div>
            <div className="text-sm text-slate-600">Fetching dates and estimates.</div>
            <div className="flex items-center justify-center gap-2 mt-4">
              {[0,1,2].map(i=>(
                <motion.div key={i} className="h-2 w-2 rounded-full bg-slate-300"
                  animate={{ y:[0,-6,0], opacity:[0.5,1,0.5] }}
                  transition={{ delay:i*0.15, duration:0.9, repeat:Infinity, ease:"easeInOut" }}
                />
              ))}
            </div>
            <div className="mt-5 px-4 py-3 rounded-2xl bg-slate-50 ring-1 ring-slate-200 text-slate-700 text-sm flex items-center gap-2">
              <Sparkles size={16} className="text-slate-500" />
              <AnimatePresence mode="wait">
                <motion.div key={idx} initial={{ opacity:0, x:8 }} animate={{ opacity:1, x:0 }} exit={{ opacity:0, x:-8 }} transition={{ duration:0.25 }}>
                  {FUN_FACTS[idx]}
                </motion.div>
              </AnimatePresence>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ---------- Center detail modal ---------- */
function Sparkline({ points }: { points: Array<number | null | undefined> }) {
  const data = points.filter((x): x is number => typeof x === "number");
  if (data.length < 2) return null;
  const w=220,h=60,pad=6;
  const min=Math.min(...data), max=Math.max(...data);
  const norm=(v:number)=> (max===min?0.5:(v-min)/(max-min));
  const step=(w-pad*2)/(data.length-1);
  const d=data.map((v,i)=>`${i===0?"M":"L"} ${pad+i*step} ${h-pad-norm(v)*(h-pad*2)}`).join(" ");
  return (
    <svg width={w} height={h} className="overflow-visible">
      <defs>
        <linearGradient id="lineGrad" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0%" stopColor="#0ea5e9" />
          <stop offset="100%" stopColor="#7c3aed" />
        </linearGradient>
      </defs>
      <path d={d} fill="none" stroke="url(#lineGrad)" strokeWidth="2" strokeLinecap="round">
        <animate attributeName="stroke-dasharray" from="0,500" to="500,0" dur="0.9s" fill="freeze" />
      </path>
    </svg>
  );
}

function EventDetailModal({
  open, onClose, ticker, name, logoUrl
}: { open: boolean; onClose: () => void; ticker: string; name: string; logoUrl?: string | null }) {
  const [detail, setDetail] = useState<EarnDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    if (!open) return;
    setLoading(true);
    setDetail(null);
    fetch(`${API_BASE_URL}/api/earnings_detail?ticker=${encodeURIComponent(ticker)}`)
      .then(r => r.json())
      .then((d: EarnDetail) => { if (active) setDetail(d); })
      .catch(() => { if (active) setDetail(null); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [open, ticker]);

  const hist = (detail?.history || []).slice().reverse();
  const sparkPoints = hist.map(p => (typeof p.epsReported === "number" ? p.epsReported : p.epsEstimate ?? null));

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-50 grid place-items-center bg-black/30"
          initial={{ opacity:0 }} animate={{ opacity:1 }} exit={{ opacity:0 }} onClick={onClose}>
          <motion.div
            className="w-[92%] max-w-2xl bg-white rounded-3xl p-6 shadow-2xl ring-1 ring-slate-200"
            initial={{ scale:0.96, y:18, opacity:0 }}
            animate={{ scale:1, y:0, opacity:1 }}
            exit={{ scale:0.98, y:10, opacity:0 }}
            transition={{ type:"spring", stiffness:160, damping:16 }}
            onClick={e=>e.stopPropagation()}
          >
            <div className="flex items-center gap-3">
              {logoUrl ? <img src={logoUrl} className="h-10 w-10 rounded bg-white ring-1 ring-slate-200" /> : <div className="h-10 w-10 rounded bg-slate-300" />}
              <div className="text-lg font-semibold">{ticker} — {name}</div>
            </div>

            {loading ? (
              <div className="mt-6 flex items-center gap-2 text-slate-600">
                <Loader2 className="animate-spin" size={18} /> Loading details…
              </div>
            ) : detail ? (
              <>
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="rounded-2xl bg-sky-50 ring-1 ring-sky-200 p-4">
                    <div className="text-sm font-semibold text-sky-800 flex items-center gap-2">
                      <CalIcon size={16} /> Upcoming
                    </div>
                    <div className="mt-1 text-sky-900">
                      {detail.next?.date ? format(new Date(detail.next.date+"T00:00:00"), "EEE, MMM d") : "TBA"}
                      {detail.next?.time && <span className="ml-1 text-sky-700">({detail.next.time})</span>}
                    </div>
                    <div className="mt-2 text-sm text-sky-800">
                      {typeof detail.next?.epsEstimate === "number" ? <>Est. EPS: <b>{detail.next.epsEstimate.toFixed(2)}</b></> : "Estimate: TBA"}
                      {typeof detail.next?.low === "number" && typeof detail.next?.high === "number" && (
                        <span className="ml-2 text-sky-700">[{detail.next.low.toFixed(2)}–{detail.next.high.toFixed(2)}]</span>
                      )}
                    </div>
                  </div>

                  <div className="rounded-2xl bg-violet-50 ring-1 ring-violet-200 p-4">
                    <div className="text-sm font-semibold text-violet-800 flex items-center gap-2">
                      <TrendingUp size={16} /> Last reported
                    </div>
                    <div className="mt-1 text-violet-900">
                      {detail.last?.date ? format(new Date(detail.last.date+"T00:00:00"), "EEE, MMM d") : "—"}
                      {detail.last?.time && <span className="ml-1 text-violet-700">({detail.last.time})</span>}
                    </div>
                    <div className="mt-2 text-sm text-violet-800">
                      {typeof detail.last?.epsReported === "number" ? <>EPS: <b>{detail.last.epsReported.toFixed(2)}</b></> : "EPS: —"}
                      {typeof detail.last?.epsEstimate === "number" && <span className="ml-2">vs est {detail.last.epsEstimate.toFixed(2)}</span>}
                      {typeof detail.last?.surprisePct === "number" && <span className="ml-2 text-violet-700">({detail.last.surprisePct.toFixed(1)}% surprise)</span>}
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <div className="text-sm font-medium text-slate-700 flex items-center gap-2">
                    <Info size={14} /> Recent EPS trend
                  </div>
                  <div className="mt-2 rounded-2xl ring-1 ring-slate-200 bg-white p-3">
                    <Sparkline points={sparkPoints} />
                    <div className="mt-1 text-xs text-slate-500">Based on recent reported EPS (fallback to estimate if unavailable).</div>
                  </div>
                </div>
              </>
            ) : <div className="mt-6 text-slate-600">No details available.</div>}

            <div className="mt-6 flex justify-end">
              <button onClick={onClose} className="px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition">Close</button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ---------- Weekly calendar (no bottom drawer, no filter chips, chips show logo+ticker only) ---------- */
export default function EarningsCalendar() {
  const [weekStart, setWeekStart] = useState<Date>(startOfWeek(new Date(), { weekStartsOn: 0 }));
  const [events, setEvents] = useState<EarnEvent[]>([]);
  const [overlay, setOverlay] = useState<boolean>(true);
  const overlayShownRef = useRef<boolean>(false);
  const [selectedDay, setSelectedDay] = useState<Date | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<EarnEvent | null>(null);
  const [factSeed] = useState<number>(() => Math.floor(Math.random() * 100000));

  useEffect(() => {
    const startISO = format(weekStart, "yyyy-MM-dd");
    const first = !overlayShownRef.current;
    if (first) {
      setOverlay(true);
      Promise.all([
        fetch(`${API_BASE_URL}/api/earnings_week?start=${startISO}`).then(r => r.json()).then((d: EarnEvent[]) => setEvents(d || [])),
        new Promise(res => setTimeout(res, FIRST_LOAD_MS)),
      ]).then(() => { setOverlay(false); overlayShownRef.current = true; });
    } else {
      fetch(`${API_BASE_URL}/api/earnings_week?start=${startISO}`).then(r => r.json()).then((d: EarnEvent[]) => setEvents(d || [])).catch(()=>setEvents([]));
    }
  }, [weekStart]);

  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => addDays(weekStart, i)), [weekStart]);
  const eventsByDay = useMemo(() => {
    const map = new Map<string, EarnEvent[]>();
    for (const ev of events) (map.get(ev.date) || map.set(ev.date, []).get(ev.date))!.push(ev);
    return map;
  }, [events]);

  const weekLabel = `${format(weekStart, "MMM d, yyyy")} – ${format(addDays(weekStart, 6), "MMM d")}`;

  return (
    <div className="min-h-[calc(100vh-64px)] text-slate-900 flex items-start justify-center pb-16">
      <LoadingOverlay show={overlay} factSeed={factSeed} />
      <div className="w-full max-w-6xl px-4 sm:px-6 mt-6">
        {/* Week nav only */}
        <div className="flex items-center gap-2 mb-4">
          <button className="h-10 w-10 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
                  onClick={() => setWeekStart(d => addWeeks(d, -1))} aria-label="Previous week">
            <ChevronLeft />
          </button>
          <div className="text-xl font-semibold">{weekLabel}</div>
          <button className="h-10 w-10 grid place-items-center rounded-xl bg-white ring-1 ring-slate-200 hover:bg-slate-50"
                  onClick={() => setWeekStart(d => addWeeks(d, +1))} aria-label="Next week">
            <ChevronRight />
          </button>
        </div>

        {/* Week grid */}
        <motion.div key={format(weekStart, "yyyy-MM-dd")}
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}
          className={`${CARD} p-4 relative overflow-hidden`}>
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-sky-50/60 via-transparent to-transparent" />
          <div className="grid grid-cols-7 gap-2 px-1 pb-2 text-xs font-medium text-slate-500">
            {["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].map(d => <div key={d} className="text-center">{d}</div>)}
          </div>

          <div className="grid grid-cols-7 gap-2">
            {days.map((day, i) => {
              const dateStr = format(day, "yyyy-MM-dd");
              const evts = eventsByDay.get(dateStr) || [];
              const isSelected = selectedDay && isSameDay(day, selectedDay);

              return (
                <motion.div key={dateStr + i}
                  className={`h-48 rounded-xl p-2 text-left ring-1 transition cursor-default ${
                    isSelected ? "bg-sky-50 ring-sky-300" : "bg-white ring-slate-200"
                  }`}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => setSelectedDay(day)}
                >
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-medium">{format(day, "MMM d")}</div>
                    {isSelected && <div className="text-[10px] px-2 py-0.5 rounded bg-sky-100 text-sky-700">Selected</div>}
                  </div>

                  <div className="mt-1 space-y-1">
                    {evts.slice(0, 5).map((e, idx) => (
                      <motion.button
                        key={e.ticker + idx}
                        initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.25, delay: idx * 0.03 }}
                        className="w-full flex items-center gap-2 rounded-lg bg-slate-100 px-2 py-1 ring-1 ring-transparent hover:ring-slate-300"
                        title={e.name}
                        onClick={(evt) => { evt.stopPropagation(); setSelectedEvent(e); }}
                      >
                        {e.logoUrl ? (
                          <img src={e.logoUrl} className="h-4 w-4 rounded bg-white ring-1 ring-slate-200" />
                        ) : (
                          <div className="h-4 w-4 rounded bg-slate-300" />
                        )}
                        <span className="text-[11px] font-semibold text-slate-700">{e.ticker}</span>
                        {/* EPS estimate intentionally hidden on chips */}
                      </motion.button>
                    ))}
                  </div>

                  {/* Only show the link when there are events */}
                  {evts.length > 0 && (
                    <div className="mt-2">
                      <button
                        className="text-[11px] text-slate-600 hover:text-slate-800"
                        onClick={(evt) => { evt.stopPropagation(); setSelectedEvent(evts[0]); }}
                      >
                        View details →
                      </button>
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Center modal only */}
        <EventDetailModal
          open={!!selectedEvent}
          onClose={() => setSelectedEvent(null)}
          ticker={selectedEvent?.ticker || ""}
          name={selectedEvent?.name || ""}
          logoUrl={selectedEvent?.logoUrl}
        />
      </div>
    </div>
  );
}
