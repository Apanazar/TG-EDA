from aiogram import Bot, Dispatcher, executor, types    
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot = Bot(token='')
dp = Dispatcher(bot, storage=storage)

companies = {
    "MD Food": {
        "🍕 Пицца Маргарита": 100, 
        "Лазанья с мясом": 200, 
        "Ризотто с грибами": 250, 
        "Спагетти Болоньезе": 300, 
        "Картофельный пюре": 400,
        "🥩 Карбонад из телятины": 450, 
        "Фоа гра с тостами": 550,
        "🥗 Рататуй": 600, 
        "🐔 Курица Кордон Блю": 750,
    },
    "Рандеву": {
        "🍣 Роллы с лососем": 100, 
        "🫕 Гриль с угрем": 200, 
        "🍤 Цезарь ролл с креветкой": 250, 
        "🥩 Томагавк": 300,
        "🍣 Ойси ролл": 350, 
        "🍣 Фильдельфия ролл": 400,
        "🍜 Рамен с морепродуктами": 450, 
        "🐠 Сашими из тунца": 550,
        "🍚 Рис с овощами": 600, 
        "🐔 Тонкое филе курицы": 750,
    },
    "Азбука Вкуса": {
        "Жареные пельмени с свининой": 100, 
        "Лапша в остром соусе": 200, 
        "🍔 Гамбургер с говядиной": 250, 
        "🍗 Куриные крылья": 300,
        "🥩 Стейк рибай": 350, 
        "Жареные картофельные дольки": 400,
        "Классический чизкейк": 450, 
        "🫔 Рулет из курицы": 550,
        "🍕 Пицца 4 сыра": 600, 
        "🍕 Пицца ассорти": 750,
    }
}


class Order(StatesGroup):
    firm = State()
    food = State()
    phone = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Список фирм", callback_data="flist")
    markup.add(button)
    await message.reply("Привет! Я бот для заказа еды. Нажми кнопку, чтобы начать.", reply_markup=markup)


@dp.message_handler(commands=['help'])
async def start_command(message: types.Message):
    text = "Помогаю..."
    await message.reply(text)


@dp.callback_query_handler(text="flist")
async def firms_list(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for firm_name in companies.keys():
        button = InlineKeyboardButton(text=firm_name, callback_data=f"firm_{firm_name}")
        markup.add(button)

    await callback_query.message.answer("Выберите фирму", reply_markup=markup)    


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('firm_'))
async def process_firm(callback_query: types.CallbackQuery, state: FSMContext):
    firm_name = callback_query.data.split('_')[1]
    user_data = await state.get_data()
    confirm_button = InlineKeyboardButton(text="Завершить", callback_data="finish_order")
    back_button = InlineKeyboardButton(text="К списку фирм", callback_data="back_to_firms_list")
    await state.update_data(firm=firm_name)
    
    last_food_index = user_data.get('last_food_index', 4)
    if callback_query.data == 'prev_food_list':
        last_food_index = max(last_food_index - 5, 4)
    else:
        last_food_index = min(last_food_index + 5, len(companies[firm_name]) - 1)

    await state.update_data(last_food_index=last_food_index)

    markup = InlineKeyboardMarkup()
    for food_name, price in list(companies[firm_name].items())[last_food_index - 4:last_food_index + 1]:
        button_text = f"{food_name} ({price} руб.)"
        button = InlineKeyboardButton(text=button_text, callback_data=f"food_{food_name}")
        markup.add(button)

    if last_food_index > 4:
        prev_button = InlineKeyboardButton(text="Далее", callback_data="prev_food_list")
        markup.add(prev_button)
        markup.add(back_button)
        markup.add(confirm_button)
    if last_food_index < len(companies[firm_name]) - 1:
        next_button = InlineKeyboardButton(text="Назад", callback_data="next_food_list")
        markup.add(next_button)
        markup.add(back_button)
        markup.add(confirm_button)
    
    await callback_query.answer()
    await callback_query.message.answer("Выберите еду", reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['prev_food_list', 'next_food_list'])
async def process_food_list_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    firm_name = user_data['firm']
    confirm_button = InlineKeyboardButton(text="Завершить", callback_data="finish_order")
    back_button = InlineKeyboardButton(text="К списку фирм", callback_data="back_to_firms_list")

    last_food_index = user_data.get('last_food_index', 4)
    if callback_query.data == 'prev_food_list':
        last_food_index = max(last_food_index - 5, 4)
    else:
        last_food_index = min(last_food_index + 5, len(companies[firm_name]) - 1)

    await state.update_data(last_food_index=last_food_index)

    markup = InlineKeyboardMarkup()
    for food_name, price in list(companies[firm_name].items())[last_food_index - 4:last_food_index + 1]:
        button_text = f"{food_name} ({price} руб.)"
        button = InlineKeyboardButton(text=button_text, callback_data=f"food_{food_name}")
        markup.add(button)

    if last_food_index > 4:
        prev_button = InlineKeyboardButton(text="Далее", callback_data="prev_food_list")
        markup.add(prev_button)
        markup.add(back_button)
        markup.add(confirm_button)
    if last_food_index < len(companies[firm_name]) - 1:
        next_button = InlineKeyboardButton(text="Назад", callback_data="next_food_list")
        markup.add(next_button)
        markup.add(back_button)
        markup.add(confirm_button)

    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'back_to_firms_list')
async def firms_list(callback_query: types.CallbackQuery, state: FSMContext):
    await state.reset_data()

    markup = InlineKeyboardMarkup()
    for firm_name in companies.keys():
        button = InlineKeyboardButton(text=firm_name, callback_data=f"firm_{firm_name}")
        markup.add(button)

    await callback_query.message.answer("Выберите фирму", reply_markup=markup)    


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('food_'))
async def process_food(callback_query: types.CallbackQuery, state: FSMContext):
    food_name = callback_query.data.split('_')[1]
    state_data = await state.get_data()
    firm = state_data.get('firm')
    price = companies[firm][food_name]
    
    selected_food = state_data.get('selected_food', [])
    selected_food.append({'name': food_name, 'price': price})
    await state.update_data(selected_food=selected_food)

    await callback_query.answer()
    await callback_query.message.answer(f"{food_name} ({price}руб.)")


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'finish_order')
async def process_finish_order(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    selected_food = state_data.get('selected_food')

    if not selected_food:
        await callback_query.answer("Вы не выбрали ни одного блюда")
    else:
        message = "Вы выбрали:\n"
        for food in selected_food:
            message += f"{food['name']} ({food['price']}руб.)\n"
        
        await callback_query.message.answer(message)

    await Order.phone.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Отправить номер телефона", request_contact=True))
    await callback_query.message.answer("Укажите ваш контактный номер для завершения заказа", reply_markup=markup)


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Order.phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    firm_name = data['firm']
    food_list = data['selected_food']

    food_name = ""
    for elem in food_list:
            food_name += f" {elem['name']} ({elem['price']}руб.)\n"

    order_time = message.date.strftime("%Y-%m-%d %H:%M:%S")
    user_full_name = message.from_user.full_name
    user_link = message.from_user.username

    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    msg = f"Пользователь: \n {user_full_name}\n (@{user_link})\nНомер: {phone}\nЗаказ:\n{food_name}Фирма: {firm_name}\nВремя заказа: {order_time}"

    markup = InlineKeyboardMarkup()
    delete_button = InlineKeyboardButton(text="Удалить заказ", callback_data="del_ticket")
    confirm_button = InlineKeyboardButton(text="Оформить заказ", callback_data="confirm_ticket")
    markup.add(delete_button)
    markup.add(confirm_button)

    await message.answer(msg, reply_markup=markup)
    await state.finish()


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'del_ticket')
async def delete_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Заказ удален")


async def send_for_user(id: int, text: str):
    user = await bot.get_chat(id)
    await bot.send_message(user.id, text)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'confirm_ticket')
async def confirm_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Заказ оформлен. Для оформления нового заказа подождите одну минуту введите /start")
    

@dp.message_handler()
async def unknown_command(message: types.Message):
    await message.answer("Извините, я не понимаю эту команду. Воспользуйтесь командой /help.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
