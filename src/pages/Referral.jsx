import { useEffect, useState } from 'react'
import { getReferral } from '../api.js'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function Referral({ uid, onBack, showToast }) {
  const [data, setData] = useState({ link:'', referrals:0, ref_earned:0, bonus:5000, list:[] })
  const [tab, setTab]   = useState('stats')

  useEffect(() => {
    if (!uid) return
    getReferral(uid).then(d => setData(d)).catch(() => {})
  }, [uid])

  function copy() {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(data.link).then(() => showToast('✅ Nusxalandi!','ok'))
    } else showToast('Havolani qo\'lda nusxalang','')
  }

  return (
    <div style={{position:'relative',zIndex:1,animation:'fadeUp .28s ease'}}>
      <div style={{padding:'16px 18px',display:'flex',alignItems:'center',gap:12}}>
        <button onClick={onBack} style={{width:36,height:36,borderRadius:10,background:'var(--s2)',border:'1px solid var(--bd)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:18,cursor:'pointer',color:'var(--tx)'}}>←</button>
        <div style={{fontSize:18,fontWeight:800}}>🤝 Referral</div>
      </div>

      {/* TABS */}
      <div style={{display:'flex',gap:5,padding:'0 18px',marginBottom:14}}>
        {['stats','list'].map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding:'7px 16px', borderRadius:20,
            border:`1px solid ${tab===t?'var(--pur)':'var(--bd)'}`,
            background: tab===t ? 'var(--pa)' : 'transparent',
            color: tab===t ? 'var(--pur2)' : 'var(--mt)',
            fontFamily:'Syne,sans-serif', fontSize:12, fontWeight:700, cursor:'pointer'
          }}>
            {t==='stats' ? '📊 Statistika' : `👥 Ro'yxat (${data.list?.length||0})`}
          </button>
        ))}
      </div>

      {tab === 'stats' && (
        <div style={{padding:'0 18px',display:'flex',flexDirection:'column',gap:10}}>
          {/* LINK CARD */}
          <div style={{background:'linear-gradient(135deg,#1e1a3a,#0f1525)',border:'1px solid rgba(124,92,252,.22)',borderRadius:20,padding:'18px 20px',position:'relative',overflow:'hidden'}}>
            <div style={{position:'absolute',top:-30,right:-30,width:120,height:120,background:'radial-gradient(circle,rgba(124,92,252,.2),transparent 70%)',borderRadius:'50%'}}/>
            <div style={{fontSize:10,color:'var(--mt)',letterSpacing:2,textTransform:'uppercase',marginBottom:5}}>Sizning havolangiz</div>
            <div style={{fontFamily:'Space Mono,monospace',fontSize:11,color:'var(--mt)',marginBottom:12,wordBreak:'break-all',position:'relative',zIndex:1}}>{data.link||'—'}</div>
            <button onClick={copy} style={{background:'linear-gradient(135deg,var(--pur),#5b3fd8)',border:'none',borderRadius:11,padding:'10px 20px',color:'#fff',fontFamily:'Syne,sans-serif',fontSize:13,fontWeight:700,cursor:'pointer',position:'relative',zIndex:1}}>
              📋 Nusxa olish
            </button>
          </div>

          {/* STATS */}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:9}}>
            <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:14,textAlign:'center'}}>
              <div style={{fontSize:28,fontWeight:800,color:'var(--pur2)',fontFamily:'Space Mono,monospace'}}>{data.referrals||0}</div>
              <div style={{fontSize:10,color:'var(--mt)',marginTop:3,textTransform:'uppercase',letterSpacing:.5}}>Taklif</div>
            </div>
            <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:14,textAlign:'center'}}>
              <div style={{fontSize:22,fontWeight:800,color:'var(--gold)',fontFamily:'Space Mono,monospace'}}>{fmt(data.ref_earned||0)}</div>
              <div style={{fontSize:10,color:'var(--mt)',marginTop:3,textTransform:'uppercase',letterSpacing:.5}}>Bonus so'm</div>
            </div>
          </div>

          {/* BONUS INFO */}
          <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:14,display:'flex',alignItems:'center'}}>
            <div style={{flex:1}}>
              <div style={{fontSize:13,fontWeight:700,marginBottom:2}}>Har bir do'st uchun</div>
              <div style={{fontSize:11,color:'var(--mt)'}}>Do'stingiz botga kirsa avtomatik</div>
            </div>
            <div style={{fontSize:16,fontWeight:800,color:'var(--gold)'}}>+{fmt(data.bonus||5000)} so'm</div>
          </div>
        </div>
      )}

      {tab === 'list' && (
        <div style={{padding:'0 18px'}}>
          {!data.list || data.list.length === 0 ? (
            <div style={{textAlign:'center',padding:'50px 20px',color:'var(--mt)'}}>
              <div style={{fontSize:40,marginBottom:10,opacity:.35}}>👥</div>
              Hali referrallar yo'q
            </div>
          ) : data.list.map((u,i) => (
            <div key={i} style={{display:'flex',alignItems:'center',gap:10,background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:'11px 13px',marginBottom:8}}>
              <div style={{width:36,height:36,borderRadius:'50%',background:'linear-gradient(135deg,var(--pur),#5b3fd4)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:14,fontWeight:800,flexShrink:0}}>
                {(u.name||'U')[0].toUpperCase()}
              </div>
              <div style={{flex:1}}>
                <div style={{fontSize:13,fontWeight:700}}>{u.name||'Foydalanuvchi'}</div>
                <div style={{fontSize:10,color:'var(--mt)',marginTop:1}}>
                  {u.username ? `@${u.username} • ` : ''}{u.date} • {u.orders} ta buyurtma
                </div>
              </div>
              <div style={{fontSize:11,fontWeight:700,color:'var(--green)'}}>✅</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
