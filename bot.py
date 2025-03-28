from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile
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
        'ask_contact': "Залиш контакт для зв'язку (номер або @нік):",
        'ask_package': "Оберіть пакет:",
        'ask_extra': "Хочеш щось додати до заявки?",
        'ask_photo': "Надішли до 5 фото авто або натисни 'Пропустити':",
        'ask_document': "Прикріпи файл (Carfax, інвойс тощо) або натисни 'Пропустити':",
        'thanks': "Дякую! Заявка відправлена. Ми з тобою зв'яжемося."
    }
}

@dp.message_handler(commands='start')
async def start_handler(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for code, label in languages.items():
        kb.add(KeyboardButton(label))
    await message.answer("Привіт! Я бот команди “ЗАЛІЗНИЙ ШТАТ”. Вибери мову:", reply_markup=kb)
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
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Clean", "Salvage")
    await Form.title_type.set()
    await message.answer(texts[lang]['ask_title'], reply_markup=kb)

@dp.message_handler(state=Form.title_type)
async def ask_accident(message: types.Message, state: FSMContext):
    await state.update_data(title_type=message.text)
    lang = (await state.get_data())['lang']
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Так", "Ні")
    await Form.accident.set()
    await message.answer(texts[lang]['ask_accident'], reply_markup=kb)

@dp.message_handler(state=Form.accident)
async def ask_location(message: types.Message, state: FSMContext):
    await state.update_data(accident=message.text)
    lang = (await state.get_data())['lang']
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📍 Надіслати геолокацію", request_location=True))
    await Form.location.set()
    await message.answer(texts[lang]['ask_location'], reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.LOCATION, state=Form.location)
async def location_handler(message: types.Message, state: FSMContext):
    loc = f"{message.location.latitude}, {message.location.longitude}"
    await state.update_data(location=loc)
    lang = (await state.get_data())['lang']
    await Form.contact.set()
    await message.answer(texts[lang]['ask_contact'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.location)
async def location_text(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    lang = (await state.get_data())['lang']
    await Form.contact.set()
    await message.answer(texts[lang]['ask_contact'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=Form.contact)
async def ask_package(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    lang = (await state.get_data())['lang']
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("🔍 Перевірка – $500", "✅ Підбір авто – $750")
    await Form.package.set()
    await message.answer(texts[lang]['ask_package'], reply_markup=kb)

@dp.message_handler(state=Form.package)
async def ask_extra(message: types.Message, state: FSMContext):
    await state.update_data(package=message.text)
    lang = (await state.get_data())['lang']
    await Form.extra.set()
    await message.answer(texts[lang]['ask_extra'], reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Пропустити"))

@dp.message_handler(state=Form.extra)
async def ask_photo(message: types.Message, state: FSMContext):
    await state.update_data(extra=message.text)
    lang = (await state.get_data())['lang']
    await Form.photo.set()
    await message.answer(texts[lang]['ask_photo'], reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Пропустити"))

@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.photo)
async def collect_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    if len(photos) >= 5:
        await ask_document(message, state)

@dp.message_handler(lambda message: message.text.lower() in ["пропустити", "skip"], state=Form.photo)
async def ask_document(message: types.Message, state: FSMContext):
    lang = (await state.get_data())['lang']
    await Form.document.set()
    await message.answer(texts[lang]['ask_document'], reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Пропустити"))

@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=Form.document)
async def handle_document(message: types.Message, state: FSMContext):
    await state.update_data(document=message.document.file_id)
    await finish(message, state)

@dp.message_handler(lambda message: message.text.lower() in ["пропустити", "skip"], state=Form.document)
async def finish(message: types.Message, state: FSMContext):
    await send_final_submission(message, state)

async def send_final_submission(message, state):
    data = await state.get_data()
    text = (
        f"📥 Нова заявка від {message.from_user.full_name} (@{message.from_user.username}):\n\n"
        f"🚗 Машина: {data['description']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📄 Тайтл: {data['title_type']}\n"
        f"💥 ДТП: {data['accident']}\n"
        f"📦 Доставка: {data['location']}\n"
        f"📞 Контакт: {data['contact']}\n"
        f"🛠️ Пакет: {data['package']}\n"
        f"✍️ Додатково: {data['extra']}"
    )
    if 'photos' in data:
        for pid in data['photos']:
            await bot.send_photo(chat_id=ADMIN_ID, photo=pid)
    if 'document' in data:
        await bot.send_document(chat_id=ADMIN_ID, document=data['document'])

    await bot.send_message(chat_id=ADMIN_ID, text=text)
    await message.answer(texts[data['lang']]['thanks'], reply_markup=ReplyKeyboardRemove())
    await state.finish()
    await start_handler(message, state)

    if __name__ == '__main__':
        print("Bot is running...")
        executor.start_polling(dp, skip_updates=True)




