from aiogram import Bot, Dispatcher, types
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,
                           InlineKeyboardButton, ReplyKeyboardRemove, InputMediaPhoto, BotCommand)
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from config import TOKEN, ADMIN_ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    language = State()
    description = State()
    budget = State()
    title_type = State()
    accident = State()
    location = State()
    contact = State()
    package = State()
    extra = State()
    photo = State()
    document = State()

languages = {
    'ua': '🇺🇦 Українська',
    'ru': 'Русский',
    'en': '🇺🇸 English'
}

texts = {
    'ua': {
        'start': "Привіт! Я бот команди \"ProCARFINDER\". Обери мову нижче:",
        'begin': "Почати",
        'ask_description': "Опиши, яку машину шукаєш:",
        'ask_budget': "Який у тебе бюджет?",
        'ask_title': "Який тип тайтлу тебе цікавить?",
        'ask_accident': "Розглядаєш авто після ДТП?",
        'ask_location': "Надішли геолокацію або місто доставки:",
        'ask_contact': "Залиши контакт для зв'язку (номер або @нік):",
        'ask_package': "Оберіть пакет:",
        'ask_extra': "Хочеш щось додати до заявки? Напиши або натисни 'Пропустити':",
        'ask_photo': "Надішли до 5 фото авто або натисни 'Пропустити':",
        'ask_document': "Прикріпи файл (Carfax, інвойс тощо) або натисни 'Пропустити':",
        'thanks': "Дякую! Заявка відправлена. Ми з тобою зв’яжемось.",
        'yes': "Так",
        'no': "Ні",
        'skip': "Пропустити",
        'check': "🔍 Перевірка авто $500",
        'full': "✅ Підбір авто $750"
    },
    'ru': {
        'start': "Привет! Я бот команды \"ProCARFINDER\". Выберите язык ниже:",
        'begin': "Начать",
        'ask_description': "Опиши, какую машину ищешь:",
        'ask_budget': "Какой у тебя бюджет?",
        'ask_title': "Какой тип тайтла тебе интересует?",
        'ask_accident': "Рассматриваешь авто после ДТП?",
        'ask_location': "Отправь геолокацию или напиши город доставки:",
        'ask_contact': "Оставь контакт (телефон или @ник):",
        'ask_package': "Выбери пакет:",
        'ask_extra': "Хочешь добавить что-то? Напиши или нажми 'Пропустить':",
        'ask_photo': "Пришли до 5 фото авто или нажми 'Пропустить':",
        'ask_document': "Прикрепи файл (Carfax, invoice и т.д.) или нажми 'Пропустить':",
        'thanks': "Спасибо! Заявка отправлена. Мы скоро свяжемся с тобой.",
        'yes': "Да",
        'no': "Нет",
        'skip': "Пропустить",
        'check': "🔍 Проверка авто $500",
        'full': "✅ Подбор авто $750"
    },
    'en': {
        'start': "Hi! I’m the \"ProCARFINDER\" bot. Choose your language:",
        'begin': "Start",
        'ask_description': "Describe the car you're looking for:",
        'ask_budget': "What's your budget?",
        'ask_title': "What title type are you interested in?",
        'ask_accident': "Are you open to cars with accident history?",
        'ask_location': "Send your location or delivery city:",
        'ask_contact': "Leave your contact (phone or @username):",
        'ask_package': "Choose a service package:",
        'ask_extra': "Want to add anything else? Type it or press 'Skip':",
        'ask_photo': "Send up to 5 car photos or press 'Skip':",
        'ask_document': "Attach a document (Carfax, invoice, etc.) or press 'Skip':",
        'thanks': "Thank you! Your request has been submitted. We'll get in touch with you soon.",
        'yes': "Yes",
        'no': "No",
        'skip': "Skip",
        'check': "🔍 Car check $500",
        'full': "✅ Full car search $750"
    }
}

@dp.message_handler(commands='start')
async def start_handler(message: types.Message, state: FSMContext):
    inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🚀", callback_data="begin"))
    await message.answer(texts['ua']['start'], reply_markup=inline_kb)

@dp.callback_query_handler(lambda c: c.data == 'begin')
async def begin_form(callback_query: types.CallbackQuery, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for code, label in languages.items():
        kb.add(KeyboardButton(label))
    await bot.send_message(callback_query.from_user.id, "Оберіть мову:", reply_markup=kb)
    await Form.language.set()

@dp.message_handler(state=Form.language)
async def set_language(message: types.Message, state: FSMContext):
    lang = None
    for code, label in languages.items():
        if message.text in label:
            lang = code
            break
    if not lang:
        await message.answer("Будь ласка, вибери мову з клавіатури.")
        return
    await state.update_data(lang=lang)
    await Form.description.set()
    await message.answer(texts[lang]['ask_description'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.description)
async def ask_budget(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    lang = (await state.get_data())['lang']
    await Form.budget.set()
    await message.answer(texts[lang]['ask_budget'])

@dp.message_handler(state=Form.budget)
async def ask_title(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    lang = (await state.get_data())['lang']
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Clean"), KeyboardButton("Salvage"))
    await Form.title_type.set()
    await message.answer(texts[lang]['ask_title'], reply_markup=kb)

@dp.message_handler(state=Form.title_type)
async def ask_accident(message: types.Message, state: FSMContext):
    await state.update_data(title_type=message.text)
    lang = (await state.get_data())['lang']
    await Form.accident.set()
    await message.answer(texts[lang]['ask_accident'])

@dp.message_handler(state=Form.accident)
async def ask_location(message: types.Message, state: FSMContext):
    await state.update_data(accident=message.text)
    lang = (await state.get_data())['lang']
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📍 Надіслати геолокацію", request_location=True))
    await Form.location.set()
    await message.answer(texts[lang]['ask_location'], reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.LOCATION, state=Form.location)
async def handle_location(message: types.Message, state: FSMContext):
    loc = f"{message.location.latitude}, {message.location.longitude}"
    await state.update_data(location=loc)
    lang = (await state.get_data())['lang']
    await Form.contact.set()
    await message.answer(texts[lang]['ask_contact'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.location)
async def handle_location_text(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    lang = (await state.get_data())['lang']
    await Form.contact.set()
    await message.answer(texts[lang]['ask_contact'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.contact)
async def ask_package(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    lang = (await state.get_data())['lang']
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔍 Перевірка авто $500"), KeyboardButton("✅ Підбір авто $750"))
    await Form.package.set()
    await message.answer(texts[lang]['ask_package'], reply_markup=kb)

@dp.message_handler(state=Form.package)
async def ask_extra(message: types.Message, state: FSMContext):
    await state.update_data(package=message.text)
    lang = (await state.get_data())['lang']
    skip_btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустити"))
    await Form.extra.set()
    await message.answer(texts[lang]['ask_extra'], reply_markup=skip_btn)

@dp.message_handler(state=Form.extra)
async def ask_photo(message: types.Message, state: FSMContext):
    await state.update_data(extra=message.text)
    lang = (await state.get_data())['lang']
    skip_btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустити"))
    await Form.photo.set()
    await message.answer(texts[lang]['ask_photo'], reply_markup=skip_btn)

@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.photo)
async def save_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    if len(photos) >= 5:
        await ask_document(message, state)

@dp.message_handler(lambda msg: msg.text == "Пропустити", state=Form.photo)
async def ask_document(message: types.Message, state: FSMContext):
    lang = (await state.get_data())['lang']
    await Form.document.set()
    await message.answer(texts[lang]['ask_document'])

@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=Form.document)
async def handle_document(message: types.Message, state: FSMContext):
    await state.update_data(document=message.document.file_id)
    await finish(message, state)

@dp.message_handler(lambda msg: msg.text == "Пропустити", state=Form.document)
async def skip_document(message: types.Message, state: FSMContext):
    await finish(message, state)

async def finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = (
        f"📥 Заявка від @{message.from_user.username}\n\n"
        f"🚗 Машина: {data['description']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📄 Тайтл: {data['title_type']}\n"
        f"💥 ДТП: {data['accident']}\n"
        f"📍 Локація: {data['location']}\n"
        f"📞 Контакт: {data['contact']}\n"
        f"🛠️ Пакет: {data['package']}\n"
        f"✍️ Додатково: {data['extra']}"
    )

    await bot.send_message(ADMIN_ID, text)

    if 'photos' in data:
        media = [InputMediaPhoto(p) for p in data['photos'][:10]]
        await bot.send_media_group(ADMIN_ID, media)

    if 'document' in data:
        await bot.send_document(ADMIN_ID, data['document'])

    lang = data['lang']
    await message.answer(texts[lang]['thanks'], reply_markup=ReplyKeyboardRemove())
    await state.finish()

async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="Розпочати роботу з ботом")
    ]
    await bot.set_my_commands(commands)

if __name__ == '__main__':
    import asyncio

    async def main():
        await set_commands(bot)
        print("Bot is running...")
        await dp.start_polling()

    asyncio.run(main())
