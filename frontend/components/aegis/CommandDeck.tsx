"use client"
import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { springs } from "@/lib/motion-tokens"
import { toggleTheme, Theme } from "@/hooks/use-theme"

export default function CommandDeck(){
  const [open,setOpen]=useState(false)
  const [q,setQ]=useState("")
  useEffect(()=>{
    const h=(e:KeyboardEvent)=>{
      if((e.metaKey||e.ctrlKey) && e.key.toLowerCase()==="k"){ e.preventDefault(); setOpen(v=>!v)}
      if((e.metaKey||e.ctrlKey) && e.key==="Enter"){ window.dispatchEvent(new CustomEvent("aegis:scan"))}
      if(e.key==="Escape") setOpen(false)
    }
    window.addEventListener("keydown",h); return()=>window.removeEventListener("keydown",h)
  },[])
  useEffect(()=>{ document.body.style.overflow=open?"hidden":""; return()=>{document.body.style.overflow=""}},[open])
  const items=[
    {id:"scan", label:"Scan now", action:()=>{ setOpen(false); window.dispatchEvent(new CustomEvent("aegis:scan"))}},
    {id:"theme", label:"Toggle theme (Obsidian / Paper / Void)", action:()=>{
      const cur=(document.documentElement.getAttribute("data-theme") as Theme)||"obsidian"
      const next:Theme=cur==="obsidian"?"paper":cur==="paper"?"void":"obsidian"
      toggleTheme(next); setOpen(false)
    }},
    {id:"health", label:"Go to Health", action:()=>{ window.location.href="/health"}},
  ].filter(i=>i.label.toLowerCase().includes(q.toLowerCase()))

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div key="bd" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} onClick={()=>setOpen(false)} className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm" />
          <motion.div key="card" initial={{opacity:0,y:12,scale:0.98}} animate={{opacity:1,y:0,scale:1}} exit={{opacity:0,y:8,scale:0.98}} transition={springs.gentle}
            className="fixed left-1/2 top-[22%] -translate-x-1/2 z-50 w-[min(560px,92vw)] rounded-lg bg-panel border border-line shadow-[0_20px_60px_rgba(0,0,0,0.45)] overflow-hidden">
            <div className="p-4 border-b border-line">
              <div className="mono text-[11px] tracking-[0.16em] text-brass mb-2">AEGIS COMMAND — type to jump</div>
              <input autoFocus value={q} onChange={e=>setQ(e.target.value)} placeholder="Type a command…"
                className="w-full h-11 px-3 rounded-md bg-inset border border-line mono text-sm text-cream placeholder:text-sage/50 focus:outline-none focus:border-line-strong" />
            </div>
            <div className="p-2">
              {items.map(it=>(
                <button key={it.id} onClick={it.action} className="w-full text-left px-3 py-3 rounded-md hover:bg-inset mono text-sm text-cream flex justify-between">
                  <span>{it.label}</span><span className="text-sage">↵</span>
                </button>
              ))}
              {items.length===0 && <div className="mono text-sm text-sage p-3">No commands matched.</div>}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
