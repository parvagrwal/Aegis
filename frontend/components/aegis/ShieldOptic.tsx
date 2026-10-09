"use client"
import { motion } from "motion/react"

// Every blade is computed directly around the true center (40,40), so blades
// and rings can never drift apart. Each blade pivots around its own tip:
// rest = iris OPEN (38°), scanning = blades sweep shut (0°).
const OPEN = 38

function pt(angleDeg: number, r: number): [number, number] {
  const t = (angleDeg * Math.PI) / 180
  return [40 + r * Math.cos(t), 40 + r * Math.sin(t)]
}

function bladePath(a: number): string {
  const [tx, ty] = pt(a - 90, 28.5)          // tip on the outer ring
  const [sx, sy] = pt(a - 90 + 62, 28.5)     // other outer corner
  return `M40 40 L${tx.toFixed(2)} ${ty.toFixed(2)} A28.5 28.5 0 0 1 ${sx.toFixed(2)} ${sy.toFixed(2)} Z`
}

export default function ShieldOptic({size=64, scanning}:{size?:number, scanning:boolean}){
  return (
    <div style={{width:size, height:size}} className="relative grid place-items-center shrink-0">
      <svg viewBox="0 0 80 80" width={size} height={size} className="overflow-visible">
        {/* lens base */}
        <circle cx="40" cy="40" r="28.5" fill="#0A0E0B"/>
        <circle cx="40" cy="40" r="28.5" fill="none" stroke="#D4AF37" strokeWidth="1.2" opacity="0.95"/>
        <circle cx="40" cy="40" r="22" fill="none" stroke="#D4AF37" strokeWidth="0.6" opacity="0.25"/>
        {/* iris blades — one element each, pivot = its own tip (px origin, no nesting) */}
        {[0,60,120,180,240,300].map(a=>{
          const [px, py] = pt(a - 90, 28.5)
          return (
            <motion.path key={a} d={bladePath(a)}
              fill="#0F1411" stroke="#D4AF37" strokeWidth="1.1" opacity="0.95"
              style={{originX:`${px.toFixed(2)}px`, originY:`${py.toFixed(2)}px`}}
              initial={false}
              animate={{rotate: scanning ? 0 : OPEN}}
              transition={{duration:0.9, ease:"easeInOut"}}
            />
          )
        })}
        {/* pupil + core, revealed when the iris is open */}
        <circle cx="40" cy="40" r="14" fill="#0A0E0B" stroke="rgba(212,175,55,0.2)" strokeWidth="0.8"/>
        <motion.circle cx="40" cy="40" r="3.2" fill="#F5D76E"
          animate={{scale:[1,1.28,1], opacity:[1,0.85,1]}}
          transition={{duration:2, repeat:Infinity, ease:"easeInOut"}}
        />
        {scanning && (
          <motion.rect x="18" y="18" width="44" height="1.6" rx="0.8" fill="#F5D76E"
            style={{filter:"blur(0.6px)"}}
            animate={{y:[0,44,0]}} transition={{duration:1.1, repeat:Infinity, ease:"easeInOut"}}
          />
        )}
      </svg>
      <span className="absolute -bottom-1 mono text-[7px] tracking-[0.22em] text-brass">AEGIS</span>
    </div>
  )
}
