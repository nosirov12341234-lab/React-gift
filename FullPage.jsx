export default function FullPage({ open, onClose, title, children }) {
  return (
    <div style={{
      position:'fixed',inset:0,zIndex:200,
      background:'var(--bg)',
      overflowY:'auto',paddingBottom:30,
      display:open?'block':'none',
      animation:open?'slideUp .3s cubic-bezier(.34,1.2,.64,1)':'none'
    }}>
      {/* Header */}
      <div style={{
        position:'sticky',top:0,zIndex:10,
        padding:'14px 18px',
        display:'flex',alignItems:'center',gap:12,
        background:'rgba(10,10,15,.92)',backdropFilter:'blur(16px)',
        borderBottom:'1px solid var(--bd)'
      }}>
        <button onClick={onClose} style={{
          width:36,height:36,borderRadius:10,
          background:'var(--s2)',border:'1px solid var(--bd)',
          display:'flex',alignItems:'center',justifyContent:'center',
          fontSize:18,cursor:'pointer',flexShrink:0,color:'var(--tx)'
        }}>✕</button>
        <div style={{fontSize:18,fontWeight:800}}>{title}</div>
      </div>
      {children}
    </div>
  )
}
