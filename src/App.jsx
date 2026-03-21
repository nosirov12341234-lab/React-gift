import { useState, useEffect } from 'react'
import StarsBg from './components/StarsBg.jsx'
import Header from './components/Header.jsx'
import BottomNav from './components/BottomNav.jsx'
import { Toast, useToast } from './components/Toast.jsx'
import Home from './pages/Home.jsx'
import Stars from './pages/Stars.jsx'
import Premium from './pages/Premium.jsx'
import TopUp from './pages/TopUp.jsx'
import History from './pages/History.jsx'
import Referral from './pages/Referral.jsx'
import Profile from './pages/Profile.jsx'
import { getSettings, getTop10 } from './api.js'
import { G } from './styles.js'

// Inject global CSS
const style = document.createElement('style')
style.textContent = G
document.head.appendChild(style)

const tgApp = window.Telegram?.WebApp
const TG_USER = tgApp?.initDataUnsafe?.user || {}
const UID = TG_USER.id || 0

export default function App() {
  const [page, setPage]       = useState('home')
  const [settings, setSettings] = useState({
    bal:0, prices:{star:210,pm3:195000,pm6:370000,pm12:680000},
    minStars:50, refBonus:5000, name:'', username:'',
    orders_count:0, referrals:0, ref_earned:0,
    supportLink:'', channelLink:''
  })
  const [starsOpen,   setStarsOpen]   = useState(false)
  const [premOpen,    setPremOpen]    = useState(false)
  const [topupOpen,   setTopupOpen]   = useState(false)
  const { toast, show: showToast } = useToast()

  // Load settings
  useEffect(() => {
    loadAll()
  }, [])

  async function loadAll() {
    try {
      const [s, td, tw, tm, ta] = await Promise.all([
        getSettings(UID),
        getTop10('daily'),
        getTop10('weekly'),
        getTop10('monthly'),
        getTop10('all'),
      ])
      setSettings(prev => ({
        ...prev,
        bal          : s.balance || 0,
        prices       : s.prices  || prev.prices,
        minStars     : s.min_stars || 50,
        refBonus     : s.referral_bonus || 5000,
        name         : TG_USER.first_name || s.name || '',
        username     : TG_USER.username   || s.username || '',
        orders_count : s.orders_count || 0,
        referrals    : s.referrals    || 0,
        ref_earned   : s.ref_earned   || 0,
        supportLink  : s.support_link  || '',
        channelLink  : s.channel_link  || '',
        top_daily    : td.top || [],
        top_weekly   : tw.top || [],
        top_monthly  : tm.top || [],
        top_all      : ta.top || [],
      }))
    } catch(e) {
      console.error('loadAll:', e)
    }
  }

  function handleNav(p) {
    if (p === 'stars')   { setStarsOpen(true);  return }
    if (p === 'premium') { setPremOpen(true);   return }
    setPage(p)
  }

  return (
    <div style={{position:'relative',minHeight:'100vh'}}>
      <StarsBg />

      <div style={{position:'relative',zIndex:1,maxWidth:430,margin:'0 auto'}}>
        <Header
          bal={settings.bal}
          onTopup={() => setTopupOpen(true)}
        />

        {/* PAGES */}
        {page==='home' && (
          <Home
            settings={settings}
            onOpenStars={()=>setStarsOpen(true)}
            onOpenPremium={()=>setPremOpen(true)}
            onOpenTopup={()=>setTopupOpen(true)}
            onNav={handleNav}
          />
        )}
        {page==='history' && (
          <History uid={UID} onBack={()=>setPage('home')} />
        )}
        {page==='referral' && (
          <Referral uid={UID} onBack={()=>setPage('home')} showToast={showToast} />
        )}
        {page==='profile' && (
          <Profile
            settings={settings}
            tgUser={TG_USER}
            onTopup={()=>setTopupOpen(true)}
            onReferral={()=>setPage('referral')}
            onHistory={()=>setPage('history')}
            showToast={showToast}
          />
        )}

        <BottomNav active={page} onChange={handleNav} />
      </div>

      {/* FULL PAGES */}
      <Stars
        open={starsOpen}
        onClose={()=>setStarsOpen(false)}
        settings={settings}
        showToast={showToast}
        uid={UID}
        tgUser={TG_USER}
      />
      <Premium
        open={premOpen}
        onClose={()=>setPremOpen(false)}
        settings={settings}
        showToast={showToast}
        uid={UID}
        tgUser={TG_USER}
      />
      <TopUp
        open={topupOpen}
        onClose={()=>setTopupOpen(false)}
        showToast={showToast}
        uid={UID}
      />

      <Toast toast={toast} />
    </div>
  )
}
