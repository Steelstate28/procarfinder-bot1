from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, InputFile
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
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}

texts = {
    'ua': {
        'start': "Привіт! Я бот команди “ЗАЛІЗНИЙ ШТАТ”. Вибери мову:",
        'ask_description': "Опиши, яку машину шукаєш:",
        'ask_budget': "Який у тебе бюджет?",
        'ask_title': "Який тип тайтлу тебе цікавить?",
        'ask_accident': "Розглядаєш авто після ДТП?",
        'ask_location': "Надішли геолокацію або місто доставки:",
        'ask_contact': "Залиши контакт для зв'язку (номер або @нік):",
        'ask_package': "Оберіть пакет:",
        'ask_extra': "Хочеш щось додати до заявки?",
        'ask_photo': "Надішли до 5 фото авто або натисни 'Пропустити':",
        'ask_document': "Прикріпи файл (Carfax, інвойс тощо) або натисни 'Пропустити':",
        'thanks': "Дякую! Заявка відправлена. Ми з тобою зв’яжемось."
    }
    # Додати 'ru' та 'en' за потребою
}

@dp.message_handler(commands='start')
async def start_handler(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🚀 Запустити", callback_data='start_form'))
    await message.answer("Привіт! Я бот команди “ЗАЛІЗНИЙ ШТАТ”. Щоб почати, натисни кнопку нижче:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'start_form')
async def start_form(callback_query: types.CallbackQuery, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for code, label in languages.items():
        kb.add(KeyboardButton(label))
    await bot.send_message(callback_query.from_user.id, "Обери мову:", reply_markup=kb)
    await Form.language.set()

@dp.message_handler(state=Form.language)
async def set_language(message: types.Message, state: FSMContext):
    selected = [k for k, v in languages.items() if v == message.text]
    if not selected:
        await message.answer("Будь ласка, вибери мову з клавіатури.")
        return
    lang = selected[0]
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
    await Form.title_type.set()
    await message.answer(texts[lang]['ask_title'])

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
    await Form.location.set()
    geo_button = KeyboardButton("📍 Надіслати геолокацію", request_location=True)
    skip_btn = KeyboardButton("Пропустити")
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(geo_button).add(skip_btn)
    await message.answer(texts[lang]['ask_location'], reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.LOCATION, state=Form.location)
async def location_received(message: types.Message, state: FSMContext):
    loc = f"{message.location.latitude}, {message.location.longitude}"
    await state.update_data(location=loc)
    lang = (await state.get_data())['lang']
    await Form.contact.set()
    await message.answer(texts[lang]['ask_contact'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.location)
async def ask_contact(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    lang = (await state.get_data())['lang']
    await Form.contact.set()
    await message.answer(texts[lang]['ask_contact'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.contact)
async def ask_package(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    lang = (await state.get_data())['lang']
    await Form.package.set()
    await message.answer(texts[lang]['ask_package'])

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
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

@dp.message_handler(state=Form.photo)
async def ask_document(message: types.Message, state: FSMContext):
    lang = (await state.get_data())['lang']
    await Form.document.set()
    await message.answer(texts[lang]['ask_document'])

@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=Form.document)
async def save_document(message: types.Message, state: FSMContext):
    await state.update_data(document=message.document.file_id)
    await finish(message, state)

@dp.message_handler(state=Form.document)
async def skip_document(message: types.Message, state: FSMContext):
    await finish(message, state)

async def finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = f"📥 Нова заявка від {message.from_user.full_name} (@{message.from_user.username}):\n\n" \
           f"🚗 Машина: {data['description']}\n" \
           f"💰 Бюджет: {data['budget']}\n" \
           f"📄 Тайтл: {data['title_type']}\n" \
           f"💥 ДТП: {data['accident']}\n" \
           f"📦 Доставка: {data['location']}\n" \
           f"📞 Контакт: {data['contact']}\n" \
           f"🛠️ Пакет: {data['package']}\n" \
           f"✍️ Додатково: {data['extra']}\n"

    await bot.send_message(chat_id=ADMIN_ID, text=text)

    if 'photos' in data:
        for pid in data['photos'][:5]:
            await bot.send_photo(chat_id=ADMIN_ID, photo=pid)

    if 'document' in data:
        await bot.send_document(chat_id=ADMIN_ID, document=data['document'])

    lang = data['lang']
    await message.answer(texts[lang]['thanks'], reply_markup=ReplyKeyboardRemove())
    await state.finish()

if __name__ == '__main__':
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)
