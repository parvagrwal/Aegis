"use client"
import { motion, AnimatePresence } from "motion/react"
import { springs } from "@/lib/motion-tokens"
import { Verdict } from "@/lib/types"
import { useEffect } from "react"

export default function VerdictMonolith({verdict, confidence}:{verdict:Verdict, confidence:number}){
  const key=verdict+confidence
  useEffect(()=>{
    if(verdict==="malicious"){
      try{
        const ctx=new (window.AudioContext||(window as any).webkitAudioContext)()
        const o=ctx.createOscillator(); const g=ctx.createGain()
        o.frequency.value=880; o.connect(g); g.connect(ctx.destination)
        g.gain.setValueAtTime(0.12, ctx.currentTime); g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime+0.12)
        o.start(); o.stop(ctx.currentTime+0.12)
      }catch{}
    }
  },[verdict])

  const isMal=verdict==="malicious"
  const isBen=verdict==="benign"

  return (
    <AnimatePresence mode="wait">
      <motion.div key={key}
        initial={{opacity:0, filter:"blur(8px)", scale:0.92}}
        animate={{opacity:1, filter:"blur(0px)", scale:1}}
        exit={{opacity:0, scale:0.96}}
        transition={springs.gentle}
        className={`relative overflow-hidden rounded-lg border h-[96px] px-5 flex items-center justify-between
          ${isMal?"bg-pink text-white border-pink shadow-[0_0_28px_rgba(255,26,94,0.35)]": isBen?"bg-transparent text-sage border-sage/30":"bg-brass text-black border-brass shadow-[0_0_20px_rgba(212,175,55,0.28)]"}`}>
        {isMal && <motion.div initial={{opacity:0.5}} animate={{opacity:0}} transition={{duration:0.45}} className="absolute inset-0 bg-white/20 pointer-events-none"/>}
        <motion.div animate={isMal?{x:[0,-2.5,2,-1.5,0]}:{x:0}} transition={{duration:0.32, delay:0.04}} className="flex items-baseline gap-4">
          <span className="font-display font-[700] tracking-[-0.04em] text-[44px] md:text-[52px] leading-none">{verdict.toUpperCase()}</span>
          <span className={`w-2.5 h-2.5 rounded-full ${isMal?"bg-white animate-pulse":isBen?"bg-sage":"bg-black/70"}`}/>
        </motion.div>
        <div className="text-right">
          <div className="mono font-black text-[18px] leading-none">{confidence.toFixed(1)}%</div>
          <div className="mono text-[11px] tracking-[0.14em] opacity-70 mt-1">{isMal?"HIGH":isBen?"LOW":"MED"}</div>
        </div>
        {isBen && (
          <div className="absolute inset-0 pointer-events-none">
            {Array.from({length:22}).map((_,i)=>{
              const ang=(i/22)*Math.PI*2
              const dist=70+((i*37)%60)
              const size=i%3===0?"w-3 h-3":i%3===1?"w-2 h-2":"w-1.5 h-1.5"
              return (
                <motion.span key={i}
                  initial={{x:140, y:48, opacity:1, scale:1}}
                  animate={{x:140+Math.cos(ang)*dist, y:48+Math.sin(ang)*dist*0.55, opacity:0, scale:0.2}}
                  transition={{duration:0.9+((i*13)%40)/100, delay:0.15}}
                  className={`absolute ${size} bg-brass rounded-full shadow-[0_0_6px_rgba(212,175,55,0.8)]`}/>
              )
            })}
            {/* expanding shockwave ring */}
            <motion.span className="absolute rounded-full border-2 border-brass"
              initial={{left:136, top:44, width:8, height:8, opacity:0.9}}
              animate={{left:30, top:-12, width:220, height:120, opacity:0}}
              transition={{duration:0.8, delay:0.1, ease:"easeOut"}}/>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}
