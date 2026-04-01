import asyncio
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- НАЛАШТУВАННЯ ---
TOKEN = "8164367109:AAFIDnNJEyJf9Ijvwq_csdl7RwF65cJNGE"
ADMIN_ID = 5010492306

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)
@app.route('/')
def index(): return "Бот бази Купава працює!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ГОЛОВНЕ МЕНЮ ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🏡 Наші будиночки"), types.KeyboardButton(text="💰 Ціни"))
    builder.row(types.KeyboardButton(text="🚣 Активний відпочинок"))
    builder.row(types.KeyboardButton(text="📍 Як дістатися"), types.KeyboardButton(text="📞 Контакти"))
    builder.row(types.KeyboardButton(text="📅 Забронювати відпочинок"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Вітаємо на базі відпочинку «Купава» (м. Світловодськ)! ✨\nОберіть розділ меню:", reply_markup=main_menu())

# --- РОБОТА КНОПОК ---

@dp.message(F.text == "🏡 Наші будиночки")
async def houses(message: types.Message):
    builder = InlineKeyboardBuilder()
    for i in range(1, 13):
        builder.button(text=f"🏠 №{i}", callback_data=f"h_{i}")
    builder.button(text="⭐ Люкс №13", callback_data="h_13")
    builder.adjust(3)
    await message.answer("Оберіть будиночок для перегляду деталей:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("h_"))
async def house_info(callback: types.CallbackQuery):
    h_id = callback.data.split("_")[1]
    price = "600 грн/доба" if h_id == "13" else "450 грн/доба"
    name = "Люкс №13" if h_id == "13" else f"Будиночок №{h_id}"
    await callback.message.answer(f"🌟 **{name}**\n💰 Ціна: {price}\n\nДля бронювання натисніть кнопку в меню.", parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text == "💰 Ціни")
async def prices(message: types.Message):
    await message.answer("💵 **Наші ціни:**\n- Будиночки №1-12: 450 грн/доба\n- Люкс №13: 600 грн/доба\n- Оренда човна: від 100 грн")

@dp.message(F.text == "🚣 Активний відпочинок")
async def active_rest(message: types.Message):
    await message.answer("🚣 **Активний відпочинок у нас:**\n- Прогулянки на човнах\n- Риболовля\n- Оренда катамаранів\n- Мангальна зона")

@dp.message(F.text == "📅 Забронювати відпочинок")
async def booking(message: types.Message):
    await message.answer("📅 **Як забронювати?**\n\nПросто напишіть сюди дату, яка вас цікавить, і ваш номер телефону. Наш адміністратор отримає заявку і зателефонує вам!")

@dp.message(F.text == "📞 Контакти")
async def contacts(message: types.Message):
    await message.answer("📞 **Наші номери:**\n+380986302601\n+380679858393\n\nТелефонуйте у будь-який час!")

@dp.message(F.text == "📍 Як дістатися")
async def location(message: types.Message):
    await message.answer("📍 **Ми у Світловодську (База Купава)**\n🗺 Карта: http://google.com/maps?q=49.0768,33.1895")

# --- ПРИЙОМ ЗАЯВОК (ВІДПРАВКА ТОБІ) ---
@dp.message()
async def handle_messages(message: types.Message):
    # Список назв кнопок, щоб бот не пересилав їх як "заявки"
    menu_btns = ["🏡 Наші будиночки", "💰 Ціни", "🚣 Активний відпочинок", "📍 Як дістатися", "📞 Контакти", "📅 Забронювати відпочинок"]
    
    if message.text not in menu_btns:
        await bot.send_message(ADMIN_ID, f"🔔 **НОВА ЗАЯВКА!**\n👤 Від: {message.from_user.full_name}\n💬 Текст: {message.text}")
        await message.answer("✅ Вашу заявку отримано! Адміністратор скоро зв'яжеться з вами.")

# --- ЗАПУСК ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
