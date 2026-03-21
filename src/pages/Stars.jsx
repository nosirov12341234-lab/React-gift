import { useState } from 'react'
import FullPage from '../components/FullPage.jsx'
import RecipientSelector from '../components/RecipientSelector.jsx'
import PromoInput from '../components/PromoInput.jsx'
import SummaryBox from '../components/SummaryBox.jsx'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

const PKGS = [
  { c:50,  sub:'Eng arzon' },
  { c:100, sub:'Mashhur'   },
  { c:250, sub:'Foydali'   },
  { c:500, sub:'🔥 Mashhur', hot:true },
  { c:1000,sub:'Katta paket'},
]

export default function Stars({ open, onClose, settings, showToast, uid, tgUser }) {
  const [sel, setSel]       = useState(500)
  const [custom, setCustom] = useState('')
  const [recip, setRecip]   = useState('self')
  const [uname, setUname]   = useState('')
  const [disc, setDisc]     = useState(0)
  const [promo, setPromo]   = useState('')

  const starPrice = settings.prices?.star || 210
  const minStars  = settings.minStars || 50
  const count     = custom ? (parseInt(custom)||0) : sel
  const base      = count * starPrice
  const discAmt   = disc>0 ? Math.round(base*disc/100) : 0
  const total     = base - discAmt
  const target    = recip==='self' ? (tgUser?.first_name||'O\'zim') : (uname||'—')

  function buy() {
    const username = recip==='self' ? (tgUser?.username||'') : uname.replace('@','')
    if (recip==='self' && !username) { showToast('Telegram username ingiz yo\'q!','err'); return }
    if (recip==='other' && !username) { showToast('Username kiriting!','err'); return }
    if (count < minStars) { showToast(`Minimum ${minStars} Stars!`,'err'); return }
    if ((settings.bal||0) < total) { showToast('Balans yetarli emas!','err'); return }
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.sendData(JSON.stringify({ action:'buy_stars', stars:count, username, price:total, promo }))
    } else {
      showToast('Telegram orqali oching!','err')
    }
  }

  return (
    <FullPage open={open} onClose={onClose} title="🌟 Stars sotib olish">
      {/* Packages */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:9,padding:'16px 18px 0'}}>
        {PKGS.map(({c,sub,hot}) => (
          <div key={c} onClick={() => { setSel(c); setCustom(''); setDisc(0); setPromo('') }} style={{
            background:'var(--s1)',
            border:`1.5px solid ${sel===c&&!custom?'var(--gold)':'var(--bd)'}`,
            background:sel===c&&!custom?'rgba(245,200,66,.07)':'var(--s1)',
            borderRadius:15,padding:'14px 11px',textAlign:'center',
            cursor:'pointer',position:'relative',transition:'all .2s'
          }}>
            {hot && <div style={{position:'absolute',top:-8,left:'50%',transform:'translateX(-50%)',background:'var(--red)',color:'#fff',fontSize:9,fontWeight:800,padding:'2px 8px',borderRadius:20,whiteSpace:'nowrap'}}>🔥 MASHHUR</div>}
            <div style={{fontFamily:'Space Mono,monospace',fontSize:22,fontWeight:700,color:'var(--gold)'}}>{fmt(c)}</div>
            <div style={{fontSize:10,color:'var(--mt)',margin:'2px 0 8px'}}>{sub}</div>
            <div style={{fontSize:12,fontWeight:700}}>{fmt(c*starPrice)} so'm</div>
          </div>
        ))}
        {/* Custom */}
        <div onClick={() => document.getElementById('stCustomInp').focus()} style={{
          background:custom?'rgba(245,200,66,.07)':'var(--s1)',
          border:`1.5px solid ${custom?'var(--gold)':'var(--bd)'}`,
          borderRadius:15,padding:'14px 11px',textAlign:'center',cursor:'pointer'
        }}>
          <div style={{fontFamily:'Space Mono,monospace',fontSize:20,fontWeight:700,color:'var(--mt)'}}>✏️</div>
          <div style={{fontSize:10,color:'var(--mt)',margin:'2px 0 8px'}}>O'zingiz</div>
          <div style={{fontSize:12,fontWeight:700,color:'var(--mt)'}}>Kiriting</div>
        </div>
      </div>

      {/* Custom input */}
      <div style={{margin:'10px 18px 0',background:'var(--s1)',border:'1.5px solid var(--bd)',borderRadius:13,padding:'12px 14px'}}>
        <div style={{fontSize:10,color:'var(--mt)',fontWeight:700,textTransform:'uppercase',letterSpacing:.5,marginBottom:5}}>
          ⭐ O'z miqdoringizni kiriting (min {minStars})
        </div>
        <div style={{display:'flex',alignItems:'center',gap:8}}>
          <span style={{fontSize:16}}>🌟</span>
          <input
            id="stCustomInp"
            type="number" min={minStars}
            value={custom}
            onChange={e => { setCustom(e.target.value); setSel(0); setDisc(0); setPromo('') }}
            placeholder={`Masalan: 750`}
            style={{flex:1,background:'transparent',border:'none',outline:'none',color:'var(--tx)',fontFamily:'Syne,sans-serif',fontSize:15}}
          />
        </div>
      </div>

      <RecipientSelector
        value={recip} onChange={setRecip}
        usernameVal={uname} onUsernameChange={setUname}
        color="gold"
      />

      <PromoInput
        uid={uid} product="star"
        onApply={(d, c) => { setDisc(d); setPromo(c) }}
      />

      <SummaryBox
        rows={[
          { label:'Stars miqdori', value:`${fmt(count)} ⭐` },
          { label:'Kimga', value:target },
          disc>0 && { label:'🎁 Chegirma', value:`-${fmt(discAmt)} so'm`, color:'var(--green)' },
        ]}
        total={total}
      />

      <button onClick={buy} style={{
        margin:'12px 18px 0',width:'calc(100% - 36px)',
        background:'linear-gradient(135deg,var(--gold),var(--gold2))',
        border:'none',borderRadius:14,padding:15,color:'#000',
        fontFamily:'Syne,sans-serif',fontSize:15,fontWeight:800,cursor:'pointer',
        display:'flex',alignItems:'center',justifyContent:'center',gap:8,
        boxShadow:'0 8px 24px rgba(245,200,66,.28)'
      }}>⚡ Sotib olish</button>
    </FullPage>
  )
}
