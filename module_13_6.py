from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен вашего бота
api = "Согласно задания: не забудьте убрать ключ для подключения к вашему боту!"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Определяем состояния
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Обычное меню
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Рассчитать", "Информация"]
    keyboard.add(*buttons)
    return keyboard

# Inline-меню
def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    button_calories = InlineKeyboardButton(
        text="Рассчитать норму калорий", callback_data="calories"
    )
    button_formulas = InlineKeyboardButton(
        text="Формулы расчёта", callback_data="formulas"
    )
    keyboard.add(button_calories, button_formulas)
    return keyboard

# Хэндлер команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот, помогающий твоему здоровью.\n"
        "Выберите одну из опций ниже:",
        reply_markup=get_main_keyboard()
    )

# Хэндлер для кнопки "Рассчитать"
@dp.message_handler(text="Рассчитать")
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=get_inline_keyboard())

# Хэндлер для информации
@dp.message_handler(text="Информация")
async def info(message: types.Message):
    await message.answer(
        "Этот бот помогает рассчитать вашу норму калорий. "
        "Используйте кнопку 'Рассчитать', чтобы начать расчет."
    )

# Хэндлер для формул расчета
@dp.callback_query_handler(text="formulas")
async def get_formulas(call: types.CallbackQuery):
    formula_text = (
        "Формула Миффлина-Сан Жеора для женщин:\n"
        "10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )
    await call.message.answer(formula_text)
    await call.answer()

# Хэндлер для начала расчета калорий
@dp.callback_query_handler(text="calories")
async def set_age(call: types.CallbackQuery):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()
    await call.answer()

# Хэндлер для ввода возраста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом. Попробуйте еще раз:")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Введите свой рост в сантиметрах:")
    await UserState.growth.set()

# Хэндлер для ввода роста
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Рост должен быть числом. Попробуйте еще раз:")
        return
    await state.update_data(growth=int(message.text))
    await message.answer("Введите свой вес в килограммах:")
    await UserState.weight.set()

# Хэндлер для ввода веса и расчета калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Вес должен быть числом. Попробуйте еще раз:")
        return
    await state.update_data(weight=int(message.text))
    data = await state.get_data()

    # Формула Миффлина - Сан Жеора для женщин:
    bmr = 10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] - 161
    await message.answer(f"Ваша норма калорий: {bmr:.2f}")

    # Завершаем состояние
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

###     Вывод в телеграмм:
"""

Alex, [18.11.2024 15:03]
/start

Alex, [18.11.2024 15:03]
Информация

Vika, [18.11.2024 15:03]
Этот бот помогает рассчитать вашу норму калорий. Используйте кнопку 'Рассчитать', чтобы начать расчет.

Vika, [18.11.2024 15:04]
Выберите опцию:

Alex, [18.11.2024 15:04]
Рассчитать

Vika, [18.11.2024 15:04]
Формула Миффлина-Сан Жеора для женщин:
10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161

Alex, [18.11.2024 15:04]
Рассчитать

Vika, [18.11.2024 15:04]
Выберите опцию:

Vika, [18.11.2024 15:04]
Введите свой возраст:

Alex, [18.11.2024 15:04]
66

Vika, [18.11.2024 15:04]
Введите свой рост в сантиметрах:

Vika, [18.11.2024 15:04]
Введите свой вес в килограммах:

Alex, [18.11.2024 15:04]
182

Alex, [18.11.2024 15:04]
87

Vika, [18.11.2024 15:04]
Ваша норма калорий: 1516.50
"""