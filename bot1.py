import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    WebAppInfo,
)

# ----------------- НАСТРОЙКИ -----------------
# Берем токен и ID админа из переменных окружения (GitHub Secrets)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0")) # Если ID нет, будет 0

if not BOT_TOKEN:
    raise ValueError("Токен не найден! Добавьте TELEGRAM_BOT_TOKEN в секреты репозитория.")

if ADMIN_ID == 0:
    logging.warning("ADMIN_ID не задан! Анкеты не будут отправляться.")

WEBAPP_URL = "https://nicelooking.github.io/zenith-widget/"   # ← замените на свою ссылку
SITE_URL = "https://nicelooking.github.io/orinsis-site/"
# ---------------------------------------------

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class Questionnaire(StatesGroup):
    full_name = State()
    birth_date = State()
    experience = State()
    heels = State()
    travel = State()
    time_commitment = State()
    finance = State()
    motivation = State()
    photo = State()
    confirm = State()


def get_keyboard(options: list, placeholder: str = "Выбери вариант"):
    keyboard = [[KeyboardButton(text=option)] for option in options]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=placeholder,
    )


# --- НАЧАЛО ДИАЛОГА ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    webapp_btn = KeyboardButton(
        text="✨ Открыть Zenith",
        web_app=WebAppInfo(url=WEBAPP_URL),
    )
    site_btn = KeyboardButton(
        text="🌐 Наш сайт",
        web_app=WebAppInfo(url=SITE_URL),
    )
    start_form_btn = KeyboardButton(text="📝 Начать заполнение анкеты")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [webapp_btn],
            [site_btn],
            [start_form_btn],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие...",
    )

    welcome_text = (
        "Привет! 🔥\n\n"
        "Рады, что ты хочешь стать частью нашей профессиональной хип-хоп команды.\n\n"
        "Ты можешь:\n"
        "• ✨ открыть **Zenith** — расслабиться и настроиться,\n"
        "• 🌐 заглянуть на **наш сайт** — узнать о команде больше,\n"
        "• 📝 или сразу перейти к **анкете**.\n\n"
        "👇 Выбери действие ниже:"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=keyboard)


# --- Обработчик кнопки запуска анкеты ---
@dp.message(F.text == "📝 Начать заполнение анкеты")
async def start_questionnaire(message: types.Message, state: FSMContext):
    await message.answer(
        "Отлично! Напиши свои **Имя и Фамилию**:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Questionnaire.full_name)


# --- 1. ФИО ---
@dp.message(Questionnaire.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(
        "Укажи свою **полную дату рождения** (в формате ДД.ММ.ГГГГ):\n"
        "Например: 15.03.2000",
        parse_mode="Markdown",
    )
    await state.set_state(Questionnaire.birth_date)


# --- 2. ДАТА РОЖДЕНИЯ ---
@dp.message(Questionnaire.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer(
        "Танцевал(а) ли ты раньше? Если да, то какими стилями занимался(ась) и как долго?",
        parse_mode="Markdown",
    )
    await state.set_state(Questionnaire.experience)


# --- 3. ОПЫТ ---
@dp.message(Questionnaire.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    kb = get_keyboard(["Да", "Нет", "Хочу попробовать"])
    await message.answer(
        "Готов(а) ли ты встать на каблуки (для некоторых постановок и хореографий)?",
        reply_markup=kb,
    )
    await state.set_state(Questionnaire.heels)


# --- 4. КАБЛУКИ ---
@dp.message(Questionnaire.heels)
async def process_heels(message: types.Message, state: FSMContext):
    await state.update_data(heels=message.text)
    kb = get_keyboard(["Да, без проблем", "С трудом, но возможно", "Нет, не смогу"])
    await message.answer(
        "Сможешь ли ты выезжать в другие города на соревнования, чемпионаты и сборы?",
        reply_markup=kb,
    )
    await state.set_state(Questionnaire.travel)


# --- 5. ВЫЕЗДЫ ---
@dp.message(Questionnaire.travel)
async def process_travel(message: types.Message, state: FSMContext):
    await state.update_data(travel=message.text)
    kb = get_keyboard(["Да, готов(а)", "Нужно совмещать с учебой/работой"])
    await message.answer(
        "Готов(а) ли ты уделять тренировкам от 6+ часов в неделю, включая индивидуальную работу?",
        reply_markup=kb,
    )
    await state.set_state(Questionnaire.time_commitment)


# --- 6. ВРЕМЯ ---
@dp.message(Questionnaire.time_commitment)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time_commitment=message.text)
    kb = get_keyboard(["Да, готов(а)", "Обсуждаемо", "Нет"])
    await message.answer(
        "Готов(а) ли ты к финансовым расходам на пошив костюмов, взносы и поездки?",
        reply_markup=kb,
    )
    await state.set_state(Questionnaire.finance)


# --- 7. ФИНАНСЫ ---
@dp.message(Questionnaire.finance)
async def process_finance(message: types.Message, state: FSMContext):
    await state.update_data(finance=message.text)
    await message.answer(
        "Расскажи немного о себе. Почему ты хочешь попасть именно к нашему тренеру и в нашу команду?",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Questionnaire.motivation)


# --- 8. МОТИВАЦИЯ ---
@dp.message(Questionnaire.motivation)
async def process_motivation(message: types.Message, state: FSMContext):
    await state.update_data(motivation=message.text)
    await message.answer(
        "Пришли, пожалуйста, свое фото (желательно во весь рост или танцевальное), чтобы мы тебя запомнили! "
        "(Отправь фото как изображение, а не файл)"
    )
    await state.set_state(Questionnaire.photo)


# --- 9. ФОТО И ПРЕДПРОСМОТР ---
@dp.message(Questionnaire.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    data = await state.get_data()

    summary = (
        "🔍 **Проверь свои данные перед отправкой:**\n\n"
        f"👤 **ФИО:** {data['full_name']}\n"
        f"📅 **Дата рождения:** {data['birth_date']}\n"
        f"🩰 **Опыт:** {data['experience']}\n"
        f"👠 **На каблуки:** {data['heels']}\n"
        f"✈️ **Выезды в др. города:** {data['travel']}\n"
        f"⏰ **Готовность по времени:** {data['time_commitment']}\n"
        f"💰 **Финансы:** {data['finance']}\n"
        f"✍️ **О себе / К тренеру:** {data['motivation']}\n"
    )

    kb = get_keyboard(["Все верно, отправить! 🚀", "Заполнить заново 🔄"])
    await message.answer_photo(
        photo=photo_id, caption=summary, parse_mode="Markdown", reply_markup=kb
    )
    await state.set_state(Questionnaire.confirm)


@dp.message(Questionnaire.photo)
async def process_photo_invalid(message: types.Message):
    await message.answer("Пожалуйста, отправь именно **фотографию**.")


# --- 10. ПОДТВЕРЖДЕНИЕ И ОТПРАВКА АДМИНУ ---
@dp.message(Questionnaire.confirm, F.text == "Все верно, отправить! 🚀")
async def process_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"

    admin_text = (
        "🔔 **НОВАЯ АНКЕТА КАНДИДАТА!**\n\n"
        f"👤 **ФИО:** {data['full_name']}\n"
        f"📅 **Дата рождения:** {data['birth_date']}\n"
        f"✈️ **Telegram:** {username} (ID: `{message.from_user.id}`)\n\n"
        f"🩰 **Опыт:** {data['experience']}\n"
        f"👠 **На каблуки:** {data['heels']}\n"
        f"✈️ **Выезды в др. города:** {data['travel']}\n"
        f"⏰ **Готовность по времени:** {data['time_commitment']}\n"
        f"💰 **Финансы:** {data['finance']}\n\n"
        f"✍️ **Мотивация:** {data['motivation']}\n"
    )

    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=data["photo"],
            caption=admin_text,
            parse_mode="Markdown",
        )
        await message.answer(
            "✅ Спасибо! Твоя анкета успешно отправлена тренеру. "
            "Мы свяжемся с тобой в ближайшее время, если твоя кандидатура пройдет отбор! ✨",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        error_text = str(e)
        logging.error(f"Ошибка отправки админу: {error_text}")
        await message.answer(
            f"❌ Не удалось отправить анкету. Ошибка: {error_text}\n"
            "Пожалуйста, попробуй позже или свяжись с администратором напрямую.",
            reply_markup=ReplyKeyboardRemove(),
        )
        try:
            await message.answer(
                "📝 Твои данные сохранены, вот копия анкеты:",
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer(admin_text, parse_mode="Markdown")
        except Exception:
            pass

    await state.clear()


@dp.message(Questionnaire.confirm, F.text == "Заполнить заново 🔄")
async def process_reset(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Хорошо, начнем сначала. Напиши свои **Имя и Фамилию**:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Questionnaire.full_name)


# --- ЗАПУСК БОТА ---
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())