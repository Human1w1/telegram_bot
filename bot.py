import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8365401619:AAFVahZXI_2fJRR1JdBiTlEHnpd1fHOL5VA"
ADMIN_ID = 1141002512# твой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# временное хранилище сообщений
user_messages = {}


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "✉️ Предложка\n\n"
        "Отправь сообщение (текст, фото, видео или голосовое),\n"
        "потом выбери: анонимно или с именем."
    )


@dp.message()
async def receive_message(message: types.Message):
    user_messages[message.from_user.id] = message

    kb = InlineKeyboardBuilder()
    kb.button(text="🔒 Анонимно", callback_data="anon")
    kb.button(text="👤 С именем", callback_data="name")
    kb.adjust(2)

    await message.answer(
        "Как отправить сообщение?",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data.in_(["anon", "name"]))
async def send_to_admin(callback: types.CallbackQuery):
    message = user_messages.get(callback.from_user.id)
    if not message:
        await callback.answer("Сообщение не найдено", show_alert=True)
        return

    is_anon = callback.data == "anon"

    if is_anon:
        header = "📨 Новое сообщение (анонимно)"
    else:
        user = callback.from_user
        name = user.username or user.full_name
        header = f"📨 Новое сообщение от @{name}"

    # ---- ТЕКСТ ----
    if message.text:
        await bot.send_message(
            ADMIN_ID,
            f"{header}\n\n{message.text}"
        )

    # ---- ФОТО ----
    elif message.photo:
        await bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=header
        )

    # ---- ВИДЕО ----
    elif message.video:
        await bot.send_video(
            ADMIN_ID,
            message.video.file_id,
            caption=header
        )

    # ---- ГОЛОСОВОЕ ----
    elif message.voice:
        await bot.send_voice(
            ADMIN_ID,
            message.voice.file_id,
            caption=header
        )

    else:
        await bot.send_message(
            ADMIN_ID,
            f"{header}\n\n(неподдерживаемый тип сообщения)"
        )

    user_messages.pop(callback.from_user.id, None)

    await callback.message.edit_text("✅ Сообщение отправлено")
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())