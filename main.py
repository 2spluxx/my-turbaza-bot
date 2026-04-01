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
    price = "450 грн/доба"
    if house_id == "13":
        text = f"🌟 **Будиночок №13 (Люкс)**\n💰 Ціна: {price}"
    else:
        text = f"🏠 **Будиночок №{house_id}**\n💰 Ціна: {price}"
    await callback.message.answer(text)
    await callback.answer()



@dp.callback_query(F.data.startswith("house_"))
async def show_house_details(callback: types.CallbackQuery):
    house_id = callback.data.split("_")[1]

    # Ціна однакова для всіх - 450 грн
    price = "450 грн/доба"

    if house_id == "13":
        text = f"🌟 **Будиночок №13 (Люкс)**\n\nОпис: додаткові зручності.\n💰 Ціна: {price}"
    else:
        text = f"🏠 **Будиночок №{house_id}**\n\nОпис: Затишний будиночок для відпочинку.\n💰 Ціна: {price}"

    await callback.message.answer(text)
    await callback.answer()


@dp.message(F.text == "💰 Ціни")
async def price_handler(message: types.Message):
    await message.answer(
        "💵 **Актуальні ціни:**\n\n"
        "• Будиночки (1-13): **450 грн/доба**\n"
        "• Додаткові послуги: уточнюйте в адміністратора."
    )


@dp.message(F.text == "📍 Як дістатися")
async def location_handler(message: types.Message):
    # Твої координати з Google Maps
    lat = 49.06470438799371  # Перша цифра (широта)
    lon = 33.31754446997391 # Друга цифра (довгота)

    await message.answer("📍 Ми знаходимося тут (натисніть на карту, щоб прокласти маршрут):")

    # Відправляємо інтерактивну карту
    await bot.send_location(chat_id=message.chat.id, latitude=lat, longitude=lon)

    # Також можна додати посилання на Google Maps для зручності
    await message.answer(f"Посилання для навігатора: https://www.google.com/maps?q={lat},{lon}")


@dp.message(F.text == "📞 Контакти")
async def contact_handler(message: types.Message):
    await message.answer("📞 Телефон: +380986302601, +380679858393 \nЧекаємо на ваші дзвінки!")

@dp.message(F.text == "🚣 Активний відпочинок")
async def active_rest_handler(message: types.Message):
    text = (
        "🚣 **Наш прокат спорядження:**\n\n"
        "• 🛶 **Байдарки** — чудовий вибір для прогулянки річкою.\n"
        "• 🏄 **САП-дошки (SUP)** — сучасний та активний відпочинок на воді.\n"
        "• ⛵ **Каяк** — для тих, хто любить швидкість та маневреність.\n\n"
        "🛠 **Катамаран** — *тимчасово на ремонті*, скоро буде в строю!\n\n"
        "📌 Щоб орендувати, зверніться до адміністратора або напишіть нам тут!"
    )
    await message.answer(text)

@dp.message(F.text == "📅 Забронювати відпочинок")
async def book_handler(message: types.Message):
    await message.answer("Вкажіть дату заїзду та номер телефону — ми зв'яжемося з вами для підтвердження!")


@dp.message()
async def process_all_messages(message: types.Message):
    # Якщо це не команда меню, пересилаємо як заявку
    menu_buttons = ["🏡 Наші будиночки", "💰 Ціни", "📍 Як дістатися", "📞 Контакти", "📅 Забронювати відпочинок"]
    if message.text not in menu_buttons:
        await bot.send_message(
            ADMIN_ID,
            f"🔔 **НОВА ЗАЯВКА!**\nВід: {message.from_user.full_name} (@{message.from_user.username})\nТекст: {message.text}"
        )
        await message.answer("✅ Дякуємо! Ваша заявка передана адміністраторам, скоро з вами зв'яжуться.")


async def main():
    print("Бот запущений! Перевіряй Telegram.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
