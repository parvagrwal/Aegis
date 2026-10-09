"use client"
import { useEffect, useState } from "react"
import { TickerEvent } from "@/lib/types"

/**
 * Replays the real eval dataset as a live-ish feed.
 * There is no WebSocket backend (backend/aegis/api/ws.py is an empty
 * placeholder), so the board streams the 373 real runnable cases in block
 * order, one every `intervalMs`, looping. Pauses when the tab is hidden.
 * The UI labels this REPLAY — it never pretends to be a live chain feed.
 */
export function useReplayFeed(intervalMs = 2400){
  const [events, setEvents] = useState<TickerEvent[]>([])
  const [live, setLive] = useState(false)

  useEffect(()=>{
    let id: ReturnType<typeof setInterval> | undefined
    let cancelled = false
    fetch("/api/v1/feed")
      .then(r=>r.json())
      .then(d=>{
        if(cancelled) return
        const all: TickerEvent[] = d.events || []
        if(all.length===0) return
        let i = 0
        const push = ()=> setEvents(prev => [all[i++ % all.length], ...prev].slice(0,20))
        push()
        setLive(true)
        id = setInterval(()=>{ if(!document.hidden) push() }, intervalMs)
      })
      .catch(()=>{ /* feed unavailable — board shows awaiting state */ })
    return ()=>{ cancelled = true; if(id) clearInterval(id) }
  },[intervalMs])

  return { events, live }
}
