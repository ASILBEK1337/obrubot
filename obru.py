from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode
from datetime import datetime, timedelta

API_TOKEN = '7638440684:AAHcYhqtuWyYSYlmcfbzDiqLsBJScPKzRl4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchi obrolari va oxirgi obro' yangilangan vaqti uchun ma'lumotlar
obro_data = {}
last_action_time = {}

# Foydalanuvchining obrosini olish funksiyasi
def get_obro(user_id):
    return obro_data.get(user_id, 0)

# Obro'ni oshirish funksiyasi
def increase_obro(user_id, amount=1):
    obro_data[user_id] = get_obro(user_id) + amount

# Obro'ni kamaytirish funksiyasi
def decrease_obro(user_id, amount=1):
    obro_data[user_id] = max(0, get_obro(user_id) - amount)

# Kunlik cheklovni tekshirish funksiyasi
def can_perform_action(user_id):
    now = datetime.now()
    if user_id in last_action_time:
        last_time = last_action_time[user_id]
        if now - last_time < timedelta(days=1):
            return False
    last_action_time[user_id] = now
    return True

# Start komandasi uchun handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Obro' boshqaruv botiga xush kelibsiz!")

# Obro'ni oshirish uchun handler
@dp.message_handler(commands=['obrooshir'])
async def handle_increase_obro(message: types.Message):
    user_id = message.from_user.id
    if can_perform_action(user_id):
        increase_obro(user_id, 1)
        new_obro = get_obro(user_id)
        await message.reply(f"Sizning obro'ingiz oshirildi! Yangi obro': {new_obro}")
    else:
        await message.reply("Kechirasiz, siz bugun obro' oshirishni allaqachon bajargansiz.")

# Obro'ni kamaytirish uchun handler
@dp.message_handler(commands=['obrokamaytir'])
async def handle_decrease_obro(message: types.Message):
    user_id = message.from_user.id
    if can_perform_action(user_id):
        decrease_obro(user_id, 1)
        new_obro = get_obro(user_id)
        await message.reply(f"Sizning obro'ingiz kamaytirildi! Yangi obro': {new_obro}")
    else:
        await message.reply("Kechirasiz, siz bugun obro' kamaytirishni allaqachon bajargansiz.")

# Foydalanuvchining obrosini ko'rish uchun handler
@dp.message_handler(commands=['obro'])
async def handle_get_obro(message: types.Message):
    user_id = message.from_user.id
    user_obro = get_obro(user_id)
    await message.reply(f"Sizning joriy obro'ingiz: {user_obro}")

# Reytingni ko'rsatish uchun handler
@dp.message_handler(commands=['reyting'])
async def handle_reyting(message: types.Message):
    sorted_obro = sorted(obro_data.items(), key=lambda x: x[1], reverse=True)
    reyting_text = "Obro' reytingi:\n"
    for i, (user_id, obro) in enumerate(sorted_obro, 1):
        username = f"Foydalanuvchi {user_id}"
        if message.chat.get_member(user_id):
            username = (await bot.get_chat_member(message.chat.id, user_id)).user.full_name
        reyting_text += f"{i}. {username} - {obro} obro'\n"
    await message.reply(reyting_text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
