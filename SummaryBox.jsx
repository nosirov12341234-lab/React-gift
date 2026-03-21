const fmt = n => Math.round(n).toLocaleString('ru-RU').replace(/\s/g,' ')

export default function SummaryBox({ rows, total, totalColor }) {
  return (
    <div style={{
      margin:'12px 18px 0',
      background:'var(--s1)',border:'1px solid var(--bd)',
      borderRadius:14,padding:'13px 15px'
    }}>
      {rows.map((r,i) => r && (
        <div key={i} style={{
          display:'flex',justifyContent:'space-between',alignItems:'center',
          padding:'5px 0',fontSize:13,
          borderTop:i>0?'1px solid var(--bd)':'none'
        }}>
          <span style={{color:'var(--mt)',fontWeight:500}}>{r.label}</span>
          <span style={{fontWeight:700,color:r.color||'var(--tx)'}}>{r.value}</span>
        </div>
      ))}
      <div style={{
        display:'flex',justifyContent:'space-between',alignItems:'center',
        padding:'9px 0 5px',
        borderTop:'1.5px dashed rgba(245,200,66,.2)',marginTop:2
      }}>
        <span style={{fontSize:14,fontWeight:800}}>To'lov</span>
        <span style={{
          fontSize:18,fontWeight:800,
          fontFamily:'Space Mono,monospace',
          color:totalColor||'var(--gold)'
        }}>{fmt(total)} so'm</span>
      </div>
    </div>
  )
}
