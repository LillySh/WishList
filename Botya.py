import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3

# bot на telebot
bot = telebot.TeleBot('2145817311:AAH3vgsN8YA9FQGa3AK1bBObLgpiqXFdTO4')


# команда start
@bot.message_handler(commands=['start'])
def start(message):
    # создаем клавиатуру внизу
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Завершить')
    bot.send_message(message.chat.id,
                     'Привет, это виртуальный вишлист, куда ты можешь добавлять свои хотелки, а также узнавать чего '
                     'хотят твои друзья', reply_markup=markup)

    # создаем кнопки
    markup = InlineKeyboardMarkup()  # создаем клавиатуру
    but_1 = InlineKeyboardButton("Хочу дарить подарки",
                                 callback_data="data_1")  # создаем кнопки, callback_data это что-то вроде id для кнопки
    but_2 = InlineKeyboardButton("Хочу подарки",
                                 callback_data="data_2")
    markup.add(but_1, but_2)
    bot.send_message(message.chat.id, "Для начала выбери кто ты?", reply_markup=markup)


@bot.callback_query_handler(lambda c: c.data == "data_2")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
    # bot.send_message(call.message.chat.id, "Напиши список своих подарков через Enter")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Удалить', 'Завершить', 'Добавить')
    bot.send_message(call.message.chat.id, "Выбери, что ты хочешь сделать со своими подарками", reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def text(message):
        # создаем базу данных
        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS  wish_list(id INTEGER, present TEXT )")

        connect.commit()

        if message.text == 'Завершить':
            bot.send_message(message.chat.id, 'До новых встреч')
            bot.polling()
        elif message.text == 'Удалить':
            connect = sqlite3.connect(r'C:/Users/Adelina/PycharmProjects/WishList/wishlist.db',
                                      check_same_thread=False)
            cursor = connect.cursor()

            cursor.execute(f"SELECT present FROM wish_list where id = {message.chat.id}")
            all_res = cursor.fetchall()
            connect.commit()
            # добавляем подарки в список, чтобы было корректно для кнопок
            list_of_present = []
            for i in range(len(all_res)):
                list_of_present.append(str(all_res[i][0]))

            # чтобы подарки кнопками выходили
            # def present_on_but():
            button_list = []
            for each in list_of_present:
                button_list.append(InlineKeyboardButton(each, callback_data=each))
            reply_markup = InlineKeyboardMarkup(
                build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
            bot.send_message(call.message.chat.id, text='Какой подарок ты хочешь удалить?',
                             reply_markup=reply_markup)

            @bot.callback_query_handler(func=lambda c: True)
            def reaction(c):
                cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
                keyboard = types.InlineKeyboardMarkup()
                # cid = c.message.chat.id
                bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}", reply_markup=keyboard)

                # удаляем из базы данных
                req = "Delete from wish_list where present = ?"
                cursor.execute(req, (cid_call,))
                connect.commit()
                bot.send_message(message.chat.id, "Этого подарка больше нет в базе")
        elif message.text == 'Добавить':
            bot.send_message(message.chat.id, 'Напиши, что ты хочешь, каждый раз с новой строки')

            @bot.message_handler(content_types=['text2'])
            def text2(message2):
                connect = sqlite3.connect('wishlist.db', check_same_thread=False)
                cursor = connect.cursor()

                cursor.execute("CREATE TABLE IF NOT EXISTS  wish_list(id INTEGER, present TEXT )")

                connect.commit()

                id_wish = [message2.chat.id, message2.text.lower()]
                cursor.execute("INSERT INTO wish_list VALUES(?,?);", id_wish)
                bot.send_message(message2.chat.id, 'Твой подарок добавлен в вишлист')
                connect.commit()


@bot.callback_query_handler(lambda c: c.data == "data_1")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на какую кнопку бот должен отвечать, без этого работать не будет
    bot.send_message(call.message.chat.id, "Скинь ссылку на пользователя в тг, которому ты хочешь сделать подарок")

    @bot.message_handler(content_types=['text'])
    def text(message):
        if message.text == 'Завершить':
            bot.send_message(message.chat.id, 'До новых встреч')
            bot.stop_polling()
        else:
            # вытаскиваем id на пользователя
            get_chat = message.text
            number = int(get_chat[
                         28:37])  # выделили id, пробелма в том, что id можно получить только если скопировать ссылку из
            # компьютерной версии
            connect = sqlite3.connect(r'C:/Users/Adelina/PycharmProjects/WishList/wishlist.db', check_same_thread=False)
            cursor = connect.cursor()

            def present_on_but():
                connect = sqlite3.connect(r'C:/Users/Adelina/PycharmProjects/WishList/wishlist.db',
                                          check_same_thread=False)
                cursor = connect.cursor()

                cursor.execute(f"SELECT present FROM wish_list where id = {number}")
                all_res = cursor.fetchall()
                connect.commit()
                # добавляем подарки в список, чтобы было корректно для кнопок
                list_of_present = []
                for i in range(len(all_res)):
                    list_of_present.append(str(all_res[i][0]))

                # чтобы подарки кнопками выходили
                # def present_on_but():
                button_list = []
                for each in list_of_present:
                    button_list.append(InlineKeyboardButton(each, callback_data=each))
                reply_markup = InlineKeyboardMarkup(
                    build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
                bot.send_message(call.message.chat.id, text='Какой подарок из предложенных ты хочешь подарить?',
                                 reply_markup=reply_markup)

            present_on_but()

            # чтобы подарки были кнопками другой способ: этот полегче
            # keyboard = InlineKeyboardMarkup()
            # keyboard.row_width = 2
            #
            # for i in range(0, len(list_of_present)):
            #     keyboard.add(InlineKeyboardButton(list_of_present[i], callback_data=str(i)))
            #
            # bot.send_message(call.message.chat.id, 'Какой подарок из предложенных ты хочешь подарить?',
            #                  reply_markup=keyboard)

            # нашли какое-то id у кнопок
            @bot.callback_query_handler(func=lambda c: True)
            def reaction(c):
                cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
                if cid_call != "yes" and cid_call != "no":
                    keyboard = types.InlineKeyboardMarkup()
                    # cid = c.message.chat.id
                    bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}", reply_markup=keyboard)

                    # удаляем из базы данных
                    req = "Delete from wish_list where present = ?"
                    cursor.execute(req, (cid_call,))
                    connect.commit()
                    bot.send_message(message.chat.id, "Этого подарка больше нет в базе")

                    # спрашиваем хочет ли он еще что-то выбрать
                    markup = InlineKeyboardMarkup()
                    but_3 = InlineKeyboardButton("Да",
                                                 callback_data="yes")  # создаем кнопки, callback_data это что-то вроде id для кнопки
                    but_4 = InlineKeyboardButton("Нет",
                                                 callback_data="no")
                    markup.add(but_3, but_4)
                    bot.send_message(message.chat.id, "Хочешь еще что-то выбрать?", reply_markup=markup)
                elif cid_call == "yes":
                    present_on_but()
                elif cid_call == "no":
                    bot.send_message(c.message.chat.id, "Хорошего дарения "
                                                        "Если захочешь вернуться просто нажми на /start")
                    bot.stop_polling()


# строим меню из множества кнопочек для первого способа
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# функция по кликабельности каждой кнопки как с build_menu

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
# @dp.message_handler(commands = ['start']) #aiogram асинхронная библиотека и это обозначается с помощью async async
# def  begin(message: types.Message): markup = InlineKeyboardMarkup() #создаем клавиатуру but_1 =
# InlineKeyboardButton("Как дела?", callback_data="data_1") #создаем кнопки, callback_data это что-то вроде id для
# кнопки markup.add(but_1)  #добавляем кнопку на клавиатуру
#
# await  bot.send_message(message.chat.id, "И снова привет", reply_markup=markup) #то есть после привет появится эта
# кнопка
#
# @dp.callback_query_handler(lambda c: c.data == "but_1") #с помощью функции lambda указываем на какую кнопку у нас
# будет реакция async def button_reaction(call: types.callback_query): await bot.answer_callback_query(call.id)  #мы
# указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет await bot.send_message(
# call.message.chat.id, "Всё хорошо, как сам?")
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
