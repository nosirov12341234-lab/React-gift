import { useState } from 'react'
import FullPage from '../components/FullPage.jsx'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function TopUp({ open, onClose, settings, showToast, uid, tgUser }) {
  const [method, setMethod]   = useState(null)
  const [amount, setAmount]   = useState('')
  const [selAmt, setSelAmt]   = useState(null)
  const [loading, setLoading] = useState(false)

  const AMOUNTS = [10000, 25000, 50000, 100000, 200000, 500000]
  const finalAmt = selAmt || (parseInt(amount) || 0)

  async function createAutoTopup() {
    if (finalAmt < 5000) { showToast('Minimum 5 000 so\'m!', 'err'); return }
    setLoading(true)
    try {
      const r = await fetch('/api/topup/card', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid, amount: finalAmt })
      })
      const d = await r.json()
      if (d.success) {
        showToast('✅ Karta ma\'lumotlari yuborildi!', 'ok')
        onClose()
      } else {
        showToast('❌ ' + d.error, 'err')
      }
    } catch { showToast('❌ Xato', 'err') }
    setLoading(false)
  }

  function openBotForScreenshot() {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.close()
    }
  }

  const support = settings.support_link || ''

  return (
    <FullPage open={open} onClose={() => { setMethod(null); onClose() }} title="💰 Hisob To'ldirish">

      {/* TO'LOV USULLARI */}
      {!method && (
        <div style={{padding:'16px 18px',display:'flex',flexDirection:'column',gap:10}}>
          <div style={{fontSize:13,color:'var(--mt)',marginBottom:4}}>To'lov usulini tanlang:</div>

          {/* AVTOMATIK */}
          <div onClick={() => setMethod('auto')} style={{
            background:'var(--s1)',border:'1.5px solid var(--gold)',
            borderRadius:16,padding:'16px',cursor:'pointer',
            display:'flex',alignItems:'center',gap:12
          }}>
            <div style={{fontSize:30}}>💳</div>
            <div style={{flex:1}}>
              <div style={{fontWeight:800,fontSize:14}}>Avtomatik (Karta)</div>
              <div style={{fontSize:11,color:'var(--mt)',marginTop:3}}>Summani kiriting → kartaga to'lang → avtomatik tasdiqlanadi</div>
            </div>
            <div style={{color:'var(--gold)'}}>›</div>
          </div>

          {/* SCREENSHOT */}
          <div onClick={() => setMethod('screen')} style={{
            background:'var(--s1)',border:'1.5px solid var(--bd)',
            borderRadius:16,padding:'16px',cursor:'pointer',
            display:'flex',alignItems:'center',gap:12
          }}>
            <div style={{fontSize:30}}>📸</div>
            <div style={{flex:1}}>
              <div style={{fontWeight:800,fontSize:14}}>Screenshot orqali</div>
              <div style={{fontSize:11,color:'var(--mt)',marginTop:3}}>Kartaga to'lang → screenshot yuboring → admin tasdiqlaydi</div>
            </div>
            <div style={{color:'var(--mt)'}}>›</div>
          </div>

          {/* ADMIN */}
          <div onClick={() => { if(support) { const tg=window.Telegram?.WebApp; if(tg) tg.openLink(support) } }} style={{
            background:'var(--s1)',border:'1.5px solid var(--bd)',
            borderRadius:16,padding:'16px',cursor:'pointer',
            display:'flex',alignItems:'center',gap:12,
            opacity: support ? 1 : 0.5
          }}>
            <div style={{fontSize:30}}>👨‍💼</div>
            <div style={{flex:1}}>
              <div style={{fontWeight:800,fontSize:14}}>Admin orqali</div>
              <div style={{fontSize:11,color:'var(--mt)',marginTop:3}}>Admin bilan bog'laning va to'lov qiling</div>
            </div>
            <div style={{color:'var(--mt)'}}>›</div>
          </div>
        </div>
      )}

      {/* AVTOMATIK TO'LOV */}
      {method === 'auto' && (
        <div style={{padding:'16px 18px',display:'flex',flexDirection:'column',gap:10}}>
          <button onClick={() => setMethod(null)} style={{background:'none',border:'none',color:'var(--mt)',fontSize:13,cursor:'pointer',textAlign:'left',padding:0,marginBottom:4}}>← Orqaga</button>

          <div style={{fontSize:13,fontWeight:700,marginBottom:4}}>💳 Avtomatik to'ldirish</div>

          {/* SUMMALAR */}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8}}>
            {AMOUNTS.map(a => (
              <div key={a} onClick={() => { setSelAmt(a); setAmount('') }} style={{
                background: selAmt===a&&!amount ? 'rgba(245,200,66,.08)' : 'var(--s1)',
                border: `1.5px solid ${selAmt===a&&!amount ? 'var(--gold)' : 'var(--bd)'}`,
                borderRadius:12,padding:'10px 6px',textAlign:'center',cursor:'pointer'
              }}>
                <div style={{fontFamily:'Space Mono,monospace',fontSize:13,fontWeight:700,color:'var(--gold)'}}>{fmt(a)}</div>
                <div style={{fontSize:9,color:'var(--mt)'}}>so'm</div>
              </div>
            ))}
          </div>

          {/* CUSTOM */}
          <div style={{background:'var(--s1)',border:'1.5px solid var(--bd)',borderRadius:12,padding:'10px 14px'}}>
            <div style={{fontSize:10,color:'var(--mt)',marginBottom:4}}>Yoki o'zingiz kiriting (min 5 000)</div>
            <input type="number" value={amount}
              onChange={e => { setAmount(e.target.value); setSelAmt(null) }}
              placeholder="Masalan: 75000"
              style={{width:'100%',background:'transparent',border:'none',outline:'none',color:'var(--tx)',fontFamily:'Syne,sans-serif',fontSize:15}}
            />
          </div>

          {finalAmt > 0 && (
            <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:12,padding:'12px 14px'}}>
              <div style={{display:'flex',justifyContent:'space-between',fontSize:13}}>
                <span style={{color:'var(--mt)'}}>To'lov summasi</span>
                <span style={{fontWeight:800,color:'var(--gold)'}}>{fmt(finalAmt)} so'm</span>
              </div>
            </div>
          )}

          <div style={{background:'rgba(245,200,66,.06)',border:'1px solid rgba(245,200,66,.2)',borderRadius:12,padding:'10px 12px',fontSize:11,color:'var(--mt)'}}>
            ⚠️ <b style={{color:'var(--gold)'}}>Diqqat!</b> To'lov summasini aniq nusxalab oling. Boshqa summa yuborilsa to'lov aniqlanmaydi. Muammo bo'lsa adminga murojaat qiling.
          </div>

          <button onClick={createAutoTopup} disabled={loading || finalAmt < 5000} style={{
            background:'linear-gradient(135deg,var(--gold),var(--gold2))',
            border:'none',borderRadius:14,padding:14,color:'#000',
            fontFamily:'Syne,sans-serif',fontSize:14,fontWeight:800,cursor:'pointer',
            opacity: loading || finalAmt < 5000 ? 0.6 : 1
          }}>
            {loading ? '⏳...' : '💳 Karta ma\'lumotlarini olish'}
          </button>
        </div>
      )}

      {/* SCREENSHOT TO'LOV */}
      {method === 'screen' && (
        <div style={{padding:'16px 18px',display:'flex',flexDirection:'column',gap:10}}>
          <button onClick={() => setMethod(null)} style={{background:'none',border:'none',color:'var(--mt)',fontSize:13,cursor:'pointer',textAlign:'left',padding:0,marginBottom:4}}>← Orqaga</button>

          <div style={{fontSize:13,fontWeight:700,marginBottom:4}}>📸 Screenshot orqali to'ldirish</div>

          <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:14,padding:'14px'}}>
            <div style={{fontSize:12,lineHeight:1.8}}>
              1️⃣ Quyidagi kartaga pul yuboring<br/>
              2️⃣ Botga /tolov buyrug'ini yuboring<br/>
              3️⃣ "📸 Screenshot orqali" ni tanlang<br/>
              4️⃣ Summani kiriting va screenshot yuboring<br/>
              5️⃣ Admin tasdiqlaydi ✅
            </div>
          </div>

          <button onClick={openBotForScreenshot} style={{
            background:'linear-gradient(135deg,var(--pur),#5b3fd8)',
            border:'none',borderRadius:14,padding:14,color:'#fff',
            fontFamily:'Syne,sans-serif',fontSize:14,fontWeight:800,cursor:'pointer',
          }}>
            🤖 Botga o'tish → /tolov
          </button>
        </div>
      )}

    </FullPage>
  )
}
