import { useState } from 'react'
import { checkPromo } from '../api.js'

export default function PromoInput({ uid, product, onApply }) {
  const [code, setCode] = useState('')
  const [msg, setMsg]   = useState(null)

  async function apply() {
    if (!code.trim()) return
    const d = await checkPromo(code.trim(), uid, product)
    if (d.success) {
      setMsg({ ok:true, text:`✅ Qo'llandi! -${d.discount}% chegirma` })
      onApply(d.discount, code.trim())
    } else {
      setMsg({ ok:false, text:'❌ '+d.error })
      onApply(0, '')
    }
  }

  return (
    <div style={{padding:'0 18px',marginTop:12}}>
      <div style={{fontSize:10,color:'var(--mt)',fontWeight:700,textTransform:'uppercase',letterSpacing:1,marginBottom:7}}>
        Promo kod (ixtiyoriy)
      </div>
      <div style={{display:'flex',gap:8}}>
        <div style={{
          flex:1,background:'var(--s1)',border:'1.5px solid var(--bd)',
          borderRadius:13,padding:'11px 14px',
          display:'flex',alignItems:'center',gap:8
        }}>
          <span style={{fontSize:15}}>🎁</span>
          <input
            value={code}
            onChange={e => { setCode(e.target.value.toUpperCase()); setMsg(null) }}
            placeholder="PROMO20"
            style={{
              flex:1,background:'transparent',border:'none',outline:'none',
              color:'var(--gold)',fontFamily:'Space Mono,monospace',
              fontSize:14,fontWeight:700,letterSpacing:1
            }}
          />
        </div>
        <button onClick={apply} style={{
          background:'var(--s2)',border:'1.5px solid var(--bd)',
          borderRadius:13,padding:'0 14px',color:'var(--tx)',
          fontFamily:'Syne,sans-serif',fontSize:12,fontWeight:700,cursor:'pointer'
        }}>Qo'llash</button>
      </div>
      {msg && (
        <div style={{
          marginTop:6,fontSize:11,padding:'6px 10px',borderRadius:9,
          background:msg.ok?'rgba(34,211,165,.1)':'rgba(255,79,109,.1)',
          color:msg.ok?'var(--green)':'var(--red)',
          border:`1px solid ${msg.ok?'rgba(34,211,165,.2)':'rgba(255,79,109,.2)'}`
        }}>{msg.text}</div>
      )}
    </div>
  )
}
