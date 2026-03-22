import { useState } from 'react'

const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function Profile({ settings, tgUser, onTopup, onReferral, onHistory, showToast }) {
  const [tab, setTab]       = useState('profile')
  const [token, setToken]   = useState('')
  const [loading, setLoading] = useState(false)
  const [docs, setDocs]     = useState(null)

  const { bal=0, orders_count=0, referrals=0, supportLink='', channelLink='' } = settings
  const name = tgUser?.first_name || settings.name || '—'
  const un   = tgUser?.username ? '@'+tgUser.username : settings.username ? '@'+settings.username : '—'
  const av   = name[0]?.toUpperCase() || 'U'
  const uid  = tgUser?.id || 0

  function openLink(url) {
    const tg = window.Telegram?.WebApp
    if (url && tg) tg.openLink(url)
    else if (url) window.open(url,'_blank')
  }

  async function createToken() {
    setLoading(true)
    try {
      const r = await fetch('/api/v1/token/create', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ uid })
      })
      const d = await r.json()
      if (d.success) {
        setToken(d.token)
        showToast('✅ Token yaratildi!','ok')
      } else {
        showToast('❌ '+d.error,'err')
      }
    } catch { showToast('❌ Xato','err') }
    setLoading(false)
  }

  async function loadDocs() {
    try {
      const r = await fetch('/api/v1/docs')
      const d = await r.json()
      setDocs(d)
    } catch { showToast('❌ Xato','err') }
  }

  function copyToken() {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(token).then(() => showToast('✅ Nusxalandi!','ok'))
    }
  }

  const tabs = [
    { id:'profile', label:'👤 Profil' },
    { id:'dev',     label:'⚡ Developer' },
  ]

  return (
    <div style={{position:'relative',zIndex:1,animation:'fadeUp .28s ease'}}>
      {/* TABS */}
      <div style={{display:'flex',gap:5,padding:'16px 18px 0'}}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); if(t.id==='dev'&&!docs) loadDocs() }} style={{
            flex:1, padding:'9px', borderRadius:12,
            border:`1.5px solid ${tab===t.id?'var(--gold)':'var(--bd)'}`,
            background: tab===t.id ? 'var(--ga)' : 'transparent',
            color: tab===t.id ? 'var(--gold)' : 'var(--mt)',
            fontFamily:'Syne,sans-serif', fontSize:12, fontWeight:700, cursor:'pointer'
          }}>{t.label}</button>
        ))}
      </div>

      {/* ─── PROFILE TAB ─── */}
      {tab === 'profile' && (
        <div style={{padding:'12px 18px 0',display:'flex',flexDirection:'column',gap:10}}>
          {/* Profile card */}
          <div style={{background:'linear-gradient(135deg,#1e1a3a,#0f1525)',border:'1px solid rgba(124,92,252,.22)',borderRadius:20,padding:'20px',textAlign:'center',position:'relative',overflow:'hidden'}}>
            <div style={{width:60,height:60,borderRadius:'50%',background:'linear-gradient(135deg,var(--gold),var(--gold2))',display:'flex',alignItems:'center',justifyContent:'center',fontSize:26,fontWeight:800,margin:'0 auto 10px',fontFamily:'Syne,sans-serif',color:'#000'}}>{av}</div>
            <div style={{fontSize:17,fontWeight:800,marginBottom:2}}>{name}</div>
            <div style={{fontSize:12,color:'var(--mt)'}}>{un}</div>
            <div style={{marginTop:14,padding:11,background:'rgba(0,0,0,.3)',borderRadius:11}}>
              <div style={{fontSize:10,color:'var(--mt)',textTransform:'uppercase',letterSpacing:1,marginBottom:3}}>Balansingiz</div>
              <div style={{fontSize:22,fontWeight:800,color:'var(--gold)',fontFamily:'Space Mono,monospace'}}>{fmt(bal)} so'm</div>
            </div>
          </div>
          {/* Stats */}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:9}}>
            <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:13,textAlign:'center'}}>
              <div style={{fontSize:20,fontWeight:800,fontFamily:'Space Mono,monospace'}}>{orders_count}</div>
              <div style={{fontSize:10,color:'var(--mt)',marginTop:2,textTransform:'uppercase',letterSpacing:.5}}>Buyurtmalar</div>
            </div>
            <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:13,textAlign:'center'}}>
              <div style={{fontSize:20,fontWeight:800,fontFamily:'Space Mono,monospace'}}>{referrals}</div>
              <div style={{fontSize:10,color:'var(--mt)',marginTop:2,textTransform:'uppercase',letterSpacing:.5}}>Referrallar</div>
            </div>
          </div>
          {/* Links */}
          {[
            { icon:'💰', label:"Hisob to'ldirish",  fn:onTopup    },
            { icon:'🤝', label:'Referral tizimi',    fn:onReferral },
            { icon:'📋', label:'Buyurtmalar tarixi', fn:onHistory  },
            supportLink && { icon:'💬', label:'Support',   fn:()=>openLink(supportLink) },
            channelLink && { icon:'📢', label:'Kanalimiz', fn:()=>openLink(channelLink) },
          ].filter(Boolean).map((item,i) => (
            <div key={i} onClick={item.fn} style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:'12px 14px',display:'flex',alignItems:'center',cursor:'pointer'}}>
              <span style={{fontSize:18,marginRight:10}}>{item.icon}</span>
              <span style={{flex:1,fontSize:13,fontWeight:600}}>{item.label}</span>
              <span style={{color:'var(--mt)'}}>›</span>
            </div>
          ))}
        </div>
      )}

      {/* ─── DEVELOPER TAB ─── */}
      {tab === 'dev' && (
        <div style={{padding:'12px 18px 0',display:'flex',flexDirection:'column',gap:10}}>
          {/* API TOKEN */}
          <div style={{background:'linear-gradient(135deg,#1a1535,#0f0e1e)',border:'1px solid rgba(124,92,252,.22)',borderRadius:16,padding:'16px'}}>
            <div style={{fontSize:14,fontWeight:800,marginBottom:4,display:'flex',alignItems:'center',gap:6}}>
              🔑 API Token
            </div>
            <div style={{fontSize:11,color:'var(--mt)',marginBottom:12,lineHeight:1.5}}>
              Token orqali Stars va Premium sotib olishingiz mumkin. Pul <b style={{color:'var(--gold)'}}>sizning balansingizdan</b> yechiladi.
            </div>
            {token ? (
              <>
                <div style={{background:'rgba(0,0,0,.4)',borderRadius:10,padding:'10px 12px',marginBottom:10,fontFamily:'Space Mono,monospace',fontSize:10,color:'var(--pur2)',wordBreak:'break-all'}}>
                  {token}
                </div>
                <div style={{display:'flex',gap:8}}>
                  <button onClick={copyToken} style={{flex:1,background:'linear-gradient(135deg,var(--pur),#5b3fd8)',border:'none',borderRadius:10,padding:'9px',color:'#fff',fontFamily:'Syne,sans-serif',fontSize:12,fontWeight:700,cursor:'pointer'}}>
                    📋 Nusxa olish
                  </button>
                  <button onClick={createToken} disabled={loading} style={{flex:1,background:'var(--s2)',border:'1px solid var(--bd)',borderRadius:10,padding:'9px',color:'var(--tx)',fontFamily:'Syne,sans-serif',fontSize:12,fontWeight:700,cursor:'pointer'}}>
                    🔄 Yangilash
                  </button>
                </div>
              </>
            ) : (
              <button onClick={createToken} disabled={loading} style={{width:'100%',background:'linear-gradient(135deg,var(--pur),#5b3fd8)',border:'none',borderRadius:11,padding:'12px',color:'#fff',fontFamily:'Syne,sans-serif',fontSize:13,fontWeight:700,cursor:'pointer',opacity:loading?0.6:1}}>
                {loading ? '⏳ Yuklanmoqda...' : '🔑 API Token olish'}
              </button>
            )}
          </div>

          {/* DOCS */}
          {docs && (
            <>
              {/* Narxlar */}
              <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:14,padding:'14px'}}>
                <div style={{fontSize:12,fontWeight:800,marginBottom:10,color:'var(--gold)'}}>💰 Joriy narxlar</div>
                {[
                  {label:'1 Stars',       val:fmt(docs.prices?.star||210)+' so\'m'},
                  {label:'Premium 3 oy',  val:fmt(docs.prices?.pm3||195000)+' so\'m'},
                  {label:'Premium 6 oy',  val:fmt(docs.prices?.pm6||370000)+' so\'m'},
                  {label:'Premium 12 oy', val:fmt(docs.prices?.pm12||680000)+' so\'m'},
                ].map((p,i) => (
                  <div key={i} style={{display:'flex',justifyContent:'space-between',fontSize:12,padding:'5px 0',borderTop:i>0?'1px solid var(--bd)':'none'}}>
                    <span style={{color:'var(--mt)'}}>{p.label}</span>
                    <span style={{fontWeight:700}}>{p.val}</span>
                  </div>
                ))}
              </div>

              {/* Endpointlar */}
              <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:14,padding:'14px'}}>
                <div style={{fontSize:12,fontWeight:800,marginBottom:10,color:'var(--pur2)'}}>📡 API Endpointlar</div>
                {docs.endpoints && Object.entries(docs.endpoints).map(([section, eps]) => (
                  <div key={section} style={{marginBottom:10}}>
                    <div style={{fontSize:10,color:'var(--mt)',fontWeight:700,textTransform:'uppercase',letterSpacing:1,marginBottom:6}}>{section}</div>
                    {Object.entries(eps).map(([ep,desc]) => (
                      <div key={ep} style={{background:'var(--s2)',borderRadius:8,padding:'8px 10px',marginBottom:5}}>
                        <div style={{fontFamily:'Space Mono,monospace',fontSize:10,color:'var(--gold)',marginBottom:3}}>{ep}</div>
                        <div style={{fontSize:11,color:'var(--mt)'}}>{desc}</div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              {/* Misol */}
              <div style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:14,padding:'14px'}}>
                <div style={{fontSize:12,fontWeight:800,marginBottom:10,color:'var(--green)'}}>💡 Misol (Stars sotib olish)</div>
                <div style={{background:'rgba(0,0,0,.4)',borderRadius:8,padding:'10px',fontFamily:'Space Mono,monospace',fontSize:10,color:'var(--tx)',lineHeight:1.6,wordBreak:'break-all'}}>
                  {`curl -X POST ${docs.base}/api/v1/stars \\\n  -H "X-API-Key: YOUR_TOKEN" \\\n  -H "Content-Type: application/json" \\\n  -d '{"username":"friend","count":100}'`}
                </div>
              </div>

              {/* Muhim eslatma */}
              <div style={{background:'rgba(245,200,66,.05)',border:'1px solid rgba(245,200,66,.2)',borderRadius:13,padding:'13px'}}>
                <div style={{fontSize:12,fontWeight:700,color:'var(--gold)',marginBottom:6}}>⚠️ Muhim</div>
                <div style={{fontSize:11,color:'var(--mt)',lineHeight:1.6}}>
                  {docs.billing}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
