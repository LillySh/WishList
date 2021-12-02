import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3

# bot на telebot
bot = telebot.TeleBot('2145817311:AAH3vgsN8YA9FQGa3AK1bBObLgpiqXFdTO4')


# команда start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет, это виртуальный вишлист, куда ты можешь добавлять свои хотелки, а также узнавать чего '
                     'хотят твои друзья')
    # создаем кнопки
    markup = InlineKeyboardMarkup()  # создаем клавиатуру
    but_1 = InlineKeyboardButton("Гость",
                                 callback_data="data_1")  # создаем кнопки, callback_data это что-то вроде id для кнопки
    but_2 = InlineKeyboardButton("Именниник",
                                 callback_data="data_2")
    markup.add(but_1, but_2)
    bot.send_message(message.chat.id, "Для начала выбери кто ты?", reply_markup=markup)


@bot.callback_query_handler(lambda c: c.data == "data_2")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
    bot.send_message(call.message.chat.id, "Напиши список своих подарков через Enter")

    @bot.message_handler(content_types=['text'])
    def text(message):
        # создаем базу данных
        connect = sqlite3.connect('wishlist.db')
        cursor = connect.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS  wish_list(id INTEGER, present TEXT )")

        connect.commit()

        id_wish = [message.chat.id, message.text]
        cursor.execute("INSERT INTO wish_list VALUES(?,?);", id_wish)
        bot.send_message(message.chat.id, 'Твой подарок добавлен в вишлист')
        connect.commit()


@bot.callback_query_handler(lambda c: c.data == "data_1")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
    bot.send_message(call.message.chat.id, "Скинь ссылку на пользователя в тг, которому ты хочешь сделать подарок")

    @bot.message_handler(content_types=['text'])
    def text(message):
        # вытаскиваем id на пользователя
        get_chat = message.text
        number = int(get_chat[
                     28:37])  # выделили id, пробелма в том, что id можно получить только если скопировать ссылку из компьютерной версии

        connect = sqlite3.connect(r'C:/Users/Adelina/PycharmProjects/telegram_bot/wishlist.db')
        cursor = connect.cursor()

        cursor.execute(f"SELECT present FROM wish_list where id = {number}")
        all_res = cursor.fetchall()
        connect.commit()
        #добавляем подарки в список, чтобы было корректно для кнопок
        list_of_present = []
        for i in range(len(all_res)):
            list_of_present.append(str(all_res[i][0]))


        # чтобы подарки кнопками выходили
        button_list = []
        for each in list_of_present:
            button_list.append(InlineKeyboardButton(each, callback_data=each))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
        bot.send_message(call.message.chat.id, text='Какой подарок из предложенных ты хочешь подарить?',
                         reply_markup=reply_markup)

#строим меню из множества кнопочек
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

#функция по кликабельности каждой кнопки как с build_menu

    #     #создаем базу данных
    # connect = sqlite3.connect('users.db')
    # cursor = connect.cursor()
    #
    # cursor.execute("CREATE TABLE IF NOT EXISTS id (number INTEGER )")
    #
    # connect.commit()
    #
    # #проверка на существование этого id
    # people_id = message.chat.id
    # cursor.execute(f"SELECT number FROM id where number = {people_id}")
    # data = cursor.fetchone()
    # if data is None: #если такого id нет, то добавь
    #     list_users = [message.chat.id]
    #     cursor.execute("INSERT INTO id VALUES(?);", list_users)
    #     connect.commit()
    # else:
    #     bot.send_message(message.chat.id, "Ты уже был добавлен в список(")


# удаление человека из базы данных
# @bot.message_handler(commands = ['delete'])
# def delete(message):
#     connect = sqlite3.connect('users.db')
#     cursor = connect.cursor()
#
#     #удаляем id из таблицы
#     people_id = message.chat.id
#     cursor.execute(f"DELETE from id where number = {people_id}")
#     connect.commit()
#     bot.send_message(message.chat.id, "Теперь тебя снова нет в базе")


# #текст
# @bot.message_handler(content_types = ['text'])
# def text(message):
#     if message.text.lover() == "hi":  #lower приходящее сообщение преобразует в маленькие буквы и потом сравнивает
#         bot.send_message(message.chat.id, 'Hi, my friend')


bot.polling()

# бот с библиотекой aiogram
# from aiogram import types, executor, Dispatcher, Bot
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup #чтобы сделать кнопки на которые можно нажимать
#
# TOKEN = "2145817311:AAH3vgsN8YA9FQGa3AK1bBObLgpiqXFdTO4"
# bot = Bot(token=TOKEN)
# dp = Dispatcher(bot)  #диспатчер это диспетчер или обработчик, который будет обрабатывать события
#
# @dp.message_handler(commands = ['start'])
# #aiogram асинхронная библиотека и это обозначается с помощью async
# async def  begin(message: types.Message):
#     markup = InlineKeyboardMarkup() #создаем клавиатуру
#     but_1 = InlineKeyboardButton("Как дела?", callback_data="data_1") #создаем кнопки, callback_data это что-то вроде id для кнопки
#     markup.add(but_1)  #добавляем кнопку на клавиатуру
#
#     await  bot.send_message(message.chat.id, "И снова привет", reply_markup=markup) #то есть после привет появится эта кнопка
#
# @dp.callback_query_handler(lambda c: c.data == "but_1") #с помощью функции lambda указываем на какую кнопку у нас будет реакция
# async def button_reaction(call: types.callback_query):
#     await bot.answer_callback_query(call.id)  #мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
#     await bot.send_message(call.message.chat.id, "Всё хорошо, как сам?")
#
#
#
# @dp.message_handler(content_types = ['text'])
# async def text(message: types.Message):
#     if message.text.lower() == "пока":
#         await bot.send_message(message.chat.id, "Жаль, что уже прощаемся")
#
#
#
# # чтобы бот работал
# executor.start_polling(dp)
