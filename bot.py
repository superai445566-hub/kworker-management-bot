import os
import json
import telebot
from flask import Flask, request
from datetime import datetime, date
import csv
from io import StringIO

# ==================== KONFIGURATSIYA ====================
TOKEN = "8578005339:AAHg4HqHZbf4-F9DC8MLocMOtaLwr5eK04s"
ADMINS = [580240189]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

print("🚀 BOT ISHGA TUSHMOQDA...")

# ==================== MA'LUMOTLARNI SAQLASH ====================
def get_db_path():
    return '/tmp/data.json' if os.path.exists('/tmp') else 'data.json'

def save_user(user_id, user_data):
    try:
        file_path = get_db_path()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
        
        data[str(user_id)] = {
            'full_name': user_data['full_name'],
            'birth_date': user_data['birth_date'],
            'work_type': user_data['work_type'],
            'position': user_data['position'],
            'photo_file_id': user_data.get('photo_file_id', ''),
            'registered_date': datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {user_id} saqlandi")
        return True
    except Exception as e:
        print(f"❌ Saqlash xatosi: {e}")
        return False

def get_user(user_id):
    try:
        file_path = get_db_path()
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(str(user_id))
    except:
        return None

def get_all_users():
    try:
        file_path = get_db_path()
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def search_users(search_term):
    """Foydalanuvchilarni qidirish"""
    users = get_all_users()
    results = {}
    
    for user_id, user_data in users.items():
        if (search_term.lower() in user_data['full_name'].lower() or 
            search_term.lower() in user_data['work_type'].lower() or 
            search_term.lower() in user_data['position'].lower()):
            results[user_id] = user_data
    
    return results

def get_daily_stats():
    """Kunlik statistika"""
    users = get_all_users()
    today = date.today().isoformat()
    
    daily_count = 0
    for user_data in users.values():
        if user_data['registered_date'][:10] == today:
            daily_count += 1
    
    return {
        'daily': daily_count,
        'total': len(users)
    }

def get_monthly_stats():
    """Oylik statistika"""
    users = get_all_users()
    current_month = date.today().strftime('%Y-%m')
    
    monthly_count = 0
    for user_data in users.values():
        if user_data['registered_date'][:7] == current_month:
            monthly_count += 1
    
    return {
        'monthly': monthly_count,
        'total': len(users)
    }

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
        "🤖 *XUSH KELIBSIZ!*",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== RO'YXATDAN O'TISH ====================
@bot.message_handler(func=lambda message: message.text == '🚀 Ro\'yxatdan o\'tish')
def start_registration(message):
    user_id = message.chat.id
    
    existing_user = get_user(user_id)
    if existing_user:
        bot.send_message(
            user_id, 
            "✅ *Siz allaqachon ro'yxatdan o'tgansiz!*",
            parse_mode="Markdown"
        )
        return
    
    user_sessions[user_id] = {'step': 'full_name'}
    bot.send_message(user_id, "1️⃣ *Ism Familiyangiz:*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'full_name')
def process_full_name(message):
    user_id = message.chat.id
    user_sessions[user_id]['full_name'] = message.text
    user_sessions[user_id]['step'] = 'birth_date'
    bot.send_message(user_id, "2️⃣ *Tug'ilgan sana:* (01.01.1990)", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'birth_date')
def process_birth_date(message):
    user_id = message.chat.id
    user_sessions[user_id]['birth_date'] = message.text
    user_sessions[user_id]['step'] = 'work_type'
    bot.send_message(user_id, "3️⃣ *Ish turi:*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'work_type')
def process_work_type(message):
    user_id = message.chat.id
    user_sessions[user_id]['work_type'] = message.text
    user_sessions[user_id]['step'] = 'position'
    bot.send_message(user_id, "4️⃣ *Lavozim:*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and user_sessions[message.chat.id]['step'] == 'position')
def process_position(message):
    user_id = message.chat.id
    user_sessions[user_id]['position'] = message.text
    user_sessions[user_id]['step'] = 'photo'
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📷 Rasm yuborish', '🚀 Rasm siz saqlash')
    
    bot.send_message(
        user_id,
        "5️⃣ *Selfi suratingizni yuboring:*",
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
    user_data = user_sessions[user_id]
    
    success = save_user(user_id, user_data)
    
    if success:
        bot.send_message(
            user_id,
            "✅ *Ma'lumotlaringiz saqlandi!*",
            parse_mode="Markdown",
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        
        for admin_id in ADMINS:
            try:
                bot.send_message(
                    admin_id,
                    f"🆕 *YANGI RO'YXATDAN O'TGAN!*\n\n"
                    f"👤 {user_data['full_name']}\n"
                    f"📅 {user_data['birth_date']}\n"
                    f"🏢 {user_data['work_type']}\n"
                    f"💼 {user_data['position']}",
                    parse_mode="Markdown"
                )
            except:
                pass
    else:
        bot.send_message(user_id, "❌ Xatolik!")
    
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    start(bot.send_message(user_id, "Bosh menyu:"))

# ==================== SHAXSIY KABINET ====================
@bot.message_handler(func=lambda message: message.text == '👤 Mening maʼlumotlarim')
def personal_cabinet(message):
    user_id = message.chat.id
    
    user_data = get_user(user_id)
    if not user_data:
        bot.send_message(user_id, "❌ Siz ro'yxatdan o'tmagansiz!")
        return
    
    info_text = (
        f"👤 *SHAXSIY KABINET*\n\n"
        f"👤 FISh: *{user_data['full_name']}*\n"
        f"📅 Tug'ilgan sana: {user_data['birth_date']}\n"
        f"🏢 Ish turi: {user_data['work_type']}\n"
        f"💼 Lavozim: {user_data['position']}"
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
    markup.row('👥 Barcha foydalanuvchilar', '🔍 Qidirish')
    markup.row('📊 Kunlik hisobot', '📈 Oylik hisobot')
    markup.row('📥 CSV yuklab olish', '🔙 Asosiy menyu')
    
    bot.send_message(
        user_id,
        "👨‍💼 *ADMIN PANEL*",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '👥 Barcha foydalanuvchilar')
def all_users(message):
    if message.chat.id not in ADMINS:
        return
    
    users = get_all_users()
    
    if not users:
        bot.send_message(message.chat.id, "📭 Hozircha foydalanuvchilar yo'q")
        return
    
    bot.send_message(message.chat.id, f"👥 *JAMI: {len(users)} ta*", parse_mode="Markdown")
    
    for user_id, user_data in list(users.items())[:5]:  # Faqat 5 tasi
        user_info = f"👤 {user_data['full_name']}\n📅 {user_data['birth_date']}\n🏢 {user_data['work_type']}\n💼 {user_data['position']}"
        bot.send_message(message.chat.id, user_info)

@bot.message_handler(func=lambda message: message.text == '🔍 Qidirish')
def search_start(message):
    if message.chat.id not in ADMINS:
        return
    
    msg = bot.send_message(message.chat.id, "🔍 *Qidirish uchun so'z kiriting:*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_search)

def process_search(message):
    if message.chat.id not in ADMINS:
        return
    
    search_term = message.text
    if not search_term:
        bot.send_message(message.chat.id, "❌ Iltimos, so'z kiriting!")
        return
    
    results = search_users(search_term)
    
    if not results:
        bot.send_message(message.chat.id, f"❌ '{search_term}' bo'yicha natija topilmadi")
        return
    
    bot.send_message(message.chat.id, f"🔍 *Natijalar: {len(results)} ta*", parse_mode="Markdown")
    
    for user_id, user_data in list(results.items())[:5]:  # Faqat 5 tasi
        user_info = f"👤 {user_data['full_name']}\n📅 {user_data['birth_date']}\n🏢 {user_data['work_type']}\n💼 {user_data['position']}"
        bot.send_message(message.chat.id, user_info)

@bot.message_handler(func=lambda message: message.text == '📊 Kunlik hisobot')
def daily_report(message):
    if message.chat.id not in ADMINS:
        return
    
    stats = get_daily_stats()
    
    report_text = (
        f"📊 *KUNLIK HISOBOT*\n\n"
        f"📈 Bugun qo'shilgan: *{stats['daily']} ta*\n"
        f"📊 Jami foydalanuvchilar: *{stats['total']} ta*\n"
        f"📅 Sana: {date.today().strftime('%d.%m.%Y')}"
    )
    
    bot.send_message(message.chat.id, report_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '📈 Oylik hisobot')
def monthly_report(message):
    if message.chat.id not in ADMINS:
        return
    
    stats = get_monthly_stats()
    
    report_text = (
        f"📈 *OYLIK HISOBOT*\n\n"
        f"📈 Bu oy qo'shilgan: *{stats['monthly']} ta*\n"
        f"📊 Jami foydalanuvchilar: *{stats['total']} ta*\n"
        f"📅 Oy: {date.today().strftime('%B %Y')}"
    )
    
    bot.send_message(message.chat.id, report_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '📥 CSV yuklab olish')
def download_csv(message):
    if message.chat.id not in ADMINS:
        return
    
    users = get_all_users()
    
    if not users:
        bot.send_message(message.chat.id, "❌ Yuklab olish uchun ma'lumot yo'q")
        return
    
    # CSV yaratish
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Sarlavha
    csv_writer.writerow(['ID', 'FISh', 'Tugilgan sana', 'Ish turi', 'Lavozim', 'Roʻyxatdan oʻtgan sana'])
    
    # Ma'lumotlar
    for user_id, user_data in users.items():
        csv_writer.writerow([
            user_id,
            user_data['full_name'],
            user_data['birth_date'],
            user_data['work_type'],
            user_data['position'],
            user_data['registered_date'][:10]
        ])
    
    csv_data.seek(0)
    
    # Fayl yuborish
    bot.send_document(
        message.chat.id,
        csv_data.getvalue().encode('utf-8'),
        visible_file_name=f'foydalanuvchilar_{date.today()}.csv',
        caption=f"📊 Jami: {len(users)} ta foydalanuvchi"
    )

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
    
    for admin_id in ADMINS:
        try:
            bot.send_message(
                admin_id,
                f"📩 *YANGI XABAR*\n\n👤 {user_id}\n💬 {user_message}",
                parse_mode="Markdown"
            )
        except:
            pass
    
    bot.send_message(user_id, "✅ Xabar yuborildi!")
    
    if user_id in user_sessions:
        del user_sessions[user_id]

# ==================== BOTNI ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    print("🌐 WEBHOOK MODE - RENDER")
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
