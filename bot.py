import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

TOKEN = os.getenv("TOKEN")  # токен через переменную окружения
ADMIN_ID = 1141002512# твой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_messages = {}

# ----- TELEGRAM -----
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("✉️ Предложка\n\nОтправь сообщение и выбери: анонимно или с именем")

@dp.message()
async def receive_message(message: types.Message):
    user_messages[message.from_user.id] = message
    kb = InlineKeyboardBuilder()
    kb.button(text="🔒 Анонимно", callback_data="anon")
    kb.button(text="👤 С именем", callback_data="name")
    kb.adjust(2)
    await message.answer("Как отправить сообщение?", reply_markup=kb.as_markup())

@dp.callback_query(F.data.in_(["anon", "name"]))
async def send_to_admin(callback: types.CallbackQuery):
    message = user_messages.pop(callback.from_user.id)
    header = "📨 Анонимно" if callback.data == "anon" else f"📨 От @{callback.from_user.username or callback.from_user.full_name}"

    if message.text:
        await bot.send_message(ADMIN_ID, f"{header}\n\n{message.text}")
    elif message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=header)
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=header)
    elif message.voice:
        await bot.send_voice(ADMIN_ID, message.voice.file_id, caption=header)

    await callback.message.edit_text("✅ Отправлено")
    await callback.answer()

# ----- WEB SERVER ДЛЯ RENDER -----
async def handle(request):
    return web.Response(text="Bot is running")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))  # Render требует PORT
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ----- MAIN -----
async def main():
    await start_web()
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())