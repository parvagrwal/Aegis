"use client"
import { useEffect, useState } from "react"
export function useSafeMotion(distance:number){
  const [reduce,setReduce]=useState(false)
  useEffect(()=>{
    const m=window.matchMedia("(prefers-reduced-motion: reduce)")
    setReduce(m.matches)
    const h=(e:MediaQueryListEvent)=>setReduce(e.matches)
    m.addEventListener("change",h); return()=>m.removeEventListener("change",h)
  },[])
  if(reduce) return { initial:{opacity:0}, animate:{opacity:1}, exit:{opacity:0} }
  return { initial:{opacity:0,y:distance}, animate:{opacity:1,y:0}, exit:{opacity:0,y:distance/2} }
}
