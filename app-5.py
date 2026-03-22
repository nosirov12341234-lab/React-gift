"""
U-Gift Flask Server - Final versiya
FragmentAPI - hash bilan
"""
import json, os, asyncio, secrets
import requests as req
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
FRAGMENT_COOKIES = os.getenv("FRAGMENT_COOKIES", "")
WALLET_MNEMONIC  = os.getenv("WALLET_MNEMONIC", "")
TON_API_KEY      = os.getenv("TON_API_KEY", "")

def get_fragment_hash():
    """Fragment.com dan hash avtomatik olish"""
    try:
        import re
        s = req.Session()
        for c in FRAGMENT_COOKIES.split(';'):
            c = c.strip()
            if '=' in c:
                k, v = c.split('=', 1)
                s.cookies.set(k.strip(), v.strip(), domain='fragment.com')
        s.headers['User-Agent'] = 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'
        r = s.get('https://fragment.com/', timeout=15)
        patterns = [r'"hash":"([^"]+)"', r"'hash':'([^']+)'", r'hash=([a-f0-9]{10,})']
        for p in patterns:
            m = re.search(p, r.text)
            if m:
                return m.group(1)
    except Exception as e:
        print(f"[Hash xato]: {e}")
    return os.getenv("FRAGMENT_HASH", "")

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

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()

def do_fragment_sync(order):
    try:
        from FragmentAPI import SyncFragmentAPI
        hash_val = get_fragment_hash()
        print(f"[Fragment hash]: {hash_val[:20] if hash_val else 'Topilmadi'}")
        api = SyncFragmentAPI(
            cookies       = FRAGMENT_COOKIES,
            hash_value    = hash_val,
            wallet_mnemonic = WALLET_MNEMONIC,
            wallet_api_key  = TON_API_KEY,
            
        )
        if order["service"] == "stars":
            r = api.buy_stars(order["username"], order["stars"])
        elif order["service"] == "premium":
            r = api.gift_premium(order["username"], order["months"])
        else:
            return False
        print(f"[Fragment result]: {r}")
        if hasattr(r, 'success'): return r.success
        if isinstance(r, dict): return r.get("success") or r.get("ok")
        return bool(r)
    except Exception as e:
        print(f"[Fragment xato]: {e}")
        return False

def process_order(uid, service, username, price, stars=None, months=None, promo="", source="app"):
    d = db()
    if uid not in d["users"]: return False, "Foydalanuvchi topilmadi"
    if not username: return False, "Username kiritilmagan"
    bal = d["users"][uid].get("balance", 0)
    if bal < price: return False, f"Balans yetarli emas. Kerak: {fmt(price)} so'm, Sizda: {fmt(bal)} so'm"
    if promo and promo in d.get("promo_codes", {}):
        pc = d["promo_codes"][promo]
        if promo not in d["users"][uid].get("promo_used", []):
            d["users"][uid].setdefault("promo_used", []).append(promo)
            pc["used"] = pc.get("used", 0) + 1
    d["users"][uid]["balance"] -= price
    svc_txt = f"⭐ Premium {months} oy" if service=="premium" else f"🌟 {fmt(stars or 0)} Stars"
    order = {
        "id": len(d["orders"])+1, "user_id": uid,
        "service": service, "username": username,
        "months": months, "stars": stars, "price": price,
        "status": "processing", "source": source,
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
        run_async(send_tg(int(uid), f"🎉 <b>Muvaffaqiyatli!</b>\n\n🛍 {svc_txt}\n👤 @{username}\n💰 {fmt(price)} so'm"))
        run_async(send_log(f"✅ #{order['id']} | {svc_txt} → @{username} | {fmt(price)} so'm | {source}"))
        return True, {"order_id": order["id"], "message": f"{svc_txt} yuborildi!"}
    else:
        d["users"][uid]["balance"] += price
        for o in d["orders"]:
            if o["id"] == order["id"]: o["status"] = "failed"
        sdb(d)
        run_async(send_log(f"❌ #{order['id']} | {svc_txt} XATO | {source}"))
        return False, "Xato yuz berdi. Balans qaytarildi."

def get_api_uid():
    token = request.headers.get("X-API-Key", "")
    if not token: return None
    d = db(); kd = d.get("api_keys", {}).get(token)
    if not kd or not kd.get("active"): return None
    d["api_keys"][token]["last_used"] = datetime.now().isoformat()
    d["api_keys"][token]["requests"]  = d["api_keys"][token].get("requests", 0) + 1
    sdb(d)
    return kd.get("uid")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if path.startswith("api/") or path.startswith("webhook/"): return jsonify({"error":"not found"}), 404
    full = os.path.join(WEBAPP_DIR, path)
    if path and os.path.exists(full): return send_from_directory(WEBAPP_DIR, path)
    return send_from_directory(WEBAPP_DIR, "index.html")

@app.route("/api/settings")
def api_settings():
    uid = request.args.get("uid", "0")
    d = db(); u = d["users"].get(str(uid), {}); s = d["settings"]
    return jsonify({
        "prices": s["prices"], "min_stars": s["min_stars"],
        "support_link": s.get("support_link",""), "channel_link": s.get("channel_link",""),
        "referral_bonus": s.get("referral_bonus", 5000),
        "balance": u.get("balance", 0), "referrals": u.get("referrals", 0),
        "ref_earned": u.get("ref_earned", 0), "username": u.get("username",""),
        "name": u.get("name",""), "orders_count": len(u.get("orders", [])),
    })

@app.route("/api/buy", methods=["POST"])
def api_buy():
    data = request.json or {}
    uid  = str(data.get("uid","0"))
    ok, result = process_order(
        uid=uid, service=data.get("service",""),
        username=data.get("username","").strip().lstrip("@"),
        price=int(data.get("price",0)),
        stars=data.get("stars"), months=data.get("months"),
        promo=data.get("promo","").upper().strip(), source="app"
    )
    if ok: return jsonify({"success": True, **result})
    return jsonify({"success": False, "error": result})

@app.route("/api/promo/check", methods=["POST"])
def api_promo_check():
    data = request.json or {}
    code = data.get("code","").upper().strip()
    uid  = str(data.get("uid","0"))
    product = data.get("product","all")
    d = db(); promos = d.get("promo_codes",{})
    if code not in promos: return jsonify({"success":False,"error":"Noto'g'ri promo kod"})
    promo = promos[code]
    if promo.get("product","all") not in ("all", product): return jsonify({"success":False,"error":"Bu mahsulot uchun emas"})
    if promo.get("limit") and promo.get("used",0) >= promo["limit"]: return jsonify({"success":False,"error":"Limit tugagan"})
    if code in d["users"].get(uid,{}).get("promo_used",[]): return jsonify({"success":False,"error":"Allaqachon ishlatgansiz"})
    return jsonify({"success":True,"discount":promo["discount"]})

@app.route("/api/topup/create", methods=["POST"])
def api_topup_create():
    data = request.json or {}
    uid  = str(data.get("uid","0"))
    amount = int(data.get("amount",0))
    if amount < 5000: return jsonify({"success":False,"error":"Minimum 5 000 so'm"})
    try:
        r = req.post(
            "https://api.qulaypay.uz/transaction/create",
            headers={"Authorization":f"Bearer {QULAYPAY_KEY}","Content-Type":"application/json"},
            json={"access_token":QULAYPAY_KEY,"amount":amount,"comment":f"U-Gift balans | ID:{uid}","provider":"click"},
            timeout=10
        )
        res = r.json(); print(f"[Qulaypay]: {res}")
        if res.get("status") == "success":
            txn = res["transaction"]
            d = db()
            d.setdefault("pending_topups",{})[txn["id"]] = {"uid":uid,"amount":amount,"created_at":datetime.now().isoformat()}
            sdb(d)
            return jsonify({"success":True,"payment_url":txn["payment_url"]})
        return jsonify({"success":False,"error":str(res.get("message","Xato"))})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)})

@app.route("/api/history")
def api_history():
    uid = request.args.get("uid","0"); d = db()
    orders = [o for o in d["orders"] if o["user_id"]==str(uid)][-20:]
    return jsonify({"orders":list(reversed(orders))})

@app.route("/api/top10")
def api_top10():
    period = request.args.get("period","daily"); d = db()
    today = datetime.now().date().isoformat(); top = {}
    for o in d["orders"]:
        if o["status"] != "completed": continue
        if period=="daily" and o["created_at"][:10] != today: continue
        elif period=="weekly":
            from datetime import timedelta
            if o["created_at"][:10] < (datetime.now()-timedelta(days=7)).date().isoformat(): continue
        elif period=="monthly":
            if o["created_at"][:7] != today[:7]: continue
        uid_o = o["user_id"]; stars = o.get("stars",0) or 0
        if uid_o not in top: top[uid_o] = {"stars":0,"orders":0}
        top[uid_o]["stars"] += stars; top[uid_o]["orders"] += 1
    result = []
    for uid_o, stats in sorted(top.items(), key=lambda x:x[1]["stars"], reverse=True)[:10]:
        u = d["users"].get(uid_o,{})
        result.append({"uid":uid_o,"name":u.get("name","Foydalanuvchi"),"stars":stats["stars"],"orders":stats["orders"]})
    return jsonify({"top":result})

@app.route("/api/referral")
def api_referral():
    uid = request.args.get("uid","0"); d = db(); u = d["users"].get(str(uid),{})
    try:
        me   = req.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe",timeout=5).json()
        link = f"https://t.me/{me['result']['username']}?start=ref_{uid}"
    except: link = ""
    ref_list = []
    for rid in u.get("referral_list",[]):
        ru = d["users"].get(rid,{})
        ref_list.append({"uid":rid,"name":ru.get("name","Foydalanuvchi"),"username":ru.get("username",""),"date":ru.get("joined","")[:10],"orders":len(ru.get("orders",[]))})
    return jsonify({"link":link,"referrals":u.get("referrals",0),"ref_earned":u.get("ref_earned",0),"bonus":d["settings"].get("referral_bonus",5000),"list":ref_list})

@app.route("/api/v1/balance")
def v1_balance():
    uid = get_api_uid()
    if not uid: return jsonify({"error":"Noto'g'ri API token"}), 401
    d = db(); u = d["users"].get(str(uid),{})
    return jsonify({"balance":u.get("balance",0),"orders_count":len(u.get("orders",[])),"referrals":u.get("referrals",0)})

@app.route("/api/v1/stars", methods=["POST"])
def v1_stars():
    uid = get_api_uid()
    if not uid: return jsonify({"error":"Noto'g'ri API token"}), 401
    data = request.json or {}
    username = data.get("username","").strip().lstrip("@")
    count    = int(data.get("count",0))
    d = db(); s = d["settings"]
    if count < s.get("min_stars",50): return jsonify({"error":f"Minimum {s.get('min_stars',50)} Stars"}), 400
    price = count * s["prices"]["star"]
    ok, result = process_order(uid=uid,service="stars",username=username,price=price,stars=count,source="api")
    if ok: return jsonify({"success":True,**result})
    return jsonify({"error":result}), 400

@app.route("/api/v1/premium", methods=["POST"])
def v1_premium():
    uid = get_api_uid()
    if not uid: return jsonify({"error":"Noto'g'ri API token"}), 401
    data = request.json or {}
    username = data.get("username","").strip().lstrip("@")
    months   = int(data.get("months",6))
    if months not in (3,6,12): return jsonify({"error":"months: 3, 6 yoki 12"}), 400
    d = db(); s = d["settings"]
    pkMap = {3:"pm3",6:"pm6",12:"pm12"}
    price = s["prices"][pkMap[months]]
    ok, result = process_order(uid=uid,service="premium",username=username,price=price,months=months,source="api")
    if ok: return jsonify({"success":True,**result})
    return jsonify({"error":result}), 400

@app.route("/api/v1/history")
def v1_history():
    uid = get_api_uid()
    if not uid: return jsonify({"error":"Noto'g'ri API token"}), 401
    d = db(); page = int(request.args.get("page",1)); limit = 20
    orders = [o for o in reversed(d["orders"]) if o["user_id"]==str(uid)]
    start = (page-1)*limit
    return jsonify({"orders":orders[start:start+limit],"total":len(orders),"page":page})

@app.route("/api/v1/token/create", methods=["POST"])
def v1_token_create():
    data = request.json or {}; uid = str(data.get("uid","0"))
    if uid not in db().get("users",{}): return jsonify({"error":"Avval /start bosing"}), 400
    d = db(); token = secrets.token_hex(32)
    old = [t for t,v in d.get("api_keys",{}).items() if v.get("uid")==uid]
    for t in old: del d["api_keys"][t]
    d.setdefault("api_keys",{})[token] = {"uid":uid,"created_at":datetime.now().isoformat(),"active":True,"requests":0,"last_used":None}
    sdb(d)
    return jsonify({"success":True,"token":token,"docs_url":"/api/v1/docs"})

@app.route("/api/v1/token/info")
def v1_token_info():
    uid = get_api_uid()
    if not uid: return jsonify({"error":"Noto'g'ri API token"}), 401
    token = request.headers.get("X-API-Key","")
    d = db(); kd = d["api_keys"][token]
    return jsonify({"uid":uid,"created_at":kd.get("created_at",""),"requests":kd.get("requests",0),"last_used":kd.get("last_used","")})

@app.route("/api/v1/token/refresh", methods=["POST"])
def v1_token_refresh():
    uid = get_api_uid()
    if not uid: return jsonify({"error":"Noto'g'ri API token"}), 401
    old = request.headers.get("X-API-Key","")
    d = db(); new_token = secrets.token_hex(32)
    del d["api_keys"][old]
    d["api_keys"][new_token] = {"uid":uid,"created_at":datetime.now().isoformat(),"active":True,"requests":0,"last_used":None}
    sdb(d); return jsonify({"success":True,"token":new_token})

@app.route("/api/v1/docs")
def v1_docs():
    base = request.host_url.rstrip("/")
    return jsonify({
        "name":"U-Gift Developer API v1","version":"1.0","base":base,
        "auth":{"type":"API Key","header":"X-API-Key: YOUR_TOKEN"},
        "billing":"API orqali xarid balansdan yechiladi",
        "endpoints":{
            "Token":{"POST /api/v1/token/create":"Yangi token","GET /api/v1/token/info":"Token info","POST /api/v1/token/refresh":"Yangilash"},
            "Hisob":{"GET /api/v1/balance":"Balans","GET /api/v1/history":"Tarix"},
            "Xarid":{"POST /api/v1/stars":"{username,count}","POST /api/v1/premium":"{username,months:3|6|12}"},
        },
        "prices": db()["settings"]["prices"],
    })

def check_admin_token():
    token = request.headers.get("X-API-Key","")
    d = db(); kd = d.get("api_keys",{}).get(token,{})
    if not kd or not kd.get("active"): return False
    return is_admin(kd.get("uid","0"))

@app.route("/api/dev/stats")
def api_dev_stats():
    if not check_admin_token(): return jsonify({"error":"Ruxsat yo'q"}), 401
    d = db(); today = datetime.now().date().isoformat()
    done = [o for o in d["orders"] if o["status"]=="completed"]
    t_ord = [o for o in done if o["created_at"][:10]==today]
    return jsonify({"users":len(d["users"]),"orders_total":len(d["orders"]),"orders_done":len(done),"revenue_total":sum(o["price"] for o in done),"revenue_today":sum(o["price"] for o in t_ord),"prices":d["settings"]["prices"]})

@app.route("/api/dev/users")
def api_dev_users():
    if not check_admin_token(): return jsonify({"error":"Ruxsat yo'q"}), 401
    d = db(); page = int(request.args.get("page",1)); limit = 20
    users = list(d["users"].items()); total = len(users)
    start = (page-1)*limit; end = start+limit
    result = [{"uid":uid,"name":u.get("name",""),"username":u.get("username",""),"balance":u.get("balance",0),"orders":len(u.get("orders",[])),"referrals":u.get("referrals",0),"banned":u.get("banned",False),"joined":u.get("joined","")[:10]} for uid,u in users[start:end]]
    return jsonify({"users":result,"total":total,"page":page,"pages":(total+limit-1)//limit})

@app.route("/api/dev/orders")
def api_dev_orders():
    if not check_admin_token(): return jsonify({"error":"Ruxsat yo'q"}), 401
    d = db(); page = int(request.args.get("page",1)); limit = 20
    orders = list(reversed(d["orders"])); total = len(orders)
    start = (page-1)*limit
    return jsonify({"orders":orders[start:start+limit],"total":total,"page":page})

@app.route("/api/dev/prices", methods=["POST"])
def api_dev_prices():
    if not check_admin_token(): return jsonify({"error":"Ruxsat yo'q"}), 401
    data = request.json or {}; d = db()
    for key in ["star","pm3","pm6","pm12"]:
        if key in data and isinstance(data[key],int) and data[key] > 0:
            d["settings"]["prices"][key] = data[key]
    sdb(d); return jsonify({"success":True,"prices":d["settings"]["prices"]})

@app.route("/webhook/qulaypay", methods=["POST"])
def qulaypay_webhook():
    data = request.json
    if not data: return jsonify({"status":"error"}), 400
    print(f"[Qulaypay]: {data}")
    txn    = data.get("transaction") or {}
    txn_id = txn.get("id") or data.get("id")
    status = txn.get("status") or data.get("status")
    amount = txn.get("amount") or data.get("amount")
    if status != "paid": return jsonify({"status":"ok"})
    d = db(); pending = d.get("pending_topups",{})
    if txn_id not in pending: return jsonify({"status":"ok"})
    topup = pending[txn_id]; uid = topup["uid"]; amt = int(topup.get("amount") or amount or 0)
    if uid in d["users"]:
        d["users"][uid]["balance"] = d["users"][uid].get("balance",0) + amt
        del d["pending_topups"][txn_id]; sdb(d)
        run_async(send_tg(int(uid), f"✅ <b>Balansingiz to'ldirildi!</b>\n\n➕ <b>+{fmt(amt)} so'm</b>\n💰 Joriy: <b>{fmt(d['users'][uid]['balance'])} so'm</b>"))
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    print(f"✅ Webapp: {WEBAPP_DIR}")
    print(f"✅ DB: {DB}")
    app.run(host="0.0.0.0", port=5000, debug=False)
