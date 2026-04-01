import asyncio
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- КОНФІГУРАЦІЯ ---
TOKEN = "8764367109:AAFiDnNJEuYJf9IJvwq_csdl7RwF65cJWGE"
ADMIN_ID = 5010492306

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (ЩОБ НЕ ЗАСИНАВ) ---
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
    await message.answer("Вас вітає турбаза! Оберіть розділ меню нижче:", reply_markup=main_menu())

@dp.message(F.text == "🏡 Наші будиночки")
async def houses_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Будиночки з 1 по 12
    for i in range(1, 13):
        builder.button(text=f"🏠 №{i}", callback_data=f"house_{i}")
    # Окремо Люкс №13
    builder.button(text="⭐ Люкс №13", callback_data="house_13")
    builder.adjust(3)
    await message.answer("Оберіть будиночок, щоб дізнатися деталі:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("house_"))
async def show_house_details(callback: types.CallbackQuery):
    house_id = callback.data.split("_")[1]
    
    if house_id == "13":
        price = "600 грн/доба"
        text = f"🌟 **Будиночок №13 (Люкс)**\n\nОпис: Покращені умови, кондиціонер, власна тераса.\n💰 Ціна: {price}"
    else:
        price = "450 грн/доба"
        text = f"🏠 **Будиночок №{house_id}**\n\nОпис: Затишний будиночок для відпочинку.\n💰 Ціна: {price}"
    
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text == "💰 Ціни")
async def price_handler(message: types.Message):
    price_text = (
        "💵 **Актуальні ціни на сезон:**\n\n"
        "🏠 Стандарт (№1-12): 450 грн/доба\n"
        "⭐ Люкс (№13): 600 грн/доба\n\n"
        "🚣 Оренда човна: 100 грн/година"
    )
    await message.answer(price_text, parse_mode="Markdown")

@dp.message(F.text == "📞 Контакти")
async def contacts_handler(message: types.Message):
    await message.answer("📞 **Наші контакти:**\n\nАдміністрація: +380XXXXXXXXX\nМи чекаємо на ваші дзвінки!")

@dp.message(F.text == "📍 Як дістатися")
async def location_handler(message: types.Message):
    await message.answer("📍 Ми знаходимося поблизу Світловодська.\n[Посилання на Google Maps]")

# --- ПРИЙОМ ЗАЯВОК (БУДЬ-ЯКИЙ ТЕКСТ) ---
@dp.message()
async def process_all_messages(message: types.Message):
    menu_buttons = ["🏡 Наші будиночки", "💰 Ціни", "📍 Як дістатися", "📞 Контакти", "📅 Забронювати відпочинок", "🚣 Активний відпочинок"]
    
    if message.text not in menu_buttons:
        # Відправка адміну
        admin_text = f"🔔 **НОВА ЗАЯВКА!**\n\n👤 Від: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}\n💬 Текст: {message.text}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
        
        # Відповідь клієнту
        await message.answer("✅ Дякуємо! Ваша заявка передана, скоро вам зателефонують.")

# --- ЗАПУСК ---
async def main():
    # Запускаємо Flask у фоновому потоці
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Бот запущений! Перевіряй Telegram.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот зупинений")
