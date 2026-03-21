export default function RecipientSelector({ value, onChange, color, usernameVal, onUsernameChange }) {
  const gold = color !== 'purple'
  const activeStyle = gold
    ? { borderColor:'var(--gold)', background:'var(--ga)', color:'var(--gold)' }
    : { borderColor:'var(--pur)', background:'var(--pa)', color:'var(--pur2)' }
  const inactiveStyle = { borderColor:'var(--bd)', background:'transparent', color:'var(--mt)' }

  return (
    <>
      <div style={{padding:'13px 18px 7px',fontSize:10,color:'var(--mt)',fontWeight:700,textTransform:'uppercase',letterSpacing:1}}>
        Kimga yuboramiz?
      </div>
      <div style={{display:'flex',gap:9,padding:'0 18px'}}>
        {['self','other'].map(t => (
          <button key={t} onClick={() => onChange(t)} style={{
            flex:1,padding:'11px 8px',borderRadius:12,
            border:`1.5px solid`,cursor:'pointer',
            fontFamily:'Syne,sans-serif',fontSize:12,fontWeight:700,
            display:'flex',alignItems:'center',justifyContent:'center',gap:6,
            transition:'all .2s',
            ...(value===t ? activeStyle : inactiveStyle)
          }}>
            {t==='self' ? '👤 O\'zimga' : '👥 Boshqaga'}
          </button>
        ))}
      </div>

      {value === 'other' && (
        <div style={{
          margin:'9px 18px 0',
          background:'var(--s1)',
          border:`1.5px solid ${gold?'var(--bd)':'var(--bd)'}`,
          borderRadius:13,padding:'12px 14px',
          transition:'border-color .2s'
        }}>
          <div style={{fontSize:10,color:'var(--mt)',fontWeight:700,textTransform:'uppercase',letterSpacing:.5,marginBottom:5}}>
            Username
          </div>
          <div style={{display:'flex',alignItems:'center',gap:8}}>
            <span style={{fontSize:16}}>@</span>
            <input
              value={usernameVal}
              onChange={e => onUsernameChange(e.target.value.replace('@',''))}
              placeholder="username"
              style={{
                flex:1,background:'transparent',border:'none',outline:'none',
                color:'var(--tx)',fontFamily:'Syne,sans-serif',fontSize:15
              }}
            />
          </div>
        </div>
      )}
    </>
  )
}
