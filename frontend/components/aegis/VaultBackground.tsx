"use client"
import { useEffect } from "react"
export default function VaultBackground(){
  useEffect(()=>{
    const h=(e:MouseEvent)=>{
      document.documentElement.style.setProperty("--mx", e.clientX+"px")
      document.documentElement.style.setProperty("--my", e.clientY+"px")
    }
    window.addEventListener("mousemove",h)
    return()=>window.removeEventListener("mousemove",h)
  },[])
  return (
    <div className="fixed inset-0 -z-10 pointer-events-none bg-[var(--bg)] overflow-hidden">
      <svg width="100%" height="100%" className="absolute inset-0 opacity-[0.07]">
        <defs>
          <pattern id="vault-grid" width="48" height="48" patternUnits="userSpaceOnUse">
            <path d="M48 0H0V48" fill="none" stroke="#D4AF37" strokeWidth="0.5"/>
          </pattern>
          <filter id="vault-noise"><feTurbulence baseFrequency="0.9" numOctaves="3" seed="2"/><feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.08 0"/></filter>
        </defs>
        <g stroke="#D4AF37" fill="none" strokeWidth="0.6" opacity="0.4">
          <path d="M-100 200 Q 400 100 800 250 T 1600 200" />
          <path d="M-100 320 Q 500 280 900 380 T 1600 320" />
          <path d="M-100 440 Q 600 400 1000 500 T 1600 440" />
        </g>
        <rect width="100%" height="100%" fill="url(#vault-grid)" />
        <rect width="100%" height="100%" filter="url(#vault-noise)" />
      </svg>
      <div className="absolute inset-0" style={{background:`radial-gradient(700px circle at var(--mx,50%) var(--my,32%), var(--cursor-color, rgba(212,175,55,0.06)), transparent 65%)`}}/>
      <div className="absolute inset-0" style={{background:`radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,0.62) 100%)`}}/>
    </div>
  )
}
