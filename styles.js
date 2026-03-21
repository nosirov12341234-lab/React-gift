export const G = `
  :root {
    --bg: #0a0a0f;
    --s1: #12121a;
    --s2: #1a1a26;
    --s3: #222232;
    --bd: rgba(255,255,255,0.07);
    --gold: #f5c842;
    --gold2: #ffaa00;
    --ga: rgba(245,200,66,0.1);
    --pur: #7c5cfc;
    --pur2: #a78bfa;
    --pa: rgba(124,92,252,0.1);
    --tx: #f0f0ff;
    --mt: #6b6b8a;
    --green: #22d3a5;
    --red: #ff4f6d;
  }

  * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html,body { height:100%; overflow-x:hidden; }
  body { background:var(--bg); color:var(--tx); font-family:'Syne',sans-serif; padding-bottom:72px; }

  body::before {
    content:'';
    position:fixed; top:-200px; left:50%;
    transform:translateX(-50%);
    width:700px; height:700px;
    background:radial-gradient(circle,rgba(124,92,252,.08),transparent 65%);
    pointer-events:none; z-index:0;
  }

  @keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
  @keyframes slideUp { from{transform:translateY(100%);opacity:0} to{transform:translateY(0);opacity:1} }
  @keyframes twinkle { 0%,100%{opacity:var(--o,.3);transform:scale(1)} 50%{opacity:.05;transform:scale(.4)} }

  .fade-up { animation: fadeUp .28s ease; }
  .slide-up { animation: slideUp .3s cubic-bezier(.34,1.2,.64,1); }
`
