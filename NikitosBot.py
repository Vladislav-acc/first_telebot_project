import telebot
from config import LINK, TOKEN, CHAT_ID, MY_ID
from db import BotDatabase, BotDatabaseConn


TEMP_ORDER = {

}

COMMAND_DICT = {
    'name': 'Ваше имя',
    'email': 'Вашу почту',
    'address': 'Ваш адрес'
}


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['send'])
def send_message_to_group(message):
    print('Шлю!')
    bot.send_message(
        CHAT_ID, 'Здарова, это тестовое сообщение, листай дальше!')


@bot.message_handler(regexp='О нас')
@bot.message_handler(commands=['start'])
def start_command(message):
    # print(bot.get_chat('@TestBotChat').id)
    markup = telebot.types.InlineKeyboardMarkup()
    link_button = telebot.types.InlineKeyboardButton(
        'Видеообзор', callback_data='link')
    start_order_button = telebot.types.InlineKeyboardButton(
        'Оформить заказ', callback_data='order')
    markup.row(link_button, start_order_button)
    bot.send_message(
        message.chat.id,
        f'Rat - современный взгляд на классический дисторшн ProCo Rat.\n\n'
        f'Устранены все проблемы оригинала: установлено стандартное гнездо питания boss style, вход и выход перенесены наверх для удобства коммутации в педалборде, корпус - легкий и компактный.\n\n'
        f'Полностью ручная сборка, заводская плата, качественные комплектующие, оригинальная микросхема LM308.\n\n'
        f'Стоимость: 7000 рублей.\n\n'
        f'Оплатить можно переводом по номеру телефона (тинькофф/сбер):\n\n'
        f'89629080844\n\n',
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    data = call.data
    if data == 'link':
        bot.send_message(call.message.chat.id, f'{LINK}')
    elif data == 'order':
        order(call.message)
    elif data == 'edit':
        edit_menu(call.message)
    elif data == 'create':
        show_new_order(call)
    elif data == 'name':
        enter_info(call.message, edit=1, value='name')
    elif data == 'email':
        enter_info(call.message, edit=1, value='email')
    elif data == 'address':
        enter_info(call.message, edit=1, value='address')
    elif data == 'back':
        order_finish(call.message)
    bot.answer_callback_query(call.id)


def send_link(call):
    bot.send_message(call.message.chat.id, f'{LINK}')


@bot.message_handler(regexp='Оформить заказ')
def order(msg):
    id = msg.chat.id
    TEMP_ORDER[id] = {'name': '', 'email': '', 'address': ''}
    enter_info(msg, value='name')
    while not TEMP_ORDER[id]['name']:
        continue
    enter_info(msg, value='email')
    while not TEMP_ORDER[id]['email']:
        continue
    enter_info(msg, value='address')
    while not TEMP_ORDER[id]['address']:
        continue
    order_finish(msg)


def enter_info(message, edit=0, value=None):
    markup = telebot.types.ForceReply(selective=False)
    msg = bot.send_message(
        message.chat.id,
        f'Введите {COMMAND_DICT[value]}: ',
        reply_markup=markup)
    bot.register_next_step_handler(msg, recieve_info, edit=edit, value=value)


def recieve_info(message, edit, value):
    TEMP_ORDER[message.chat.id][value] = message.text
    if edit:
        edit_menu(message)


def order_finish(message):
    markup = telebot.types.InlineKeyboardMarkup()
    edit_button = telebot.types.InlineKeyboardButton(
        'Редактировать', callback_data='edit')
    create_order_button = telebot.types.InlineKeyboardButton(
        'Подтвердить заказ', callback_data='create')
    markup.row(create_order_button, edit_button)
    id = message.chat.id
    bot.send_message(
        id,
        f'Проверьте правильность заполненных полей и завершите оформление заказа:\n'
        f'Имя: {TEMP_ORDER[id]["name"]}\n'
        f'Почта: {TEMP_ORDER[id]["email"]}\n'
        f'Адрес: {TEMP_ORDER[id]["address"]}',
        reply_markup=markup)


def show_new_order(call):
    id = call.message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    about_button = telebot.types.KeyboardButton(
        'О нас')
    order_button = telebot.types.KeyboardButton(
        'Оформить заказ')
    markup.row(about_button, order_button)
    bot.send_message(
        id,
        f"Спасибо за заказ! "
        f"Мы свяжемся с Вами в ближайшее время!", reply_markup=markup)
    bot.send_message(
        MY_ID,
        f'Новый заказ подъехал!\n\n'
        f'Имя: {TEMP_ORDER[id]["name"]}\n'
        f'Почта: {TEMP_ORDER[id]["email"]}\n'
        f'Адрес: {TEMP_ORDER[id]["address"]}')
    # функция вставки в базу данных
    db = BotDatabase('database.db')
    db.insert_into_db(id,
                      TEMP_ORDER[id]["name"],
                      TEMP_ORDER[id]["email"],
                      TEMP_ORDER[id]["address"])
    db.close_db()
    del TEMP_ORDER[id]


def edit_menu(message):
    markup = telebot.types.InlineKeyboardMarkup()
    edit_name_button = telebot.types.InlineKeyboardButton(
        'Имя', callback_data='name')
    edit_email_button = telebot.types.InlineKeyboardButton(
        'Email', callback_data='email')
    edit_address_button = telebot.types.InlineKeyboardButton(
        'Адрес', callback_data='address')
    back_to_order_button = telebot.types.InlineKeyboardButton(
        'Назад к подтверждению заказа', callback_data='back')
    markup.row(edit_name_button, edit_email_button, edit_address_button)
    markup.row(back_to_order_button)
    bot.send_message(
        message.chat.id,
        f'Выберите информацию для редактирования: ',
        reply_markup=markup)


if __name__ == '__main__':
    db = BotDatabase('database.db')
    db.create_database()
    db.close_db()
    bot.polling(none_stop=True)
