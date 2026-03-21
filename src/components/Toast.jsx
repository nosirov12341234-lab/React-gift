import { useState, useCallback, useRef } from 'react'

let _show = null
export function useToast() {
  const [toast, setToast] = useState({ msg:'', type:'', on:false })
  const timer = useRef()

  const show = useCallback((msg, type='') => {
    if (timer.current) clearTimeout(timer.current)
    setToast({ msg, type, on: true })
    timer.current = setTimeout(() => setToast(t => ({...t, on:false})), 3000)
  }, [])

  return { toast, show }
}

export function Toast({ toast }) {
  const { msg, type, on } = toast
  return (
    <div style={{
      position:'fixed', bottom:82, left:'50%',
      transform:`translateX(-50%) translateY(${on?0:50}px)`,
      background:'var(--s2)',
      border:`1px solid ${type==='ok'?'var(--green)':type==='err'?'var(--red)':'var(--bd)'}`,
      color: type==='ok'?'var(--green)':type==='err'?'var(--red)':'var(--tx)',
      borderRadius:12, padding:'9px 16px',
      fontSize:12, fontWeight:600,
      transition:'transform .3s cubic-bezier(.34,1.4,.64,1)',
      zIndex:9999, whiteSpace:'nowrap', pointerEvents:'none'
    }}>
      {msg}
    </div>
  )
}
