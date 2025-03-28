from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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
    delivery = State()
    contact = State()
    package = State()
    extra = State()

languages = {
    'ua': '🇺🇦 Українська',
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}

texts = {
    'ua': {
        'start': "Привіт! Я бот команди “ЗАЛІЗНИЙ ШТАТ”. Вибери мову:",
        'ask_description': "Опиши, яку машину шукаєш (марка, модель, рік, пробіг, колір тощо):",
        'ask_budget': "Який у тебе бюджет?",
        'ask_title': "Який тип тайтлу тебе цікавить?",
        'ask_accident': "Розглядаєш авто після ДТП? (Так / Ні)",
        'ask_delivery': "Куди має бути доставка (штат або місто)?",
        'ask_contact': "Залиш контакт для зв'язку (номер або @нік):",
        'ask_package': "Оберіть пакет:\n\n1. 🔍 Перевірка авто перед покупкою – $500\n2. ✅ Підбір авто “під ключ” – $750\n\n*Якщо авто не підійде, можна доплатити $250 для переходу на повний пакет*",
        'ask_extra': "Хочеш щось додати до заявки? Напиши повідомлення або натисни 'Пропустити':",
        'thanks': "Дякую! Заявка відправлена. Ми скоро з тобою зв’яжемось."
    },
    'ru': {
        'start': "Привет! Я бот команды “ЗАЛІЗНИЙ ШТАТ”. Выбери язык:",
        'ask_description': "Опиши, какую машину ты ищешь (марка, модель, год, пробег, цвет и т.д.):",
        'ask_budget': "Какой у тебя бюджет?",
        'ask_title': "Какой тип тайтла интересует?",
        'ask_accident': "Рассматриваешь авто после ДТП? (Да / Нет)",
        'ask_delivery': "Куда нужна доставка (штат или город)?",
        'ask_contact': "Оставь контакт для связи (номер или @ник):",
        'ask_package': "Выбери пакет:\n\n1. 🔍 Проверка авто перед покупкой – $500\n2. ✅ Подбор авто “под ключ” – $750\n\n*Если авто не подойдет — можно доплатить $250 и перейти на полный пакет*",
        'ask_extra': "Хочешь что-то добавить к заявке? Напиши сообщение или нажми 'Пропустить':",
        'thanks': "Спасибо! Заявка отправлена. Мы скоро с тобой свяжемся."
    },
    'en': {
        'start': "Hi! I'm the “ZALIZNYI SHTAT” bot. Choose your language:",
        'ask_description': "Describe what kind of car you're looking for (make, model, year, mileage, color, etc.):",
        'ask_budget': "What's your budget?",
        'ask_title': "Which title type are you interested in?",
        'ask_accident': "Are you open to cars with accident history? (Yes / No)",
        'ask_delivery': "Where should the car be delivered (state or city)?",
        'ask_contact': "Leave your contact (phone or @username):",
        'ask_package': "Choose a service package:\n\n1. 🔍 Vehicle check before purchase – $500\n2. ✅ Full auto search – $750\n\n*If the vehicle isn’t suitable — you can pay extra $250 and upgrade to full package*",
        'ask_extra': "Want to add anything else to your request? Type your message or press 'Skip':",
        'thanks': "Thank you! Your request was sent. We’ll contact you soon."
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
    await message.answer(texts[lang]['ask_description'], reply_markup=types.ReplyKeyboardRemove())

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
async def ask_delivery(message: types.Message, state: FSMContext):
    await state.update_data(accident=message.text)
    lang = (await state.get_data())['lang']
    await Form.delivery.set()
    await message.answer(texts[lang]['ask_delivery'])

@dp.message_handler(state=Form.delivery)
async def ask_contact(message: types.Message, state: FSMContext):
    await state.update_data(delivery=message.text)
    lang = (await state.get_data())['lang']
    await Form.contact.set()
    await message.answer(texts[lang]['ask_contact'])

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
    skip_btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустити") if lang == 'ua' else ("Пропустить" if lang == 'ru' else "Skip"))
    await Form.extra.set()
    await message.answer(texts[lang]['ask_extra'], reply_markup=skip_btn)

@dp.message_handler(state=Form.extra)
async def finish(message: types.Message, state: FSMContext):
    await state.update_data(extra=message.text)
    data = await state.get_data()
    text = f"📥 Нова заявка від {message.from_user.full_name} (@{message.from_user.username}):\n\n" \
           f"🚗 Машина: {data['description']}\n" \
           f"💰 Бюджет: {data['budget']}\n" \
           f"📄 Тайтл: {data['title_type']}\n" \
           f"💥 ДТП: {data['accident']}\n" \
           f"📦 Доставка: {data['delivery']}\n" \
           f"📞 Контакт: {data['contact']}\n" \
           f"🛠️ Пакет: {data['package']}\n" \
           f"✍️ Додатково: {data['extra']}\n"

    await bot.send_message(chat_id=ADMIN_ID, text=text)
    await message.answer(texts[data['lang']]['thanks'], reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

if __name__ == '__main__':
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)

