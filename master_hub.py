import telebot
from telebot import types
import json
import os

# --- الإعدادات الأساسية ---
BOT_TOKEN = "8070560190:AAFjbU4sfFLjS77uE4X_csCG-T71za3eAvg"
ADMIN_ID = 8305841557
BASE_URL = "https://phantom-military-v3.onrender.com" # رابط سيرفرك

bot = telebot.TeleBot(BOT_TOKEN)

# --- نظام قاعدة البيانات المصغرة ---
DB_FILE = "database.json"
def load_db():
    if not os.path.exists(DB_FILE):
        data = {"bots": [], "users": [], "vips": []}
        save_db(data)
        return data
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- لوحة التحكم والواجهة ---
@bot.message_handler(commands=['start'])
def start(message):
    db = load_db()
    if message.chat.id not in db["users"]:
        db["users"].append(message.chat.id)
        save_db(db)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📱 بوتات الأرقام", "💎 أرقام VIP للبيع")
    markup.add("🛠️ أدوات Termux", "👨‍💻 المطور")
    if message.chat.id == ADMIN_ID:
        markup.add("⚙️ لوحة تحكم الآدمن")
    
    bot.send_message(message.chat.id, "🚀 **مرحباً بك في بوت الخدمات الشامل**\n\nاختر من القائمة أدناه:", reply_markup=markup, parse_mode="Markdown")

# --- إدارة المتجر والبيانات (للمستخدم) ---
@bot.message_handler(func=lambda m: m.text == "📱 بوتات الأرقام")
def list_bots(message):
    db = load_db()
    if not db["bots"]:
        bot.send_message(message.chat.id, "⚠️ لا توجد بوتات مضافة حالياً.")
        return
    markup = types.InlineKeyboardMarkup()
    for b in db["bots"]:
        markup.add(types.InlineKeyboardButton(f"🟢 {b['name']}", url=f"https://t.me/{b['link'].replace('@','')}"))
    bot.send_message(message.chat.id, "🌐 **قائمة البوتات النشطة:**", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 أرقام VIP للبيع")
def show_vip(message):
    db = load_db()
    if not db["vips"]:
        bot.send_message(message.chat.id, "✨ المتجر فارغ حالياً.")
        return
    text = "💎 **عروض الأرقام المميزة:**\n\n"
    markup = types.InlineKeyboardMarkup()
    for item in db["vips"]:
        text += f"📱 `{item['number']}` ➔ 💰 {item['price']}\n"
        markup.add(types.InlineKeyboardButton(f"💳 شراء {item['number']}", url=f"https://t.me/{ADMIN_ID}"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- لوحة تحكم الآدمن (للآدمن فقط) ---
@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة تحكم الآدمن" and m.chat.id == ADMIN_ID)
def admin_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ أضف بوت", callback_data="add_bot"),
               types.InlineKeyboardButton("➕ أضف رقم VIP", callback_data="add_vip"))
    markup.add(types.InlineKeyboardButton("📢 إرسال إعلان", callback_data="broadcast"))
    markup.add(types.InlineKeyboardButton("🖥️ فتح Phantom Admin", url=f"{BASE_URL}/admin?uid={ADMIN_ID}"))
    bot.send_message(message.chat.id, "🛠️ **إعدادات المطور:**", reply_markup=markup, parse_mode="Markdown")

# --- معالجة الإضافات ---
@bot.callback_query_handler(func=lambda call: call.data in ["add_bot", "add_vip", "broadcast"])
def handle_admin_actions(call):
    if call.data == "add_bot":
        msg = bot.send_message(ADMIN_ID, "أرسل: (اسم البوت - يوزر_البوت)")
        bot.register_next_step_handler(msg, save_new_bot)
    elif call.data == "add_vip":
        msg = bot.send_message(ADMIN_ID, "أرسل: (الرقم - السعر)")
        bot.register_next_step_handler(msg, save_new_vip)
    elif call.data == "broadcast":
        msg = bot.send_message(ADMIN_ID, "أرسل نص الإعلان للجميع:")
        bot.register_next_step_handler(msg, do_broadcast)

def save_new_bot(message):
    try:
        db = load_db(); name, link = message.text.split(" - ")
        db["bots"].append({"name": name, "link": link}); save_db(db)
        bot.send_message(ADMIN_ID, "✅ تم الحفظ.")
    except: bot.send_message(ADMIN_ID, "❌ خطأ في التنسيق.")

def save_new_vip(message):
    try:
        db = load_db(); num, price = message.text.split(" - ")
        db["vips"].append({"number": num, "price": price}); save_db(db)
        bot.send_message(ADMIN_ID, "✅ تم إضافة الرقم للمتجر.")
    except: bot.send_message(ADMIN_ID, "❌ خطأ في التنسيق.")

def do_broadcast(message):
    db = load_db(); count = 0
    for user in db["users"]:
        try: bot.send_message(user, f"📢 **إعلان هام:**\n\n{message.text}", parse_mode="Markdown"); count += 1
        except: continue
    bot.send_message(ADMIN_ID, f"✅ تم الإرسال لـ {count} مستخدم.")

# تشغيل البوت
print("Master Bot is Live!")
bot.polling()
