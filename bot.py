import os
import json
import telebot
from flask import Flask, request
from datetime import datetime

# ==================== KONFIGURATSIYA ====================
TOKEN = "8578005339:AAHg4HqHZbf4-F9DC8MLocMOtaLwr5eK04s"
ADMINS = [580240189]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

print("🚀 BOT ISHGA TUSHMOQDA...")

# ==================== MA'LUMOTLARNI SAQLASH ====================
def get_db_path():
    """JSON fayl joylashuvi"""
    return '/tmp/data.json' if os.path.exists('/tmp') else 'data.json'

def save_user(user_id, user_data):
    """Foydalanuvchi ma'lumotlarini saqlash"""
    try:
        file_path = get_db_path()
        
        # Mavjud ma'lumotlarni o'qish
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
        
        # Yangi ma'lumotni qo'shish
        data[str(user_id)] = {
            'full_name': user_data['full_name'],
            'birth_date': user_data['birth_date'],
            'work_type': user_data['work_type'],
            'position': user_data['position'],
            'photo_file_id': user_data.get('photo_file_id', ''),
            'registered_date': datetime.now().isoformat()
        }
        
        # Faylga yozish
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {user_id} saqlandi: {user_data['full_name']}")
        return True
    except Exception as e:
        print(f"❌ Saqlash xatosi: {e}")
        return False

def get_user(user_id):
    """Foydalanuvchi ma'lumotlarini olish"""
    try:
        file_path = get_db_path()
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(str(user_id))
    except:
        return None

def get_all_users():
    """Barcha foydalanuvchilar"""
    try:
        file_path = get_db_path()
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# ==================== VAQTINCHA SAQLASH ====================
user_sessions = {}

# ==================== WEBHOOK ====================
@app.route('/')
def home():
    return "🤖 BOT ISHLAYAPTI! ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Bad request', 400

# ==================== ASOSIY MENYU ====================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🚀 Ro\'yxatdan o\'tish', '👤 Mening maʼlumotlarim')
    markup.row('👨‍💼 Admin paneli', '✍️ Adminga yozish')
    
    bot.send_message(
        user_id,
        "🤖 *XUSH KELIBSIZ!*\n\n"
        "Ishchi ma'lumotlarini to'plash botiga xush kelibsiz.",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== RO'YXATDAN O'TISH ====================
@bot.message_handler(func=lambda message: message.text == '🚀 Ro\'yxatdan o\'tish')
def start_registration(message):
    user_id = message.chat.id
    
    # Oldin ro'yxatdan o'tganmi tekshirish
    existing_user = get_user(user_id)
    if existing_user:
        bot.send_message(
            user_id, 
            "✅ *Siz allaqachon ro'yxatdan o'tgansiz!*\n\n"
            f"👤 Ism: {existing_user['full_name']}\n"
            f"📅 Sana: {existing_user['birth_date']}\n\n"
            "Ma'lumotlaringizni ko'rish uchun \"👤 Mening maʼlumotlarim\" tugmasini bosing.",
            parse_mode="Markdown"
        )
        return
    
    # Yangi ro'yxatdan o'tish
    user_sessions[user_id] = {'step': 'full_name'}
    
    bot.send_message(
        user_id,
        "👋 *Ro'yxatdan o'tish boshlandi!*\n\n"
        "Quyidagi ma'lumotlarni ketma-ket kiriting:",
        parse_mode="Markdown"
    )
    bot.send_message(user_id, "1️⃣ *Familiya Ism Sharifingizni* kiriting:", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'full_name')
def process_full_name(message):
    user_id = message.chat.id
    user_sessions[user_id]['full_name'] = message.text
    user_sessions[user_id]['step'] = 'birth_date'
    bot.send_message(user_id, "2️⃣ *Tug'ilgan sanangizni* kiriting (01.01.1990):", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'birth_date')
def process_birth_date(message):
    user_id = message.chat.id
    user_sessions[user_id]['birth_date'] = message.text
    user_sessions[user_id]['step'] = 'work_type'
    bot.send_message(user_id, "3️⃣ *Qaysi ish turi* bo'yicha kelgansiz?\n(Masalan: Qurilish, IT, Savdo):", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'work_type')
def process_work_type(message):
    user_id = message.chat.id
    user_sessions[user_id]['work_type'] = message.text
    user_sessions[user_id]['step'] = 'position'
    bot.send_message(user_id, "4️⃣ *Lavozimingizni* kiriting:", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'position')
def process_position(message):
    user_id = message.chat.id
    user_sessions[user_id]['position'] = message.text
    user_sessions[user_id]['step'] = 'photo'
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📷 Rasm yuborish', '🚀 Rasm siz saqlash')
    
    bot.send_message(
        user_id,
        "5️⃣ *O'zingizning selfi suratingizni* yuboring:\n\n"
        "Agar rasm yubormasangiz, \"🚀 Rasm siz saqlash\" tugmasini bosing.",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '🚀 Rasm siz saqlash')
def save_without_photo(message):
    user_id = message.chat.id
    if user_id in user_sessions and user_sessions[user_id]['step'] == 'photo':
        user_sessions[user_id]['photo_file_id'] = ''
        complete_registration(user_id)

@bot.message_handler(content_types=['photo'])
def process_photo(message):
    user_id = message.chat.id
    if user_id in user_sessions and user_sessions[user_id]['step'] == 'photo':
        photo_file_id = message.photo[-1].file_id
        user_sessions[user_id]['photo_file_id'] = photo_file_id
        complete_registration(user_id)

def complete_registration(user_id):
    """Ro'yxatdan o'tishni yakunlash"""
    user_data = user_sessions[user_id]
    
    # Ma'lumotlarni saqlash
    success = save_user(user_id, user_data)
    
    if success:
        # Foydalanuvchiga xabar
        bot.send_message(
            user_id,
            "✅ *TABRIKLAYMIZ!*\n\n"
            "Ma'lumotlaringiz muvaffaqiyatli saqlandi.\n"
            "Ro'yxatdan o'tish yakunlandi!",
            parse_mode="Markdown",
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        
        # Adminlarga bildirishnoma
        for admin_id in ADMINS:
            try:
                bot.send_message(
                    admin_id,
                    f"🆕 *YANGI RO'YXATDAN O'TGAN!*\n\n"
                    f"👤 {user_data['full_name']}\n"
                    f"📅 {user_data['birth_date']}\n"
                    f"🏢 {user_data['work_type']}\n"
                    f"💼 {user_data['position']}\n"
                    f"🆔 {user_id}\n"
                    f"📸 Rasm: {'✅ Bor' if user_data.get('photo_file_id') else '❌ Yoq'}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Admin xabari: {e}")
    else:
        bot.send_message(user_id, "❌ Ma'lumotlarni saqlashda xatolik!")
    
    # Sessiyani tozalash
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    # Asosiy menyuni qaytarish
    start(message)

# ==================== SHAXSIY KABINET ====================
@bot.message_handler(func=lambda message: message.text == '👤 Mening maʼlumotlarim')
def personal_cabinet(message):
    user_id = message.chat.id
    
    user_data = get_user(user_id)
    if not user_data:
        bot.send_message(user_id, "❌ Siz hali ro'yxatdan o'tmagansiz!")
        return
    
    info_text = (
        f"👤 *SHAXSIY KABINET*\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 FISh: *{user_data['full_name']}*\n"
        f"📅 Tug'ilgan sana: {user_data['birth_date']}\n"
        f"🏢 Ish turi: {user_data['work_type']}\n"
        f"💼 Lavozim: {user_data['position']}\n"
        f"📅 Ro'yxatdan o'tgan: {user_data['registered_date'][:10]}\n\n"
        f"✅ Ma'lumotlaringiz saqlangan"
    )
    
    if user_data.get('photo_file_id'):
        try:
            bot.send_photo(user_id, user_data['photo_file_id'], caption=info_text, parse_mode="Markdown")
        except:
            bot.send_message(user_id, info_text, parse_mode="Markdown")
    else:
        bot.send_message(user_id, info_text, parse_mode="Markdown")

# ==================== ADMIN PANELI ====================
@bot.message_handler(func=lambda message: message.text == '👨‍💼 Admin paneli')
def admin_panel(message):
    user_id = message.chat.id
    
    if user_id not in ADMINS:
        bot.send_message(user_id, "❌ *Siz admin emassiz!*", parse_mode="Markdown")
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👥 Barcha foydalanuvchilar', '📊 Statistika')
    markup.row('🔙 Asosiy menyu')
    
    bot.send_message(
        user_id,
        "👨‍💼 *ADMIN PANEL*\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '👥 Barcha foydalanuvchilar')
def all_users(message):
    if message.chat.id not in ADMINS:
        return
    
    users = get_all_users()
    
    if not users:
        bot.send_message(message.chat.id, "📭 Hozircha hech qanday foydalanuvchi yo'q")
        return
    
    bot.send_message(message.chat.id, f"👥 *JAMI FOYDALANUVCHILAR: {len(users)} ta*", parse_mode="Markdown")
    
    for user_id, user_data in list(users.items())[:10]:  # Birinchi 10 tasi
        user_info = (
            f"👤 *{user_data['full_name']}*\n"
            f"📅 {user_data['birth_date']}\n"
            f"🏢 {user_data['work_type']}\n"
            f"💼 {user_data['position']}\n"
            f"🆔 {user_id}"
        )
        bot.send_message(message.chat.id, user_info, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '📊 Statistika')
def statistics(message):
    if message.chat.id not in ADMINS:
        return
    
    users = get_all_users()
    total = len(users)
    
    stat_text = (
        f"📊 *BOT STATISTIKASI*\n\n"
        f"👥 Jami foydalanuvchilar: {total} ta\n"
        f"📅 Hisobot vaqti: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"✅ Bot to'liq ishlayapti!"
    )
    
    bot.send_message(message.chat.id, stat_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '🔙 Asosiy menyu')
def back_to_main(message):
    start(message)

# ==================== ADMINGA XABAR ====================
@bot.message_handler(func=lambda message: message.text == '✍️ Adminga yozish')
def message_to_admin(message):
    user_id = message.chat.id
    user_sessions[user_id] = {'step': 'admin_message'}
    bot.send_message(user_id, "📝 *Xabaringizni yozing:*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'admin_message')
def process_admin_message(message):
    user_id = message.chat.id
    user_message = message.text
    
    # Adminlarga yuborish
    for admin_id in ADMINS:
        try:
            bot.send_message(
                admin_id,
                f"📩 *YANGI XABAR*\n\n"
                f"👤 Foydalanuvchi: {user_id}\n"
                f"💬 Xabar: {user_message}",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Admin xabari: {e}")
    
    bot.send_message(user_id, "✅ Xabaringiz adminga yuborildi!")
    
    # Sessiyani tozalash
    if user_id in user_sessions:
        del user_sessions[user_id]

# ==================== BOTNI ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    print("🌐 WEBHOOK MODE - RENDER")
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
