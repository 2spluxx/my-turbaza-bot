import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


TOKEN = "8764367109:AAFiDnNJEuYJf9IJvwq_csdl7RwF65cJWGE"
ADMIN_ID = 5010492306

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Головне меню
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🏡 Наші будиночки"), types.KeyboardButton(text="💰 Ціни"))
    builder.row(types.KeyboardButton(text="🚣 Активний відпочинок")) # Нова кнопка
    builder.row(types.KeyboardButton(text="📍 Як дістатися"), types.KeyboardButton(text="📞 Контакти"))
    builder.row(types.KeyboardButton(text="📅 Забронювати відпочинок"))
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"Вітаємо, {message.from_user.first_name}! 👋\n"
        "Вас вітає бот нашої турбази. Оберіть потрібний розділ:",
        reply_markup=main_menu()
    )


@dp.message(F.text == "🏡 Наші будиночки")
async def houses_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    for i in range(1, 13):
        builder.button(text=f"🏠 №{i}", callback_data=f"house_{i}")
    builder.button(text="⭐ Люкс №13", callback_data="house_13")
    builder.adjust(3)
    await message.answer("Оберіть будиночок:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("house_"))
async def show_house_details(callback: types.CallbackQuery):
    house_id = callback.data.split("_")[1]
    
    if house_id == "13":
        price = "600 грн/доба"
        text = f"🌟 **Будиночок №13 (Люкс)**\n💰 Ціна: {price}"
    else:
        price = "450 грн/доба"
        text = f"🏠 **Будиночок №{house_id}**\n💰 Ціна: {price}"
    
    await callback.message.answer(text)
    await callback.answer()



@dp.callback_query(F.data.
