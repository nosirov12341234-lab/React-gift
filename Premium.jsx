import { useState } from 'react'
import FullPage from '../components/FullPage.jsx'
import RecipientSelector from '../components/RecipientSelector.jsx'
import PromoInput from '../components/PromoInput.jsx'
import SummaryBox from '../components/SummaryBox.jsx'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function Premium({ open, onClose, settings, showToast, uid, tgUser }) {
  const [months, setMonths] = useState(6)
  const [recip, setRecip]   = useState('self')
  const [uname, setUname]   = useState('')
  const [disc, setDisc]     = useState(0)
  const [promo, setPromo]   = useState('')

  const prices  = settings.prices || {}
  const pkMap   = { 3:'pm3', 6:'pm6', 12:'pm12' }
  const basePrice = prices[pkMap[months]] || 0
  const discAmt   = disc>0 ? Math.round(basePrice*disc/100) : 0
  const total     = basePrice - discAmt
  const target    = recip==='self' ? (tgUser?.first_name||'O\'zim') : (uname||'—')

  const plans = [
    { m:3,  key:'pm3',  sub:'Boshlang\'ich' },
    { m:6,  key:'pm6',  sub:'Eng mashhur', pop:true },
    { m:12, key:'pm12', sub:'Tejamkor' },
  ]

  function buy() {
    const username = recip==='self' ? (tgUser?.username||'') : uname.replace('@','')
    if (recip==='self' && !username) { showToast('Telegram username ingiz yo\'q!','err'); return }
    if (recip==='other' && !username) { showToast('Username kiriting!','err'); return }
    if ((settings.bal||0) < total) { showToast('Balans yetarli emas!','err'); return }
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.sendData(JSON.stringify({ action:'buy_premium', months, username, price:total, promo }))
    } else {
      showToast('Telegram orqali oching!','err')
    }
  }

  return (
    <FullPage open={open} onClose={onClose} title="👑 Premium Gift">
      {/* Plans */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:9,padding:'16px 18px 0'}}>
        {plans.map(({m,key,sub,pop}) => (
          <div key={m} onClick={() => { setMonths(m); setDisc(0); setPromo('') }} style={{
            background:months===m?'rgba(124,92,252,.08)':'var(--s1)',
            border:`1.5px solid ${months===m?'var(--pur)':'var(--bd)'}`,
            borderRadius:15,padding:'14px 11px',textAlign:'center',
            cursor:'pointer',position:'relative',transition:'all .2s'
          }}>
            {pop && <div style={{position:'absolute',top:-8,left:'50%',transform:'translateX(-50%)',background:'var(--gold)',color:'#000',fontSize:9,fontWeight:800,padding:'2px 8px',borderRadius:20,whiteSpace:'nowrap'}}>⭐ MASHHUR</div>}
            <div style={{fontFamily:'Space Mono,monospace',fontSize:26,fontWeight:700,color:'var(--pur2)'}}>{m}</div>
            <div style={{fontSize:10,color:'var(--mt)',margin:'2px 0 8px'}}>oy</div>
            <div style={{fontSize:11,fontWeight:700}}>{fmt(prices[key]||0)}</div>
            <div style={{fontSize:9,color:'var(--mt)'}}>so'm</div>
          </div>
        ))}
      </div>

      <RecipientSelector
        value={recip} onChange={setRecip}
        usernameVal={uname} onUsernameChange={setUname}
        color="purple"
      />

      <PromoInput
        uid={uid} product={pkMap[months]}
        onApply={(d,c) => { setDisc(d); setPromo(c) }}
      />

      <SummaryBox
        rows={[
          { label:'Muddat', value:`${months} oy` },
          { label:'Kimga', value:target },
          disc>0 && { label:'🎁 Chegirma', value:`-${fmt(discAmt)} so'm`, color:'var(--green)' },
        ]}
        total={total}
        totalColor="var(--pur2)"
      />

      <button onClick={buy} style={{
        margin:'12px 18px 0',width:'calc(100% - 36px)',
        background:'linear-gradient(135deg,var(--pur),#5b3fd8)',
        border:'none',borderRadius:14,padding:15,color:'#fff',
        fontFamily:'Syne,sans-serif',fontSize:15,fontWeight:800,cursor:'pointer',
        display:'flex',alignItems:'center',justifyContent:'center',gap:8,
        boxShadow:'0 8px 24px rgba(124,92,252,.28)'
      }}>⚡ Sotib olish</button>
    </FullPage>
  )
}
