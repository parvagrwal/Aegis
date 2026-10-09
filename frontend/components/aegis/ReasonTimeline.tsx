"use client"
import { motion } from "motion/react"

export default function ReasonTimeline({ items }: { items: string[] }) {
  if (!items?.length) {
    return (
      <div className="mono text-[13px] leading-6 text-sage bg-inset border border-line rounded-md p-3">
        no policy features fired — baseline prior only
      </div>
    )
  }
  return (
    <div className="relative pl-6">
      {/* vertical brass spine */}
      <div className="absolute left-[7px] top-2 bottom-2 w-[1px] bg-gradient-to-b from-brass/50 via-line to-transparent" />
      <motion.div
        initial="hidden"
        animate="visible"
        variants={{ hidden:{}, visible:{ transition:{ staggerChildren:0.07, delayChildren:0.08 }}}}
        className="space-y-2.5"
      >
        {items.map((r,i)=>(
          <motion.div
            key={i}
            variants={{ hidden:{opacity:0, x:-8}, visible:{opacity:1, x:0} }}
            className="relative flex gap-3 p-3 rounded-md bg-inset border border-line"
          >
            <span className="absolute -left-[22px] top-[18px] w-[9px] h-[9px] rounded-full bg-brass border-2 border-[var(--bg)] shadow-[0_0_0_1px_rgba(212,175,55,0.25)]" />
            <span className="mono text-[12.5px] leading-5 text-cream/90">{r}</span>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}
