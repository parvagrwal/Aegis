"use client"
import ShieldOptic from "./ShieldOptic"
import { toggleTheme, Theme } from "@/hooks/use-theme"
import { useEffect, useState } from "react"
export default function Header(){
  const [theme,setTheme]=useState<Theme>("obsidian")
  const [scanning,setScanning]=useState(false)
  useEffect(()=>{ const t=localStorage.getItem("aegis-theme") as Theme; if(t){ setTheme(t); document.documentElement.setAttribute("data-theme",t)} },[])
  useEffect(()=>{
    const h=(e:any)=> setScanning(Boolean(e.detail))
    window.addEventListener("aegis:scanning" as any, h)
    return ()=> window.removeEventListener("aegis:scanning" as any, h)
  },[])
  const next:Theme=theme==="obsidian"?"paper":theme==="paper"?"void":"obsidian"
  return (
    <header className="sticky top-0 z-40 bg-[var(--inset)]/85 backdrop-blur-xl border-b border-line">
      <div className="mx-auto max-w-[1280px] px-4 md:px-6 h-[64px] flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <ShieldOptic size={44} scanning={scanning}/>
          <span className="font-display font-[700] tracking-[0.16em] text-brass text-[16px]">AEGIS</span>
          <span className="hidden sm:inline mono text-[11px] tracking-[0.18em] text-sage">COMMAND DECK</span>
        </div>
        <nav className="flex items-center gap-5 mono text-[13px]">
          <a href="/" className="text-sage hover:text-cream">Dashboard</a>
          <a href="/health" className="text-sage hover:text-cream">Health</a>
          <button onClick={()=>{toggleTheme(next); setTheme(next)}} className="h-8 px-3 rounded-md border border-line bg-panel text-cream text-xs tracking-widest hover:bg-panel-raised">
            THEME: {theme.toUpperCase()}
          </button>
        </nav>
      </div>
    </header>
  )
}
