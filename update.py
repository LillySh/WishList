import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
#from functions import build_menu

# bot на telebot
bot = telebot.TeleBot('токен')



# команда start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет, это виртуальный вишлист, куда ты можешь добавлять свои хотелки, а также узнавать чего '
                     'хотят твои друзья')
    # создаем кнопки
    markup = InlineKeyboardMarkup()  # создаем клавиатуру
    but_1 = InlineKeyboardButton("Cделать подарок",
                                 callback_data="data_1")  # создаем кнопки, callback_data это что-то вроде id для кнопки
    but_2 = InlineKeyboardButton("Получить подарок",
                                 callback_data="data_2")
    markup.add(but_1, but_2)
    bot.send_message(message.chat.id, "Ты хочешь ", reply_markup=markup)


# именинник
@bot.callback_query_handler(lambda c: c.data == "data_2")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет

    whattodo = InlineKeyboardMarkup()  # создаем клавиатуру
    but_new = InlineKeyboardButton("Создать новый список",
                                   callback_data="new_wishlist")
    but_old = InlineKeyboardButton("Изменить готовый список",
                                   callback_data="old_wishlist")
    whattodo.add(but_new, but_old)
    bot.send_message(call.message.chat.id, "А теперь выбери, что нужно сделать", reply_markup=whattodo)

    # если создаём новый вишлист
    @bot.callback_query_handler(lambda c: c.data == "new_wishlist")
    def button_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(
            call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
        bot.send_message(call.message.chat.id, "Представься: напиши своё имя и фамилию")

    @bot.message_handler(content_types=['text'])
    def get_username(message):  # получаем имя пользователя
        global username
        username = message.text.title()
        first_name = username.split(" ", 1)[0]

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS  wish_list(username TEXT, present TEXT )")
        connect.commit()

        check = cursor.execute('SELECT username FROM wish_list WHERE username=?', (username,))
        if check.fetchone() is None:
            bot.send_message(message.chat.id,
                             f'Приятно познакомиться, {first_name}! Напиши список своих подарков через Enter')
            bot.register_next_step_handler(message, create_db)
        else:
            bot.send_message(message.chat.id, 'Невероятно, но твой полный тёзка составил свой список раньше!'
                                              '\nМы не хотим, чтобы ваши списки перепутались. Может используем другую форму имени?'
                                              '\nP.S. Не забудь напомнить друзьям, под каким именем в итоге создался список;)')
        connect.commit()

    def create_db(message):
        # если пользователь закончил список
        if message.text.lower() == "готово":
            bot.send_message(call.from_user.id,
                             "Вишлист готов! Все, кто знает как тебя зовут, смогут найти его и выбрать подарок. "
                             "Если что, ты всегда можешь вернуться и изменить свой список.")
            start(message)
        else:
            connect = sqlite3.connect('wishlist.db', check_same_thread=False)
            cursor = connect.cursor()

            cursor.execute("CREATE TABLE IF NOT EXISTS  wish_list(username TEXT, present TEXT )")
            connect.commit()

            id_wish = [username, message.text]
            cursor.execute("INSERT INTO wish_list VALUES(?,?);", id_wish)
            bot.send_message(message.chat.id, 'Подарок добавлен в вишлист. '
                                              'Можешь придумать что-то ещё, а как закончишь, напиши "готово"')

            connect.commit()
            bot.register_next_step_handler(message, create_db)

    # если редачим старый вишлист
    @bot.callback_query_handler(lambda c: c.data == "old_wishlist")
    def oldbutton_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(
            call.id)
        bot.send_message(call.message.chat.id, "Напомни, как тебя зовут?")
        bot.register_next_step_handler(call.message, remember_username)

    @bot.message_handler(content_types=['text'])
    def remember_username(message):
        global username
        username = message.text.title()
        first_name = username.split(" ", 1)[0]

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        remember_check = cursor.execute('SELECT username FROM wish_list WHERE username=?', (username,))
        if remember_check.fetchone() is None:
            bot.send_message(message.chat.id,
                             f'Не можем тебя найти, {first_name}. Проверь, всё ли написано верно? Нам нужны имя и фамилия.')
            bot.register_next_step_handler(message, remember_username)
        else:
            whattodo = InlineKeyboardMarkup()
            but_add = InlineKeyboardButton("Добавить подарок",
                                           callback_data="author_add")
            but_del = InlineKeyboardButton("Удалить подарок",
                                           callback_data="author_del")
            whattodo.add(but_add, but_del)
            bot.send_message(call.message.chat.id, "А теперь выбери, что нужно сделать", reply_markup=whattodo)

    @bot.callback_query_handler(lambda c: c.data == "author_add")
    def add_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(
            call.id)
        bot.send_message(call.message.chat.id, "Напиши список своих подарков через Enter")
        bot.register_next_step_handler(call.message, create_db)


    @bot.callback_query_handler(lambda c: c.data == "author_del")
    def del_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(
            call.id)

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        cursor.execute("SELECT present FROM wish_list where username=?", (username,))
        all_res = cursor.fetchall()
        connect.commit()
        # добавляем подарки в список, чтобы было корректно для кнопок
        list_of_present = []
        for i in range(len(all_res)):
            list_of_present.append(str(all_res[i][0]))

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
            bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}", reply_markup=keyboard)
            # удаляем из базы данных
            req = "Delete from wish_list where present = ?"
            cursor.execute(req, (cid_call,))
            connect.commit()
            bot.send_message(c.message.chat.id, "Такого подарка больше нет в твоём вишлисте")
            start(c.message)


@bot.callback_query_handler(lambda c: c.data == "data_1")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
    bot.send_message(call.message.chat.id, "Кому выбираем подарок? Напиши имя и фамилию счастливчика.")
    bot.register_next_step_handler(call.message, present_on_but)


@bot.message_handler(content_types=['text'])
def present_on_but(message):
    # вытаскиваем  пользователя
    person = message.text.title()

    connect = sqlite3.connect('wishlist.db', check_same_thread=False)
    cursor = connect.cursor()

    cursor.execute("SELECT present FROM wish_list WHERE username = ?", (person,))
    all_res = cursor.fetchall()
    connect.commit()
    # добавляем подарки в список, чтобы было корректно для кнопок
    list_of_present = []
    for i in range(len(all_res)):
        list_of_present.append(str(all_res[i][0]))
    # чтобы подарки кнопками выходили
    button_list = []
    for each in list_of_present:
        button_list.append(InlineKeyboardButton(each, callback_data=each))
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
    bot.send_message(message.chat.id, text='Какой подарок из предложенных ты хочешь подарить?',
                     reply_markup=reply_markup)

    @bot.callback_query_handler(func=lambda c: True)
    def reaction(c):
        cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
        if cid_call != "yes" and cid_call != "no":
            keyboard = InlineKeyboardMarkup()
            bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}", reply_markup=keyboard)
            # удаляем из базы данных

            req = "Delete from wish_list where present = ?"
            cursor.execute(req, (cid_call,))
            connect.commit()
            bot.send_message(c.message.chat.id, "Этого подарка больше нет в базе")

            # спрашиваем хочет ли он еще что-то выбрать
            markup = InlineKeyboardMarkup()
            but_3 = InlineKeyboardButton("Да",
                                         callback_data="yes")  # создаем кнопки, callback_data это что-то вроде id для кнопки
            but_4 = InlineKeyboardButton("Нет",
                                         callback_data="no")
            markup.add(but_3, but_4)
            bot.send_message(message.chat.id, "Хочешь еще что-то выбрать?", reply_markup=markup)
        elif cid_call == "yes":
            bot.register_next_step_handler(message, present_on_but)
        elif cid_call == "no":
            bot.send_message(c.message.chat.id, "Пусть этот подарок принесёт огромную радость! "
                                                "Если захочешь вернуться просто нажми на /start")
            bot.stop_polling()



#строим меню из множества кнопочек
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

bot.polling()

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