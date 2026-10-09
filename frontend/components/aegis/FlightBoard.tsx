"use client"
import { motion, AnimatePresence } from "motion/react"
import { useReplayFeed } from "@/hooks/use-replay-feed"

/**
 * FlightBoard — split-flap style live board.
 * There is no WebSocket backend, so this replays the 373 real runnable eval
 * cases via useReplayFeed. Labeled REPLAY — never presented as a live chain.
 */
export default function FlightBoard({onPick}:{onPick:(h:string)=>void}){
  const { events, live } = useReplayFeed()

  return (
    <div className="card bg-inset border border-line overflow-hidden">
      <div className="h-9 px-3 flex items-center justify-between border-b border-line bg-panel/50">
        <span className="mono text-[11px] tracking-[0.16em] text-brass flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${live?"bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]":"bg-zinc-500"}`}/>FLIGHT BOARD
        </span>
        <span className="mono text-xs text-sage">replay · {events.length}</span>
      </div>

      {/* infinite flight strip */}
      <div className="relative h-10 overflow-hidden border-b border-line bg-panel/30 group">
        {events.length>0 ? (
          <div className="flight-track absolute inset-y-0 flex items-center gap-2 whitespace-nowrap animate-[flight_28s_linear_infinite] group-hover:[animation-play-state:paused] will-change-transform">
            {[...events, ...events].map((e,i)=>(
              <button key={i+e.hash} onClick={()=>onPick(e.hash)}
                className={`shrink-0 px-3 py-1 rounded-sm border mono text-xs tracking-wide ${e.verdict==="malicious"?"bg-pink/10 text-pink border-pink/25":e.verdict==="uncertain"?"bg-brass/10 text-brass border-brass/20":"bg-transparent text-sage border-line"}`}>
                {e.hash.slice(0,6)}…{e.hash.slice(-4)} · {e.verdict}
              </button>
            ))}
          </div>
        ): <div className="h-full grid place-items-center mono text-xs text-sage">awaiting feed…</div>}
      </div>

      <div className="divide-y divide-line/60">
        <AnimatePresence mode="popLayout" initial={false}>
          {events.slice(0,6).map(e=>(
            <motion.button key={e.hash} layout
              initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} exit={{opacity:0,y:-8}}
              onClick={()=>onPick(e.hash)}
              className="w-full h-12 px-3 grid grid-cols-[1fr_auto] items-center hover:bg-panel-raised text-left">
              <span className="mono text-xs text-cream">{e.hash.slice(0,6)}...{e.hash.slice(-4)}</span>
              <span className={`mono text-[11px] px-2 py-1 rounded-full font-bold ${e.verdict==="malicious"?"bg-pink text-white":"bg-brass text-black"}`}>{Math.round(e.confidence)}%</span>
            </motion.button>
          ))}
        </AnimatePresence>
        {events.length===0 && <div className="mono text-xs text-sage p-4">awaiting first scan…</div>}
      </div>
      <style>{`@keyframes flight{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}`}</style>
    </div>
  )
}
