import asyncio
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- КОНФІГУРАЦІЯ ---
# ВСТАВ СЮДИ СВІЙ ТОКЕН (ЯКЩО ВІН ПОМИЛКОВИЙ — ОНОВИ ЧЕРЕЗ /REVOKE)
TOKEN = "8764367109:AAH6-pVwVEtEVexiZ10Pwu4LM_9chTB9jHk"
ADMIN_ID = 5010492306

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- КЛАВІАТУРИ ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🏡 Наші будиночки"), types.KeyboardButton(text="💰 Ціни"))
    builder.row(types.KeyboardButton(text="🚣 Активний відпочинок"))
    builder.row(types.KeyboardButton(text="📍 Як дістатися"), types.KeyboardButton(text="📞 Контакти"))
    builder.row(types.KeyboardButton(text="📅 Забронювати відпочинок"))
    return builder.as_markup(resize_keyboard=True)

# --- ОБРОБНИКИ КОМАНД ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Вітаємо на базі відпочинку «Купава» (м. Світловодськ)! ✨\nОберіть потрібний розділ:", reply_markup=main_menu())

@dp.message(F.text == "🏡 Наші будиночки")
async def houses_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    for i in range(1, 13):
        builder.button(text=f"🏠 №{i}", callback_data=f"house_{i}")
    builder.button(text="⭐ Люкс №13", callback_data="house_13")
    builder.adjust(3)
    await message.answer("Оберіть будиночок для детальної інформації:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("house_"))
async def show_house_details(callback: types.CallbackQuery):
    house_id = callback.data.split("_")[1]
    if house_id == "13":
        price = "600 грн/доба"
        text = f"🌟 **Будиночок №13 (Люкс)**\n\nКомфортний номер з усіма зручностями та видом на Дніпро.\n💰 Ціна: {price}"
    else:
        price = "450 грн/доба"
        text = f"🏠 **Будиночок №{house_id}**\n\nЗатишний стандартний будиночок.\n💰 Ціна: {price}"
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text == "💰 Ціни")
async def price_handler(message: types.Message):
    price_text = (
        "💵 **Ціни на відпочинок:**\n\n"
        "🏠 Будиночки №1-12: 450 грн/доба\n"
        "⭐ Люкс №13: 600 грн/доба\n"
        "🚣 Човни/Катамарани: уточнюйте на базі"
    )
    await message.answer(price_text, parse_mode="Markdown")

@dp.message(F.text == "📞 Контакти")
async def contacts_handler(message: types.Message):
    contacts_text = (
        "📞 **Наші номери телефонів:**\n\n"
        "📲 +380986302601\n"
        "📲 +380679858393\n\n"
        "Телефонуйте для бронювання!"
    )
    await message.answer(contacts_text)

@dp.message(F.text == "📍 Як дістатися")
async def location_handler(message: types.Message):
    location_text = (
        "📍 **База відпочинку «Купава»**\n"
        "Ми знаходимося у м. Світловодськ.\n\n"
        "🗺 **Маршрут у Google Maps:**\n"
        "https://www.google.com/maps?q=49.0768,33.1895"
    )
    await message.answer(location_text, disable_web_page_preview=False)

@dp.message()
async def process_all_messages(message: types.Message):
    menu_buttons = ["🏡 Наші будиночки", "💰 Ціни", "📍 Як дістатися", "📞 Контакти", "📅 Забронювати відпочинок", "🚣 Активний відпочинок"]
    if message.text not in menu_buttons:
        admin_text = f"🔔 **НОВА ЗАЯВКА!**\n\n👤 Від: {message.from_user.full_name}\n💬 Текст: {message.text}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
        await message.answer("✅ Ваше повідомлення отримано! Ми зателефонуємо вам найближчим часом.")

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("Бот Купава запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
