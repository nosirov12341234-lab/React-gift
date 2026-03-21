import { useState } from 'react'
import FullPage from '../components/FullPage.jsx'
import { createTopup } from '../api.js'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')
const OPTS = [10000,25000,50000,100000,200000,500000]

export default function TopUp({ open, onClose, showToast, uid }) {
  const [sel, setSel]     = useState(50000)
  const [custom, setCustom] = useState('')
  const [loading, setLoading] = useState(false)

  const amount = custom ? (parseInt(custom)||0) : sel

  async function pay() {
    if (amount < 5000) { showToast('Minimum 5 000 so\'m!','err'); return }
    setLoading(true)
    try {
      const d = await createTopup(uid, amount)
      if (d.success) {
        const tg = window.Telegram?.WebApp
        if (tg) tg.openLink(d.payment_url)
        else window.open(d.payment_url,'_blank')
        showToast('✅ To\'lov sahifasi ochildi!','ok')
      } else {
        showToast('❌ '+d.error,'err')
      }
    } catch {
      showToast('❌ Xato yuz berdi','err')
    }
    setLoading(false)
  }

  return (
    <FullPage open={open} onClose={onClose} title="💳 Hisob To'ldirish">
      {/* Options */}
      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:8,padding:'14px 18px 0'}}>
        {OPTS.map(o => (
          <div key={o} onClick={() => { setSel(o); setCustom('') }} style={{
            background:sel===o&&!custom?'rgba(245,200,66,.1)':'var(--s1)',
            border:`1.5px solid ${sel===o&&!custom?'var(--gold)':'var(--bd)'}`,
            borderRadius:13,padding:'12px 8px',textAlign:'center',cursor:'pointer',transition:'all .2s'
          }}>
            <div style={{fontFamily:'Space Mono,monospace',fontSize:13,fontWeight:700,color:'var(--gold)'}}>{fmt(o)}</div>
            <div style={{fontSize:10,color:'var(--mt)',marginTop:2}}>so'm</div>
          </div>
        ))}
      </div>

      {/* Custom */}
      <div style={{margin:'10px 18px 0',background:'var(--s1)',border:'1.5px solid var(--bd)',borderRadius:13,padding:'12px 14px'}}>
        <div style={{fontSize:10,color:'var(--mt)',fontWeight:700,textTransform:'uppercase',letterSpacing:.5,marginBottom:5}}>
          Yoki o'z miqdoringizni kiriting (min 5 000 so'm)
        </div>
        <div style={{display:'flex',alignItems:'center',gap:8}}>
          <span>🪙</span>
          <input
            type="number" min="5000"
            value={custom}
            onChange={e => { setCustom(e.target.value); setSel(0) }}
            placeholder="Masalan: 75 000"
            style={{flex:1,background:'transparent',border:'none',outline:'none',color:'var(--tx)',fontFamily:'Syne,sans-serif',fontSize:15}}
          />
        </div>
      </div>

      {/* QulayPay info */}
      <div style={{margin:'12px 18px 0',background:'rgba(34,211,165,.05)',border:'1px solid rgba(34,211,165,.15)',borderRadius:13,padding:'12px 14px'}}>
        <div style={{fontSize:12,fontWeight:700,color:'var(--green)',marginBottom:7,display:'flex',alignItems:'center',gap:6}}>
          ✅ QulayPay — xavfsiz to'lov
        </div>
        <div style={{display:'flex',gap:7,flexWrap:'wrap',marginBottom:8}}>
          {['💳 Click','💳 Payme','💳 Uzcard','💳 Humo'].map(m => (
            <div key={m} style={{background:'var(--s2)',border:'1px solid var(--bd)',borderRadius:8,padding:'5px 10px',fontSize:11,fontWeight:700}}>{m}</div>
          ))}
        </div>
        <div style={{fontSize:11,color:'var(--mt)'}}>To'lov tugmasini bossangiz, to'lov usulini o'zingiz tanlaysiz</div>
      </div>

      {/* Summary */}
      <div style={{margin:'12px 18px 0',background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:14,padding:'13px 15px'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'5px 0'}}>
          <span style={{fontSize:14,fontWeight:800}}>To'lov miqdori</span>
          <span style={{fontSize:18,fontWeight:800,fontFamily:'Space Mono,monospace',color:'var(--gold)'}}>
            {fmt(amount)} so'm
          </span>
        </div>
      </div>

      <button onClick={pay} disabled={loading} style={{
        margin:'12px 18px 0',width:'calc(100% - 36px)',
        background:'linear-gradient(135deg,var(--gold),var(--gold2))',
        border:'none',borderRadius:14,padding:15,color:'#000',
        fontFamily:'Syne,sans-serif',fontSize:15,fontWeight:800,cursor:'pointer',
        opacity:loading?0.6:1,boxShadow:'0 8px 24px rgba(245,200,66,.28)'
      }}>
        {loading ? '⏳ Yuklanmoqda...' : '💳 QulayPay orqali to\'lash'}
      </button>
    </FullPage>
  )
}
