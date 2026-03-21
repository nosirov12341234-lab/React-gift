import { useState } from 'react'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function Home({ settings, onOpenStars, onOpenPremium, onOpenTopup, onNav }) {
  const [topPeriod, setTopPeriod] = useState('daily')
  const { bal=0, prices={}, refBonus=5000, top=[] } = settings

  const periods = [
    { id:'daily',   label:'Kunlik'   },
    { id:'weekly',  label:'Haftalik' },
    { id:'monthly', label:'Oylik'    },
    { id:'all',     label:'Umumiy'   },
  ]
  const medals = ['🥇','🥈','🥉']
  const avColors = [
    'linear-gradient(135deg,#f5c842,#e6a800)',
    'linear-gradient(135deg,#c0c0c0,#a0a0a0)',
    'linear-gradient(135deg,#cd7f32,#b86b20)',
  ]

  return (
    <div style={{position:'relative',zIndex:1,animation:'fadeUp .28s ease'}}>
      {/* HERO */}
      <div style={{padding:'18px 18px 0',textAlign:'center'}}>
        <div style={{fontSize:10,color:'var(--mt)',letterSpacing:3,textTransform:'uppercase',marginBottom:4}}>
          Xush kelibsiz
        </div>
        <div style={{fontSize:21,fontWeight:800}}>
          Salom, <span style={{
            background:'linear-gradient(90deg,var(--gold),var(--pur2))',
            WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'
          }}>{settings.name||'Do\'st'}</span> 👋
        </div>
      </div>

      {/* BALANCE CARD */}
      <div style={{margin:'14px 18px 0'}}>
        <div style={{
          background:'linear-gradient(135deg,#1e1a3a,#0f1525)',
          border:'1px solid rgba(124,92,252,.22)',
          borderRadius:20,padding:'18px 20px',position:'relative',overflow:'hidden'
        }}>
          <div style={{position:'absolute',top:-30,right:-30,width:120,height:120,background:'radial-gradient(circle,rgba(124,92,252,.2),transparent 70%)',borderRadius:'50%'}}/>
          <div style={{position:'absolute',bottom:-15,left:10,width:80,height:80,background:'radial-gradient(circle,rgba(245,200,66,.08),transparent 70%)',borderRadius:'50%'}}/>
          <div style={{fontSize:10,color:'var(--mt)',letterSpacing:2,textTransform:'uppercase',marginBottom:5}}>Hisobingiz</div>
          <div style={{fontSize:30,fontWeight:800,fontFamily:'Space Mono,monospace',marginBottom:2}}>
            {fmt(bal)} <span style={{fontSize:15,color:'var(--mt)',fontFamily:'Syne,sans-serif',fontWeight:400}}>so'm</span>
          </div>
          <div style={{fontSize:11,color:'var(--mt)',marginBottom:15}}>
            ≈ {Math.floor(bal/(prices.star||210))} ⭐ Stars
          </div>
          <div style={{display:'flex',gap:9,position:'relative',zIndex:1}}>
            <button onClick={onOpenTopup} style={{
              flex:1,background:'linear-gradient(135deg,var(--pur),#5b3fd8)',
              border:'none',borderRadius:11,padding:10,color:'#fff',
              fontFamily:'Syne,sans-serif',fontSize:13,fontWeight:700,cursor:'pointer'
            }}>＋ To'ldirish</button>
            <button onClick={() => onNav('history')} style={{
              flex:1,background:'var(--s2)',border:'1px solid var(--bd)',
              borderRadius:11,padding:10,color:'var(--tx)',
              fontFamily:'Syne,sans-serif',fontSize:13,fontWeight:700,cursor:'pointer'
            }}>📋 Tarix</button>
          </div>
        </div>
      </div>

      {/* SERVICES */}
      <div style={{padding:'18px 18px 0'}}>
        <div style={{fontSize:14,fontWeight:700,marginBottom:12}}>⭐ Sotib Olish</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
          {/* Stars */}
          <div onClick={onOpenStars} style={{
            background:'linear-gradient(145deg,#161205,#12121a)',
            border:'1px solid rgba(245,200,66,.18)',
            borderRadius:16,padding:'15px 13px',cursor:'pointer',
            transition:'all .22s',position:'relative',overflow:'hidden'
          }}>
            <span style={{fontSize:26,marginBottom:8,display:'block'}}>🌟</span>
            <div style={{fontSize:13,fontWeight:800,marginBottom:3}}>Stars</div>
            <div style={{fontSize:10,color:'var(--mt)',marginBottom:8,lineHeight:1.4}}>
              O'zingizga yoki do'stingizga Telegram Stars
            </div>
            <div style={{fontSize:12,fontWeight:700,color:'var(--gold)',display:'flex',alignItems:'center',gap:4}}>
              <span>🪙</span>{fmt(prices.star||210)} so'm / ta
            </div>
          </div>
          {/* Premium */}
          <div onClick={onOpenPremium} style={{
            background:'linear-gradient(145deg,#0f0c1c,#12121a)',
            border:'1px solid rgba(124,92,252,.18)',
            borderRadius:16,padding:'15px 13px',cursor:'pointer',
            transition:'all .22s',position:'relative',overflow:'hidden'
          }}>
            <div style={{position:'absolute',top:8,right:8,background:'var(--red)',color:'#fff',fontSize:9,fontWeight:800,padding:'2px 6px',borderRadius:20}}>🔥 TOP</div>
            <span style={{fontSize:26,marginBottom:8,display:'block'}}>👑</span>
            <div style={{fontSize:13,fontWeight:800,marginBottom:3}}>Premium</div>
            <div style={{fontSize:10,color:'var(--mt)',marginBottom:8,lineHeight:1.4}}>
              O'zingizga yoki do'stingizga Premium Gift
            </div>
            <div style={{fontSize:12,fontWeight:700,color:'var(--gold)',display:'flex',alignItems:'center',gap:4}}>
              <span>🪙</span>{fmt(prices.pm3||195000)} so'm/3oy
            </div>
          </div>
        </div>
      </div>

      {/* REFERRAL */}
      <div onClick={() => onNav('referral')} style={{
        margin:'14px 18px 0',
        background:'linear-gradient(135deg,#1a1535,#0f0e1e)',
        border:'1px solid rgba(124,92,252,.18)',
        borderRadius:15,padding:14,
        display:'flex',alignItems:'center',gap:12,cursor:'pointer'
      }}>
        <div style={{width:42,height:42,flexShrink:0,background:'linear-gradient(135deg,var(--pur),#5b3fd4)',borderRadius:12,display:'flex',alignItems:'center',justifyContent:'center',fontSize:20}}>🤝</div>
        <div style={{flex:1}}>
          <div style={{fontSize:13,fontWeight:700}}>Do'stingizni taklif qiling</div>
          <div style={{fontSize:10,color:'var(--mt)',marginTop:2}}>Har bir do'st uchun bonus oling</div>
        </div>
        <div style={{background:'var(--pa)',border:'1px solid rgba(124,92,252,.22)',borderRadius:9,padding:'4px 9px',fontSize:12,fontWeight:800,color:'var(--pur2)',whiteSpace:'nowrap'}}>
          +{fmt(refBonus)} so'm
        </div>
      </div>

      {/* TOP 10 */}
      <div style={{padding:'18px 18px 0'}}>
        <div style={{fontSize:14,fontWeight:700,marginBottom:12}}>🏆 Top Foydalanuvchilar</div>
        <div style={{display:'flex',gap:5,overflowX:'auto',marginBottom:11,scrollbarWidth:'none'}}>
          {periods.map(p => (
            <button key={p.id} onClick={() => setTopPeriod(p.id)} style={{
              padding:'5px 13px',borderRadius:20,
              border:`1px solid ${topPeriod===p.id?'var(--gold)':'var(--bd)'}`,
              background:topPeriod===p.id?'var(--ga)':'transparent',
              color:topPeriod===p.id?'var(--gold)':'var(--mt)',
              fontFamily:'Syne,sans-serif',fontSize:11,fontWeight:700,
              cursor:'pointer',whiteSpace:'nowrap'
            }}>{p.label}</button>
          ))}
        </div>
        <div style={{display:'flex',flexDirection:'column',gap:7}}>
          {(settings[`top_${topPeriod}`]||[]).length === 0 ? (
            <div style={{textAlign:'center',padding:'40px 20px',color:'var(--mt)'}}>
              <div style={{fontSize:40,marginBottom:10,opacity:.35}}>🏆</div>
              Hali ma'lumot yo'q
            </div>
          ) : (settings[`top_${topPeriod}`]||[]).map((u,i) => (
            <div key={i} style={{display:'flex',alignItems:'center',gap:10,background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:'10px 12px'}}>
              <div style={{width:24,fontSize:16,textAlign:'center'}}>{medals[i]||i+1}</div>
              <div style={{width:32,height:32,borderRadius:'50%',background:avColors[i]||'linear-gradient(135deg,var(--pur),#5b3fd4)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:13,fontWeight:800,color:i<3?'#000':'#fff',flexShrink:0}}>
                {(u.name||'U')[0].toUpperCase()}
              </div>
              <div style={{flex:1}}>
                <div style={{fontSize:12,fontWeight:700}}>{u.name||'Foydalanuvchi'}</div>
                <div style={{fontSize:10,color:'var(--mt)',marginTop:1}}>{u.orders} ta buyurtma</div>
              </div>
              <div style={{fontSize:12,fontWeight:800,color:'var(--gold)'}}>⭐ {fmt(u.stars)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
