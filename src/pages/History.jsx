import { useEffect, useState } from 'react'
import { getHistory } from '../api.js'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function History({ uid, onBack }) {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!uid) return
    getHistory(uid).then(d => {
      setOrders(d.orders||[])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [uid])

  const stMap = { completed:{label:'✅ Bajarildi',cls:'done'}, failed:{label:'❌ Xato',cls:'fail'}, processing:{label:'⏳ Kutilmoqda',cls:'pend'} }
  const stColor = { done:'var(--green)', fail:'var(--red)', pend:'#f59e0b' }
  const stBg    = { done:'rgba(34,211,165,.1)', fail:'rgba(255,79,109,.1)', pend:'rgba(245,158,11,.1)' }
  const stBd    = { done:'rgba(34,211,165,.2)', fail:'rgba(255,79,109,.2)', pend:'rgba(245,158,11,.2)' }

  return (
    <div style={{position:'relative',zIndex:1,animation:'fadeUp .28s ease'}}>
      <div style={{padding:'16px 18px',display:'flex',alignItems:'center',gap:12}}>
        <button onClick={onBack} style={{width:36,height:36,borderRadius:10,background:'var(--s2)',border:'1px solid var(--bd)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:18,cursor:'pointer',color:'var(--tx)'}}>←</button>
        <div style={{fontSize:18,fontWeight:800}}>📋 Buyurtmalar</div>
      </div>

      <div style={{padding:'0 18px'}}>
        {loading ? (
          <div style={{textAlign:'center',padding:'50px 20px',color:'var(--mt)'}}>
            <div style={{fontSize:40,marginBottom:10,opacity:.35}}>⏳</div>Yuklanmoqda...
          </div>
        ) : orders.length === 0 ? (
          <div style={{textAlign:'center',padding:'50px 20px',color:'var(--mt)'}}>
            <div style={{fontSize:40,marginBottom:10,opacity:.35}}>📭</div>Hali buyurtmalar yo'q
          </div>
        ) : orders.map(o => {
          const svc = o.service==='stars' ? `🌟 ${fmt(o.stars||0)} Stars` : `👑 Premium ${o.months||3} oy`
          const nm  = o.service==='stars' ? 'Stars' : 'Premium'
          const ic  = o.service==='stars' ? '🌟' : '👑'
          const st  = stMap[o.status]||{label:'⏳',cls:'pend'}
          return (
            <div key={o.id} style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:16,marginBottom:9,overflow:'hidden'}}>
              <div style={{padding:'13px 14px'}}>
                <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:8}}>
                  <div style={{display:'inline-flex',alignItems:'center',gap:4,borderRadius:20,padding:'3px 9px',fontSize:10,fontWeight:700,background:stBg[st.cls],color:stColor[st.cls],border:`1px solid ${stBd[st.cls]}`}}>
                    {st.label}
                  </div>
                  <span style={{fontSize:10,color:'var(--mt)'}}>#{o.id}</span>
                </div>
                <div style={{display:'flex',alignItems:'center',gap:9}}>
                  <span style={{fontSize:22}}>{ic}</span>
                  <div>
                    <div style={{fontFamily:'Syne,sans-serif',fontSize:16,fontWeight:800}}>{nm}</div>
                    <div style={{fontSize:11,color:'var(--mt)',marginTop:1}}>{svc}</div>
                  </div>
                </div>
              </div>
              <div style={{padding:'12px 14px',borderTop:'1px dashed var(--bd)'}}>
                <div style={{display:'flex',justifyContent:'space-between',fontSize:12,padding:'3px 0'}}>
                  <span style={{color:'var(--mt)',fontWeight:500}}>Kimga</span>
                  <span style={{fontWeight:700}}>@{o.username||'?'}</span>
                </div>
                <div style={{display:'flex',justifyContent:'space-between',fontSize:12,padding:'3px 0',borderTop:'1px solid var(--bd)'}}>
                  <span style={{color:'var(--mt)',fontWeight:500}}>Sana</span>
                  <span style={{fontWeight:700}}>{o.created_at?.slice(0,16).replace('T',' ')||'—'}</span>
                </div>
                <div style={{display:'flex',justifyContent:'space-between',fontSize:13,padding:'8px 0 3px',borderTop:'1px solid var(--bd)'}}>
                  <span style={{fontWeight:800}}>To'langan</span>
                  <span style={{fontWeight:900,color:'var(--gold)'}}>{fmt(o.price)} so'm</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
