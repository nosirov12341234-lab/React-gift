import { useEffect, useRef } from 'react'

export default function StarsBg() {
  const ref = useRef()

  useEffect(() => {
    const el = ref.current
    if (!el) return
    for (let i = 0; i < 80; i++) {
      const s = document.createElement('div')
      const sz = Math.random() > .8 ? 3 : 2
      s.style.cssText = `
        position:absolute;border-radius:50%;background:#fff;
        left:${Math.random()*100}%;top:${Math.random()*100}%;
        width:${sz}px;height:${sz}px;
        --d:${2+Math.random()*4}s;
        --o:${.1+Math.random()*.35};
        animation:twinkle var(--d) ease-in-out infinite;
        opacity:var(--o);
        animation-delay:${Math.random()*5}s;
      `
      el.appendChild(s)
    }
    return () => { if (el) el.innerHTML = '' }
  }, [])

  return (
    <div ref={ref} style={{
      position:'fixed',inset:0,pointerEvents:'none',zIndex:0,overflow:'hidden'
    }}/>
  )
}
