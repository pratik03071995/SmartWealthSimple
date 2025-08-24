import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Rocket, LineChart, ChevronRight, ArrowLeft, Shield } from 'lucide-react'

/** ======== LIGHT THEME ======== */
const CARD_BG = "bg-white border border-slate-200"
const GRADIENT_BAR = "bg-gradient-to-r from-sky-400 via-emerald-400 to-teal-400"
const BUTTON_GRADIENT = "bg-gradient-to-r from-sky-400 to-emerald-400"

/** ======== STEPS / OPTIONS ======== */
const steps = ["Welcome", "Basics", "Strategy", "Sectors", "Sub-sectors", "Goals", "Results"] as const

const sectorList = [
  "AI & Semiconductors","EV & Clean Energy","Biotech & HealthTech","FinTech",
  "Cloud & SaaS","Cybersecurity","Space & Robotics","E-commerce & Consumer Tech",
  "Industrial Tech","Green Materials"
]

const subSectorMap: Record<string, string[]> = {
  "AI & Semiconductors": ["GPUs", "ASICs", "Edge AI", "EDA", "Chip Equipment"],
  "EV & Clean Energy": ["Batteries", "Charging", "Solar", "Wind", "Grid Tech"],
  "Biotech & HealthTech": ["Genomics", "Diagnostics", "Wearables", "Telemed"],
  "FinTech": ["Payments", "Lending", "InsurTech", "Crypto Infra"],
  "Cloud & SaaS": ["DevOps", "Collaboration", "ERP", "Security SaaS"],
  "Cybersecurity": ["Network", "Endpoint", "Cloud Sec", "IAM"],
  "Space & Robotics": ["Launch", "Satellites", "Drones", "Automation"],
  "E-commerce & Consumer Tech": ["Marketplaces", "Logistics", "Social", "Retail"],
  "Industrial Tech": ["Sensors", "Automation", "Materials", "IoT"],
  "Green Materials": ["Recycling", "Bio-based", "Carbon Capture", "Alt Concrete"]
}

/** ======== COMPANY LOGOS (demo via Clearbit) ======== */
const COMPANY_LOGOS: Record<string, string> = {
  NVDA: "https://logo.clearbit.com/nvidia.com",
  NVIDIA: "https://logo.clearbit.com/nvidia.com",
  TSLA: "https://logo.clearbit.com/tesla.com",
  TESLA: "https://logo.clearbit.com/tesla.com",
  GOOGL: "https://logo.clearbit.com/abc.xyz",
  GOOGLE: "https://logo.clearbit.com/google.com",
  AAPL: "https://logo.clearbit.com/apple.com",
  APPLE: "https://logo.clearbit.com/apple.com",
  AMZN: "https://logo.clearbit.com/amazon.com",
  AMAZON: "https://logo.clearbit.com/amazon.com",
  MSFT: "https://logo.clearbit.com/microsoft.com",
  MICROSOFT: "https://logo.clearbit.com/microsoft.com",
}
const logoFor = (t: string) => COMPANY_LOGOS[t?.toUpperCase?.()] || null

/** ======== VERY SOFT BACKGROUND BLOBS ======== */
function SoftBackground() {
  return (
    <div className="absolute inset-0 -z-10 overflow-hidden">
      <div className="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-sky-200/40 blur-3xl" />
      <div className="absolute top-1/3 -right-20 h-96 w-96 rounded-full bg-emerald-200/40 blur-3xl" />
      <div className="absolute bottom-0 left-1/3 h-[28rem] w-[28rem] rounded-full bg-teal-200/40 blur-3xl" />
    </div>
  )
}

/** ======== SMALL HELPERS ======== */
const inputLight = "w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-900 placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-sky-300"

function ProgressBar({ step }: { step: number }) {
  const pct = (step / (steps.length - 1)) * 100
  return (
    <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden mt-4 mb-2">
      <motion.div
        className={`h-full ${GRADIENT_BAR}`}
        style={{ width: `${pct}%` }}
        layout
        transition={{ type: "spring", stiffness: 120, damping: 20 }}
      />
    </div>
  )
}

function Field({ label, children }: { label: string, children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
      {children}
    </div>
  )
}

function Select({ options, value, onChange }: { options: string[], value: string, onChange: (v: any) => void }) {
  return (
    <select className={inputLight} value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Select…</option>
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  )
}

function toggleFrom(list: string[], v: string, setter: (x: string[]) => void) {
  if (list.includes(v)) setter(list.filter(x => x !== v)); else setter([...list, v])
}

/** ======== CLICKABLE CARDS & CHIPS ======== */
function ToggleCard({ label, selected, onClick, icon }: {
  label: string, selected: boolean, onClick: () => void, icon?: React.ReactNode
}) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`flex items-center gap-2 rounded-2xl border px-4 py-3 text-left transition shadow-sm
        ${selected ? "border-sky-400 bg-sky-50" : "border-slate-300 bg-white hover:bg-slate-50"}`}
    >
      {icon}
      <span className="text-slate-800 font-medium">{label}</span>
      {selected && <span className="ml-auto rounded-full bg-sky-100 text-sky-700 px-2 text-xs">Selected</span>}
    </motion.button>
  )
}

function Chip({ label, selected, onClick }: { label: string, selected: boolean, onClick: () => void }) {
  return (
    <motion.button
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`rounded-full border px-3 py-1.5 text-sm transition
        ${selected ? "border-emerald-400 bg-emerald-50 text-emerald-700"
                   : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"}`}
    >
      {label}
    </motion.button>
  )
}

/** ======== SPARKLINE (light) ======== */
function Sparkline({ data, height = 60 }: { data: number[]; height?: number }) {
  const width = 240
  const min = Math.min(...data)
  const max = Math.max(...data)
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width
    const y = height - ((v - min) / (max - min || 1)) * height
    return [x, y]
  })
  const d = points.map((p, i) => (i === 0 ? `M ${p[0]},${p[1]}` : `L ${p[0]},${p[1]}`)).join(" ")
  const change = ((data[data.length - 1] - data[0]) / (data[0] || 1)) * 100
  const positive = change >= 0
  return (
    <div className="flex items-center gap-3">
      <svg width={width} height={height} className="overflow-visible">
        <defs>
          <linearGradient id="lineGradLight" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
        </defs>
        <motion.path
          d={d}
          fill="none"
          stroke="url(#lineGradLight)"
          strokeWidth="2.5"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2 }}
        />
      </svg>
      <div className={`text-sm font-semibold ${positive ? 'text-emerald-600' : 'text-rose-600'}`}>
        {positive ? '▲' : '▼'} {Math.abs(change).toFixed(1)}%
      </div>
    </div>
  )
}

/** ======== RESULT CARD ======== */
function ResultCard({ pick }: { pick: any }) {
  const logo = logoFor(pick.ticker || pick.name)
  const [range, setRange] = useState<'1Y' | '5Y'>('1Y')
  const data = range === '1Y' ? (pick.series1Y || []) : (pick.series5Y || [])

  return (
    <motion.div
      className={`${CARD_BG} rounded-2xl p-5 mb-4 shadow-md`}
      initial={{ opacity: 0, y: 30, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 140, damping: 18 }}
    >
      <div className="flex items-center gap-3 mb-3">
        {logo ? (
          <img src={logo} alt="logo" className="h-8 w-8 rounded-md bg-white object-contain ring-1 ring-slate-200" />
        ) : (
          <div className="h-8 w-8 grid place-items-center rounded-md bg-slate-100">
            <Shield className="text-sky-500" size={18} />
          </div>
        )}
        <div>
          <div className="text-lg font-semibold text-slate-900">{pick.ticker} — {pick.name}</div>
          <div className="text-xs text-slate-600">{pick.thesis}</div>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button
            className={`px-2 py-1 text-xs rounded ${range==='1Y' ? 'bg-sky-100 text-sky-700 ring-1 ring-sky-200' : 'bg-white text-slate-600 ring-1 ring-slate-200'}`}
            onClick={() => setRange('1Y')}
          >1Y</button>
          <button
            className={`px-2 py-1 text-xs rounded ${range==='5Y' ? 'bg-sky-100 text-sky-700 ring-1 ring-sky-200' : 'bg-white text-slate-600 ring-1 ring-slate-200'}`}
            onClick={() => setRange('5Y')}
          >5Y</button>
        </div>
      </div>

      {data?.length ? <Sparkline data={data} /> : <div className="text-slate-500 text-sm">No chart data</div>}

      <div className="grid grid-cols-2 gap-2 mt-4">
        {Object.entries(pick.stats || {}).map(([k, v]) => (
          <div key={k} className="text-xs text-slate-700 bg-slate-50 rounded px-2 py-1 ring-1 ring-slate-200">
            <span className="font-medium">{k}:</span> {v}
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/** ======== MAIN WIZARD (no internal header) ======== */
export default function SmartWealthNeonWizard() {
  const [step, setStep] = useState(0)
  const [name, setName] = useState("")
  const [age, setAge] = useState<number | ''>("")
  const [horizon, setHorizon] = useState("")
  const [risk, setRisk] = useState("")
  const [sectors, setSectors] = useState<string[]>([])
  const [subSectors, setSubSectors] = useState<string[]>([])
  const [goalReturn, setGoalReturn] = useState("")
  const [monthlyContribution, setMonthlyContribution] = useState("")
  const [capital, setCapital] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [picks, setPicks] = useState<any[]>([])

  const availableSubSectors = sectors.flatMap(s => subSectorMap[s] || [])

  const canNext = () => {
    if (step === 1) return name.trim().length > 0 && Number(age) > 0
    if (step === 2) return !!horizon && !!risk
    if (step === 3) return sectors.length > 0
    if (step === 4) return subSectors.length > 0
    if (step === 5) return !!goalReturn || !!monthlyContribution || !!capital
    return true
  }

  // demo series generator (used if API doesn’t return series1Y/series5Y)
  function genSeries(mode: 'up' | 'volatile' = 'up', len = 60) {
    let v = 100, arr: number[] = []
    for (let i = 0; i < len; i++) {
      const drift = mode === 'up' ? 0.35 : (Math.random() * 0.2 - 0.1)
      v += drift + (Math.random() - 0.5) * (mode === 'up' ? 1.0 : 1.8)
      arr.push(Math.max(1, v))
    }
    return arr
  }

  const submit = async () => {
    if (!canNext()) return
    setSubmitting(true)
    const payload = { name, age, horizon, risk, sectors, subSectors, goalReturn, monthlyContribution, capital }
    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      const enriched = (Array.isArray(data) ? data : []).map((p: any, i: number) => ({
        ...p,
        series1Y: p.series1Y || genSeries(i % 2 === 0 ? 'up' : 'volatile', 60),
        series5Y: p.series5Y || genSeries(i % 2 === 0 ? 'up' : 'volatile', 120),
      }))
      setPicks(enriched)
      setStep(6)
    } catch (e) {
      alert("Error fetching picks.")
    } finally {
      setSubmitting(false)
    }
  }

  const next = () => { if (canNext()) setStep(s => Math.min(s + 1, steps.length - 1)) }
  const prev = () => setStep(s => Math.max(s - 1, 0))

  return (
    <div className="relative min-h-[calc(100vh-6rem)] flex items-start justify-center text-slate-900 overflow-hidden">
      <SoftBackground />

      <div className="w-full max-w-2xl mx-auto z-10 px-4 sm:px-0 pt-4">
        <ProgressBar step={step} />
        <motion.div
          key={step}
          className={`${CARD_BG} rounded-3xl shadow-xl px-8 py-10 mt-6`}
          initial={{ opacity: 0, y: 20, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.98 }}
          transition={{ type: "spring", stiffness: 140, damping: 18 }}
        >
          <AnimatePresence mode="wait">
            {step === 0 && (
              <motion.div
                key="welcome"
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -30 }}
                transition={{ duration: 0.35 }}
              >
                <div className="flex flex-col items-center text-center">
                  <Rocket className="text-sky-500 mb-2" size={44} />
                  <h1 className="text-2xl font-bold mb-2">Welcome to SmartWealth</h1>
                  <p className="text-slate-600 mb-4">Answer a few questions. We’ll craft a sector-aware, risk-aligned shortlist of potential multi-baggers.</p>
                  <button
                    className={`mt-4 px-6 py-2 rounded-xl ${BUTTON_GRADIENT} text-white font-semibold shadow-md hover:shadow-lg hover:scale-[1.02] transition`}
                    onClick={next}
                  >
                    Start
                  </button>
                </div>
              </motion.div>
            )}

            {step === 1 && (
              <motion.div key="basics" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><LineChart size={22}/> Basics</h2>
                <Field label="Your Name">
                  <input className={inputLight} value={name} onChange={e=>setName(e.target.value)} placeholder="Name" />
                </Field>
                <Field label="Age">
                  <input className={inputLight} type="number" min={1} value={age} onChange={e=>setAge(Number(e.target.value))} placeholder="Age" />
                </Field>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div key="strategy" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><LineChart size={22}/> Strategy</h2>
                <Field label="Investment Horizon">
                  <Select options={["1 year","3 years","5 years","10+ years"]} value={horizon} onChange={setHorizon} />
                </Field>
                <Field label="Risk Tolerance">
                  <Select options={["Low","Medium","High"]} value={risk} onChange={setRisk} />
                </Field>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div key="sectors" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><LineChart size={22}/> Sectors</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {sectorList.map(sec => (
                    <ToggleCard
                      key={sec}
                      label={sec}
                      selected={sectors.includes(sec)}
                      onClick={() => toggleFrom(sectors, sec, setSectors)}
                      icon={<div className="h-6 w-6 grid place-items-center rounded-lg bg-sky-100 text-sky-600">★</div>}
                    />
                  ))}
                </div>
              </motion.div>
            )}

            {step === 4 && (
              <motion.div key="subsectors" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><LineChart size={22}/> Sub-sectors</h2>
                {sectors.length === 0 ? (
                  <div className="text-slate-600">Pick at least one sector first.</div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {sectors.flatMap(sec =>
                      (subSectorMap[sec] || []).map(ss => (
                        <Chip
                          key={`${sec}-${ss}`}
                          label={ss}
                          selected={subSectors.includes(ss)}
                          onClick={() => toggleFrom(subSectors, ss, setSubSectors)}
                        />
                      ))
                    )}
                  </div>
                )}
              </motion.div>
            )}

            {step === 5 && (
              <motion.div key="goals" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><LineChart size={22}/> Goals</h2>
                <Field label="Target Annual Return (%)">
                  <input className={inputLight} type="number" min={0} value={goalReturn} onChange={e=>setGoalReturn(e.target.value)} placeholder="e.g. 25" />
                </Field>
                <Field label="Monthly Contribution ($)">
                  <input className={inputLight} type="number" min={0} value={monthlyContribution} onChange={e=>setMonthlyContribution(e.target.value)} placeholder="e.g. 500" />
                </Field>
                <Field label="Initial Capital ($)">
                  <input className={inputLight} type="number" min={0} value={capital} onChange={e=>setCapital(e.target.value)} placeholder="e.g. 10000" />
                </Field>
              </motion.div>
            )}

            {step === 6 && (
              <motion.div key="results" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">Results</h2>
                <div className="mb-4 text-slate-700 text-sm">
                  <div><b>Horizon:</b> {horizon}</div>
                  <div><b>Risk:</b> {risk}</div>
                  <div><b>Sectors:</b> {sectors.join(', ')}</div>
                  <div><b>Sub-sectors:</b> {subSectors.join(', ')}</div>
                  <div><b>Goals:</b> {goalReturn && `Return ${goalReturn}%`} {monthlyContribution && `Monthly $${monthlyContribution}`} {capital && `Capital $${capital}`}</div>
                </div>
                <div>
                  {picks.map((p, i) => <ResultCard key={i} pick={p} />)}
                </div>
                <button
                  className={`mt-4 px-6 py-2 rounded-xl ${BUTTON_GRADIENT} text-white font-semibold shadow-md hover:shadow-lg hover:scale-[1.02] transition`}
                  onClick={() => setStep(0)}
                >
                  Restart
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Bottom nav */}
          <div className="flex justify-between mt-8">
            {step > 0 && step < 6 && (
              <button
                className="flex items-center gap-1 px-4 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition ring-1 ring-slate-200"
                onClick={prev}
              >
                <ArrowLeft size={18}/> Back
              </button>
            )}
            {step < 5 && step !== 0 && (
              <button
                className={`flex items-center gap-1 px-6 py-2 rounded-xl font-semibold shadow-md transition
                  ${canNext() ? `${BUTTON_GRADIENT} text-white hover:shadow-lg hover:scale-[1.02]` : "bg-slate-100 text-slate-400 cursor-not-allowed ring-1 ring-slate-200"}
                `}
                onClick={next}
                disabled={!canNext()}
              >
                Next <ChevronRight size={18}/>
              </button>
            )}
            {step === 5 && (
              <button
                className={`flex items-center gap-1 px-6 py-2 rounded-xl font-semibold shadow-md transition
                  ${canNext() && !submitting ? `${BUTTON_GRADIENT} text-white hover:shadow-lg hover:scale-[1.02]` : "bg-slate-100 text-slate-400 cursor-not-allowed ring-1 ring-slate-200"}
                `}
                onClick={submit}
                disabled={!canNext() || submitting}
              >
                {submitting ? "Loading..." : <>Show my picks <ChevronRight size={18}/></>}
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
