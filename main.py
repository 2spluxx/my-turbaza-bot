import asyncio
import os
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- НАЛАШТУВАННЯ ---
TOKEN = "8764367109:AAH6-pVwVEtEVexiZ10Pwu4LM_9chTB9jHk"
ADMIN_ID = 5010492306

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (Keep-alive) ---
app = Flask(__name__)
@app.route('/')
def index(): return "Бот бази Купава працює!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- КНОПКИ ГОЛОВНОГО МЕНЮ ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🏡 Наші будиночки"), types.KeyboardButton(text="💰 Ціни"))
    builder.row(types.KeyboardButton(text="🚣 Активний відпочинок"))
    builder.row(types.KeyboardButton(text="📍 Як дістатися"), types.KeyboardButton(text="📞 Контакти"))
    builder.row(types.KeyboardButton(text="📅 Забронювати відпочинок"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Вітаємо на базі відпочинку «Купава» (м. Світловодськ)! ✨\nОберіть розділ меню:", 
        reply_markup=main_menu()
    )

# --- ПЕРЕГЛЯД БУДИНОЧКІВ (INLINE) ---
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
    
    # Можна додати опис для кожного будиночка тут
    await callback.message.answer(
        f"🌟 **{name}**\n💰 Ціна: {price}\n\nЩоб забронювати, натисніть кнопку в меню нижче.", 
        parse_mode="Markdown"
    )
    await callback.answer()

# --- ІНФОРМАЦІЙНІ РОЗДІЛИ ---
@dp.message(F.text == "💰 Ціни")
async def prices(message: types.Message):
    await message.answer("💵 **Наші ціни:**\n- Будиночки №1-12: 450 грн/доба\n- Люкс №13: 600 грн/доба\n- Оренда човна: від 100 грн")

@dp.message(F.text == "🚣 Активний відпочинок")
async def active_rest(message: types.Message):
    await message.answer("🚣 **Дозвілля на базі:**\n- Прогулянки на човнах\n- Риболовля\n- Оренда катамаранів\n- Зона для мангалів")

@dp.message(F.text == "📞 Контакти")
async def contacts(message: types.Message):
    await message.answer("📞 **Наші номери:**\n+380986302601\n+380679858393\n\nТелефонуйте, ми завжди на зв'язку!")

@dp.message(F.text == "📍 Як дістатися")
async def location(message: types.Message):
    await message.answer("📍 **Ми у Світловодську (База Купава)**\n🗺 Карта: [Натисніть тут](https://www.google.com/maps?q=49.0711,33.2081)", disable_web_page_preview=False)

# --- БРОНЮВАННЯ ТА ОБРОБКА КОНТАКТІВ ---
@dp.message(F.text == "📅 Забронювати відпочинок")
async def booking(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📱 Надіслати мій номер", request_contact=True))
    builder.row(types.KeyboardButton(text="⬅️ Назад"))
    
    await message.answer(
        "📅 **Бронювання**\n\nНатисніть кнопку нижче, щоб надіслати свій номер телефону, або просто напишіть повідомлення з датою відпочинку.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(F.contact)
async def handle_contact(message: types.Message):
    contact = message.contact
    user_mention = f"[@{message.from_user.username}]" if message.from_user.username else f"ID: {message.from_user.id}"
    admin_text = f"🔔 **НОВА ЗАЯВКА (КОНТАКТ)!**\n👤 Ім'я: {contact.first_name}\n📞 Тел: {contact.phone_number}\n🔗 Профіль: {user_mention}"
    await bot.send_message(ADMIN_ID, admin_text)
    await message.answer("✅ Номер отримано! Адміністратор скоро зателефонує вам.", reply_markup=main_menu())

@dp.message()
async def handle_messages(message: types.Message):
    menu_btns = ["🏡 Наші будиночки", "💰 Ціни", "🚣 Активний відпочинок", "📍 Як дістатися", "📞 Контакти", "📅 Забронювати відпочинок", "⬅️ Назад"]
    if message.text == "⬅️ Назад":
        await message.answer("Головне меню:", reply_markup=main_menu())
        return
    if message.text and message.text not in menu_btns:
        user_info = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
        await bot.send_message(ADMIN_ID, f"🔔 **НОВА ЗАЯВКА!**\n👤 Від: {user_info}\n💬 Текст: {message.text}")
        await message.answer("✅ Ваше повідомлення надіслано адміністратору! Чекайте на відповідь.")

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот вимкнений")
