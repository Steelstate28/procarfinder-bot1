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
        'thanks': "Дякую! Заявка відправлена. Ми з тобою зв'яжемось."
    }
}

@dp.message_handler(commands='start')
async def start_handler(message: types.Message, state: FSMContext):
    start_btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🚀 Запустити", callback_data='begin')
    )
    await message.answer("Щоб почати, натисни кнопку нижче:", reply_markup=start_btn)

@dp.callback_query_handler(lambda call: call.data == 'begin')
async def begin_form(call: types.CallbackQuery, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for code, label in languages.items():
        kb.add(KeyboardButton(label))
    await call.message.answer(texts['ua']['start'], reply_markup=kb)
    await Form.language.set()

@dp.message_handler(state=Form.language)
async def ask_description(message: types.Message, state: FSMContext):
    selected = [k for k, v in languages.items() if v == message.text]
    if not selected:
        await message.answer("Будь ласка, вибери мову з клавіатури.")
        return
    lang = selected[0]
    await state.update_data(lang=lang)
    await message.answer(texts[lang]['ask_description'], reply_markup=ReplyKeyboardRemove())
    await Form.description.set()

@dp.message_handler(state=Form.description)
async def ask_budget(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    lang = (await state.get_data())['lang']
    await message.answer(texts[lang]['ask_budget'])
    await Form.budget.set()

@dp.message_handler(state=Form.budget)
async def ask_title(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    lang = (await state.get_data())['lang']
    await message.answer(texts[lang]['ask_title'])
    await Form.title_type.set()

@dp.message_handler(state=Form.title_type)
async def ask_accident(message: types.Message, state: FSMContext):
    await state.update_data(title_type=message.text)
    lang = (await state.get_data())['lang']
    await message.answer(texts[lang]['ask_accident'])
    await Form.accident.set()

@dp.message_handler(state=Form.accident)
async def ask_location(message: types.Message, state: FSMContext):
    await state.update_data(accident=message.text)
    lang = (await state.get_data())['lang']
    await message.answer(texts[lang]['ask_location'])
    await Form.location.set()

@dp.message_handler(content_types=['location', 'text'], state=Form.location)
async def ask_contact(message: types.Message, state: FSMContext):
    if message.location:
        location_text = f"{message.location.latitude}, {message.location.longitude}"
    else:
        location_text = message.text
    await state.update_data(location=location_text)
    lang = (await state.get_data())['lang']
    await message.answer(texts[lang]['ask_contact'])
    await Form.contact.set()

@dp.message_handler(state=Form.contact)
async def ask_package(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    lang = (await state.get_data())['lang']
    await message.answer(texts[lang]['ask_package'])
    await Form.package.set()

@dp.message_handler(state=Form.package)
async def ask_extra(message: types.Message, state: FSMContext):
    await state.update_data(package=message.text)
    lang = (await state.get_data())['lang']
    btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустити"))
    await message.answer(texts[lang]['ask_extra'], reply_markup=btn)
    await Form.extra.set()

@dp.message_handler(state=Form.extra)
async def ask_photo(message: types.Message, state: FSMContext):
    await state.update_data(extra=message.text)
    lang = (await state.get_data())['lang']
    btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустити"))
    await message.answer(texts[lang]['ask_photo'], reply_markup=btn)
    await Form.photo.set()

@dp.message_handler(state=Form.photo, content_types=types.ContentType.PHOTO)
async def ask_document(message: types.Message, state: FSMContext):
    photos = [photo.file_id for photo in message.photo]
    await state.update_data(photo=photos)
    lang = (await state.get_data())['lang']
    btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустити"))
    await message.answer(texts[lang]['ask_document'], reply_markup=btn)
    await Form.document.set()

@dp.message_handler(state=Form.photo)
async def skip_photo(message: types.Message, state: FSMContext):
    if message.text.lower() in ["пропустити", "skip"]:
        await state.update_data(photo=None)
        lang = (await state.get_data())['lang']
        await message.answer(texts[lang]['ask_document'])
        await Form.document.set()

@dp.message_handler(state=Form.document, content_types=types.ContentType.DOCUMENT)
async def finish_form(message: types.Message, state: FSMContext):
    await state.update_data(document=message.document.file_id)
    await send_summary(message, state)

@dp.message_handler(state=Form.document)
async def skip_document(message: types.Message, state: FSMContext):
    if message.text.lower() in ["пропустити", "skip"]:
        await state.update_data(document=None)
        await send_summary(message, state)

def format_summary(data, user):
    return (
        f"📥 Нова заявка від {user.full_name} (@{user.username}):\n\n"
        f"🚗 Машина: {data['description']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📄 Тайтл: {data['title_type']}\n"
        f"💥 ДТП: {data['accident']}\n"
        f"📍 Доставка: {data['location']}\n"
        f"📞 Контакт: {data['contact']}\n"
        f"🛠️ Пакет: {data['package']}\n"
        f"✍️ Додатково: {data['extra']}"
    )

async def send_summary(message, state):
    data = await state.get_data()
    summary = format_summary(data, message.from_user)
    await bot.send_message(ADMIN_ID, summary)
    if data.get('photo'):
        for pid in data['photo']:
            await bot.send_photo(ADMIN_ID, pid)
    if data.get('document'):
        await bot.send_document(ADMIN_ID, data['document'])
    lang = data['lang']
    await message.answer(texts[lang]['thanks'], reply_markup=ReplyKeyboardRemove())
    await state.finish()

if __name__ == '__main__':
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)
