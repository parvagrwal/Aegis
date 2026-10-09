export const springs = {
  snappy: { type:"spring" as const, stiffness:400, damping:30 },
  gentle: { type:"spring" as const, stiffness:200, damping:25 },
  slow: { type:"spring" as const, stiffness:140, damping:20 },
  release: { type:"spring" as const, stiffness:300, damping:30 }
}
export const motionTokens = {
  duration:{ fast:0.15, normal:0.25, slow:0.4, crawl:1.2 },
  easing:{ smooth:[0.25,0.1,0.25,1] as const, linear:"linear" as const },
  scale:{ press:0.98, pop:1.02, subtle:0.96 },
  distance:{ sm:8, md:16, lg:24, xl:40 }
}
