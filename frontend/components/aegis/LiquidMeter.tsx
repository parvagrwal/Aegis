"use client"
import { motion } from "motion/react"
export default function LiquidMeter({value}:{value:number}){
  const color=value>70?"#FF1A5E":value>40?"#D4AF37":"#10B981"
  const glow=value>70?"0 0 16px rgba(255,26,94,0.35)":value>40?"0 0 14px rgba(212,175,55,0.28)":"0 0 12px rgba(16,185,129,0.25)"
  return (
    <div className="space-y-2">
      <div className="flex justify-between mono text-[11px] tracking-widest text-sage"><span>0%</span><span className="text-cream font-bold">{value.toFixed(1)}% RISK</span><span>100%</span></div>
      <div className="h-[10px] rounded-full bg-inset border border-line overflow-hidden relative">
        <div className="absolute inset-0 rounded-full" style={{boxShadow:"inset 0 1px 0 rgba(255,255,255,0.06)"}}/>
        <motion.div initial={{width:0}} animate={{width:`${value}%`}} transition={{type:"spring", stiffness:220, damping:26}}
          className="h-full relative rounded-full" style={{background:color, boxShadow:glow}}>
          <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 12">
            <motion.path d="M0 6 Q 12 0 24 6 T 48 6 T 72 6 T 100 6 V12 H0 Z" fill="white" opacity="0.18"
              animate={{d:["M0 6 Q 12 0 24 6 T 48 6 T 72 6 T 100 6 V12 H0 Z","M0 6 Q 12 12 24 6 T 48 6 T 72 6 T 100 6 V12 H0 Z","M0 6 Q 12 0 24 6 T 48 6 T 72 6 T 100 6 V12 H0 Z"]}}
              transition={{duration:1.6, repeat:Infinity, ease:"easeInOut"}}/>
          </svg>
          <motion.div key={value} initial={{x:"-100%"}} animate={{x:"100%"}} transition={{duration:0.9, ease:"easeOut", delay:0.12}}
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -skew-x-12"/>
        </motion.div>
      </div>
    </div>
  )
}
