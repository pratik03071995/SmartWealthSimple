// web/src/components/LearnHub.tsx
import React, { useMemo, useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from "framer-motion";
import {
  BookOpen, GraduationCap, Lightbulb, Calculator, Sparkles,
  BarChart3, ShieldCheck, Info, PiggyBank, Trophy, Scale,
  LineChart as LineIcon, Check, Landmark, Percent, DollarSign, Layers, HelpCircle
} from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
  LineChart as ReLineChart, Line, Legend
} from "recharts";

/* ------------------------------ Shared helpers ------------------------------ */
const CARD = "bg-white border border-slate-200 rounded-3xl shadow-xl";
const SECTION = "rounded-3xl bg-white/70 backdrop-blur supports-[backdrop-filter]:bg-white/60 ring-1 ring-slate-200 p-5";

const fmtUSD0 = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const fmtUSD2 = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 2 });
const clampNum = (x: number, fb = 0) => (Number.isFinite(x) ? x : fb);

/* Animated number */
function AnimatedNumber({
  value, prefix = "", suffix = "", fractionDigits = 0, durationMs = 700,
}: { value: number; prefix?: string; suffix?: string; fractionDigits?: number; durationMs?: number }) {
  const [display, setDisplay] = useState<number>(value);
  useEffect(() => {
    const startVal = display, endVal = value, start = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      setDisplay(startVal + (endVal - startVal) * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);
  const formatted = Number(display).toLocaleString(undefined, {
    minimumFractionDigits: fractionDigits, maximumFractionDigits: fractionDigits,
  });
  return <span>{prefix}{formatted}{suffix}</span>;
}

/* Reusable number input */
function NumberField({
  label, value, onChange, min, step = "any", suffix, hint
}: {
  label: string; value: number | string; onChange: (v: number) => void; min?: number; step?: string; suffix?: string; hint?: string
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
      <div className="flex items-center rounded-xl ring-1 ring-slate-200 bg-white px-3 py-2">
        <input
          className="w-full outline-none"
          type="number"
          min={min}
          step={step}
          value={value}
          onChange={(e)=> onChange(clampNum(parseFloat(e.target.value)))}
        />
        {suffix && <span className="ml-2 text-slate-500 text-sm">{suffix}</span>}
      </div>
      {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
    </div>
  );
}

/* ------------------------------ BASICS (expanded) ------------------------------ */
type GlossItem = {
  id: string; title: string; tagline: string; content: string; example?: string; icon: React.ReactNode;
};
const GLOSSARY: GlossItem[] = [
  { id:"eps",   title:"EPS (Earnings per Share)",  tagline:"Profit per share", icon:<BarChart3 size={18}/>,
    content:"EPS = net income ÷ diluted shares. Trends & consistency matter more than any single quarter.",
    example:"$100M earnings / 50M shares = $2.00 EPS" },
  { id:"pe",    title:"P/E Ratio",                 tagline:"Price vs. earnings power", icon:<Calculator size={18}/>,
    content:"P/E compares share price to EPS. Use vs peers & the company’s own history.",
    example:"$40 price / $2 EPS = 20× P/E" },
  { id:"peg",   title:"PEG Ratio",                 tagline:"Price vs growth", icon:<Percent size={18}/>,
    content:"PEG = P/E ÷ EPS growth (%). ~1 can imply fair vs growth, but inputs are noisy.",
    example:"P/E 20 ÷ 20% growth → PEG ≈ 1" },
  { id:"ps",    title:"Price-to-Sales",            tagline:"For low/negative EPS", icon:<DollarSign size={18}/>,
    content:"P/S = market cap ÷ revenue. Useful for early-stage firms; margins still matter.",
    example:"$10B cap / $1B sales = 10× P/S" },
  { id:"evEbt", title:"EV / EBITDA",               tagline:"Capital-structure neutral", icon:<Scale size={18}/>,
    content:"Compares enterprise value to cash earnings. Good cross-company sanity check.",
    example:"$30B EV / $2B EBITDA = 15× EV/EBITDA" },
  { id:"fcf",   title:"Free Cash Flow (FCF)",      tagline:"Owner earnings", icon:<Layers size={18}/>,
    content:"FCF = operating cash flow − capex. Funds buybacks, dividends, debt paydown, M&A.",
    example:"$2B OCF − $0.6B capex = $1.4B FCF" },
  { id:"roic",  title:"ROIC vs WACC",              tagline:"Quality & value creation", icon:<Trophy size={18}/>,
    content:"If ROIC > WACC, the firm creates value. Wide & durable spreads command premiums.",
    example:"ROIC 16% vs WACC 9% → value creation" },
  { id:"margin",title:"Margins",                   tagline:"Gross → Operating → Net", icon:<LineIcon size={18}/>,
    content:"Margin structure shows pricing power & efficiency. Watch multi-year direction.",
    example:"Gross 60% → Op 30% → Net 22%" },
  { id:"lev",   title:"Leverage & Coverage",       tagline:"Debt safety", icon:<Landmark size={18}/>,
    content:"Debt/EBITDA, Interest coverage (EBIT/Interest), maturity ladder: stress-test in downturns.",
    example:"2.0× Debt/EBITDA; 6× coverage = comfortable" },
];

function GlossaryGrid() {
  const [open, setOpen] = useState<string | null>("eps");
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      {GLOSSARY.map((g, i) => {
        const active = open === g.id;
        return (
          <motion.button
            key={g.id}
            onClick={() => setOpen(active ? null : g.id)}
            initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}
            transition={{ delay: i*0.03 }}
            className={`${SECTION} text-left hover:shadow-lg transition ${active ? "ring-sky-300 bg-sky-50/70" : ""}`}
          >
            <div className="flex items-center gap-2 text-slate-900 font-semibold">
              <span className={`h-9 w-9 rounded-xl grid place-items-center ring-1 ${active ? "bg-sky-100 ring-sky-200 text-sky-700" : "bg-slate-100 ring-slate-200 text-slate-700"}`}>
                {g.icon}
              </span>
              {g.title}
            </div>
            <div className="mt-1 text-sm text-slate-600">{g.tagline}</div>
            <AnimatePresence initial={false}>
              {active && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}
                  className="overflow-hidden"
                >
                  <div className="mt-3 text-slate-700">{g.content}</div>
                  {g.example && (
                    <div className="mt-3 text-sm rounded-xl bg-white ring-1 ring-slate-200 p-3 flex items-start gap-2">
                      <Info size={14} className="text-slate-500 mt-0.5" />
                      <div><span className="font-medium">Example:</span> {g.example}</div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        );
      })}
    </div>
  );
}

/* ------------------------------ COMPOUNDING LAB (aspect tuned + explainer) ------------------------------ */
function simulateSeries(
  years: number, cagrPct: number, initial: number, monthly: number, contribBump: number
) {
  const months = Math.max(1, Math.floor(clampNum(years, 1) * 12));
  const r = Math.pow(1 + clampNum(cagrPct, 0)/100, 1/12) - 1;
  let value = clampNum(initial, 0);
  let contrib = clampNum(initial, 0);
  let m = clampNum(monthly, 0);
  const data: { m:number, value:number, contrib:number }[] = [];

  for (let i=0; i<=months; i++) {
    if (i>0) {
      value = value * (1 + r) + m;
      contrib += m;
    }
    if (i>0 && i % 12 === 0) m = m * (1 + clampNum(contribBump, 0)/100);
    data.push({ m:i, value, contrib });
  }
  return { data, final:value, invested:contrib, growth:value - contrib };
}

function CompoundingLab({
  initial, setInitial, monthly, setMonthly, years, setYears, cagrPct, setCagrPct, contribBump, setContribBump
}: {
  initial: number; setInitial: (n:number)=>void;
  monthly: number; setMonthly: (n:number)=>void;
  years: number; setYears: (n:number)=>void;
  cagrPct: number; setCagrPct: (n:number)=>void;
  contribBump: number; setContribBump: (n:number)=>void;
}) {
  const sim = useMemo(() => simulateSeries(years, cagrPct, initial, monthly, contribBump),
    [initial, monthly, years, cagrPct, contribBump]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      {/* LEFT: Calculator + KPIs */}
      <motion.div className={SECTION} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <PiggyBank size={18} /> Your Plan
        </div>
        <div className="mt-2 text-sm text-slate-600 flex items-center gap-2">
          <HelpCircle size={14} className="text-slate-500" />
          This calculator shows how your money could grow over time if you invest regularly and earn an average annual return (CAGR).
        </div>
        <div className="mt-4 grid grid-cols-2 gap-3">
          <NumberField label="Initial lump sum" value={initial} onChange={setInitial} min={0} />
          <NumberField label="Monthly contribution" value={monthly} onChange={setMonthly} min={0} />
          <NumberField label="Years" value={years} onChange={(v)=>setYears(Math.max(1, Math.round(v)))} min={1} step="1" />
          <NumberField label="Expected CAGR" value={cagrPct} onChange={setCagrPct} min={-50} suffix="%" />
          <NumberField label="Annual raise on monthly" value={contribBump} onChange={setContribBump} min={0} suffix="%" hint="Optional: e.g. +3%/yr" />
        </div>

        {/* KPIs */}
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <motion.div className="rounded-2xl bg-emerald-50 ring-1 ring-emerald-200 p-4"
            initial={{scale:0.98, opacity:0}} animate={{scale:1, opacity:1}}>
            <div className="text-sm text-emerald-800">Final Value</div>
            <div className="text-2xl font-semibold text-emerald-900">
              <AnimatedNumber value={Math.max(0, Math.round(sim.final))} prefix="$" />
            </div>
          </motion.div>
          <motion.div className="rounded-2xl bg-sky-50 ring-1 ring-sky-200 p-4"
            initial={{scale:0.98, opacity:0}} animate={{scale:1, opacity:1}}>
            <div className="text-sm text-sky-800">Total Invested</div>
            <div className="text-2xl font-semibold text-sky-900">
              <AnimatedNumber value={Math.max(0, Math.round(sim.invested))} prefix="$" />
            </div>
          </motion.div>
          <motion.div className="rounded-2xl bg-violet-50 ring-1 ring-violet-200 p-4"
            initial={{scale:0.98, opacity:0}} animate={{scale:1, opacity:1}}>
            <div className="text-sm text-violet-800">Compounding Gain</div>
            <div className="text-2xl font-semibold text-violet-900">
              <AnimatedNumber value={Math.max(0, Math.round(sim.growth))} prefix="$" />
            </div>
          </motion.div>
        </div>

        <div className="mt-3 text-xs text-slate-500 flex items-center gap-2">
          <Info size={12}/> Monthly compounding; contributions added each month; contribution raises every 12 months.
        </div>
      </motion.div>

      {/* RIGHT: Chart (balanced aspect) */}
      <motion.div className={SECTION} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <LineIcon size={18} /> Portfolio vs. Contributions
        </div>
        <div className="mt-3 h-[22rem] rounded-xl ring-1 ring-slate-200 p-3">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sim.data}>
              <defs>
                <linearGradient id="gradA" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0ea5e9" stopOpacity={0.8}/>
                  <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="gradB" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity={0.7}/>
                  <stop offset="100%" stopColor="#6366f1" stopOpacity={0.08}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="m" tick={{ fontSize: 12 }} tickFormatter={(m)=>`${Math.floor(Number(m)/12)}y`} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v)=>v>=1000?`${Math.round(Number(v)/1000)}k`:`${v}`} />
              <Tooltip
                formatter={(v:any, name:any)=>[fmtUSD2(Number(v)), name==="value"?"Portfolio":"Contrib"]}
                labelFormatter={(m)=>`${Math.floor(Number(m)/12)} years`}
              />
              <Area type="monotone" dataKey="contrib" stroke="#6366f1" fill="url(#gradB)" />
              <Area type="monotone" dataKey="value" stroke="#0ea5e9" fill="url(#gradA)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </div>
  );
}

/* ------------------------------ ETF Compare (kept) + hover popovers ------------------------------ */
const ETF_CAGRS: { ticker: string; name: string; cagrPct: number; facts: string[]; quick?: string }[] = [
  { ticker: "QQQ",  name: "Invesco QQQ",            cagrPct: 15.0, quick:"Nasdaq-100 (mega-cap tech tilt).", facts: [
    "QQQ tracks the Nasdaq-100—tilted to mega-cap tech.",
    "Historically higher volatility than broad market.",
    "Top holdings often drive the bulk of returns."
  ] },
  { ticker: "SPY",  name: "SPDR S&P 500",           cagrPct: 10.5, quick:"US large-caps across 11 sectors.", facts: [
    "SPY is the oldest US ETF (1993).",
    "Broad large-cap exposure across 11 sectors.",
    "Often a benchmark for US equity performance."
  ] },
  { ticker: "VTI",  name: "Vanguard Total Market",  cagrPct: 10.2, quick:"~4,000 US stocks (total market).", facts: [
    "Covers ~4,000 US stocks from large to micro caps.",
    "Low-cost, total-market approach.",
    "Small caps can add cyclicality."
  ] },
  { ticker: "VOO",  name: "Vanguard S&P 500",       cagrPct: 10.5, quick:"S&P 500 exposure (low fee).", facts: [
    "Similar exposure to SPY with lower fee.",
    "Highly diversified across blue-chip leaders.",
    "Core building block for many portfolios."
  ] },
  { ticker: "SCHD", name: "Schwab Dividend Equity", cagrPct: 9.5,  quick:"Quality dividend tilt.", facts: [
    "Quality dividend tilt with profitability screens.",
    "Dividend growth focus over pure high yield.",
    "Sector weights differ vs. the S&P 500."
  ] },
  { ticker: "SMH",  name: "VanEck Semiconductor",   cagrPct: 14.0, quick:"Semiconductor ecosystem.", facts: [
    "Includes designers, foundries, and equipment makers.",
    "Cyclical but critical to global tech.",
    "AI and edge compute are secular drivers."
  ] },
  { ticker: "SOXX", name: "iShares Semiconductor",  cagrPct: 14.0, quick:"Alt. semiconductor basket.", facts: [
    "Alternative semiconductor basket to SMH.",
    "Broad exposure to key chip supply-chain players.",
    "Performance can cluster around chip cycles."
  ] },
  { ticker: "XLK",  name: "Tech Select Sector",     cagrPct: 13.0, quick:"S&P 500 technology sector.", facts: [
    "Technology sub-index of S&P 500.",
    "Concentrated in megacap software & hardware.",
    "Secular growth balanced by valuation swings."
  ] },
  { ticker: "XLF",  name: "Financials Select",      cagrPct: 7.5,  quick:"Banks/insurers/capital mkts.", facts: [
    "Banks, insurers, capital markets.",
    "Rate cycles strongly impact net interest margins.",
    "Credit quality and capital buffers matter."
  ] },
  { ticker: "XLV",  name: "Health Care Select",     cagrPct: 9.0,  quick:"Pharma/devices/services.", facts: [
    "Pharma, biotech, medical devices & services.",
    "Defensive traits with innovation upside.",
    "Policy/regulatory risk can move the group."
  ] },
  { ticker: "IWM",  name: "iShares Russell 2000",   cagrPct: 8.0,  quick:"US small caps (cyclical).", facts: [
    "Small caps are more rate- and credit-sensitive.",
    "Historically recover strongly out of recessions.",
    "Valuations vary widely across constituents."
  ] },
  { ticker: "ARKK", name: "ARK Innovation",         cagrPct: 7.0,  quick:"Disruptive themes (concentrated).", facts: [
    "Concentrated bets in disruptive themes.",
    "Can be highly volatile and trend-driven.",
    "Position sizing is key for risk control."
  ] },
];

const LINE_COLORS = [
  "#0ea5e9","#2563eb","#6366f1","#7c3aed","#06b6d4","#3b82f6",
  "#60a5fa","#a78bfa","#0891b2","#5b21b6","#7dd3fc","#94a3b8"
];

function ParallaxBackdrop() {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 40, damping: 15 });
  const springY = useSpring(y, { stiffness: 40, damping: 15 });
  const mv1x = useTransform(springX, [-200, 200], [-12, 12]);
  const mv1y = useTransform(springY, [-200, 200], [ -8,  8]);
  const mv2x = useTransform(springX, [-200, 200], [  8, -8]);
  const mv2y = useTransform(springY, [-200, 200], [ 12, -12]);

  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onMove = (e: MouseEvent) => {
      const r = el.getBoundingClientRect();
      x.set(e.clientX - (r.left + r.width/2));
      y.set(e.clientY - (r.top + r.height/2));
    };
    el.addEventListener("mousemove", onMove);
    return () => el.removeEventListener("mousemove", onMove);
  }, [x, y]);

  return (
    <div ref={ref} className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute w-[520px] h-[520px] rounded-full blur-3xl"
        style={{
          x: mv1x, y: mv1y, left: "10%", top: "-30%",
          background: "radial-gradient(280px 280px at 50% 50%, rgba(99,102,241,.18) 0%, transparent 65%)",
        }}
      />
      <motion.div
        className="absolute w-[520px] h-[520px] rounded-full blur-3xl"
        style={{
          x: mv2x, y: mv2y, right: "5%", top: "-30%",
          background: "radial-gradient(280px 280px at 50% 50%, rgba(14,165,233,.25) 0%, transparent 65%)",
        }}
      />
      <motion.div
        className="absolute w-[520px] h-[520px] rounded-full blur-3xl"
        style={{
          x: mv1x, y: mv1y, left: "0%", bottom: "-30%",
          background: "radial-gradient(280px 280px at 40% 40%, rgba(99,102,241,.20) 0%, transparent 65%)",
        }}
      />
    </div>
  );
}

function simulateETFSeries(
  years: number, cagrPct: number, initial: number, monthly: number, contribBump: number
) {
  const months = Math.max(1, Math.floor(clampNum(years, 1) * 12));
  const r = Math.pow(1 + clampNum(cagrPct, 0)/100, 1/12) - 1;
  let value = clampNum(initial, 0);
  let m = clampNum(monthly, 0);
  const points: { year:number, value:number }[] = [{ year:0, value }];

  for (let i=1; i<=months; i++) {
    value = value * (1 + r) + m;
    if (i % 12 === 0) {
      const y = i/12;
      points.push({ year:y, value });
      m = m * (1 + clampNum(contribBump, 0)/100);
    }
  }
  if (points[points.length-1].year !== years) points.push({ year: years, value });
  return points;
}

function ETFCompare({
  years, initial, monthly, contribBump
}: { years: number; initial: number; monthly: number; contribBump: number }) {
  const [selected, setSelected] = useState<string[]>(["QQQ","SPY","VTI","SMH"]);
  const [active, setActive] = useState<string>("QQQ");
  const [hovered, setHovered] = useState<string | null>(null);
  const [factIdx, setFactIdx] = useState<number>(0);

  useEffect(() => {
    setFactIdx(0);
    const id = setInterval(() => setFactIdx(i => i + 1), 3000);
    return () => clearInterval(id);
  }, [active]);

  const toggle = (t: string) => {
    setSelected(prev => prev.includes(t)
      ? prev.filter(x=>x!==t)
      : (prev.length>=6 ? [...prev.slice(1), t] : [...prev, t]));
    setActive(t);
  };

  const series = useMemo(() => {
    const yearsAll = Array.from({length: Math.max(1, years)+1}, (_, i)=>i);
    const rows = yearsAll.map(y => ({ year: y } as any));
    ETF_CAGRS.forEach((e) => {
      const pts = simulateETFSeries(years, e.cagrPct, initial, monthly, contribBump);
      pts.forEach(p => {
        const row = rows.find(r => r.year === p.year);
        if (row) row[e.ticker] = p.value;
      });
    });
    return rows;
  }, [years, initial, monthly, contribBump]);

  const activeMeta = ETF_CAGRS.find(e => e.ticker === active) || ETF_CAGRS[0];
  const activeFact = activeMeta.facts[(factIdx % activeMeta.facts.length + activeMeta.facts.length) % activeMeta.facts.length];

  return (
    <motion.div className={`${SECTION} relative`} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
      <ParallaxBackdrop />
      <div className="flex items-center gap-2 text-slate-800 font-semibold relative z-10">
        <Trophy size={18} /> ETF Compare
      </div>
      <div className="text-sm text-slate-600 mt-1 relative z-10">
        Select ETFs to compare your plan using **placeholder** CAGRs. Colors match the site palette.
      </div>

      {/* Tiles */}
      <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 relative z-10">
        {ETF_CAGRS.map((e, idx) => {
          const on = selected.includes(e.ticker);
          const color = LINE_COLORS[idx % LINE_COLORS.length];
          const showHover = hovered === e.ticker;
          return (
            <motion.div key={e.ticker} className="relative">
              <motion.button
                onMouseEnter={()=>setHovered(e.ticker)}
                onMouseLeave={()=>setHovered(null)}
                onFocus={()=>setHovered(e.ticker)}
                onBlur={()=>setHovered(null)}
                onClick={()=>toggle(e.ticker)}
                initial={{opacity:0, y:8}} animate={{opacity:1, y:0}} transition={{delay: idx*0.02}}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.98 }}
                className={`relative rounded-xl px-3 py-2 text-left text-sm transition group w-full
                  ring-1 ${on ? "bg-sky-600/10 ring-sky-400 shadow-lg" : "bg-white/70 ring-slate-200 hover:bg-slate-50"}`}
                style={{ borderLeft: `4px solid ${color}` }}
                title={`${e.name} — ${e.quick || ""}`}
              >
                <AnimatePresence>
                  {on && (
                    <motion.span
                      initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}
                      className="absolute top-1.5 right-1.5 h-5 w-5 rounded-full grid place-items-center bg-sky-500 text-white shadow ring-1 ring-white/60"
                    >
                      <Check size={12}/>
                    </motion.span>
                  )}
                </AnimatePresence>
                <div className="font-semibold text-slate-800">{e.ticker}</div>
                <div className="text-[11px] text-slate-500">CAGR {e.cagrPct}%</div>
              </motion.button>

              {/* Hover popover */}
              <AnimatePresence>
                {showHover && (
                  <motion.div
                    initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 6 }}
                    className="absolute left-0 right-0 z-20 mt-1 px-3 py-2 rounded-xl bg-white ring-1 ring-slate-200 shadow"
                  >
                    <div className="text-[12px] font-medium text-slate-800">{e.name}</div>
                    <div className="text-[11px] text-slate-600">{e.quick}</div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>

      {/* Multi-line comparison */}
      <div className="mt-4 h-[24rem] rounded-xl ring-1 ring-slate-200 p-3 bg-white/80 relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <ReLineChart data={series}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="year" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v)=>v>=1000?`${Math.round(Number(v)/1000)}k`:`${v}`} />
            <Tooltip formatter={(v:any, name:any)=>[fmtUSD2(Number(v)), name]} labelFormatter={(y)=>`Year ${y}`} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {ETF_CAGRS.map((e, idx) => {
              const color = LINE_COLORS[idx % LINE_COLORS.length];
              const on = selected.includes(e.ticker);
              return (
                <Line
                  key={e.ticker}
                  type="monotone"
                  dataKey={e.ticker}
                  stroke={color}
                  strokeWidth={on ? 3 : 2}
                  dot={false}
                  hide={!on}
                  activeDot={{ r: 5 }}
                />
              );
            })}
          </ReLineChart>
        </ResponsiveContainer>
      </div>

      {/* Active fact strip */}
      <div className="mt-3 rounded-xl bg-slate-50 ring-1 ring-slate-200 p-3 text-sm text-slate-700 flex items-start gap-2 relative z-10">
        <Sparkles size={16} className="text-slate-500 mt-0.5" />
        <AnimatePresence mode="wait">
          <motion.div
            key={active + "-" + (factIdx % activeMeta.facts.length)}
            initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }}
          >
            <b>{active}</b> — {activeMeta.name}. {activeFact}
          </motion.div>
        </AnimatePresence>
      </div>
      <div className="mt-2 text-xs text-slate-500 relative z-10">
        Educational illustration only. Replace placeholder CAGRs with real total-return data when ready.
      </div>
    </motion.div>
  );
}

/* ------------------------------ VALUATION (4 separate cards with intros) ------------------------------ */
function ValIntro({ title, blurb }: { title: string; blurb: string }) {
  return (
    <div className="flex items-start gap-2 text-sm text-slate-600 mb-3">
      <HelpCircle size={16} className="text-slate-500 mt-0.5" />
      <div><span className="font-medium text-slate-800">{title} — </span>{blurb}</div>
    </div>
  );
}

function ValuationLab() {
  // P/E Snapshot
  const [peEPS, setPeEPS] = useState(5.0);
  const [peTarget, setPeTarget] = useState(20.0);
  const [mosPct, setMosPct] = useState(20.0);
  const peFair = peEPS * peTarget;
  const peBuy  = peFair * (1 - mosPct/100);

  // EV/EBITDA
  const [evEbitda, setEvEbitda] = useState(12.0);
  const [ebitda, setEbitda] = useState(2000); // $m
  const [netDebt, setNetDebt] = useState(500); // $m
  const [shares, setShares] = useState(1000); // $m
  const evFair = evEbitda * ebitda;
  const mktCapFair = Math.max(0, evFair - netDebt);
  const priceFair = shares > 0 ? (mktCapFair * 1e6) / (shares * 1e6) : 0;

  // PEG
  const [peNow, setPeNow] = useState(18);
  const [growthPct, setGrowthPct] = useState(20);
  const peg = growthPct > 0 ? peNow / growthPct : NaN;

  // Mini DCF (toy)
  const [fcf0, setFcf0] = useState(1000); // $m
  const [gYears, setGYears] = useState(5);
  const [gRate, setGRate] = useState(12);
  const [discRate, setDiscRate] = useState(10);
  const [exitMult, setExitMult] = useState(18);
  const dcf = useMemo(() => {
    const years = Math.max(1, Math.round(gYears));
    const g = gRate/100, r = discRate/100;
    let f = fcf0;
    let pv = 0;
    const series: {y:number, f:number, pv:number}[] = [];
    for (let y=1; y<=years; y++) {
      f = f * (1 + g);
      const pvY = f / Math.pow(1+r, y);
      pv += pvY;
      series.push({ y, f, pv: pvY });
    }
    const terminal = (f * exitMult) / Math.pow(1+r, years);
    const totalPV = pv + terminal;
    return { totalPV, series, terminal, lastFCF:f };
  }, [fcf0, gYears, gRate, discRate, exitMult]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      {/* Card 1: P/E Snapshot */}
      <motion.div className={SECTION} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <Calculator size={18}/> P/E Snapshot
        </div>
        <ValIntro
          title="What it is"
          blurb="Estimate a fair price from next-year EPS × a target P/E. Add a margin of safety to find a ‘buy-below’ price."
        />
        <div className="text-xs text-slate-600 mb-3">
          Example: If EPS is $5 and a reasonable P/E is 20×, fair price ≈ <b>$100</b>. With 20% safety, buy-below ≈ <b>$80</b>.
        </div>
        <div className="grid grid-cols-2 gap-3">
          <NumberField label="Next-year EPS" value={peEPS} onChange={setPeEPS} min={0} />
          <NumberField label="Target P/E" value={peTarget} onChange={setPeTarget} min={0} />
          <NumberField label="Margin of Safety" value={mosPct} onChange={setMosPct} min={0} suffix="%" />
        </div>
        <div className="mt-3 grid grid-cols-2 gap-3">
          <div className="rounded-xl bg-sky-50 ring-1 ring-sky-200 p-3">
            <div className="text-xs text-sky-800">Fair Price</div>
            <div className="text-lg font-semibold text-sky-900"><AnimatedNumber value={peFair} prefix="$" fractionDigits={2} /></div>
          </div>
          <div className="rounded-xl bg-emerald-50 ring-1 ring-emerald-200 p-3">
            <div className="text-xs text-emerald-800">Buy-Below (MoS)</div>
            <div className="text-lg font-semibold text-emerald-900"><AnimatedNumber value={peBuy} prefix="$" fractionDigits={2} /></div>
          </div>
        </div>
      </motion.div>

      {/* Card 2: EV/EBITDA */}
      <motion.div className={SECTION} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <Scale size={18}/> EV / EBITDA
        </div>
        <ValIntro
          title="What it is"
          blurb="Enterprise Value (EV) divided by EBITDA helps compare companies regardless of debt. You pick a reasonable multiple."
        />
        <div className="text-xs text-slate-600 mb-3">
          Example: EV/EBITDA 12× × $2,000m EBITDA → <b>$24,000m EV</b>. Subtract net debt to get market cap; divide by shares for price.
        </div>
        <div className="grid grid-cols-2 gap-3">
          <NumberField label="EV / EBITDA" value={evEbitda} onChange={setEvEbitda} min={0} />
          <NumberField label="EBITDA ($m)" value={ebitda} onChange={setEbitda} min={0} />
          <NumberField label="Net Debt ($m)" value={netDebt} onChange={setNetDebt} />
          <NumberField label="Shares Out ($m)" value={shares} onChange={setShares} min={0.1} />
        </div>
        <div className="mt-3 grid grid-cols-2 gap-3">
          <div className="rounded-xl bg-violet-50 ring-1 ring-violet-200 p-3">
            <div className="text-xs text-violet-800">Fair EV</div>
            <div className="text-lg font-semibold text-violet-900"><AnimatedNumber value={evFair} prefix="$" suffix="m" /></div>
          </div>
          <div className="rounded-xl bg-slate-50 ring-1 ring-slate-200 p-3">
            <div className="text-xs text-slate-700">Fair Price</div>
            <div className="text-lg font-semibold text-slate-900"><AnimatedNumber value={priceFair} prefix="$" fractionDigits={2}/></div>
          </div>
        </div>
      </motion.div>

      {/* Card 3: PEG Sense-Check */}
      <motion.div className={SECTION} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <Percent size={18}/> PEG Sense-Check
        </div>
        <ValIntro
          title="What it is"
          blurb="PEG compares valuation to growth (P/E ÷ growth%). Around 1 can be ‘fair’ for many firms, but growth inputs can be noisy."
        />
        <div className="text-xs text-slate-600 mb-3">
          Example: P/E 18 and growth 20% → PEG ≈ <b>0.90</b>.
        </div>
        <div className="grid grid-cols-2 gap-3">
          <NumberField label="Current P/E" value={peNow} onChange={setPeNow} min={0} />
          <NumberField label="EPS Growth %" value={growthPct} onChange={setGrowthPct} />
        </div>
        <div className="mt-3 rounded-xl bg-amber-50 ring-1 ring-amber-200 p-3">
          <div className="text-xs text-amber-800">PEG</div>
          <div className="text-lg font-semibold text-amber-900">
            {Number.isFinite(peg) ? <AnimatedNumber value={peg} fractionDigits={2}/> : "—"}
          </div>
        </div>
      </motion.div>

      {/* Card 4: Mini DCF */}
      <motion.div className={SECTION} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <Calculator size={18}/> Mini DCF (toy)
        </div>
        <ValIntro
          title="What it is"
          blurb="Project free cash flow (FCF) for a few years, discount it back, then add a simple exit multiple. This is a teaching sketch."
        />
        <div className="text-xs text-slate-600 mb-3">
          Example: FCF grows 12% for 5 years, discounted at 10%, with an exit multiple on year-5 FCF.
        </div>

        <div className="grid grid-cols-2 gap-3">
          <NumberField label="Starting FCF ($m)" value={fcf0} onChange={setFcf0} />
          <NumberField label="High-growth years" value={gYears} onChange={(v)=>setGYears(Math.max(1, Math.round(v)))} step="1" />
          <NumberField label="FCF Growth %" value={gRate} onChange={setGRate} />
          <NumberField label="Discount rate %" value={discRate} onChange={setDiscRate} />
          <NumberField label="Exit multiple (x FCF)" value={exitMult} onChange={setExitMult} />
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-2xl bg-emerald-50 ring-1 ring-emerald-200 p-4">
            <div className="text-sm text-emerald-800">PV of Stage 1</div>
            <div className="text-2xl font-semibold text-emerald-900">
              <AnimatedNumber value={dcf.series.reduce((s, r)=>s+r.pv,0)} prefix="$" suffix="m" fractionDigits={1}/>
            </div>
          </div>
          <div className="rounded-2xl bg-sky-50 ring-1 ring-sky-200 p-4">
            <div className="text-sm text-sky-800">Terminal PV</div>
            <div className="text-2xl font-semibold text-sky-900">
              <AnimatedNumber value={dcf.terminal} prefix="$" suffix="m" fractionDigits={1}/>
            </div>
          </div>
          <div className="rounded-2xl bg-violet-50 ring-1 ring-violet-200 p-4">
            <div className="text-sm text-violet-800">Enterprise Value (PV)</div>
            <div className="text-2xl font-semibold text-violet-900">
              <AnimatedNumber value={dcf.totalPV} prefix="$" suffix="m" fractionDigits={1}/>
            </div>
          </div>
        </div>

        <div className="mt-3 h-56 rounded-xl ring-1 ring-slate-200 p-3 bg-white">
          <ResponsiveContainer width="100%" height="100%">
            <ReLineChart data={dcf.series.map(s=>({year:s.y, fcf:s.f, pv:s.pv}))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="year" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v:any, n:any)=>[n==="fcf"?`${v.toFixed(1)}m FCF`:`${v.toFixed(1)}m PV`, n==="fcf"?"FCF":"PV contribution"]} />
              <Line type="monotone" dataKey="fcf" stroke="#0ea5e9" strokeWidth={3} dot={false} />
              <Line type="monotone" dataKey="pv"  stroke="#6366f1" strokeWidth={2} dot={false} />
            </ReLineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-3 text-xs text-slate-500 flex items-center gap-2">
          <Info size={12}/> Extremely simplified DCF for learning only (no working capital, taxes nuance, SBC, etc.).
        </div>
      </motion.div>
    </div>
  );
}

/* ------------------------------ RISK PRIMER (kept + two extra cards) ------------------------------ */
function RiskPrimer() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <div className={SECTION}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <ShieldCheck size={18} /> Risk isn't just volatility
        </div>
        <ul className="mt-3 text-sm text-slate-700 space-y-2 list-disc pl-5">
          <li>Balance sheet: cash, debt maturities, interest coverage.</li>
          <li>Margins & cyclicality: how earnings behave in downturns.</li>
          <li>Customer concentration & switching costs.</li>
          <li>Execution risk: new products, integrations, regulation.</li>
          <li>Diversify across sectors and time horizons.</li>
        </ul>
        <div className="mt-3 text-xs text-slate-500 flex items-center gap-2">
          <Info size={12}/> Guidance often drives moves more than the headline EPS.
        </div>
      </div>

      <div className={SECTION}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <BarChart3 size={18} /> Quick Checklist
        </div>
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          <div className="rounded-xl bg-slate-50 ring-1 ring-slate-200 p-3">
            <div className="font-medium">Quality</div>
            <div className="text-slate-600">ROIC above WACC? Durable moat?</div>
          </div>
          <div className="rounded-2xl bg-slate-50 ring-1 ring-slate-200 p-3">
            <div className="font-medium">Growth</div>
            <div className="text-slate-600">Revenue & EPS trends healthy?</div>
          </div>
          <div className="rounded-2xl bg-slate-50 ring-1 ring-slate-200 p-3">
            <div className="font-medium">Financials</div>
            <div className="text-slate-600">Leverage manageable? FCF positive?</div>
          </div>
          <div className="rounded-2xl bg-slate-50 ring-1 ring-slate-200 p-3">
            <div className="font-medium">Valuation</div>
            <div className="text-slate-600">Fair vs peers/history? Why mispriced?</div>
          </div>
        </div>
      </div>

      {/* NEW: Mitigation Playbook */}
      <div className={SECTION}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <Lightbulb size={18} /> Mitigation Playbook (high return aim, controlled risk)
        </div>
        <ul className="mt-3 text-sm text-slate-700 space-y-2 list-disc pl-5">
          <li><b>Position sizing:</b> make big bets rare; 2–5% typical, increase only with conviction & data.</li>
          <li><b>Barbell your risk:</b> mix a core (broad ETFs) with a small “shots-on-goal” bucket.</li>
          <li><b>Time diversify:</b> dollar-cost average into volatile names to smooth entry timing.</li>
          <li><b>Rebalance:</b> trim winners that dominate; add to quality laggards within thesis.</li>
          <li><b>Scenario test:</b> ask “what breaks if revenue falls 20%?” before sizing.</li>
        </ul>
      </div>

      {/* NEW: Position Sizing & Barbell */}
      <div className={SECTION}>
        <div className="flex items-center gap-2 text-slate-800 font-semibold">
          <Layers size={18} /> Position Sizing & Barbell
        </div>
        <div className="mt-3 text-sm text-slate-700">
          A practical approach for high potential, high uncertainty stocks:
        </div>
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="rounded-xl bg-sky-50 ring-1 ring-sky-200 p-3 text-sm">
            <div className="font-medium text-sky-800">Core (70–90%)</div>
            <div className="text-sky-900/90">Broad ETFs (SPY/VOO/VTI) + quality compounders. Goal: steady compounding.</div>
          </div>
          <div className="rounded-xl bg-violet-50 ring-1 ring-violet-200 p-3 text-sm">
            <div className="font-medium text-violet-800">Exploratory (10–30%)</div>
            <div className="text-violet-900/90">Small positions in themes (AI, semis, biotech) with strict stop-adds, not stop-losses.</div>
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-500 flex items-center gap-2">
          <Info size={12}/> Educational only. Tune to your risk tolerance, horizon, and liquidity needs.
        </div>
      </div>
    </div>
  );
}

/* ------------------------------ Main Learn Page ------------------------------ */
export default function LearnHub() {
  const [tab, setTab] = useState<"basics" | "valuation" | "compounding" | "risk">("compounding");

  // Shared state for Compounding Lab + ETF Compare
  const [initial, setInitial] = useState(5000);
  const [monthly, setMonthly] = useState(500);
  const [years, setYears] = useState(10);
  const [cagrPct, setCagrPct] = useState(12);
  const [contribBump, setContribBump] = useState(3);

  return (
    <div className="min-h-[calc(100vh-64px)] text-slate-900 flex items-start justify-center pb-20">
      <div className="w-full max-w-6xl px-4 sm:px-6 mt-6">
        {/* Hero */}
        <motion.div className={`${CARD} p-6 relative overflow-hidden`} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
          <div className="absolute inset-0 pointer-events-none -z-10">
            <motion.div
              className="absolute w-[520px] h-[520px] rounded-3xl blur-3xl"
              style={{ left: "10%", top: "-30%", background: "radial-gradient(280px 280px at 30% 30%, #e0f2fe 0%, transparent 60%)" }}
              animate={{ opacity:[0.5,1,0.5] }} transition={{ duration: 6, repeat: Infinity, ease:"easeInOut" }}
            />
            <motion.div
              className="absolute w-[520px] h-[520px] rounded-3xl blur-3xl"
              style={{ right: "5%", top: "-20%", background: "radial-gradient(300px 300px at 70% 40%, #ffedd5 0%, transparent 60%)" }}
              animate={{ opacity:[0.5,1,0.5] }} transition={{ duration: 7, repeat: Infinity, ease:"easeInOut" }}
            />
          </div>

          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-2xl bg-white ring-1 ring-slate-200 grid place-items-center">
              <GraduationCap className="text-slate-700" />
            </div>
            <div>
              <div className="text-xl font-bold">SmartWealth Academy</div>
              <div className="text-sm text-slate-600">Interactive fundamentals, valuation, simulations, and comparisons.</div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-4 flex items-center gap-2 flex-wrap">
            {[
              {k:"basics", label:"Basics", Icon: BookOpen},
              {k:"valuation", label:"Valuation", Icon: Scale},
              {k:"compounding", label:"Compounding Lab", Icon: PiggyBank},
              {k:"risk", label:"Risk", Icon: ShieldCheck},
            ].map(({k, label, Icon}) => {
              const active = tab === (k as any);
              return (
                <button
                  key={k}
                  onClick={()=>setTab(k as any)}
                  className={`px-4 py-2 rounded-xl ring-1 transition flex items-center gap-2 text-sm
                    ${active ? "bg-sky-50 text-sky-800 ring-sky-200" : "bg-white text-slate-700 ring-slate-200 hover:bg-slate-50"}`}
                >
                  <Icon size={16} /> {label}
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {tab === "basics" && (
            <motion.div key="basics" className="mt-5" initial={{opacity:0, y:12}} animate={{opacity:1, y:0}} exit={{opacity:0, y:-8}}>
              <div className={`${SECTION} mb-5`}>
                <div className="flex items-center gap-2 text-slate-800 font-semibold">
                  <Lightbulb size={18} /> Foundations
                </div>
                <div className="text-sm text-slate-600 mt-2">
                  Open cards for quick definitions and examples: EPS, P/E, PEG, EV/EBITDA, P/S, FCF, ROIC, margins, leverage & coverage.
                </div>
              </div>
              <GlossaryGrid />
            </motion.div>
          )}

          {tab === "valuation" && (
            <motion.div key="valuation" className="mt-5" initial={{opacity:0, y:12}} animate={{opacity:1, y:0}} exit={{opacity:0, y:-8}}>
              <ValuationLab />
            </motion.div>
          )}

          {tab === "compounding" && (
            <motion.div key="compounding" className="mt-5" initial={{opacity:0, y:12}} animate={{opacity:1, y:0}} exit={{opacity:0, y:-8}}>
              <CompoundingLab
                initial={initial} setInitial={setInitial}
                monthly={monthly} setMonthly={setMonthly}
                years={years} setYears={setYears}
                cagrPct={cagrPct} setCagrPct={setCagrPct}
                contribBump={contribBump} setContribBump={setContribBump}
              />
              <div className="mt-5">
                <ETFCompare years={years} initial={initial} monthly={monthly} contribBump={contribBump} />
              </div>
            </motion.div>
          )}

          {tab === "risk" && (
            <motion.div key="risk" className="mt-5" initial={{opacity:0, y:12}} animate={{opacity:1, y:0}} exit={{opacity:0, y:-8}}>
              <RiskPrimer />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Bottom tip */}
        <div className="mt-8 text-xs text-slate-500 flex items-center gap-2">
          <Info size={12}/>
          Educational only. Not investment advice. Markets are volatile; use multiple sources and consider professional guidance.
        </div>
      </div>
    </div>
  );
}
