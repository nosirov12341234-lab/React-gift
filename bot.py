"""
U-Gift Bot - Final versiya
3 xil to'lov: Avtomatik karta, Screenshot, Admin orqali
"""
import asyncio, logging, json, os, re, secrets
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, MenuButtonDefault
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN      = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TON_API_KEY    = os.getenv("TON_API_KEY", "")
WEB_URL        = os.getenv("WEB_URL", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())
DB  = os.path.join(os.path.expanduser("~"), "ugift-react", "database.json")

def db():
    if os.path.exists(DB):
        with open(DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "users":{}, "orders":[], "admins":{},
        "promo_codes":{}, "pending_topups":{}, "api_keys":{},
        "settings":{
            "bot_active":True, "min_stars":50,
            "referral_bonus":5000, "required_channels":[],
            "logs_channel":None, "support_link":"",
            "channel_link":"", "logo_file_id":None,
            "prices":{"star":210,"pm3":195000,"pm6":370000,"pm12":680000},
            "card_number":"", "card_holder":"",
            "card_wait_minutes":5, "card_bot_id":0,
        }
    }

def sdb(data):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_admin(uid): return uid == SUPER_ADMIN_ID or str(uid) in db().get("admins", {})
def is_super(uid): return uid == SUPER_ADMIN_ID
def fmt(n): return f"{int(n):,}".replace(",", " ")

class A(StatesGroup):
    broadcast=State(); channel=State(); logs=State()
    support=State(); channel_link=State(); admin_id=State()
    ban_id=State(); ref_bonus=State(); promo_code=State()
    promo_disc=State(); promo_limit=State(); promo_product=State()
    price_key=State(); logo=State(); min_stars=State()
    card_number=State(); card_holder=State()
    card_wait=State(); card_bot_id=State()
    card_topup=State(); screenshot_topup=State()
    give_bal=State()

async def send_log(text):
    d = db(); ch = d["settings"].get("logs_channel")
    if ch:
        try: await bot.send_message(ch, text, parse_mode="HTML")
        except: pass

async def check_sub(uid):
    d = db()
    for ch in d["settings"]["required_channels"]:
        try:
            m = await bot.get_chat_member(ch, uid)
            if m.status in ["left","kicked"]: return False
        except: pass
    return True

async def remove_menu_button():
    try: await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
    except: pass

def make_kb(channel_link="", support_link=""):
    rows = []
    if WEB_URL and WEB_URL.startswith("https://"):
        rows.append([InlineKeyboardButton(text="🛍 Gift Market ni ochish", web_app=WebAppInfo(url=WEB_URL))])
    row = []
    if channel_link: row.append(InlineKeyboardButton(text="📢 Kanal", url=channel_link))
    if support_link: row.append(InlineKeyboardButton(text="💬 Support", url=support_link))
    if row: rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

def generate_unique_amount(base_amount: int) -> int:
    """Band bo'lmagan unikal summa topish"""
    d = db(); now = datetime.now()
    active = set()
    for t in d.get("pending_topups", {}).values():
        if t.get("method") != "card": continue
        exp = t.get("expires","")
        try:
            if datetime.fromisoformat(exp) > now:
                active.add(t.get("unique_amount", 0))
        except: pass
    for extra in range(10):
        candidate = base_amount + extra
        if candidate not in active:
            return candidate
    return base_amount

# ─── START ───
@dp.message(Command("start"))
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    d = db(); uid = str(msg.from_user.id)
    if not d["settings"]["bot_active"] and not is_admin(msg.from_user.id):
        await msg.answer("🔧 Bot hozirda o'chirilgan."); return
    if uid not in d["users"]:
        d["users"][uid] = {
            "balance":0, "orders":[], "referrals":0, "ref_earned":0,
            "joined":datetime.now().isoformat(), "banned":False,
            "promo_used":[], "referral_list":[], "referred_by":None,
            "username":msg.from_user.username or "",
            "name":msg.from_user.full_name or "",
        }
        args = msg.text.split()
        if len(args) > 1 and args[1].startswith("ref_"):
            ref_id = args[1][4:]
            if ref_id in d["users"] and ref_id != uid:
                bonus = d["settings"]["referral_bonus"]
                d["users"][ref_id]["balance"] = d["users"][ref_id].get("balance",0) + bonus
                d["users"][ref_id]["referrals"] = d["users"][ref_id].get("referrals",0) + 1
                d["users"][ref_id]["ref_earned"] = d["users"][ref_id].get("ref_earned",0) + bonus
                d["users"][ref_id].setdefault("referral_list",[]).append(uid)
                d["users"][uid]["referred_by"] = ref_id
                try: await bot.send_message(int(ref_id), f"🎉 Yangi referral!\n➕ <b>+{fmt(bonus)} so'm</b>!", parse_mode="HTML")
                except: pass
        sdb(d)
    else:
        d["users"][uid]["username"] = msg.from_user.username or ""
        d["users"][uid]["name"] = msg.from_user.full_name or ""
        sdb(d)
    d = db()
    if d["users"][uid].get("banned"): await msg.answer("🚫 Bloklangansiz."); return
    args = msg.text.split()
    if len(args) > 1 and args[1] == "admin" and is_admin(msg.from_user.id):
        await cmd_admin(msg, state); return
    if not await check_sub(msg.from_user.id):
        chs = d["settings"]["required_channels"]
        btns = [[InlineKeyboardButton(text=f"📢 {ch}", url=f"https://t.me/{ch.lstrip('@')}")] for ch in chs]
        btns.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
        await msg.answer("📢 <b>Kanallarga obuna bo'ling:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
        return
    bal = d["users"][uid].get("balance",0)
    logo = d["settings"].get("logo_file_id")
    channel = d["settings"].get("channel_link","")
    support = d["settings"].get("support_link","")
    text = (f"👋 <b>Salom, {msg.from_user.first_name}!</b>\n\n"
            f"⭐ <b>U-Gift Market</b>\n\n"
            f"💰 Balans: <b>{fmt(bal)} so'm</b>\n\n"
            f"👇 Quyidagi tugmani bosib marketga kiring:")
    kb = make_kb(channel, support)
    if logo: await msg.answer_photo(logo, caption=text, parse_mode="HTML", reply_markup=kb)
    else: await msg.answer(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "check_sub")
async def cb_check_sub(cb: types.CallbackQuery, state: FSMContext):
    if await check_sub(cb.from_user.id):
        await cb.message.delete()
        await cmd_start(cb.message, state)
    else: await cb.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)

# ─── TO'LOV TURLARI ───
@dp.message(Command("tolov"))
async def cmd_topup(msg: types.Message):
    d = db(); uid = str(msg.from_user.id)
    if uid not in d["users"]: await msg.answer("Avval /start bosing"); return
    card = d["settings"].get("card_number","")
    support = d["settings"].get("support_link","")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Avtomatik (karta)", callback_data="topup_auto")],
        [InlineKeyboardButton(text="📸 Screenshot orqali", callback_data="topup_screen")],
        [InlineKeyboardButton(text="👨‍💼 Admin orqali", url=support if support else "https://t.me/")],
    ])
    await msg.answer(
        f"💰 <b>Hisob to'ldirish</b>\n\n"
        f"To'lov usulini tanlang:",
        parse_mode="HTML", reply_markup=kb
    )

# ─── AVTOMATIK TO'LOV ───
@dp.callback_query(F.data == "topup_auto")
async def cb_topup_auto(cb: types.CallbackQuery, state: FSMContext):
    d = db()
    card = d["settings"].get("card_number","")
    if not card:
        await cb.answer("❌ Karta sozlanmagan!", show_alert=True); return
    await cb.message.edit_text(
        f"💳 <b>Avtomatik to'ldirish</b>\n\n"
        f"Qancha so'm to'ldirmoqchisiz?\n"
        f"<i>Minimum: 5 000 so'm</i>",
        parse_mode="HTML"
    )
    await state.set_state(A.card_topup)

@dp.message(A.card_topup)
async def enter_card_topup(msg: types.Message, state: FSMContext):
    try:
        amount = int(msg.text.replace(" ","").replace(",",""))
        if amount < 5000: await msg.answer("❌ Minimum 5 000 so'm!"); return
        d = db(); uid = str(msg.from_user.id)
        card = d["settings"].get("card_number","")
        holder = d["settings"].get("card_holder","")
        wait = d["settings"].get("card_wait_minutes", 5)
        unique = generate_unique_amount(amount)
        expires = (datetime.now() + timedelta(minutes=wait)).isoformat()
        txn_id = secrets.token_hex(8)
        d.setdefault("pending_topups",{})[txn_id] = {
            "uid"          : uid,
            "amount"       : amount,
            "unique_amount": unique,
            "method"       : "card",
            "expires"      : expires,
            "created_at"   : datetime.now().isoformat(),
        }
        sdb(d)
        await state.clear()
        await msg.answer(
            f"💳 <b>To'lov ma'lumotlari</b>\n\n"
            f"🏦 Karta: <code>{card}</code>\n"
            f"👤 Egasi: <b>{holder}</b>\n\n"
            f"💰 To'lov summasi:\n"
            f"<b><code>{fmt(unique)}</code> so'm</b>\n\n"
            f"⚠️ <b>Iltimos summani nusxalab oling!</b>\n"
            f"Boshqa summa yuborilsa to'lov aniqlanmaydi.\n\n"
            f"⏰ Vaqt: <b>{wait} daqiqa</b>\n\n"
            f"❓ Muammo bo'lsa /yordam",
            parse_mode="HTML"
        )
    except ValueError: await msg.answer("❌ Faqat raqam kiriting!")

# ─── SCREENSHOT TO'LOV ───
@dp.callback_query(F.data == "topup_screen")
async def cb_topup_screen(cb: types.CallbackQuery, state: FSMContext):
    d = db(); card = d["settings"].get("card_number","")
    holder = d["settings"].get("card_holder","")
    await cb.message.edit_text(
        f"📸 <b>Screenshot orqali to'ldirish</b>\n\n"
        f"1️⃣ Quyidagi kartaga pul yuboring:\n"
        f"🏦 Karta: <code>{card}</code>\n"
        f"👤 Egasi: <b>{holder}</b>\n\n"
        f"2️⃣ To'lov screenshotini yuboring\n"
        f"3️⃣ Admin tasdiqlaydi (5-30 daqiqa)\n\n"
        f"Qancha so'm to'ldirmoqchisiz?",
        parse_mode="HTML"
    )
    await state.set_state(A.screenshot_topup)

@dp.message(A.screenshot_topup)
async def enter_screenshot_amount(msg: types.Message, state: FSMContext):
    try:
        amount = int(msg.text.replace(" ","").replace(",",""))
        if amount < 5000: await msg.answer("❌ Minimum 5 000 so'm!"); return
        await state.update_data(screen_amount=amount)
        await msg.answer(
            f"✅ Summa: <b>{fmt(amount)} so'm</b>\n\n"
            f"Endi to'lov screenshotini yuboring 📸",
            parse_mode="HTML"
        )
    except ValueError: await msg.answer("❌ Faqat raqam!")

@dp.message(A.screenshot_topup, F.photo)
async def receive_screenshot(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("screen_amount", 0)
    uid = str(msg.from_user.id)
    d = db()
    txn_id = secrets.token_hex(8)
    d.setdefault("pending_topups",{})[txn_id] = {
        "uid"       : uid,
        "amount"    : amount,
        "method"    : "screenshot",
        "photo_id"  : msg.photo[-1].file_id,
        "status"    : "pending",
        "created_at": datetime.now().isoformat(),
    }
    sdb(d)
    await state.clear()

    # Adminga yuborish
    support = d["settings"].get("support_link","")
    await msg.answer(
        f"✅ <b>Screenshot qabul qilindi!</b>\n\n"
        f"💰 Summa: <b>{fmt(amount)} so'm</b>\n"
        f"⏳ Admin tez orada tasdiqlaydi\n\n"
        f"❓ Savol bo'lsa: {support if support else 'Admin bilan bog\'laning'}",
        parse_mode="HTML"
    )

    # Adminga xabar
    try:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_screen_{txn_id}"),
            InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"reject_screen_{txn_id}"),
        ]])
        await bot.send_photo(
            SUPER_ADMIN_ID,
            msg.photo[-1].file_id,
            caption=f"📸 <b>Screenshot to'lov</b>\n\n"
                    f"👤 {msg.from_user.full_name} (@{msg.from_user.username})\n"
                    f"🆔 {uid}\n"
                    f"💰 {fmt(amount)} so'm\n"
                    f"🔑 {txn_id}",
            parse_mode="HTML", reply_markup=kb
        )
    except: pass

@dp.callback_query(F.data.startswith("confirm_screen_"))
async def confirm_screen(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id): return
    txn_id = cb.data.replace("confirm_screen_","")
    d = db()
    if txn_id not in d.get("pending_topups",{}):
        await cb.answer("❌ Topilmadi!"); return
    topup = d["pending_topups"][txn_id]
    uid   = topup["uid"]
    amt   = topup["amount"]
    d["users"][uid]["balance"] = d["users"][uid].get("balance",0) + amt
    del d["pending_topups"][txn_id]; sdb(d)
    await cb.message.edit_caption(
        cb.message.caption + f"\n\n✅ <b>Tasdiqlandi!</b> +{fmt(amt)} so'm",
        parse_mode="HTML"
    )
    try:
        await bot.send_message(int(uid),
            f"✅ <b>Balansingiz to'ldirildi!</b>\n\n"
            f"➕ <b>+{fmt(amt)} so'm</b>\n"
            f"💰 Joriy: <b>{fmt(d['users'][uid]['balance'])} so'm</b>",
            parse_mode="HTML")
    except: pass
    await send_log(f"✅ Screenshot to'lov tasdiqlandi\n👤 {uid}\n💰 +{fmt(amt)} so'm")

@dp.callback_query(F.data.startswith("reject_screen_"))
async def reject_screen(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id): return
    txn_id = cb.data.replace("reject_screen_","")
    d = db()
    if txn_id in d.get("pending_topups",{}):
        uid = d["pending_topups"][txn_id]["uid"]
        del d["pending_topups"][txn_id]; sdb(d)
        try:
            await bot.send_message(int(uid),
                "❌ <b>To'lovingiz rad etildi.</b>\n\n"
                "Savol bo'lsa adminlar bilan bog'laning.",
                parse_mode="HTML")
        except: pass
    await cb.message.edit_caption(cb.message.caption + "\n\n❌ <b>Rad etildi</b>", parse_mode="HTML")

# ─── ADMIN ───
def adm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika",       callback_data="adm_stats"),
         InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm_users")],
        [InlineKeyboardButton(text="💰 Narxlar",          callback_data="adm_prices"),
         InlineKeyboardButton(text="🎁 Promo kodlar",     callback_data="adm_promos")],
        [InlineKeyboardButton(text="📋 Buyurtmalar",      callback_data="adm_orders"),
         InlineKeyboardButton(text="📢 Broadcast",        callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="🖼 Logo",             callback_data="adm_logo"),
         InlineKeyboardButton(text="⚙️ Sozlamalar",       callback_data="adm_settings")],
        [InlineKeyboardButton(text="👑 Adminlar",         callback_data="adm_admins"),
         InlineKeyboardButton(text="📢 Kanallar",         callback_data="adm_channels")],
        [InlineKeyboardButton(text="💳 Karta sozlash",    callback_data="adm_card"),
         InlineKeyboardButton(text="📸 Screenshotlar",    callback_data="adm_screens")],
        [InlineKeyboardButton(text="🔑 Dev API token",    callback_data="adm_dev_token")],
        [InlineKeyboardButton(
            text=f"🤖 Bot {'✅' if db()['settings']['bot_active'] else '❌'}",
            callback_data="adm_toggle_bot")],
    ])

async def adm_text():
    d = db(); s = d["settings"]; p = s["prices"]
    done  = len([o for o in d["orders"] if o["status"]=="completed"])
    rev   = sum(o["price"] for o in d["orders"] if o["status"]=="completed")
    today = datetime.now().date().isoformat()
    t_rev = sum(o["price"] for o in d["orders"] if o["status"]=="completed" and o["created_at"][:10]==today)
    screens = len([t for t in d.get("pending_topups",{}).values() if t.get("method")=="screenshot"])
    return (
        f"👨‍💼 <b>Admin Panel — U-Gift</b>\n\n"
        f"<code>━━━━━━━━━━━━━━━━</code>\n"
        f"💳 Karta: <b>{s.get('card_number','Sozlanmagan')}</b>\n"
        f"👤 Egasi: <b>{s.get('card_holder','—')}</b>\n"
        f"⏰ Kutish: <b>{s.get('card_wait_minutes',5)} daqiqa</b>\n"
        f"<code>━━━━━━━━━━━━━━━━</code>\n"
        f"👥 Foydalanuvchilar: <b>{len(d['users'])}</b>\n"
        f"✅ Bajarilgan: <b>{done}</b>\n"
        f"📸 Kutilayotgan screenshot: <b>{screens}</b>\n"
        f"📅 Bugungi: <b>{fmt(t_rev)} so'm</b>\n"
        f"💰 Jami: <b>{fmt(rev)} so'm</b>"
    )

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_main")]])

@dp.message(Command("admin"))
async def cmd_admin(msg: types.Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.clear()
    await msg.answer(await adm_text(), parse_mode="HTML", reply_markup=adm_kb())

@dp.callback_query(F.data == "adm_main")
async def cb_adm_main(cb: types.CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id): return
    if state: await state.clear()
    try: await cb.message.edit_text(await adm_text(), parse_mode="HTML", reply_markup=adm_kb())
    except: await cb.message.answer(await adm_text(), parse_mode="HTML", reply_markup=adm_kb())

# ─── KARTA SOZLASH ───
@dp.callback_query(F.data == "adm_card")
async def cb_card(cb: types.CallbackQuery):
    if not is_super(cb.from_user.id): return
    d = db(); s = d["settings"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Karta: {s.get('card_number','Yo\'q')}", callback_data="adm_set_card")],
        [InlineKeyboardButton(text=f"👤 Egasi: {s.get('card_holder','Yo\'q')}", callback_data="adm_set_holder")],
        [InlineKeyboardButton(text=f"⏰ Kutish: {s.get('card_wait_minutes',5)} daqiqa", callback_data="adm_set_wait")],
        [InlineKeyboardButton(text=f"🤖 CardBot ID: {s.get('card_bot_id','Sozlanmagan')}", callback_data="adm_set_cardbot")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_main")],
    ])
    await cb.message.edit_text(
        "💳 <b>Karta sozlamalari</b>\n\n"
        "Bu yerda to'lov kartangizni sozlang.",
        parse_mode="HTML", reply_markup=kb
    )

@dp.callback_query(F.data.in_({"adm_set_card","adm_set_holder","adm_set_wait","adm_set_cardbot"}))
async def cb_set_card(cb: types.CallbackQuery, state: FSMContext):
    labels = {
        "adm_set_card"   : ("💳 Yangi karta raqami:", A.card_number),
        "adm_set_holder" : ("👤 Karta egasi (Ism Familiya):", A.card_holder),
        "adm_set_wait"   : ("⏰ Kutish vaqti (daqiqa):", A.card_wait),
        "adm_set_cardbot": ("🤖 CardXabarBot ID (raqam):", A.card_bot_id),
    }
    lbl, st = labels[cb.data]
    await cb.message.edit_text(lbl); await state.set_state(st)

@dp.message(A.card_number)
async def e_card_num(msg: types.Message, state: FSMContext):
    d = db(); d["settings"]["card_number"] = msg.text.strip(); sdb(d)
    await msg.answer(f"✅ Karta: <code>{msg.text.strip()}</code>", parse_mode="HTML")
    await state.clear(); await cmd_admin(msg, state)

@dp.message(A.card_holder)
async def e_card_holder(msg: types.Message, state: FSMContext):
    d = db(); d["settings"]["card_holder"] = msg.text.strip(); sdb(d)
    await msg.answer(f"✅ Egasi: <b>{msg.text.strip()}</b>", parse_mode="HTML")
    await state.clear(); await cmd_admin(msg, state)

@dp.message(A.card_wait)
async def e_card_wait(msg: types.Message, state: FSMContext):
    try:
        v = int(msg.text)
        if v < 1 or v > 60: await msg.answer("❌ 1-60 daqiqa!"); return
        d = db(); d["settings"]["card_wait_minutes"] = v; sdb(d)
        await msg.answer(f"✅ Kutish: <b>{v} daqiqa</b>", parse_mode="HTML")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Faqat raqam!")

@dp.message(A.card_bot_id)
async def e_card_bot(msg: types.Message, state: FSMContext):
    try:
        v = int(msg.text.strip())
        d = db(); d["settings"]["card_bot_id"] = v; sdb(d)
        await msg.answer(f"✅ CardBot ID: <code>{v}</code>", parse_mode="HTML")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Faqat raqam!")

# ─── SCREENSHOTLAR ───
@dp.callback_query(F.data == "adm_screens")
async def cb_screens(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id): return
    d = db()
    screens = {k:v for k,v in d.get("pending_topups",{}).items() if v.get("method")=="screenshot"}
    if not screens:
        await cb.answer("📸 Kutilayotgan screenshot yo'q!", show_alert=True); return
    text = f"📸 <b>Kutilayotgan screenshotlar ({len(screens)}):</b>\n\n"
    for txn_id, t in list(screens.items())[:5]:
        u = d["users"].get(t["uid"],{})
        text += f"👤 {u.get('name','?')} | 💰 {fmt(t['amount'])} so'm | 🔑 {txn_id[:8]}\n"
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb())

# ─── STATISTIKA ───
@dp.callback_query(F.data == "adm_stats")
async def cb_stats(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id): return
    d = db(); today = datetime.now().date().isoformat()
    t_rev = sum(o["price"] for o in d["orders"] if o["status"]=="completed" and o["created_at"][:10]==today)
    total_rev = sum(o["price"] for o in d["orders"] if o["status"]=="completed")
    screens = len([t for t in d.get("pending_topups",{}).values() if t.get("method")=="screenshot"])
    await cb.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{len(d['users'])}</b>\n"
        f"📋 Jami: <b>{len(d['orders'])}</b>\n"
        f"✅ Bajarilgan: <b>{len([o for o in d['orders'] if o['status']=='completed'])}</b>\n"
        f"❌ Xato: <b>{len([o for o in d['orders'] if o['status']=='failed'])}</b>\n"
        f"📸 Screenshot kutmoqda: <b>{screens}</b>\n\n"
        f"📅 Bugungi: <b>{fmt(t_rev)} so'm</b>\n"
        f"💰 Jami: <b>{fmt(total_rev)} so'm</b>",
        parse_mode="HTML", reply_markup=back_kb())

# ─── FOYDALANUVCHILAR ───
@dp.callback_query(F.data == "adm_users")
async def cb_users(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id): return
    d = db()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Ro'yxat",         callback_data="adm_ulist_1"),
         InlineKeyboardButton(text="🔍 Qidirish",        callback_data="adm_usearch")],
        [InlineKeyboardButton(text="🚫 Bloklash",        callback_data="adm_ban"),
         InlineKeyboardButton(text="✅ Ochish",           callback_data="adm_unban")],
        [InlineKeyboardButton(text="💰 Balans berish",   callback_data="adm_give_bal")],
        [InlineKeyboardButton(text="🔙 Orqaga",          callback_data="adm_main")],
    ])
    await cb.message.edit_text(
        f"👥 Jami: <b>{len(d['users'])}</b>\nBanlangan: <b>{len([u for u in d['users'].values() if u.get('banned')])}</b>",
        parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.startswith("adm_ulist_"))
async def cb_ulist(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id): return
    page = int(cb.data.replace("adm_ulist_",""))
    d = db(); users = list(d["users"].items())
    per = 10; total = len(users); start = (page-1)*per; end = start+per
    text = f"👥 <b>Foydalanuvchilar</b> ({start+1}-{min(end,total)} / {total})\n\n"
    for uid, u in users[start:end]:
        ban = "🚫" if u.get("banned") else "✅"
        text += f"{ban} <code>{uid}</code> | {u.get('name','?')}\n💰 {fmt(u.get('balance',0))} so'm | 📋 {len(u.get('orders',[]))} ta\n\n"
    nav = []
    if page > 1: nav.append(InlineKeyboardButton(text="◀️", callback_data=f"adm_ulist_{page-1}"))
    if end < total: nav.append(InlineKeyboardButton(text="▶️", callback_data=f"adm_ulist_{page+1}"))
    rows = [nav] if nav else []
    rows.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_users")])
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@dp.callback_query(F.data.in_({"adm_ban","adm_unban","adm_give_bal","adm_usearch"}))
async def cb_ban_act(cb: types.CallbackQuery, state: FSMContext):
    labels = {
        "adm_ban"     : "🚫 Bloklash — ID kiriting:",
        "adm_unban"   : "✅ Ochish — ID kiriting:",
        "adm_give_bal": "💰 ID va SUMMA kiriting:\n<i>Masalan: 123456789 50000</i>",
        "adm_usearch" : "🔍 Foydalanuvchi ID kiriting:",
    }
    await cb.message.edit_text(labels[cb.data], parse_mode="HTML")
    await state.update_data(ban_action=cb.data); await state.set_state(A.ban_id)

@dp.message(A.ban_id)
async def enter_ban(msg: types.Message, state: FSMContext):
    try:
        parts = msg.text.strip().split(); uid = str(int(parts[0]))
        data = await state.get_data(); d = db(); action = data.get("ban_action")
        if uid not in d["users"]: await msg.answer("❌ Topilmadi!"); await state.clear(); return
        if action == "adm_usearch":
            u = d["users"][uid]
            await msg.answer(
                f"👤 <b>Foydalanuvchi</b>\n\n🆔 <code>{uid}</code>\n"
                f"👤 {u.get('name','?')}\n📱 @{u.get('username','?')}\n"
                f"💰 Balans: <b>{fmt(u.get('balance',0))} so'm</b>\n"
                f"📋 Buyurtmalar: <b>{len(u.get('orders',[]))}</b>\n"
                f"👥 Referrallar: <b>{u.get('referrals',0)}</b>\n"
                f"🚫 Ban: <b>{'Ha' if u.get('banned') else 'Yo\\'q'}</b>",
                parse_mode="HTML")
        elif action == "adm_ban":
            d["users"][uid]["banned"] = True; sdb(d)
            await msg.answer(f"🚫 Bloklandi: <code>{uid}</code>", parse_mode="HTML")
        elif action == "adm_unban":
            d["users"][uid]["banned"] = False; sdb(d)
            await msg.answer(f"✅ Ochildi: <code>{uid}</code>", parse_mode="HTML")
        elif action == "adm_give_bal":
            if len(parts) < 2: await msg.answer("❌ Format: ID SUMMA"); return
            amt = int(parts[1]); d["users"][uid]["balance"] = d["users"][uid].get("balance",0) + amt; sdb(d)
            try: await bot.send_message(int(uid), f"✅ Hisobingizga <b>+{fmt(amt)} so'm</b> qo'shildi!", parse_mode="HTML")
            except: pass
            await msg.answer(f"✅ {fmt(amt)} so'm berildi!", parse_mode="HTML")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Noto'g'ri format!")

# ─── NARXLAR ───
@dp.callback_query(F.data == "adm_prices")
async def cb_prices(cb: types.CallbackQuery):
    if not is_super(cb.from_user.id): return
    d = db(); p = d["settings"]["prices"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🪙 1 Stars: {fmt(p['star'])} so'm", callback_data="adm_p_star")],
        [InlineKeyboardButton(text=f"👑 3oy: {fmt(p['pm3'])} so'm",      callback_data="adm_p_pm3")],
        [InlineKeyboardButton(text=f"👑 6oy: {fmt(p['pm6'])} so'm",      callback_data="adm_p_pm6")],
        [InlineKeyboardButton(text=f"💎 12oy: {fmt(p['pm12'])} so'm",    callback_data="adm_p_pm12")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_main")],
    ])
    await cb.message.edit_text("💰 <b>Narxlar</b>", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.in_({"adm_p_star","adm_p_pm3","adm_p_pm6","adm_p_pm12"}))
async def cb_set_price(cb: types.CallbackQuery, state: FSMContext):
    if not is_super(cb.from_user.id): return
    key = cb.data.replace("adm_p_","")
    labels = {"star":"1 Stars","pm3":"Premium 3oy","pm6":"Premium 6oy","pm12":"Premium 12oy"}
    await cb.message.edit_text(f"💰 <b>{labels[key]}</b> yangi narxi:", parse_mode="HTML")
    await state.update_data(price_key=key); await state.set_state(A.price_key)

@dp.message(A.price_key)
async def enter_price(msg: types.Message, state: FSMContext):
    try:
        v = int(msg.text.replace(" ","").replace(",",""))
        if v <= 0: await msg.answer("❌ 0 dan katta!"); return
        data = await state.get_data(); d = db()
        d["settings"]["prices"][data["price_key"]] = v; sdb(d)
        await msg.answer(f"✅ Narx yangilandi: <b>{fmt(v)} so'm</b>", parse_mode="HTML")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Faqat raqam!")

# ─── PROMO ───
@dp.callback_query(F.data == "adm_promos")
async def cb_promos(cb: types.CallbackQuery):
    if not is_super(cb.from_user.id): return
    d = db(); promos = d.get("promo_codes",{})
    pt = "\n".join([f"• <code>{k}</code> — {v['discount']}% | {v.get('used',0)}/{v.get('limit','∞')}" for k,v in promos.items()]) if promos else "Yo'q"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yaratish", callback_data="adm_new_promo"),
         InlineKeyboardButton(text="🗑 Tozalash", callback_data="adm_clear_promos")],
        [InlineKeyboardButton(text="🔙 Orqaga",   callback_data="adm_main")],
    ])
    await cb.message.edit_text(f"🎁 <b>Promo kodlar:</b>\n\n{pt}", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "adm_new_promo")
async def new_promo(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text("🎁 Promo kod nomi:"); await state.set_state(A.promo_code)

@dp.message(A.promo_code)
async def enter_promo_code(msg: types.Message, state: FSMContext):
    await state.update_data(promo_code=msg.text.strip().upper())
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Hammasi", callback_data="pp_all")],
        [InlineKeyboardButton(text="🌟 Stars",   callback_data="pp_star")],
        [InlineKeyboardButton(text="👑 Premium", callback_data="pp_pm3")],
    ])
    await msg.answer("🛍 Qaysi mahsulot?", reply_markup=kb); await state.set_state(A.promo_product)

@dp.callback_query(F.data.startswith("pp_"))
async def cb_promo_prod(cb: types.CallbackQuery, state: FSMContext):
    await state.update_data(promo_product=cb.data[3:])
    await cb.message.edit_text("📈 Chegirma foizi (1-90):"); await state.set_state(A.promo_disc)

@dp.message(A.promo_disc)
async def enter_promo_disc(msg: types.Message, state: FSMContext):
    try:
        v = int(msg.text)
        if v < 1 or v > 90: await msg.answer("❌ 1-90!"); return
        await state.update_data(promo_disc=v)
        await msg.answer("🔢 Necha kishi? (0=cheksiz):"); await state.set_state(A.promo_limit)
    except: await msg.answer("❌ Faqat raqam!")

@dp.message(A.promo_limit)
async def enter_promo_limit(msg: types.Message, state: FSMContext):
    try:
        limit = int(msg.text); data = await state.get_data(); d = db()
        d["promo_codes"][data["promo_code"]] = {
            "discount": data["promo_disc"], "product": data.get("promo_product","all"),
            "limit": limit if limit > 0 else None, "used": 0,
            "created_at": datetime.now().isoformat()
        }; sdb(d)
        await msg.answer(f"✅ <b>Promo yaratildi!</b>\n\n🎁 <code>{data['promo_code']}</code>\n📉 {data['promo_disc']}%", parse_mode="HTML")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Faqat raqam!")

@dp.callback_query(F.data == "adm_clear_promos")
async def clear_promos(cb: types.CallbackQuery):
    d = db(); d["promo_codes"] = {}; sdb(d)
    await cb.answer("✅"); await cb_promos(cb)

# ─── BUYURTMALAR ───
@dp.callback_query(F.data == "adm_orders")
async def cb_orders(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id): return
    d = db(); orders = d["orders"][-10:]
    if not orders: await cb.answer("Yo'q!", show_alert=True); return
    st = {"completed":"✅","failed":"❌","processing":"⏳"}
    text = "📋 <b>So'nggi buyurtmalar:</b>\n\n"
    for o in reversed(orders):
        svc = {"premium":f"P{o.get('months',3)}oy","stars":f"{fmt(o.get('stars',0))}⭐"}.get(o["service"],o["service"])
        text += f"{st.get(o['status'],'❓')} #{o['id']} @{o.get('username','?')} — {svc} — {fmt(o['price'])} so'm\n"
    await cb.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb())

# ─── BROADCAST ───
@dp.callback_query(F.data == "adm_broadcast")
async def cb_broadcast(cb: types.CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id): return
    await cb.message.edit_text("📢 Xabar yozing:"); await state.set_state(A.broadcast)

@dp.message(A.broadcast)
async def enter_broadcast(msg: types.Message, state: FSMContext):
    d = db(); sent = failed = 0
    prog = await msg.answer(f"⏳ 0/{len(d['users'])}")
    for i, uid in enumerate(d["users"]):
        try: await bot.send_message(int(uid), f"📢 <b>Xabar:</b>\n\n{msg.text}", parse_mode="HTML"); sent += 1
        except: failed += 1
        if i % 20 == 0:
            try: await prog.edit_text(f"⏳ {i}/{len(d['users'])}")
            except: pass
        await asyncio.sleep(0.05)
    await prog.edit_text(f"✅ Yuborildi! ✅{sent} ❌{failed}")
    await state.clear(); await cmd_admin(msg, state)

# ─── LOGO ───
@dp.callback_query(F.data == "adm_logo")
async def cb_logo(cb: types.CallbackQuery, state: FSMContext):
    if not is_super(cb.from_user.id): return
    await cb.message.edit_text("🖼 Logo rasmini yuboring:"); await state.set_state(A.logo)

@dp.message(A.logo)
async def enter_logo(msg: types.Message, state: FSMContext):
    if not msg.photo: await msg.answer("❌ Rasm!"); return
    d = db(); d["settings"]["logo_file_id"] = msg.photo[-1].file_id; sdb(d)
    await msg.answer("✅ Logo saqlandi!")
    await state.clear(); await cmd_admin(msg, state)

# ─── SOZLAMALAR ───
@dp.callback_query(F.data == "adm_settings")
async def cb_settings(cb: types.CallbackQuery):
    if not is_super(cb.from_user.id): return
    d = db(); s = d["settings"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⭐ Min Stars: {s['min_stars']}", callback_data="adm_set_minstars")],
        [InlineKeyboardButton(text=f"👥 Ref bonus: {fmt(s['referral_bonus'])} so'm", callback_data="adm_set_refbonus")],
        [InlineKeyboardButton(text="💬 Support linki", callback_data="adm_set_support")],
        [InlineKeyboardButton(text="📣 Kanal linki",   callback_data="adm_set_chanlink")],
        [InlineKeyboardButton(text="🔙 Orqaga",        callback_data="adm_main")],
    ])
    await cb.message.edit_text("⚙️ <b>Sozlamalar</b>", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.in_({"adm_set_minstars","adm_set_refbonus","adm_set_support","adm_set_chanlink"}))
async def cb_set_settings(cb: types.CallbackQuery, state: FSMContext):
    d = {
        "adm_set_minstars": ("⭐ Min Stars:", A.min_stars),
        "adm_set_refbonus": ("👥 Ref bonus (so'm):", A.ref_bonus),
        "adm_set_support" : ("💬 Support linki:", A.support),
        "adm_set_chanlink": ("📣 Kanal linki:", A.channel_link),
    }
    lbl, st = d[cb.data]
    await cb.message.edit_text(lbl); await state.set_state(st)

@dp.message(A.min_stars)
async def e_min(msg: types.Message, state: FSMContext):
    try:
        v = int(msg.text)
        d = db(); d["settings"]["min_stars"] = v; sdb(d)
        await msg.answer(f"✅ Min Stars: {v}")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Raqam!")

@dp.message(A.ref_bonus)
async def e_ref(msg: types.Message, state: FSMContext):
    try:
        v = int(msg.text.replace(" ",""))
        d = db(); d["settings"]["referral_bonus"] = v; sdb(d)
        await msg.answer(f"✅ Ref bonus: {fmt(v)} so'm")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Raqam!")

@dp.message(A.support)
async def e_sup(msg: types.Message, state: FSMContext):
    d = db(); d["settings"]["support_link"] = msg.text.strip(); sdb(d)
    await msg.answer("✅ Saqlandi!")
    await state.clear(); await cmd_admin(msg, state)

@dp.message(A.channel_link)
async def e_chan(msg: types.Message, state: FSMContext):
    d = db(); d["settings"]["channel_link"] = msg.text.strip(); sdb(d)
    await msg.answer("✅ Saqlandi!")
    await state.clear(); await cmd_admin(msg, state)

# ─── KANALLAR ───
@dp.callback_query(F.data == "adm_channels")
async def cb_channels(cb: types.CallbackQuery):
    if not is_super(cb.from_user.id): return
    d = db(); chs = d["settings"]["required_channels"]; logs = d["settings"].get("logs_channel","Yo'q")
    ct = "\n".join([f"• {c}" for c in chs]) if chs else "Yo'q"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Qo'shish", callback_data="adm_add_ch")],
        [InlineKeyboardButton(text="📝 Logs",     callback_data="adm_set_logs")],
        [InlineKeyboardButton(text="🗑 Tozalash",  callback_data="adm_clear_ch")],
        [InlineKeyboardButton(text="🔙 Orqaga",   callback_data="adm_main")],
    ])
    await cb.message.edit_text(f"📢 <b>Kanallar:</b>\n{ct}\n\n📝 Logs: {logs}", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "adm_add_ch")
async def add_ch(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text("📢 Kanal @username:"); await state.set_state(A.channel)

@dp.message(A.channel)
async def e_ch(msg: types.Message, state: FSMContext):
    d = db(); d["settings"]["required_channels"].append(msg.text.strip()); sdb(d)
    await msg.answer(f"✅ {msg.text.strip()}")
    await state.clear(); await cmd_admin(msg, state)

@dp.callback_query(F.data == "adm_clear_ch")
async def clear_ch(cb: types.CallbackQuery):
    d = db(); d["settings"]["required_channels"] = []; sdb(d)
    await cb.answer("✅"); await cb_channels(cb)

@dp.callback_query(F.data == "adm_set_logs")
async def set_logs(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text("📝 Logs kanal:"); await state.set_state(A.logs)

@dp.message(A.logs)
async def e_logs(msg: types.Message, state: FSMContext):
    d = db(); d["settings"]["logs_channel"] = msg.text.strip(); sdb(d)
    await msg.answer("✅ Saqlandi!")
    await state.clear(); await cmd_admin(msg, state)

# ─── ADMINLAR ───
@dp.callback_query(F.data == "adm_admins")
async def cb_admins(cb: types.CallbackQuery):
    if not is_super(cb.from_user.id): return
    d = db(); admins = d.get("admins",{})
    at = "\n".join([f"• <code>{a}</code>" for a in admins]) if admins else "Yo'q"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Qo'shish",  callback_data="adm_add_admin"),
         InlineKeyboardButton(text="➖ O'chirish", callback_data="adm_del_admin")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_main")],
    ])
    await cb.message.edit_text(f"👑 <b>Adminlar:</b>\n\n{at}", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.in_({"adm_add_admin","adm_del_admin"}))
async def manage_admin(cb: types.CallbackQuery, state: FSMContext):
    action = "qo'shish" if cb.data=="adm_add_admin" else "o'chirish"
    await cb.message.edit_text(f"👑 Admin ID ({action}):")
    await state.update_data(admin_action=cb.data); await state.set_state(A.admin_id)

@dp.message(A.admin_id)
async def enter_admin(msg: types.Message, state: FSMContext):
    try:
        aid = int(msg.text.strip())
        if aid == SUPER_ADMIN_ID: await msg.answer("❌ Mumkin emas!"); await state.clear(); return
        data = await state.get_data(); d = db()
        if data.get("admin_action") == "adm_add_admin":
            d["admins"][str(aid)] = {"added": datetime.now().isoformat()}; sdb(d)
            await msg.answer(f"✅ Admin: <code>{aid}</code>", parse_mode="HTML")
        else:
            if str(aid) in d["admins"]: del d["admins"][str(aid)]; sdb(d); await msg.answer("✅ O'chirildi")
            else: await msg.answer("❌ Topilmadi!")
        await state.clear(); await cmd_admin(msg, state)
    except: await msg.answer("❌ Noto'g'ri ID!")

@dp.callback_query(F.data == "adm_toggle_bot")
async def toggle_bot(cb: types.CallbackQuery, state: FSMContext):
    if not is_super(cb.from_user.id): return
    d = db(); d["settings"]["bot_active"] = not d["settings"]["bot_active"]; sdb(d)
    await cb.answer(f"Bot {'✅' if d['settings']['bot_active'] else '❌'}", show_alert=True)
    await cb_adm_main(cb, None)

# ─── DEV API TOKEN ───
@dp.callback_query(F.data == "adm_dev_token")
async def cb_dev_token(cb: types.CallbackQuery):
    if not is_super(cb.from_user.id): return
    import secrets as sec
    d = db(); token = sec.token_hex(32)
    d.setdefault("api_keys",{})[token] = {
        "uid": str(cb.from_user.id), "created_at": datetime.now().isoformat(),
        "active": True, "requests": 0
    }; sdb(d)
    await cb.message.edit_text(
        f"🔑 <b>Developer API Token</b>\n\n"
        f"<code>{token}</code>\n\n"
        f"<b>Ishlatish:</b>\n<code>X-API-Key: {token}</code>\n\n"
        f"📖 Hujjat: <code>/api/v1/docs</code>",
        parse_mode="HTML", reply_markup=back_kb()
    )

# ─── MAIN ───
async def main():
    log.info("🚀 U-Gift Bot ishga tushmoqda...")
    await remove_menu_button()
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
