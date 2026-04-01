import asyncio
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- КОНФІГУРАЦІЯ ---
TOKEN = "8764367109:AAH6-pVwVEtEVexiZ10Pwu4LM_9chTB9jHk"
ADMIN_ID = 5010492306

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- МІНІ-СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)
@app.route('/')
def index(): return "Bot is alive"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- МЕНЮ ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🏡 Наші будиночки"), types.KeyboardButton(text="💰 Ціни"))
    builder.row(types.KeyboardButton(text="📍 Як дістатися"), types.KeyboardButton(text="📞 Контакти"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Вітаємо у «Купаві» (Світловодськ)! ✨", reply_markup=main_menu())

@dp.message(F.text == "🏡 Наші будиночки")
async def houses(message: types.Message):
    builder = InlineKeyboardBuilder()
    for i in range(1, 13):
        builder.button(text=f"🏠 №{i}", callback_data=f"h_{i}")
    builder.button(text="⭐ Люкс №13", callback_data="h_13")
    builder.adjust(3)
    await message.answer("Оберіть будиночок:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("h_"))
async def house_info(callback: types.CallbackQuery):
    h_id = callback.data.split("_")[1]
    price = "600 грн" if h_id == "13" else "450 грн"
    name = "Люкс №13" if h_id == "13" else f"Будиночок №{h_id}"
    await callback.message.answer(f"🌟 **{name}**\n💰 Ціна: {price}/доба", parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text == "📞 Контакти")
async def contacts(message: types.Message):
    await message.answer("📞 Бронювання:\n+380986302601\n+380679858393")

@dp.message(F.text == "📍 Як дістатися")
async def location(message: types.Message):
    await message.answer("📍 База «Купава», м. Світловодськ\n🗺 Карта: https://maps.app.goo.gl/3f4Y4U1X1X1X1X1X")

@dp.message()
async def forward_to_admin(message: types.Message):
    await bot.send_message(ADMIN_ID, f"🔔 Заявка від {message.from_user.full_name}:\n{message.text}")
    await message.answer("✅ Ваша заявка отримана, ми скоро зателефонуємо!")

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
