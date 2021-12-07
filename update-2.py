import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
from functions import build_menu

# bot на telebot
bot = telebot.TeleBot('5094415944:AAERFjqMlsWWWtFKw4pwHsXMPMl8jUOsAdk')


# команда start
@bot.message_handler(commands=['start'])
def start(message):
    global your_id
    your_id = message.from_user.id

    # создаем клавиатуру внизу
    down = types.ReplyKeyboardMarkup(resize_keyboard=True)
    down.row('Завершить')

    #bot.send_message(message.chat.id,
                     # 'Привет, это виртуальный вишлист, куда ты можешь добавлять свои хотелки, а также узнавать чего '
                     # 'хотят твои друзья')
    # создаем кнопки
    markup = InlineKeyboardMarkup()  # создаем клавиатуру
    but_1 = InlineKeyboardButton("Cделать подарок",
                                 callback_data="data_1")  # создаем кнопки, callback_data это что-то вроде id для кнопки
    but_2 = InlineKeyboardButton("Получить подарок",
                                 callback_data="data_2")
    markup.add(but_1)
    markup.add(but_2)
    bot.send_message(message.chat.id, "Привет, это виртуальный вишлист, куда ты можешь добавлять свои хотелки, а также узнавать чего "
                                     "хотят твои друзья. \nТы здесь для того, чтобы ", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def ending(message):
    if message.text == 'Завершить':
        bot.send_message(message.chat.id, 'До новых встреч')

# именинник
@bot.callback_query_handler(lambda c: c.data == "data_2")
def receive_reaction(call: types.CallbackQuery):
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
    def checkid_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS  wish_list(id INTEGER, username TEXT, present TEXT )")
        connect.commit()

        check_id = cursor.execute("SELECT id FROM wish_list where id=?", (your_id,))
        connect.commit()
        if check_id.fetchall() is None:
            bot.send_message(call.message.chat.id, "Представься: напиши своё имя и фамилию"
                                                   "\n Именно по имени и фамилии твои друзья смогут найти твой вишлист")
            bot.register_next_step_handler(call.message, get_username)
        else:
            goto_edit = InlineKeyboardMarkup()  # создаем клавиатуру
            but_go = InlineKeyboardButton("Перейти к редактированию",
                                         callback_data="old_wishlist")
            goto_edit.add(but_go)
            bot.send_message(call.message.chat.id, "У тебя уже есть действующий вишлист.", reply_markup=goto_edit)
            #bot.register_next_step_handler(call.message, get_username)


    @bot.message_handler(content_types=['text'])
    def get_username(message):  # получаем имя пользователя
        global username
        username = message.text.title()
        try:
            first_name = username.split(" ", 1)[0] # чисто для обращения
            last_name = username.split(" ", 1)[1] # имя уже выделили, поэтому лениво проверим на наличие второго

            connect = sqlite3.connect('wishlist.db', check_same_thread=False)
            cursor = connect.cursor()

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
        except IndexError:
            bot.send_message(message.chat.id,
                             "Будь внимательнее: чтобы создать вишлист, нам нужны имя и фамилия. Попробуй ещё раз")
            bot.register_next_step_handler(message, get_username)


    @bot.message_handler(content_types=['text'])
    def create_db(message):
        # если пользователь закончил список
        if message.text.lower() == "готово":
            bot.send_message(call.from_user.id,
                             "Вишлист готов! Все, кто знает как тебя зовут, смогут найти его и выбрать подарок. "
                             "Если что, ты всегда можешь вернуться и изменить свой список, просто нажми на /start")
            #start(message)
        else:
            connect = sqlite3.connect('wishlist.db', check_same_thread=False)
            cursor = connect.cursor()

            id_wish = [your_id, username, message.text]
            cursor.execute("INSERT INTO wish_list VALUES(?,?,?);", id_wish)
            connect.commit()
            bot.send_message(message.chat.id, 'Подарок добавлен в вишлист. '
                                              'Можешь придумать что-то ещё, а как закончишь, напиши "готово"')

            #connect.commit()
            bot.register_next_step_handler(message, create_db)

    # если редачим старый вишлист
    @bot.callback_query_handler(lambda c: c.data == "old_wishlist")
    def oldbutton_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        remember_check = cursor.execute('SELECT id FROM wish_list WHERE id=?', (your_id,))
        connect.commit()
        if remember_check.fetchone() is None: #если во второй раз заходить, не узнаёт. ,
            bot.send_message(call.message.chat.id,
                             "Кажется, для тебя список ещё не создавлся. Срочно исправляем!"
                             "\nПредставься: напиши своё имя и фамилию"
                             "\n Именно по имени и фамилии твои друзья смогут найти твой вишлист")
            bot.register_next_step_handler(call.message, get_username)
        else:
            # cursor.execute("SELECT present FROM wish_list where id=?", (your_id,))
            # all_res = cursor.fetchall()
            # connect.commit()
            # # добавляем подарки в список, чтобы было корректно для кнопок
            # list_of_present = []
            # for i in range(len(all_res)):
            #     list_of_present.append(str(all_res[i][0]))

            whattodo = InlineKeyboardMarkup()
            but_add = InlineKeyboardButton("Добавить подарок",
                                           callback_data="author_add")
            but_del = InlineKeyboardButton("Удалить подарок",
                                           callback_data="author_del")
            but_ch = InlineKeyboardButton("Изменить подарок",
                                          callback_data="author_ch")
            whattodo.add(but_add, but_del, but_ch)
            bot.send_message(call.message.chat.id, "А теперь выбери, что нужно сделать", reply_markup=whattodo)

        #добавить
        @bot.callback_query_handler(lambda c: c.data == "author_add")
        def add_reaction(call: types.CallbackQuery):
            bot.answer_callback_query(
                call.id)
            editmode_username = cursor.execute("SELECT username FROM wish_list where id=?", (your_id,))
            editmode_username = editmode_username.fetchone()[0]
            connect.commit()
            global username
            username = editmode_username
            bot.send_message(call.message.chat.id, "Напиши список своих подарков через Enter")
            bot.register_next_step_handler(call.message, create_db)

        # удалить
        @bot.callback_query_handler(lambda c: c.data == "author_del")
        def del_reaction(call: types.CallbackQuery):
            bot.answer_callback_query(call.id)

            list_of_present = list_of_presents("SELECT present FROM wish_list where id=?", your_id)
            button_list = []
            for each in list_of_present:
                button_list.append(InlineKeyboardButton(each, callback_data=each))
            reply_markup = InlineKeyboardMarkup(
                build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
            bot.send_message(call.message.chat.id, text='Какой подарок ты хочешь удалить?',
                             reply_markup=reply_markup)

            @bot.callback_query_handler(func=lambda c: True)
            def del_reaction2(c: types.CallbackQuery):
                bot.answer_callback_query(c.id)
                #global cid_call
                cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
                if cid_call != "no":
                    #keyboard = InlineKeyboardMarkup()
                    bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}") #,reply_markup=keyboard)
                    # удаляем из базы данных
                    req = "Delete from wish_list where present = ?"
                    cursor.execute(req, (cid_call,))
                    connect.commit()
                    bot.send_message(c.message.chat.id, "Такого подарка больше нет в твоём вишлисте")
                    # спрашиваем хочет ли он еще что-то выбрать
                    markup = InlineKeyboardMarkup()
                    but_yes = InlineKeyboardButton("Да",
                                                    callback_data="author_del")
                    but_no = InlineKeyboardButton("Нет",
                                                    callback_data="no")
                    markup.add(but_yes, but_no)
                    bot.send_message(c.message.chat.id, "Хочешь еще что-то выбрать?", reply_markup=markup)

                elif cid_call == "no":
                    bot.send_message(c.message.chat.id, "Готово! "
                                                        "Если захочешь вернуться, просто нажми на /start")


        # изменить
        # @bot.callback_query_handler(lambda c: c.data == "author_ch")  # изменяем какой-то подарок на другой
        # def button_reaction(call: types.CallbackQuery):
        #     list_of_present = list_of_presents("SELECT present FROM wish_list where id=?", your_id)
        #     button_list = []
        #     for each in list_of_present:
        #         button_list.append(InlineKeyboardButton(each, callback_data=each))
        #     reply_markup = InlineKeyboardMarkup(
        #         build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
        #     bot.send_message(call.message.chat.id, text='Какой подарок ты хочешь изменить?', reply_markup=reply_markup)
        #
        # @bot.callback_query_handler(func=lambda c: True)
        # def reaction(c: types.CallbackQuery):
        #     bot.answer_callback_query(c.id)
        #     global change_giveup
        #     change_giveup = c.data  # получаем callback_data у кнопки, которая была нажата
        #     keyboard = types.InlineKeyboardMarkup()
        #     # cid = c.message.chat.id
        #     bot.send_message(c.message.chat.id, f"Был выбран подарок: {change_giveup}", reply_markup=keyboard)
        #
        #     # заменяем на новое значение
        #     bot.send_message(c.message.chat.id, "На что ты хочешь его заменить?")
        #     bot.register_next_step_handler(call.message, changing)
        #     # changing(send, cid_call)
        #
        # @bot.message_handler(content_types=['text'])
        # def changing(message):
        #     change = message.text
        #     #val = (message, cid_call)
        #     req = "UPDATE wish_list SET present = ? where present = ?"
        #     cursor.execute(req, (change, change_giveup))
        #     connect.commit()
        #
        #     bot.send_message(message.chat.id, "Твой подарок изменен")
        @bot.callback_query_handler(lambda c: c.data == "author_ch")
        def ch_reaction(call: types.CallbackQuery):
            bot.answer_callback_query(call.id)
            list_of_present = list_of_presents("SELECT present FROM wish_list where id=?", your_id)
            button_list = []
            for each in list_of_present:
                button_list.append(InlineKeyboardButton(each, callback_data=each))
            reply_markup = InlineKeyboardMarkup(
                build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
            bot.send_message(call.message.chat.id, text='Какой подарок ты хочешь изменить?',
                             reply_markup=reply_markup)

            @bot.callback_query_handler(func=lambda c: True)
            def ch_reaction2(c: types.CallbackQuery):
                bot.answer_callback_query(c.id)
                global change_cbdata
                change_cbdata = c.data  # получаем callback_data у кнопки, которая была нажата
                if change_cbdata != "no":
                    #keyboard = types.InlineKeyboardMarkup()
                    bot.send_message(c.message.chat.id, f"Был выбран подарок: {change_cbdata}")
                    # заменяем на новое значение
                    bot.send_message(call.message.chat.id, "На что ты хочешь его заменить?")
                    bot.register_next_step_handler(call.message, changing)
                else:
                    change_cbdata = ""
                    bot.send_message(c.message.chat.id, "Готово! "
                                                        "Если захочешь вернуться, просто нажми на /start")

            @bot.message_handler(content_types=['text'])
            def changing(message):
                change = message.text
                req = "UPDATE wish_list SET present = ? where present = ?"
                cursor.execute(req, (change, change_cbdata,))
                connect.commit()

                bot.send_message(message.chat.id, "Твой подарок изменен")

                # спрашиваем хочет ли он еще что-то выбрать
                markup = InlineKeyboardMarkup()
                but_yes = InlineKeyboardButton("Да",
                                                callback_data="author_ch")
                but_no = InlineKeyboardButton("Нет",
                                                callback_data="no")
                markup.add(but_yes, but_no)
                bot.send_message(message.chat.id, "Хочешь еще что-то выбрать?", reply_markup=markup)

#гость
@bot.callback_query_handler(lambda c: c.data == "data_1")
def give_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
    bot.send_message(call.message.chat.id, "Кому выбираем подарок? Напиши имя и фамилию счастливчика.")
    bot.register_next_step_handler(call.message, checkname)

@bot.message_handler(content_types=['text'])
def checkname(message):
    #global person
    person = message.text.title()
    try:
        first_name = person.split(" ", 1)[0]   #ограничители
        last_name = person.split(" ", 1)[1]
        alter_person = last_name + " " + first_name
        confusion_check = (person, alter_person)

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS  wish_list(id INTEGER, username TEXT, present TEXT )")
        connect.commit()

        check_name = cursor.execute("SELECT id FROM wish_list where username in (?, ?)", (confusion_check))
        connect.commit()

        if check_name.fetchone() is None:
            bot.send_message(message.chat.id, f" {person} не создавал(а) у нас свой вишлист."
                                                   "\nПроверь, нет ли ошибок в имени или фамилии, и попробуй снова")
            bot.register_next_step_handler(message, checkname)
        else:
            receiver_id = check_name.fetchone()[0] #получили id
            present_on_but(receiver_id)
    except IndexError:
        bot.send_message(message.chat.id, "Будь внимательнее: чтобы найти вишлист, нам нужны имя и фамилия. Попробуй ещё раз")
        bot.register_next_step_handler(message, checkname)


@bot.message_handler(content_types=['text'])
def present_on_but(receiver_id):
    id_arg = receiver_id #взяли айдишкин

    connect = sqlite3.connect('wishlist.db', check_same_thread=False)
    cursor = connect.cursor()

    req = "SELECT present FROM wish_list WHERE id = ?"
    cursor.execute(req, (id_arg,))

    #cursor.execute("SELECT present FROM wish_list WHERE id = ?", (id_arg),)
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
    bot.send_message(your_id, text='Какой подарок из предложенных ты хочешь подарить?',
                        reply_markup=reply_markup)

    @bot.callback_query_handler(func=lambda c: True)
    def choice_reaction(c: types.CallbackQuery):
        bot.answer_callback_query (c.id)
        cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
        if cid_call not in ["yes", "no"]:
            keyboard = InlineKeyboardMarkup()
            bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}", reply_markup=keyboard)

            # удаляем из базы данных
            req = "Delete from wish_list where present = ?"
            cursor.execute(req, (cid_call,))
            connect.commit()
            #bot.send_message(c.message.chat.id, "Этого подарка больше нет в базе")

            # спрашиваем хочет ли он еще что-то выбрать
            markup = InlineKeyboardMarkup()
            but_yes = InlineKeyboardButton("Да",
                                         callback_data="yes")
            but_no = InlineKeyboardButton("Нет",
                                         callback_data="no")
            markup.add(but_yes, but_no)
            bot.send_message(c.message.chat.id, "Хочешь еще что-то выбрать?", reply_markup=markup)
        elif cid_call == "yes":
            bot.register_next_step_handler(c.message, present_on_but(receiver_id))
        elif cid_call == "no":
            bot.send_message(c.message.chat.id, "Готово! "
                                                "Если захочешь вернуться, просто нажми на /start")



#строим меню из множества кнопочек
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

# чтобы получать список подарков
def list_of_presents(req, id):
    connect = sqlite3.connect('wishlist.db', check_same_thread=False)
    cursor = connect.cursor()

    cursor.execute(req, (id,))

    all_res = cursor.fetchall()
    connect.commit()

    # добавляем подарки в список, чтобы было корректно для кнопок
    list_of_present = []
    for i in range(len(all_res)):
        list_of_present.append(str(all_res[i][0]))

    return list_of_present


bot.polling()
#bot.infinity_polling()
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