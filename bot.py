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

print("🤖 BOT ISHGA TUSHDI - YANGI KOD")

# ==================== MA'LUMOTLARNI SAQLASH ====================
DB_FILE = 'users_data.json'

def save_user_data(user_id, data):
    """Foydalanuvchi ma'lumotlarini saqlash"""
    try:
        # Fayl mavjudligini tekshirish
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        else:
            all_data = {}
        
        # Yangi ma'lumotni qo'shish
        all_data[str(user_id)] = {
            'full_name': data['full_name'],
            'birth_date': data['birth_date'], 
            'work_type': data['work_type'],
            'position': data['position'],
            'photo': data.get('photo', ''),
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Faylga yozish
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ SAQLANDI: {user_id} - {data['full_name']}")
        return True
        
    except Exception as e:
        print(f"❌ XATO: {e}")
        return False

def load_user_data(user_id):
    """Foydalanuvchi ma'lumotlarini o'qish"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            return all_data.get(str(user_id))
        return None
    except:
        return None

def get_all_users():
    """Barcha foydalanuvchilar"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except:
        return {}

# ==================== FOYDALANUVCHI SESSIYALARI ====================
user_temp = {}

# ==================== WEBHOOK ====================
@app.route('/')
def home():
    return "🤖 BOT ISHLAYAPTI"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return ''

# ==================== BOSHLASH ====================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📝 Ro\'yxatdan o\'tish', '👤 Mening ma\'lumotlarim')
    markup.row('📊 Admin panel')
    
    bot.send_message(
        user_id,
        "🤖 *Ishchi ma'lumotlari botiga xush kelibsiz!*",
        parse_mode="Markdown", 
        reply_markup=markup
    )

# ==================== RO'YXATDAN O'TISH ====================
@bot.message_handler(func=lambda message: message.text == '📝 Ro\'yxatdan o\'tish')
def start_registration(message):
    user_id = message.chat.id
    
    # Avval ro'yxatdan o'tganmi tekshirish
    existing = load_user_data(user_id)
    if existing:
        bot.send_message(
            user_id,
            f"✅ *Siz allaqachon ro'yxatdan o'tgansiz!*\n\n"
            f"Ism: {existing['full_name']}\n"
            f"Ma'lumotlaringizni ko'rish uchun '👤 Mening ma\'lumotlarim' tugmasini bosing.",
            parse_mode="Markdown"
        )
        return
    
    # Yangi ro'yxatdan o'tish
    user_temp[user_id] = {'step': 'name'}
    bot.send_message(user_id, "👤 *Ism familiyangizni kiriting:*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_temp and user_temp[message.chat.id]['step'] == 'name')
def get_name(message):
    user_id = message.chat.id
    user_temp[user_id]['full_name'] = message.text
    user_temp[user_id]['step'] = 'birth_date'
    bot.send_message(user_id, "📅 *Tug'ilgan sanangiz (01.01.1990):*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_temp and user_temp[message.chat.id]['step'] == 'birth_date')
def get_birth_date(message):
    user_id = message.chat.id
    user_temp[user_id]['birth_date'] = message.text
    user_temp[user_id]['step'] = 'work_type'
    bot.send_message(user_id, "🏢 *Ish turi:*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_temp and user_temp[message.chat.id]['step'] == 'work_type')
def get_work_type(message):
    user_id = message.chat.id
    user_temp[user_id]['work_type'] = message.text
    user_temp[user_id]['step'] = 'position'
    bot.send_message(user_id, "💼 *Lavozimingiz:*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_temp and user_temp[message.chat.id]['step'] == 'position')
def get_position(message):
    user_id = message.chat.id
    user_temp[user_id]['position'] = message.text
    user_temp[user_id]['step'] = 'photo'
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📸 Rasm yuborish', '➡️ Rasm siz davom etish')
    
    bot.send_message(
        user_id,
        "📷 *Selfi suratingizni yuboring yoki 'Rasm siz davom etish' tugmasini bosing:*",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '➡️ Rasm siz davom etish')
def skip_photo(message):
    user_id = message.chat.id
    if user_id in user_temp and user_temp[user_id]['step'] == 'photo':
        user_temp[user_id]['photo'] = ''
        finish_registration(user_id)

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    user_id = message.chat.id
    if user_id in user_temp and user_temp[user_id]['step'] == 'photo':
        user_temp[user_id]['photo'] = message.photo[-1].file_id
        finish_registration(user_id)

def finish_registration(user_id):
    """Ro'yxatdan o'tishni yakunlash"""
    user_data = user_temp[user_id]
    
    # Ma'lumotlarni saqlash
    success = save_user_data(user_id, user_data)
    
    if success:
        # Foydalanuvchiga xabar
        bot.send_message(
            user_id,
            "🎉 *TABRIKLAYMIZ!*\n\n"
            "✅ Ma'lumotlaringiz muvaffaqiyatli saqlandi!\n"
            "Endi '👤 Mening ma\'lumotlarim' tugmasi orqali ma'lumotlaringizni ko'rishingiz mumkin.",
            parse_mode="Markdown",
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        
        # Adminlarga xabar
        for admin_id in ADMINS:
            try:
                bot.send_message(
                    admin_id,
                    f"🆕 *YANGI RO'YXATDAN O'TISH!*\n\n"
                    f"👤 {user_data['full_name']}\n"
                    f"📅 {user_data['birth_date']}\n" 
                    f"🏢 {user_data['work_type']}\n"
                    f"💼 {user_data['position']}\n"
                    f"🆔 {user_id}",
                    parse_mode="Markdown"
                )
            except:
                pass
    else:
        bot.send_message(user_id, "❌ Ma'lumotlarni saqlashda xatolik!")
    
    # Sessiyani tozalash
    if user_id in user_temp:
        del user_temp[user_id]
    
    # Bosh menyuga qaytish
    start(message)

# ==================== SHAXSIY KABINET ====================
@bot.message_handler(func=lambda message: message.text == '👤 Mening ma\'lumotlarim')
def show_my_data(message):
    user_id = message.chat.id
    
    user_data = load_user_data(user_id)
    if not user_data:
        bot.send_message(user_id, "❌ Siz hali ro'yxatdan o'tmagansiz!")
        return
    
    info_text = (
        f"👤 *SIZNING MA'LUMOTLARINGIZ*\n\n"
        f"🆔 ID: {user_id}\n"
        f"📝 Ism: {user_data['full_name']}\n"
        f"📅 Tug'ilgan sana: {user_data['birth_date']}\n"
        f"🏢 Ish turi: {user_data['work_type']}\n"
        f"💼 Lavozim: {user_data['position']}\n"
        f"⏰ Saqlangan: {user_data['saved_at']}\n\n"
        f"✅ Ma'lumotlaringiz saqlangan"
    )
    
    bot.send_message(user_id, info_text, parse_mode="Markdown")

# ==================== ADMIN PANEL ====================
@bot.message_handler(func=lambda message: message.text == '📊 Admin panel')
def admin_panel(message):
    user_id = message.chat.id
    
    if user_id not in ADMINS:
        bot.send_message(user_id, "❌ Siz admin emassiz!")
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👥 Barcha foydalanuvchilar', '📈 Statistika')
    markup.row('🔙 Bosh menyu')
    
    bot.send_message(user_id, "👨‍💼 *Admin Panel*", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '👥 Barcha foydalanuvchilar')
def show_all_users(message):
    if message.chat.id not in ADMINS:
        return
    
    users = get_all_users()
    
    if not users:
        bot.send_message(message.chat.id, "📭 Hozircha foydalanuvchilar yo'q")
        return
    
    bot.send_message(message.chat.id, f"👥 *Jami foydalanuvchilar: {len(users)} ta*", parse_mode="Markdown")
    
    for user_id, user_data in users.items():
        user_info = f"👤 {user_data['full_name']}\n📅 {user_data['birth_date']}\n🏢 {user_data['work_type']}\n💼 {user_data['position']}\n🆔 {user_id}"
        bot.send_message(message.chat.id, user_info)

@bot.message_handler(func=lambda message: message.text == '📈 Statistika')
def show_stats(message):
    if message.chat.id not in ADMINS:
        return
    
    users = get_all_users()
    total = len(users)
    
    stats_text = (
        f"📊 *BOT STATISTIKASI*\n\n"
        f"👥 Jami foydalanuvchilar: {total} ta\n"
        f"📅 Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"✅ Bot ishlayapti"
    )
    
    bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '🔙 Bosh menyu')
def back_to_main(message):
    start(message)

# ==================== SERVER ====================
if __name__ == "__main__":
    print("🚀 SERVER ISHGA TUSHDI")
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
