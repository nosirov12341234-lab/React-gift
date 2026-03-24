"""
U-Gift Userbot - Telethon
CardXabarBot xabarlarini o'qib avtomatik balans to'ldiradi
"""
import asyncio, json, os, re, logging
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

API_ID    = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH  = os.getenv("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DB = os.path.join(os.path.expanduser("~"), "ugift-react", "database.json")
SESSION = os.path.join(os.path.expanduser("~"), "ugift-react", "userbot.session")

def db():
    if os.path.exists(DB):
        with open(DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sdb(data):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fmt(n): return f"{int(n):,}".replace(",", " ")

def parse_card_message(text: str) -> dict | None:
    """CardXabarBot xabarini parse qilish"""
    try:
        # Summani olish: ➕ 50 003.00 UZS
        amount_match = re.search(r'➕\s*([\d\s]+\.?\d*)\s*UZS', text)
        if not amount_match:
            amount_match = re.search(r'\+\s*([\d\s]+\.?\d*)\s*UZS', text)
        if not amount_match:
            return None

        amount_str = amount_match.group(1).replace(' ', '').replace(',', '')
        amount = int(float(amount_str))

        # Vaqtni olish: 🕓 23.03.26 23:56
        time_match = re.search(r'🕓\s*(\d{2}\.\d{2}\.\d{2})\s*(\d{2}:\d{2})', text)
        if not time_match:
            time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})\s*(\d{2}:\d{2})', text)

        pay_time = None
        if time_match:
            date_str = time_match.group(1)
            time_str = time_match.group(2)
            try:
                day, month, year = date_str.split('.')
                hour, minute = time_str.split(':')
                pay_time = datetime(2000+int(year), int(month), int(day), int(hour), int(minute))
            except: pass

        return {"amount": amount, "pay_time": pay_time or datetime.now()}
    except Exception as e:
        log.error(f"Parse xato: {e}")
        return None

def find_pending(parsed: dict) -> tuple[str, dict] | None:
    """Pending topupni topish"""
    if not parsed: return None
    d = db()
    amount = parsed["amount"]
    now    = datetime.now()

    for txn_id, topup in d.get("pending_topups", {}).items():
        if topup.get("method") != "card": continue
        # Vaqt tekshirish
        expires = topup.get("expires")
        if expires:
            try:
                if datetime.fromisoformat(expires) < now:
                    continue
            except: pass
        # Summa tekshirish
        if topup.get("unique_amount") == amount:
            return txn_id, topup
    return None

async def confirm_topup(txn_id: str, topup: dict, client: TelegramClient):
    """To'lovni tasdiqlash va balans to'ldirish"""
    d    = db()
    uid  = topup["uid"]
    amt  = topup["amount"]  # Asl summa (so'm)

    if uid not in d["users"]:
        log.warning(f"Foydalanuvchi topilmadi: {uid}")
        return

    d["users"][uid]["balance"] = d["users"][uid].get("balance", 0) + amt
    del d["pending_topups"][txn_id]
    sdb(d)

    log.info(f"✅ Balans to'ldirildi: {uid} → +{fmt(amt)} so'm")

    # Foydalanuvchiga xabar
    try:
        from aiogram import Bot
        b = Bot(token=BOT_TOKEN)
        await b.send_message(
            int(uid),
            f"✅ <b>Balansingiz to'ldirildi!</b>\n\n"
            f"➕ <b>+{fmt(amt)} so'm</b>\n"
            f"💰 Joriy balans: <b>{fmt(d['users'][uid]['balance'])} so'm</b>",
            parse_mode="HTML"
        )
        await b.session.close()
    except Exception as e:
        log.error(f"Xabar xatosi: {e}")

    # Logs kanalga
    try:
        logs_ch = d["settings"].get("logs_channel")
        if logs_ch:
            from aiogram import Bot
            b = Bot(token=BOT_TOKEN)
            await b.send_message(
                logs_ch,
                f"💰 Karta to'lov tasdiqlandi!\n"
                f"👤 ID: {uid}\n"
                f"➕ +{fmt(amt)} so'm",
                parse_mode="HTML"
            )
            await b.session.close()
    except: pass

async def main():
    log.info("🤖 Userbot ishga tushmoqda...")

    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()

    me = await client.get_me()
    log.info(f"✅ Ulandi: {me.first_name} (@{me.username})")

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        msg = event.message
        sender = await event.get_sender()

        # Faqat CardXabarBot dan
        if not sender: return
        sender_name = getattr(sender, 'username', '') or ''
        if 'cardxabar' not in sender_name.lower() and 'card' not in sender_name.lower():
            # Bot ID bilan ham tekshirish
            d = db()
            card_bot_id = d["settings"].get("card_bot_id", 0)
            if card_bot_id and sender.id != card_bot_id:
                return
            elif not card_bot_id:
                return

        text = msg.text or msg.message or ""
        log.info(f"[CardBot xabar]: {text[:100]}")

        if "Perevod" not in text and "perevod" not in text and "➕" not in text:
            return

        parsed = parse_card_message(text)
        if not parsed:
            log.warning("Xabar parse qilinmadi")
            return

        log.info(f"[Parse]: summa={parsed['amount']}")

        result = find_pending(parsed)
        if result:
            txn_id, topup = result
            log.info(f"✅ Pending topildi: {txn_id}")
            await confirm_topup(txn_id, topup, client)
        else:
            log.warning(f"Pending topilmadi: summa={parsed['amount']}")

    log.info("👂 Xabarlar kutilmoqda...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

# ─── O'RNATISH ───
# pip install telethon --break-system-packages
# Birinchi marta ishga tushirganda telefon raqam va SMS kod so'raydi
# Session fayli ~/ugift-react/userbot.session da saqlanadi
