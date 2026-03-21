export default function Header({ bal, onTopup }) {
  const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

  return (
    <div style={{
      position:'sticky',top:0,zIndex:50,
      padding:'13px 18px',
      display:'flex',alignItems:'center',justifyContent:'space-between',
      background:'rgba(10,10,15,.9)',backdropFilter:'blur(16px)',
      borderBottom:'1px solid var(--bd)'
    }}>
      {/* Logo */}
      <div style={{display:'flex',alignItems:'center',gap:9}}>
        <div style={{
          width:34,height:34,
          background:'linear-gradient(135deg,var(--gold),var(--gold2))',
          borderRadius:10,display:'flex',alignItems:'center',justifyContent:'center',
          fontSize:17,boxShadow:'0 0 14px rgba(245,200,66,.3)'
        }}>⭐</div>
        <span style={{
          fontSize:17,fontWeight:800,letterSpacing:'1.5px',
          background:'linear-gradient(90deg,var(--gold),var(--pur2))',
          WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'
        }}>U-GIFT</span>
      </div>

      {/* Right */}
      <div style={{display:'flex',alignItems:'center',gap:8}}>
        {/* Plus button */}
        <button onClick={onTopup} style={{
          width:32,height:32,
          background:'linear-gradient(135deg,var(--pur),#5b3fd8)',
          border:'none',borderRadius:9,
          display:'flex',alignItems:'center',justifyContent:'center',
          fontSize:18,fontWeight:700,color:'#fff',cursor:'pointer',
          transition:'all .2s'
        }}>＋</button>

        {/* Balance pill */}
        <div onClick={onTopup} style={{
          background:'var(--s2)',border:'1px solid var(--bd)',
          borderRadius:20,padding:'5px 11px',
          display:'flex',alignItems:'center',gap:5,
          fontSize:13,fontWeight:700,cursor:'pointer'
        }}>
          <span style={{fontSize:14}}>🪙</span>
          <span style={{color:'var(--gold)'}}>{fmt(bal)}</span>
          <span style={{color:'var(--mt)',fontSize:11}}>so'm</span>
        </div>
      </div>
    </div>
  )
}
