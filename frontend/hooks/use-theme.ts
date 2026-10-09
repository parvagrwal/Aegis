"use client"
export type Theme="obsidian"|"paper"|"void"
export function toggleTheme(next:Theme){
  const apply=()=>{ document.documentElement.setAttribute("data-theme",next); localStorage.setItem("aegis-theme",next) }
  // @ts-ignore View Transitions
  if((document as any).startViewTransition) (document as any).startViewTransition(apply)
  else apply()
}
