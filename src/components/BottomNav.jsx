const tabs = [
  { id:'home',    icon:'🏠', label:'BOSH'    },
  { id:'stars',   icon:'🌟', label:'STARS'   },
  { id:'premium', icon:'👑', label:'PREMIUM' },
  { id:'profile', icon:'👤', label:'PROFIL'  },
]

export default function BottomNav({ active, onChange }) {
  return (
    <div style={{
      position:'fixed',bottom:0,left:0,right:0,
      background:'rgba(10,10,15,.96)',
      backdropFilter:'blur(20px)',
      borderTop:'1px solid var(--bd)',
      display:'flex',maxWidth:430,margin:'0 auto',
      padding:'6px 0 18px',zIndex:100
    }}>
      {tabs.map(t => (
        <div key={t.id} onClick={() => onChange(t.id)} style={{
          flex:1,display:'flex',flexDirection:'column',
          alignItems:'center',gap:3,cursor:'pointer',padding:4
        }}>
          <div style={{
            fontSize:19,
            filter:active===t.id?'drop-shadow(0 0 5px rgba(245,200,66,.55))':'none',
            transition:'filter .2s'
          }}>{t.icon}</div>
          <div style={{
            fontSize:9,fontWeight:700,letterSpacing:'.5px',
            color:active===t.id?'var(--gold)':'var(--mt)',
            transition:'color .2s'
          }}>{t.label}</div>
        </div>
      ))}
    </div>
  )
}
