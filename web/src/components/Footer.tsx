import React from "react";

export default function Footer() {
  return (
    <footer
      role="contentinfo"
      className="fixed bottom-0 left-0 right-0 z-40"
      aria-label="Disclaimer"
    >
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800" />
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6">
          <div className="h-10 flex items-center justify-center">
            <p className="text-[12px] text-slate-200/90 text-center">
              Educational only — not investment advice. Markets are volatile; use multiple sources and consider professional
              guidance before investing.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
