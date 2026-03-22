"""
U-Gift Flask Server - Final versiya
- /api/buy endpoint (tg.sendData o'rniga)
- Referral to'liq ishlaydi
- Developer API (token bilan)
- Faqat Click to'lov
- Admin orqali to'ldirish
"""
import json, os, asyncio, secrets, hashlib
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

WEBAPP_DIR       = os.path.join(os.path.expanduser("~"), "webapp")
app              = Flask(__name__, static_folder=WEBAPP_DIR, static_url_path="")
DB               = os.path.join(os.path.expanduser("~"), "ugift-react", "database.json")
QULAYPAY_KEY     = os.getenv("QULAYPAY_API_KEY", "")
BOT_TOKEN        = os.getenv("BOT_TOKEN", "")
SUPER_ADMIN_ID   = int(os.getenv("ADMIN_ID", "0"))
TON_API_KEY      = os.getenv("TON_API_KEY", "")
FRAGMENT_COOKIES = os.getenv("FRAGMENT_COOKIES", "")

def db():
    if os.path.exists(DB):
        with open(DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "users":{}, "orders":[], "admins":{},
        "promo_codes":{}, "pending_topups":{}, "api_keys":{},
        "settings":{
            "prices":{"star":210,"pm3":195000,"pm6":370000,"pm12":680000},
            "referral_bonus":5000, "min_stars":50,
            "required_channels":[], "logs_channel":None,
            "support_link":"", "channel_link":"",
            "logo_file_id":None, "bot_active":True,
        }
    }

def sdb(data):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fmt(n): return f"{int(n):,}".replace(",", " ")
def is_admin(uid): return int(uid) == SUPER_ADMIN_ID or str(uid) in db().get("admins", {})

async def send_tg(chat_id, text):
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            await s.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
    except: pass

async def send_log(text):
    d = db(); ch = d["settings"].get("logs_channel")
    if ch:
        try:
            import aiohttp
            async with aiohttp.ClientSession() as s:
                await s.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={"chat_id": ch, "text": text, "parse_mode": "HTML"})
        except: pass

def do_fragment_sync(order):
    try:
        from FragmentAPI import SyncFragmentAPI
        api = SyncFragmentAPI(cookies=FRAGMENT_COOKIES, wallet_api_key=TON_API_KEY)
        if order["service"] == "premium":
            r = api.gift_premium(order["username"], order["months"])
        elif order["service"] == "stars":
            r = api.buy_stars(order["username"], order["stars"])
        else: return False
        return bool(r)
    except Exception as e:
        print(f"[Fragment]: {e}"); return False

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()

# ─── REACT SPA ───
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if path.startswith("api/") or path.startswith("webhook/"):
        return jsonify({"error": "not found"}), 404
    full = os.path.join(WEBAPP_DIR, path)
    if path and os.path.exists(full):
        return send_from_directory(WEBAPP_DIR, path)
    return send_from_directory(WEBAPP_DIR, "index.html")

# ─── API: SETTINGS ───
@app.route("/api/settings")
def api_settings():
    uid = request.args.get("uid", "0")
    d   = db(); u = d["users"].get(str(uid), {}); s = d["settings"]
    return jsonify({
        "prices"        : s["prices"],
        "min_stars"     : s["min_stars"],
        "support_link"  : s.get("support_link", ""),
        "channel_link"  : s.get("channel_link", ""),
        "referral_bonus": s.get("referral_bonus", 5000),
        "balance"       : u.get("balance", 0),
        "referrals"     : u.get("referrals", 0),
        "ref_earned"    : u.get("ref_earned", 0),
        "username"      : u.get("username", ""),
        "name"          : u.get("name", ""),
        "orders_count"  : len(u.get("orders", [])),
    })

# ─── API: BUY (asosiy) ───
@app.route("/api/buy", methods=["POST"])
def api_buy():
    data     = request.json or {}
    uid      = str(data.get("uid", "0"))
    service  = data.get("service", "")
    username = data.get("username", "").strip().lstrip("@")
    price    = int(data.get("price", 0))
    stars    = data.get("stars")
    months   = data.get("months")
    promo    = data.get("promo", "").upper().strip()
    d        = db()

    if uid not in d["users"]:
        return jsonify({"success": False, "error": "Avval /start bosing"})
    if not username:
        return jsonify({"success": False, "error": "Username kiritilmagan"})

    bal = d["users"][uid].get("balance", 0)
    if bal < price:
        return jsonify({"success": False,
                       "error": f"Balans yetarli emas. Kerak: {fmt(price)} so'm, Sizda: {fmt(bal)} so'm"})

    # Promo
    if promo and promo in d.get("promo_codes", {}):
        pc = d["promo_codes"][promo]
        if promo not in d["users"][uid].get("promo_used", []):
            d["users"][uid].setdefault("promo_used", []).append(promo)
            pc["used"] = pc.get("used", 0) + 1

    d["users"][uid]["balance"] -= price
    svc_txt = f"⭐ Premium {months} oy" if service == "premium" else f"🌟 {fmt(stars or 0)} Stars"

    order = {
        "id"        : len(d["orders"]) + 1,
        "user_id"   : uid,
        "service"   : service,
        "username"  : username,
        "months"    : months,
        "stars"     : stars,
        "price"     : price,
        "status"    : "processing",
        "created_at": datetime.now().isoformat(),
    }
    d["orders"].append(order)
    d["users"][uid].setdefault("orders", []).append(order["id"])
    sdb(d)

    success = do_fragment_sync(order)
    d = db()

    if success:
        for o in d["orders"]:
            if o["id"] == order["id"]: o["status"] = "completed"
        sdb(d)
        run_async(send_tg(int(uid),
            f"🎉 <b>Muvaffaqiyatli yuborildi!</b>\n\n"
            f"🛍 {svc_txt}\n👤 @{username}\n💰 {fmt(price)} so'm\n\n✨ Rahmat!"))
        run_async(send_log(f"✅ #{order['id']} | {svc_txt} → @{username} | {fmt(price)} so'm"))
        return jsonify({"success": True, "order_id": order["id"], "message": f"{svc_txt} yuborildi!"})
    else:
        d["users"][uid]["balance"] += price
        for o in d["orders"]:
            if o["id"] == order["id"]: o["status"] = "failed"
        sdb(d)
        run_async(send_log(f"❌ #{order['id']} | {svc_txt} XATO"))
        return jsonify({"success": False, "error": "Xato yuz berdi. Balans qaytarildi."})

# ─── API: PROMO CHECK ───
@app.route("/api/promo/check", methods=["POST"])
def api_promo_check():
    data    = request.json or {}
    code    = data.get("code", "").upper().strip()
    uid     = str(data.get("uid", "0"))
    product = data.get("product", "all")
    d       = db(); promos = d.get("promo_codes", {})
    if code not in promos:
        return jsonify({"success": False, "error": "Noto'g'ri promo kod"})
    promo = promos[code]
    if promo.get("product", "all") not in ("all", product):
        return jsonify({"success": False, "error": "Bu mahsulot uchun emas"})
    if promo.get("limit") and promo.get("used", 0) >= promo["limit"]:
        return jsonify({"success": False, "error": "Limit tugagan"})
    if code in d["users"].get(uid, {}).get("promo_used", []):
        return jsonify({"success": False, "error": "Allaqachon ishlatgansiz"})
    return jsonify({"success": True, "discount": promo["discount"]})

# ─── API: TOPUP (faqat Click) ───
@app.route("/api/topup/create", methods=["POST"])
def api_topup_create():
    data   = request.json or {}
    uid    = str(data.get("uid", "0"))
    amount = int(data.get("amount", 0))
    if amount < 5000:
        return jsonify({"success": False, "error": "Minimum 5 000 so'm"})
    import requests as req
    try:
        r = req.post(
            "https://api.qulaypay.uz/transaction/create",
            headers={"Authorization": f"Bearer {QULAYPAY_KEY}", "Content-Type": "application/json"},
            json={
                "access_token": QULAYPAY_KEY,
                "amount"      : amount,
                "comment"     : f"U-Gift balans | ID:{uid}",
                "provider"    : "click",
            },
            timeout=10
        )
        res = r.json()
        print(f"[Qulaypay]: {res}")
        if res.get("status") == "success":
            txn = res["transaction"]
            d   = db()
            d.setdefault("pending_topups", {})[txn["id"]] = {
                "uid": uid, "amount": amount, "created_at": datetime.now().isoformat()
            }
            sdb(d)
            return jsonify({"success": True, "payment_url": txn["payment_url"]})
        else:
            return jsonify({"success": False, "error": str(res.get("message", "Xato"))})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ─── API: HISTORY ───
@app.route("/api/history")
def api_history():
    uid    = request.args.get("uid", "0")
    d      = db()
    orders = [o for o in d["orders"] if o["user_id"] == str(uid)][-20:]
    return jsonify({"orders": list(reversed(orders))})

# ─── API: TOP10 ───
@app.route("/api/top10")
def api_top10():
    period = request.args.get("period", "daily")
    d      = db(); today = datetime.now().date().isoformat(); top = {}
    for o in d["orders"]:
        if o["status"] != "completed": continue
        if period == "daily" and o["created_at"][:10] != today: continue
        elif period == "weekly":
            from datetime import timedelta
            if o["created_at"][:10] < (datetime.now()-timedelta(days=7)).date().isoformat(): continue
        elif period == "monthly":
            if o["created_at"][:7] != today[:7]: continue
        uid_o = o["user_id"]; stars = o.get("stars", 0) or 0
        if uid_o not in top: top[uid_o] = {"stars": 0, "orders": 0}
        top[uid_o]["stars"] += stars; top[uid_o]["orders"] += 1
    result = []
    for uid_o, stats in sorted(top.items(), key=lambda x: x[1]["stars"], reverse=True)[:10]:
        u = d["users"].get(uid_o, {})
        result.append({"uid":uid_o,"name":u.get("name","Foydalanuvchi"),"stars":stats["stars"],"orders":stats["orders"]})
    return jsonify({"top": result})

# ─── API: REFERRAL ───
@app.route("/api/referral")
def api_referral():
    uid = request.args.get("uid", "0")
    d   = db(); u = d["users"].get(str(uid), {})
    import requests as req
    try:
        me   = req.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=5).json()
        link = f"https://t.me/{me['result']['username']}?start=ref_{uid}"
    except: link = ""
    return jsonify({
        "link"      : link,
        "referrals" : u.get("referrals", 0),
        "ref_earned": u.get("ref_earned", 0),
        "bonus"     : d["settings"].get("referral_bonus", 5000),
        "list"      : [
            {
                "uid" : rid,
                "name": d["users"].get(rid, {}).get("name", "Foydalanuvchi"),
                "date": d["users"].get(rid, {}).get("joined", "")[:10]
            }
            for rid in u.get("referral_list", [])
        ]
    })

# ─── DEVELOPER API ───
@app.route("/api/dev/token", methods=["POST"])
def api_dev_token():
    """Developer API token olish"""
    data = request.json or {}
    uid  = str(data.get("uid", "0"))
    if not is_admin(uid):
        return jsonify({"success": False, "error": "Ruxsat yo'q"})
    d     = db()
    token = secrets.token_hex(32)
    d.setdefault("api_keys", {})[token] = {
        "uid"       : uid,
        "created_at": datetime.now().isoformat(),
        "active"    : True
    }
    sdb(d)
    return jsonify({"success": True, "token": token})

def check_api_token():
    """API token tekshirish"""
    token = request.headers.get("X-API-Key", "")
    d     = db()
    return d.get("api_keys", {}).get(token, {}).get("active", False)

@app.route("/api/dev/stats")
def api_dev_stats():
    """Developer: statistika"""
    if not check_api_token():
        return jsonify({"error": "Noto'g'ri API token"}), 401
    d     = db(); today = datetime.now().date().isoformat()
    orders_done = [o for o in d["orders"] if o["status"] == "completed"]
    t_orders    = [o for o in orders_done if o["created_at"][:10] == today]
    return jsonify({
        "users"          : len(d["users"]),
        "orders_total"   : len(d["orders"]),
        "orders_done"    : len(orders_done),
        "orders_failed"  : len([o for o in d["orders"] if o["status"] == "failed"]),
        "revenue_total"  : sum(o["price"] for o in orders_done),
        "revenue_today"  : sum(o["price"] for o in t_orders),
        "orders_today"   : len(t_orders),
        "promo_codes"    : len(d.get("promo_codes", {})),
        "prices"         : d["settings"]["prices"],
    })

@app.route("/api/dev/prices", methods=["POST"])
def api_dev_prices():
    """Developer: narxlarni yangilash"""
    if not check_api_token():
        return jsonify({"error": "Noto'g'ri API token"}), 401
    data = request.json or {}
    d    = db()
    for key in ["star", "pm3", "pm6", "pm12"]:
        if key in data and isinstance(data[key], int) and data[key] > 0:
            d["settings"]["prices"][key] = data[key]
    sdb(d)
    return jsonify({"success": True, "prices": d["settings"]["prices"]})

@app.route("/api/dev/users")
def api_dev_users():
    """Developer: foydalanuvchilar ro'yxati"""
    if not check_api_token():
        return jsonify({"error": "Noto'g'ri API token"}), 401
    d      = db()
    page   = int(request.args.get("page", 1))
    limit  = int(request.args.get("limit", 20))
    users  = list(d["users"].items())
    total  = len(users)
    start  = (page - 1) * limit
    end    = start + limit
    result = []
    for uid, u in users[start:end]:
        result.append({
            "uid"       : uid,
            "name"      : u.get("name", ""),
            "username"  : u.get("username", ""),
            "balance"   : u.get("balance", 0),
            "orders"    : len(u.get("orders", [])),
            "referrals" : u.get("referrals", 0),
            "banned"    : u.get("banned", False),
            "joined"    : u.get("joined", "")[:10],
        })
    return jsonify({"users": result, "total": total, "page": page, "pages": (total+limit-1)//limit})

@app.route("/api/dev/orders")
def api_dev_orders():
    """Developer: buyurtmalar"""
    if not check_api_token():
        return jsonify({"error": "Noto'g'ri API token"}), 401
    d      = db()
    page   = int(request.args.get("page", 1))
    limit  = int(request.args.get("limit", 20))
    orders = list(reversed(d["orders"]))
    total  = len(orders)
    start  = (page - 1) * limit
    end    = start + limit
    return jsonify({"orders": orders[start:end], "total": total, "page": page})

@app.route("/api/dev/docs")
def api_dev_docs():
    """Developer API hujjati"""
    base = request.host_url.rstrip("/")
    return jsonify({
        "name"   : "U-Gift Developer API",
        "version": "1.0",
        "base_url": base,
        "auth"   : "Header: X-API-Key: YOUR_TOKEN",
        "token_url": f"{base}/api/dev/token (POST, uid kerak, faqat admin)",
        "endpoints": {
            "GET  /api/dev/stats"          : "Statistika",
            "GET  /api/dev/users"          : "Foydalanuvchilar (page, limit)",
            "GET  /api/dev/orders"         : "Buyurtmalar (page, limit)",
            "POST /api/dev/prices"         : "Narxlarni yangilash {star, pm3, pm6, pm12}",
            "GET  /api/settings?uid=ID"    : "Foydalanuvchi sozlamalari",
            "GET  /api/history?uid=ID"     : "Buyurtmalar tarixi",
            "GET  /api/top10?period=daily" : "Top 10 (daily/weekly/monthly/all)",
            "GET  /api/referral?uid=ID"    : "Referral ma'lumotlari",
        },
        "example": {
            "get_stats": f"curl -H 'X-API-Key: TOKEN' {base}/api/dev/stats",
            "update_prices": f"curl -X POST -H 'X-API-Key: TOKEN' -H 'Content-Type: application/json' -d '{{\"star\":250}}' {base}/api/dev/prices"
        }
    })

# ─── QULAYPAY WEBHOOK ───
@app.route("/webhook/qulaypay", methods=["POST"])
def qulaypay_webhook():
    data = request.json
    if not data: return jsonify({"status": "error"}), 400
    print(f"[Qulaypay webhook]: {data}")
    txn    = data.get("transaction") or {}
    txn_id = txn.get("id") or data.get("id")
    status = txn.get("status") or data.get("status")
    amount = txn.get("amount") or data.get("amount")
    if status != "paid": return jsonify({"status": "ok"})
    d = db(); pending = d.get("pending_topups", {})
    if txn_id not in pending: return jsonify({"status": "ok"})
    topup = pending[txn_id]; uid = topup["uid"]
    amt   = int(topup.get("amount") or amount or 0)
    if uid in d["users"]:
        d["users"][uid]["balance"] = d["users"][uid].get("balance", 0) + amt
        del d["pending_topups"][txn_id]; sdb(d)
        run_async(send_tg(int(uid),
            f"✅ <b>Balansingiz to'ldirildi!</b>\n\n"
            f"➕ <b>+{fmt(amt)} so'm</b>\n"
            f"💰 Joriy: <b>{fmt(d['users'][uid]['balance'])} so'm</b>"))
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print(f"✅ Webapp: {WEBAPP_DIR}")
    print(f"✅ DB: {DB}")
    app.run(host="0.0.0.0", port=5000, debug=False)
