const BASE = ''

export async function getSettings(uid) {
  const r = await fetch(`${BASE}/api/settings?uid=${uid}`)
  return r.json()
}

export async function checkPromo(code, uid, product) {
  const r = await fetch(`${BASE}/api/promo/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, uid, product })
  })
  return r.json()
}

export async function createTopup(uid, amount) {
  const r = await fetch(`${BASE}/api/topup/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ uid, amount })
  })
  return r.json()
}

export async function getHistory(uid) {
  const r = await fetch(`${BASE}/api/history?uid=${uid}`)
  return r.json()
}

export async function getTop10(period = 'daily') {
  const r = await fetch(`${BASE}/api/top10?period=${period}`)
  return r.json()
}

export async function getReferral(uid) {
  const r = await fetch(`${BASE}/api/referral?uid=${uid}`)
  return r.json()
}
