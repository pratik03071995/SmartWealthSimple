import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles, Rocket, LineChart, ChevronRight, ArrowLeft,
  Shield, Github
} from 'lucide-react'

const steps = [
  "Welcome", "Basics", "Strategy", "Sectors", "Sub-sectors", "Goals", "Results"
]

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

const neonGradients = [
  "bg-gradient-to-br from-[#00ffe7] via-[#1e3a8a] to-[#7f5af0]",
  "bg-gradient-to-tr from-[#ff00c8] via-[#7f5af0] to-[#00ffe7]",
  "bg-gradient-to-bl from-[#7f5af0] via-[#00ffe7] to-[#ff00c8]"
]

function useParallaxBlobs(blobCount: number) {
  const [positions, setPositions] = useState(Array(blobCount).fill({x:0, y:0}))
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const { innerWidth, innerHeight } = window
      const mx = e.clientX / innerWidth - 0.5
      const my = e.clientY / innerHeight - 0.5
      setPositions([
        { x: mx * 40, y: my * 40 },
        { x: mx * -30, y: my * 30 },
        { x: mx * 60, y: my * -60 }
      ])
    }
    window.addEventListener('mousemove', handler)
    return () => window.removeEventListener('mousemove', handler)
  }, [])
  return positions
}

function Starfield({ count = 60 }) {
  const [stars, setStars] = useState<{x:number,y:number,opacity:number}[]>([])
  useEffect(() => {
    setStars(Array(count).fill(0).map(() => ({
      x: Math.random()*100,
      y: Math.random()*100,
      opacity: Math.random()*0.5+0.5
    })))
  }, [count])
  return (
    <div className="absolute inset-0 pointer-events-none z-0">
      {stars.map((s,i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: s.opacity }}
          transition={{ duration: 2, repeat: Infinity, repeatType: "reverse", delay: i*0.05 }}
          style={{
            position: 'absolute',
            left: `${s.x}%`,
            top: `${s.y}%`,
            width: 2,
            height: 2,
            borderRadius: 9999,
            background: 'white',
            boxShadow: '0 0 8px #00ffe7'
          }}
        />
      ))}
    </div>
  )
}

function ProgressBar({ step }: { step: number }) {
  return (
    <motion.div
      className="h-2 w-full bg-white/10 rounded-full overflow-hidden mt-4 mb-2"
      initial={false}
    >
      <motion.div
        className="h-full bg-gradient-to-r from-[#00ffe7] via-[#7f5af0] to-[#ff00c8]"
        style={{ width: `${(step/(steps.length-1))*100}%` }}
        layout
        transition={{ type: "spring", stiffness: 120, damping: 20 }}
      />
    </motion.div>
  )
}

function Field({ label, children }: { label: string, children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-white/80 mb-1">{label}</label>
      {children}
    </div>
  )
}

function Select({ options, value, onChange, multiple=false }: {
  options: string[], value: string|string[], onChange: (v:any)=>void, multiple?: boolean
}) {
  return (
    <select
      className="input w-full"
      value={multiple ? undefined : value}
      multiple={multiple}
      onChange={e => {
        if (multiple) {
          const vals = Array.from(e.target.selectedOptions).map(o=>o.value)
          onChange(vals)
        } else {
          onChange(e.target.value)
        }
      }}
    >
      {!multiple && <option value="">Select...</option>}
      {options.map(opt => (
        <option key={opt} value={opt}>{opt}</option>
      ))}
    </select>
  )
}

function ResultCard({ pick }: { pick: any }) {
  return (
    <motion.div
      className="bg-white/10 border border-white/15 rounded-2xl p-5 mb-4 shadow-lg backdrop-blur-lg"
      initial={{ opacity: 0, y: 40, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 120, damping: 18 }}
    >
      <div className="flex items-center gap-3 mb-2">
        <Shield className="text-[#00ffe7]" size={28} />
        <div>
          <div className="text-lg font-bold text-white">{pick.ticker} — {pick.name}</div>
          <div className="text-xs text-white/60">{pick.thesis}</div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mt-2">
        {Object.entries(pick.stats).map(([k,v])=>(
          <div key={k} className="text-xs text-white/80 bg-white/5 rounded px-2 py-1">
            <span className="font-semibold">{k}:</span> {v}
          </div>
        ))}
      </div>
    </motion.div>
  )
}

function AnimatedBackground() {
  const positions = useParallaxBlobs(3)
  return (
    <div className="absolute inset-0 -z-10 overflow-hidden">
      {positions.map((pos, i) => (
        <motion.div
          key={i}
          className={`absolute w-[480px] h-[480px] ${neonGradients[i]} opacity-40 blur-3xl`}
          style={{
            left: `${20 + i*30}%`,
            top: `${10 + i*25}%`,
            borderRadius: '50%',
            filter: 'blur(80px)'
          }}
          animate={{
            x: pos.x,
            y: pos.y,
            scale: 1 + Math.sin(Date.now()/1000 + i)*0.03
          }}
          transition={{ type: "spring", stiffness: 40, damping: 20 }}
        />
      ))}
      <Starfield count={60} />
    </div>
  )
}

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

  // Step validation
  const canNext = () => {
    if (step === 1) return name.trim().length > 0 && Number(age) > 0
    if (step === 2) return horizon && risk
    if (step === 3) return sectors.length > 0
    if (step === 4) return subSectors.length > 0
    if (step === 5) return goalReturn || monthlyContribution || capital
    return true
  }

  const next = () => {
    if (step < steps.length-1) setStep(s => s+1)
  }
  const prev = () => {
    if (step > 0) setStep(s => s-1)
  }

  const submit = async () => {
    setSubmitting(true)
    const payload = {
      name, age, horizon, risk, sectors, subSectors, goalReturn, monthlyContribution, capital
    }
    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      setPicks(data)
      setStep(6)
    } catch (e) {
      alert("Error fetching picks.")
    } finally {
      setSubmitting(false)
    }
  }

  // Sub-sector options for selected sectors
  const availableSubSectors = sectors.flatMap(s => subSectorMap[s] || [])

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#0a0a23] text-white overflow-hidden">
      <AnimatedBackground />
      <div className="absolute top-0 left-0 w-full px-6 pt-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <Sparkles className="text-[#00ffe7]" size={32} />
          <span className="font-bold text-xl tracking-wide bg-gradient-to-r from-[#00ffe7] via-[#7f5af0] to-[#ff00c8] bg-clip-text text-transparent">SmartWealth AI</span>
          <span className="ml-3 px-2 py-0.5 rounded bg-white/10 text-xs text-white/60 border border-white/15 backdrop-blur">Educational only</span>
        </div>
        <a href="https://github.com/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-white/40 hover:text-[#00ffe7] transition">
          <Github size={20} /> <span className="text-xs">GitHub</span>
        </a>
      </div>
      <div className="w-full max-w-xl mx-auto z-10">
        <ProgressBar step={step} />
        <motion.div
          className="bg-white/5 border border-white/15 rounded-3xl shadow-2xl backdrop-blur-lg px-8 py-10 mt-8"
          initial={{ opacity: 0, y: 40, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 120, damping: 18 }}
        >
          <AnimatePresence mode="wait">
            {step === 0 && (
              <motion.div
                key="welcome"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <div className="flex flex-col items-center">
                  <Rocket className="text-[#ff00c8] mb-2" size={48} />
                  <h1 className="text-2xl font-bold mb-2">Welcome to SmartWealth Neon Wizard</h1>
                  <p className="text-white/70 mb-4 text-center">Get personalized stock picks powered by AI. Your info is private and never stored.</p>
                  <button
                    className="mt-4 px-6 py-2 rounded-xl bg-gradient-to-r from-[#00ffe7] to-[#ff00c8] text-white font-semibold shadow-lg hover:scale-105 transition"
                    onClick={next}
                  >
                    Start
                  </button>
                </div>
              </motion.div>
            )}
            {step === 1 && (
              <motion.div
                key="basics"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><LineChart size={24}/> Basics</h2>
                <Field label="Your Name">
                  <input className="input w-full" value={name} onChange={e=>setName(e.target.value)} placeholder="Name" />
                </Field>
                <Field label="Age">
                  <input className="input w-full" type="number" min={1} value={age} onChange={e=>setAge(Number(e.target.value))} placeholder="Age" />
                </Field>
              </motion.div>
            )}
            {step === 2 && (
              <motion.div
                key="strategy"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><Shield size={24}/> Strategy</h2>
                <Field label="Investment Horizon">
                  <Select options={["1 year","3 years","5 years","10+ years"]} value={horizon} onChange={setHorizon} />
                </Field>
                <Field label="Risk Tolerance">
                  <Select options={["Low","Medium","High"]} value={risk} onChange={setRisk} />
                </Field>
              </motion.div>
            )}
            {step === 3 && (
              <motion.div
                key="sectors"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><LineChart size={24}/> Sectors</h2>
                <Field label="Select Sectors">
                  <Select options={sectorList} value={sectors} onChange={setSectors} multiple />
                </Field>
              </motion.div>
            )}
            {step === 4 && (
              <motion.div
                key="subsectors"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><LineChart size={24}/> Sub-sectors</h2>
                <Field label="Select Sub-sectors">
                  <Select options={availableSubSectors} value={subSectors} onChange={setSubSectors} multiple />
                </Field>
              </motion.div>
            )}
            {step === 5 && (
              <motion.div
                key="goals"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><LineChart size={24}/> Goals</h2>
                <Field label="Target Annual Return (%)">
                  <input className="input w-full" type="number" min={0} value={goalReturn} onChange={e=>setGoalReturn(e.target.value)} placeholder="e.g. 12" />
                </Field>
                <Field label="Monthly Contribution ($)">
                  <input className="input w-full" type="number" min={0} value={monthlyContribution} onChange={e=>setMonthlyContribution(e.target.value)} placeholder="e.g. 500" />
                </Field>
                <Field label="Initial Capital ($)">
                  <input className="input w-full" type="number" min={0} value={capital} onChange={e=>setCapital(e.target.value)} placeholder="e.g. 10000" />
                </Field>
              </motion.div>
            )}
            {step === 6 && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><Sparkles size={24}/> Results</h2>
                <div className="mb-4 text-white/80 text-sm">
                  <div><b>Horizon:</b> {horizon}</div>
                  <div><b>Risk:</b> {risk}</div>
                  <div><b>Sectors:</b> {sectors.join(', ')}</div>
                  <div><b>Sub-sectors:</b> {subSectors.join(', ')}</div>
                  <div><b>Goals:</b> {goalReturn && `Return ${goalReturn}%`} {monthlyContribution && `Monthly $${monthlyContribution}`} {capital && `Capital $${capital}`}</div>
                </div>
                <div>
                  {picks.map((pick, i) => <ResultCard key={i} pick={pick} />)}
                </div>
                <button
                  className="mt-4 px-6 py-2 rounded-xl bg-gradient-to-r from-[#00ffe7] to-[#ff00c8] text-white font-semibold shadow-lg hover:scale-105 transition"
                  onClick={()=>setStep(0)}
                >
                  Restart
                </button>
              </motion.div>
            )}
          </AnimatePresence>
          <div className="flex justify-between mt-8">
            {step > 0 && step < 6 && (
              <button
                className="flex items-center gap-1 px-4 py-2 rounded-xl bg-white/10 text-white/70 hover:bg-white/20 transition"
                onClick={prev}
              >
                <ArrowLeft size={18}/> Back
              </button>
            )}
            {step < 5 && (
              <button
                className={`flex items-center gap-1 px-6 py-2 rounded-xl font-semibold shadow-lg transition
                  ${canNext() ? "bg-gradient-to-r from-[#00ffe7] to-[#ff00c8] text-white hover:scale-105" : "bg-white/10 text-white/40 cursor-not-allowed"}
                `}
                onClick={next}
                disabled={!canNext()}
              >
                Next <ChevronRight size={18}/>
              </button>
            )}
            {step === 5 && (
              <button
                className={`flex items-center gap-1 px-6 py-2 rounded-xl font-semibold shadow-lg transition
                  ${canNext() && !submitting ? "bg-gradient-to-r from-[#00ffe7] to-[#ff00c8] text-white hover:scale-105" : "bg-white/10 text-white/40 cursor-not-allowed"}
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
