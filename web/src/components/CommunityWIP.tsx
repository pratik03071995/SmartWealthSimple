import React from "react";
import { motion } from "framer-motion";
import { Hammer, MessagesSquare } from "lucide-react";

const CARD = "bg-white border border-slate-200 rounded-3xl shadow-xl";

export default function CommunityWIP() {
  return (
    <div className="min-h-[calc(100vh-64px)] flex items-start justify-center pb-16">
      <div className="w-full max-w-3xl px-4 sm:px-6 mt-8">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className={`${CARD} p-8`}
        >
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-slate-100 grid place-items-center ring-1 ring-slate-200">
              <MessagesSquare size={18} className="text-slate-700" />
            </div>
            <div className="text-xl font-semibold text-slate-900">
              Community (Boardroom)
            </div>
          </div>

          <div className="mt-4 text-slate-700">
            Real-time chat rooms, threads, and community boards are{" "}
            <b>on the roadmap</b>.
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-sky-50 ring-1 ring-sky-200 p-4">
              <div className="text-sm font-medium text-sky-800">
                What’s coming
              </div>
              <ul className="mt-2 text-sm text-sky-900 list-disc pl-5 space-y-1">
                <li>Sectors & ticker-specific channels</li>
                <li>Threaded discussions, reactions</li>
                <li>Polls, AMAs, and “analyst notes”</li>
              </ul>
            </div>
            <div className="rounded-2xl bg-amber-50 ring-1 ring-amber-200 p-4">
              <div className="text-sm font-medium text-amber-800">
                Status
              </div>
              <div className="mt-2 text-sm text-amber-900 flex items-center gap-2">
                <Hammer size={16} /> Work in progress — coming soon!
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
