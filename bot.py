import telebot
from telebot import types
import os

# --- الإعدادات الأساسية ---
TOKEN = '8653852389:AAEv2Q3tESRHOocbMiTAYZq4bVlx34ckyHI'
ADMIN_ID = 1466599415  
VIDEO_FILE = "video.txt"
DATA_FILE = "users_data.txt"

bot = telebot.TeleBot(TOKEN)

# --- وظائف إدارة البيانات ---
def load_data():
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            for line in f:
                p = line.strip().split(':')
                if len(p) == 2: data[p[0]] = int(p[1])
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        for uid, count in data.items(): f.write(f"{uid}:{count}\n")

def get_video():
    if os.path.exists(VIDEO_FILE):
        with open(VIDEO_FILE, "r") as f: return f.read().strip()
    return "https://www.tiktok.com"

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    u_id = str(message.chat.id)
    data = load_data()
    bot_username = bot.get_me().username
    
    # نظام الإحالة عند الدخول من رابط شخص آخر
    if len(message.text.split()) > 1:
        referrer = message.text.split()[1]
        if referrer != u_id and u_id not in data:
            data[referrer] = data.get(referrer, 0) + 1
            try: bot.send_message(referrer, f"🔔 مبروك! دخل شخص جديد عبر رابطك. رصيدك الحالي: {data[referrer]}/3")
            except: pass

    if u_id not in data: data[u_id] = 0
    save_data(data)

    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📊 إحصائيات المنصة", callback_data="admin_stats"),
            types.InlineKeyboardButton("📢 إرسال إعلان للكل", callback_data="broadcast")
        )
        bot.send_message(u_id, "👋 أهلاً يا Boss!\n\nلتغيير رابط المشاهدة، أرسله مباشرة هنا (يجب أن يبدأ بـ http).", reply_markup=markup)
    else:
        invites = data.get(u_id, 0)
        ref_link = f"https://t.me/{bot_username}?start={u_id}"
        
        if invites >= 3:
            v_url = get_video()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📺 شاهد الفيديو الآن", url=v_url))
            markup.add(types.InlineKeyboardButton("✅ فتح الخدمات", callback_data="unlock"))
            bot.send_message(u_id, "🔥 مبروك! لقد أتممت الإحالات. شاهد الفيديو الأخير لتفعيل الخدمات مجاناً:", reply_markup=markup)
        else:
            bot.send_message(u_id, f"⚠️ **الخدمات مغلقة!**\n\nيجب دعوة **3 أشخاص** لفتح البوت.\nإحالاتك الحالية: {invites}/3\n\nرابطك للنشر:\n`{ref_link}`", parse_mode="Markdown")

# --- لوحة تحكم المدير (تغيير الرابط) ---
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text.startswith("http"))
def update_link(message):
    with open(VIDEO_FILE, "w") as f: f.write(message.text)
    bot.send_message(ADMIN_ID, "✅ تم تحديث الرابط بنجاح! سيظهر الآن لجميع المستخدمين الذين أكملوا الإحالات.")

# --- التفاعلات (Callback) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "unlock":
        bot.answer_callback_query(call.id, "🔓 جاري التحقق...")
        bot.send_message(call.message.chat.id, "✅ تم التفعيل! يمكنك الآن إرسال رابط فيديوك لنقوم بترويجه لك.")
    elif call.data == "admin_stats":
        data = load_data()
        bot.send_message(ADMIN_ID, f"📊 عدد المستخدمين الكلي: {len(data)}")
    elif call.data == "broadcast":
        msg = bot.send_message(ADMIN_ID, "📢 أرسل الإعلان الآن (نص أو صورة):")
        bot.register_next_step_handler(msg, send_to_all)

def send_to_all(message):
    data = load_data()
    count = 0
    for u_id in data.keys():
        try:
            bot.copy_message(u_id, message.chat.id, message.message_id)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ تم إرسال الإعلان لـ {count} مستخدم.")

print("--- [TDZ PLATFORM IS LIVE & READY] ---")
bot.polling(none_stop=True)

