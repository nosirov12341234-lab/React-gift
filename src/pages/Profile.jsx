const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function Profile({ settings, tgUser, onTopup, onReferral, onHistory, showToast }) {
  const { bal=0, orders_count=0, referrals=0, supportLink='', channelLink='' } = settings
  const name = tgUser?.first_name || settings.name || '—'
  const un   = tgUser?.username ? '@'+tgUser.username : settings.username ? '@'+settings.username : '—'
  const av   = name[0]?.toUpperCase() || 'U'

  function openLink(url) {
    const tg = window.Telegram?.WebApp
    if (url && tg) tg.openLink(url)
    else if (url) window.open(url,'_blank')
  }

  return (
    <div style={{position:'relative',zIndex:1,animation:'fadeUp .28s ease'}}>
      <div style={{padding:'16px 18px 0',fontSize:18,fontWeight:800}}>👤 Profil</div>
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
          { icon:'💰', label:'Hisob to\'ldirish', fn:onTopup },
          { icon:'🤝', label:'Referral tizimi',   fn:onReferral },
          { icon:'📋', label:'Buyurtmalar tarixi', fn:onHistory },
          supportLink && { icon:'💬', label:'Support', fn:()=>openLink(supportLink) },
          channelLink && { icon:'📢', label:'Kanalimiz', fn:()=>openLink(channelLink) },
        ].filter(Boolean).map((item,i) => (
          <div key={i} onClick={item.fn} style={{background:'var(--s1)',border:'1px solid var(--bd)',borderRadius:13,padding:'12px 14px',display:'flex',alignItems:'center',cursor:'pointer'}}>
            <span style={{fontSize:18,marginRight:10}}>{item.icon}</span>
            <span style={{flex:1,fontSize:13,fontWeight:600}}>{item.label}</span>
            <span style={{color:'var(--mt)'}}>›</span>
          </div>
        ))}
      </div>
    </div>
  )
}
