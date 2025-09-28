import telebot, random, re, time, requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ Bot Token
TOKEN = "8212496378:AAGumpVE1106BYVk6ARJeu1rPlEu8ECWdEA"
bot = telebot.TeleBot(TOKEN)

# ✅ Owner ID
OWNER_ID = 1002782727729  

# ✅ Channel & Group Links
CHANNEL_USERNAME = "ThePremiumAccess"
GROUP_USERNAME = "B2GgC-QBuDs0ZmNl"

# ✅ Check user joined or not
def is_subscribed(user_id):
    try:
        chat_member1 = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        chat_member2 = bot.get_chat_member(f"https://t.me/+{GROUP_USERNAME}", user_id)
        if chat_member1.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except:
        return False

# ✅ Force Join Message
def force_join_message():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}"))
    markup.add(InlineKeyboardButton("💬 Join Group", url=f"https://t.me/+{GROUP_USERNAME}"))
    return ("🚫 Please join our Channel and Group first to use this bot.\n\n"
            "✅ After joining, try again."), markup

# ✅ Luhn Algorithm
def luhn(card):
    nums = [int(x) for x in card]
    return (sum(nums[-1::-2]) + sum(sum(divmod(2 * x, 10)) for x in nums[-2::-2])) % 10 == 0

# ✅ Generate credit card number
def generate_card(bin_format):
    bin_format = bin_format.lower()
    if len(bin_format) < 16:
        bin_format += "x" * (16 - len(bin_format))
    else:
        bin_format = bin_format[:16]
    while True:
        cc = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in bin_format)
        if luhn(cc):
            return cc

# ✅ Generate card info block
def generate_output(bin_input, username):
    parts = bin_input.split("|")
    bin_format = parts[0] if len(parts) > 0 else ""
    mm_input = parts[1] if len(parts) > 1 and parts[1] != "xx" else None
    yy_input = parts[2] if len(parts) > 2 and parts[2] != "xxxx" else None
    cvv_input = parts[3] if len(parts) > 3 and parts[3] != "xxx" else None

    bin_clean = re.sub(r"[^\d]", "", bin_format)[:6]

    if not bin_clean.isdigit() or len(bin_clean) < 6:
        return f"❌ Invalid BIN provided.\n\nExample:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>"

    scheme = "MASTERCARD" if bin_clean.startswith("5") else "VISA" if bin_clean.startswith("4") else "UNKNOWN"
    ctype = "DEBIT" if bin_clean.startswith("5") else "CREDIT" if bin_clean.startswith("4") else "UNKNOWN"

    cards = []
    start = time.time()
    for _ in range(10):
        cc = generate_card(bin_format)
        mm = mm_input if mm_input else str(random.randint(1, 12)).zfill(2)
        yy_full = yy_input if yy_input else str(random.randint(2026, 2032))
        yy = yy_full[-2:]
        cvv = cvv_input if cvv_input else str(random.randint(100, 999))
        cards.append(f"<code>{cc}|{mm}|{yy}|{cvv}</code>")
    elapsed = round(time.time() - start, 3)

    card_lines = "\n".join(cards)

    text = f"""<b>───────────────</b>
<b>Info</b> - ↯ {scheme} - {ctype}
<b>───────────────</b>
<b>Bin</b> - ↯ {bin_clean} |<b>Time</b> - ↯ {elapsed}s
<b>Input</b> - ↯ <code>{bin_input}</code>
<b>───────────────</b>
{card_lines}
<b>───────────────</b>
<b>Requested By</b> - ↯ @{username} [Free]
"""
    return text

# ✅ /start command
@bot.message_handler(commands=['start'])
def start_handler(message):
    if not is_subscribed(message.from_user.id):
        text, markup = force_join_message()
        return bot.reply_to(message, text, reply_markup=markup)

    user_id = str(message.from_user.id)
    with open("users.txt", "a+") as f:
        f.seek(0)
        if user_id not in f.read().splitlines():
            f.write(user_id + "\n")

    text = (
       "🤖 Bot Status: Active ✅\n\n"
        "📢 For announcements and updates, join us 👉 [here](https://t.me/ThePremiumAccess)\n\n"
        "💡 Tip: To use me in your group, make sure I'm added as admin."
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# ✅ /gen command
@bot.message_handler(commands=['gen'])
def gen_handler(message):
    if not is_subscribed(message.from_user.id):
        text, markup = force_join_message()
        return bot.reply_to(message, text, reply_markup=markup)

    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Example:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>", parse_mode="HTML")

    bin_input = parts[1].strip()
    username = message.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("Re-Generate ♻️", callback_data=f"again|{bin_input}"))
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=btn)

# ✅ /gen button callback
@bot.callback_query_handler(func=lambda call: call.data.startswith("again|"))
def again_handler(call):
    if not is_subscribed(call.from_user.id):
        text, markup = force_join_message()
        return bot.answer_callback_query(call.id, text, show_alert=True)

    bin_input = call.data.split("|", 1)[1]
    username = call.fr
