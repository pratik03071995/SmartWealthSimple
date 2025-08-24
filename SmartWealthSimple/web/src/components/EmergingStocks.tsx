import React, { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ChevronRight } from "lucide-react";

const CARD = "bg-white border border-slate-200 rounded-3xl shadow-xl";

const SECTORS = [
  "Semiconductors",
  "AI & Cloud",
  "Biotech",
  "Fintech",
  "Clean Energy",
  "Cybersecurity",
  "E-commerce",
  "Industrial Automation",
];

const DUMMY: Record<string, string[]> = {
  Semiconductors: ["NVDA", "AMD", "AVGO", "TSM", "ASML", "MU", "ON", "PLAB", "SMCI", "ARM"],
  "AI & Cloud": ["MSFT", "GOOGL", "AMZN", "DDOG", "SNOW", "MDB", "PLTR", "NET", "CRWD", "ZS"],
  Biotech: ["VRTX", "REGN", "ILMN", "EXAS", "SGEN", "MRNA", "BNTX", "DNA", "DVAX", "CRSP"],
  Fintech: ["SQ", "PYPL", "SOFI", "AXP", "MA", "V", "NU", "ADYEY", "FIS", "FICO"],
  "Clean Energy": ["ENPH", "FSLR", "TSLA", "PLUG", "BE", "RUN", "NEE", "SEDG", "ALB", "BLDP"],
  Cybersecurity: ["PANW", "CRWD", "ZS", "S", "OKTA", "FTNT", "TENB", "CYBR", "SPLK", "VRNS"],
  "E-commerce": ["AMZN", "MELI", "SHOP", "ETSY", "SE", "PDD", "CPNG", "EBAY", "W", "GLBE"],
  "Industrial Automation": ["ISRG", "ROK", "ETN", "PH", "IR", "CGNX", "FANUY", "ABB", "ROK", "KEYS"],
};

export default function EmergingStocks() {
  const [sector, setSector] = useState<string>(SECTORS[0]);
  const [topN, setTopN] = useState<5 | 10>(5);

  const picks = useMemo(() => (DUMMY[sector] || []).slice(0, topN), [sector, topN]);

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-start justify-center pb-16">
      <div className="w-full max-w-5xl px-4 sm:px-6 mt-8">
        {/* Header card */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className={`${CARD} p-6 mb-4`}
        >
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-slate-100 grid place-items-center ring-1 ring-slate-200">
              <Sparkles size={18} className="text-slate-700" />
            </div>
            <div>
              <div className="text-xl font-semibold text-slate-900">Top Emerging Stocks</div>
              <div className="text-sm text-slate-600">
                Pick a sector and we’ll show a <b>dummy short-list</b> (real model coming soon).
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <select
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              className="h-10 px-3 rounded-xl bg-white ring-1 ring-slate-200 text-slate-800"
            >
              {SECTORS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>

            <div className="flex items-center gap-2 rounded-xl ring-1 ring-slate-200 bg-slate-50 p-1">
              {[5, 10].map((n) => (
                <button
                  key={n}
                  onClick={() => setTopN(n as 5 | 10)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition ${
                    topN === n
                      ? "bg-white text-slate-900 ring-1 ring-slate-200"
                      : "text-slate-700 hover:text-slate-900"
                  }`}
                >
                  Top {n}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Picks grid */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          <AnimatePresence>
            {picks.map((tkr, i) => (
              <motion.div
                key={tkr}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ delay: i * 0.03 }}
                className={`${CARD} p-4`}
              >
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-xl bg-sky-100 text-sky-800 grid place-items-center ring-1 ring-sky-200 font-semibold">
                    {tkr}
                  </div>
                  <div className="font-semibold text-slate-900">{tkr}</div>
                </div>
                <div className="mt-2 text-sm text-slate-600">
                  Snapshot, thesis and key metrics coming soon.
                </div>
                <div className="mt-3">
                  <button className="text-sm text-slate-700 hover:text-slate-900 inline-flex items-center gap-1">
                    View thesis <ChevronRight size={14} />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
