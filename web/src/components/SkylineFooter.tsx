import React from "react";
import { Info, Link as LinkIcon, Instagram, Twitter, Facebook, Youtube } from "lucide-react";

const CARD =
  "bg-white/80 backdrop-blur ring-1 ring-slate-200 rounded-2xl shadow-xl";

export default function SkylineFooter() {
  return (
    <section className="w-full">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 mt-8 mb-28">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* About */}
          <div className={`${CARD} p-4`}>
            <div className="flex items-center gap-2 text-slate-800 font-semibold">
              <Info size={16} /> About SmartWealth
            </div>
            <p className="mt-2 text-sm text-slate-700">
              We’re building an AI-assisted research companion to help you learn,
              screen, and track potential multi-baggers—responsibly. Signals,
              not hype. Education first.
            </p>
            <p className="mt-3 text-xs text-slate-500">
              <span className="font-medium">Note:</span> This app is educational
              only, not investment advice.
            </p>
          </div>

          {/* Quick links */}
          <div className={`${CARD} p-4`}>
            <div className="flex items-center gap-2 text-slate-800 font-semibold">
              <LinkIcon size={16} /> Quick links
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <a href="/" className="px-3 py-2 rounded-xl ring-1 ring-slate-200 bg-slate-50 text-sm text-slate-800 hover:bg-white transition">Advisor</a>
              <a href="/earnings" className="px-3 py-2 rounded-xl ring-1 ring-slate-200 bg-slate-50 text-sm text-slate-800 hover:bg-white transition">Earnings</a>
              <a href="/learn" className="px-3 py-2 rounded-xl ring-1 ring-slate-200 bg-slate-50 text-sm text-slate-800 hover:bg-white transition col-span-2">
                Learn — fundamentals, risk & valuation
              </a>
            </div>
          </div>

          {/* Social */}
          <div className={`${CARD} p-4`}>
            <div className="flex items-center gap-2 text-slate-800 font-semibold">
              <LinkIcon size={16} /> Follow us
            </div>
            <p className="mt-2 text-sm text-slate-700">
              Placeholders for now—links coming soon.
            </p>
            <div className="mt-3 flex items-center gap-2">
              <button className="h-9 w-9 rounded-xl ring-1 ring-slate-200 grid place-items-center hover:bg-slate-50 transition" aria-label="Instagram">
                <Instagram size={16} />
              </button>
              <button className="h-9 w-9 rounded-xl ring-1 ring-slate-200 grid place-items-center hover:bg-slate-50 transition" aria-label="Twitter / X">
                <Twitter size={16} />
              </button>
              <button className="h-9 w-9 rounded-xl ring-1 ring-slate-200 grid place-items-center hover:bg-slate-50 transition" aria-label="Facebook">
                <Facebook size={16} />
              </button>
              <button className="h-9 w-9 rounded-xl ring-1 ring-slate-200 grid place-items-center hover:bg-slate-50 transition" aria-label="YouTube">
                <Youtube size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
