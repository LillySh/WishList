import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3


# bot на telebot
bot = telebot.TeleBot('5094415944:AAERFjqMlsWWWtFKw4pwHsXMPMl8jUOsAdk')


# команда start
@bot.message_handler(commands=['start'])
def start(message):
    # global your_id
    # your_id = message.from_user.id

    # создаем клавиатуру внизу
    down = types.ReplyKeyboardMarkup(resize_keyboard=True)
    down.row('Завершить')

    # создаем кнопки
    markup = InlineKeyboardMarkup()  # создаем клавиатуру
    but_1 = InlineKeyboardButton("\U0001F381 Cделать подарок \U0001F381",
                                 callback_data="data_1")  # создаем кнопки, callback_data это что-то вроде id для кнопки
    but_2 = InlineKeyboardButton("\U0001F973 Получить подарок \U0001F973",
                                 callback_data="data_2")
    markup.add(but_1)
    markup.add(but_2)
    bot.send_message(message.chat.id, "Привет!\U0001F44B \nДобро пожаловать в виртуальный вишлист, "
                                      "где ты можешь создать список своих желаний, а также узнать, чего "
                                     "хотят твои друзья. \n\nТы здесь для того, чтобы ", reply_markup=markup)
# где-то здесь видимо будет кнопка завершить
@bot.message_handler(content_types=['text'])
def ending(message):
    #if message.text == 'Завершить':
    bot.send_message(message.chat.id, '\U0001F31F До новых встреч! \U0001F31F'
                                      '\nТы всегда можешь вернуться, нажав /start')

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

        cursor.execute("SELECT id FROM wish_list where id=?", (call.message.chat.id,))
        check_id = cursor.fetchall()
        connect.commit()
        if check_id == []:
            bot.send_message(call.message.chat.id, "\U0000270D Представься: напиши своё имя и фамилию."
                                                   "\n Именно по этим данным твои друзья смогут найти этот вишлист")
            bot.register_next_step_handler(call.message, get_username)
        else:
            goto_edit = InlineKeyboardMarkup()  # создаем клавиатуру
            but_go = InlineKeyboardButton("Перейти к редактированию",
                                         callback_data="old_wishlist")
            goto_edit.add(but_go)
            bot.send_message(call.message.chat.id, "У тебя уже есть действующий вишлист \U0001F609",
                             reply_markup=goto_edit)

    @bot.message_handler(content_types=['text'])
    def get_username(message):  # получаем имя пользователя
        if message.text == 'Завершить':  # почва для кнопки
            ending(message)
        else:
            global username
            username = message.text.title()
            if len(username.split(' ')) == 2: #новая проверка на введение ИФ именинником, у гостя старая останется
                first_name = username.split(" ", 1)[0] # чисто для обращения

                connect = sqlite3.connect('wishlist.db', check_same_thread=False)
                cursor = connect.cursor()

                check = cursor.execute('SELECT username FROM wish_list WHERE username=?', (username,))
                if check.fetchone() is None:
                    bot.send_message(message.chat.id,
                                     f'Приятно познакомиться, {first_name} \U0001F60A '
                                     'Напиши список своих подарков через Enter')
                    bot.register_next_step_handler(message, create_db)
                else:
                    bot.send_message(message.chat.id, 'Невероятно, но твой полный тёзка составил свой список раньше! \U0001F92F'
                                                      '\nМы не хотим, чтобы ваши списки перепутались. Может используем другую форму имени?'
                                                      '\nP.S. Не забудь напомнить друзьям, под каким именем в итоге создался список \U0001F609')
                    bot.register_next_step_handler(message, get_username)
            else:
                bot.send_message(message.chat.id,
                                 "Будь внимательнее: чтобы создать вишлист, нам нужны имя и фамилия. Попробуй ещё раз \U0001F917")
                bot.register_next_step_handler(message, get_username)


    @bot.message_handler(content_types=['text'])
    def create_db(message):
        # если пользователь закончил список
        if message.text.lower() == "готово": #предлагаю на кнопку не менять
            bot.send_message(call.from_user.id,
                             "\U00002728 Вишлист готов! \U00002728"
                             "\nВсе, кто знает как тебя зовут, смогут найти его и выбрать подарок. "
                             "\nЕсли что, ты всегда можешь вернуться и изменить свой список, просто нажми на /start")

        elif message.text == 'Завершить': # но я её всё равно вставила, потому что меня будет раздражать, что она есть и не работает
                ending(message)

        else:
            connect = sqlite3.connect('wishlist.db', check_same_thread=False)
            cursor = connect.cursor()

            id_wish = [message.chat.id, username, message.text]
            cursor.execute("INSERT INTO wish_list VALUES(?,?,?);", id_wish)
            connect.commit()
            bot.send_message(message.chat.id, 'Подарок добавлен в вишлист. '
                                              'Можешь придумать что-то ещё, а как закончишь, напиши "готово"')
            bot.register_next_step_handler(message, create_db)

    # если редачим старый вишлист
    @bot.callback_query_handler(lambda c: c.data == "old_wishlist")
    def oldbutton_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        remember_check = cursor.execute('SELECT COUNT(id) FROM wish_list WHERE id=?', (call.message.chat.id,))
        connect.commit()
        if remember_check.fetchone()[0] == 0:
            bot.send_message(call.message.chat.id,
                             "\U0001F914 Кажется, для тебя список ещё не создавлся. Срочно исправляем!"
                             "\nПредставься: напиши своё имя и фамилию"
                             "\n Именно по имени и фамилии твои друзья смогут найти этот вишлист")
            bot.register_next_step_handler(call.message, get_username)
        else:
            whattodo = InlineKeyboardMarkup()
            but_add = InlineKeyboardButton("Добавить",
                                           callback_data="author_add")
            but_del = InlineKeyboardButton("Удалить",
                                           callback_data="author_del")
            but_ch = InlineKeyboardButton("Изменить",
                                          callback_data="author_ch")
            whattodo.add(but_add, but_del, but_ch)
            bot.send_message(call.message.chat.id, "А теперь выбери, что нужно сделать с твоимии подарками", reply_markup=whattodo)

            cursor.execute("SELECT present FROM wish_list where id=?", (call.message.chat.id,))
            all_res = cursor.fetchall()
            connect.commit()
            # добавляем подарки в список, чтобы было корректно для кнопок
            list_of_present = []
            for i in range(len(all_res)):
                list_of_present.append(str(all_res[i][0]))

        #добавить
        @bot.callback_query_handler(lambda c: c.data == "author_add")
        def add_reaction(call: types.CallbackQuery):
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, 'Напиши список своих подарков через Enter.'
                                                   '\nКак закончишь, нажми на кнопку "Завершить" внизу экрана \U0001F609')
            bot.register_next_step_handler(call.message, add_value_to_sql)

        def add_value_to_sql(message):
            if message.text == 'Завершить': # почва для кнопки
                ending(message)

            else:
                cursor.execute("SELECT username FROM wish_list where id=?", (call.message.chat.id,))
                username = cursor.fetchone()[0]

                id_wish = [message.chat.id, username, message.text]

                cursor.execute("INSERT INTO wish_list VALUES(?,?,?);", id_wish)
                connect.commit()
                mes = bot.send_message(message.chat.id, "Подарок добавлен в вишлист."
                                                        "\nЧто-то ещё?")

                bot.register_next_step_handler(mes, add_value_to_sql)

        # удалить
        @bot.callback_query_handler(lambda c: c.data == "author_del")
        def del_reaction(call: types.CallbackQuery):
            bot.answer_callback_query(call.id)

            cursor.execute("SELECT present FROM wish_list where id=?", (call.message.chat.id,))
            all_res = cursor.fetchall()
            connect.commit()

            # добавляем подарки в список, чтобы было корректно для кнопок
            list_of_present = []
            for i in range(len(all_res)):
                list_of_present.append(str(all_res[i][0]))

            if list_of_present == []:
                bot.send_message(call.message.chat.id, 'Ууупс, похоже, подарков больше не осталось! \U0001F648'
                                                       '\nТеперь ты можешь создать новый вишлист!\U0001F917 '
                                                       '\nПросто нажми /start')
            else:
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
                    cid_call = c.data  # получаем callback_data у кнопки, которая была нажата

                    if cid_call != "no":
                        #keyboard = InlineKeyboardMarkup()
                        bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}") #,reply_markup=keyboard)
                        # удаляем из базы данных
                        req = "Delete from wish_list where present = ?"
                        cursor.execute(req, (cid_call,))
                        connect.commit()
                        bot.send_message(c.message.chat.id, "Такого подарка больше нет в твоём вишлисте \U0001F44C")
                        # спрашиваем хочет ли он еще что-то выбрать
                        markup = InlineKeyboardMarkup()
                        but_yes = InlineKeyboardButton("\U00002705",
                                                         callback_data="author_del")
                        but_no = InlineKeyboardButton("\U0000274C",
                                                        callback_data="no")
                        markup.add(but_yes, but_no)
                        bot.send_message(c.message.chat.id, "Хочешь выбрать что-то ещё?", reply_markup=markup)

                    elif cid_call == "no":
                        bot.send_message(c.message.chat.id, "Готово! "
                                                            "Если захочешь вернуться, просто нажми на /start")

        @bot.callback_query_handler(lambda c: c.data == "author_ch")
        def ch_reaction(call: types.CallbackQuery):
            bot.answer_callback_query(call.id)
            #list_of_present = list_of_presents("SELECT present FROM wish_list where id=?", call.message.chat.id)
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
                #if change_cbdata != "no":
                bot.send_message(c.message.chat.id, f"Был выбран подарок: {change_cbdata}")
                # заменяем на новое значение
                bot.send_message(call.message.chat.id, "На что ты хочешь его заменить?")
                bot.register_next_step_handler(call.message, changing)

            @bot.message_handler(content_types=['text'])
            def changing(message):
                if message.text == 'Завершить':
                    ending(message)
                else:
                    req = "UPDATE wish_list SET present = ? where present = ?"
                    cursor.execute(req, (message.text, change_cbdata,))
                    connect.commit()
                    bot.send_message(message.chat.id, "Твой подарок изменен")

                    ending(message)

#гость
@bot.callback_query_handler(lambda c: c.data == "data_1")
def give_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на что, на какую кнопку бот должен отвечать, без этого работать не будет
    bot.send_message(call.message.chat.id, "Кому выбираем подарок?\U0001F929 \nНапиши имя и фамилию счастливчика.")
    bot.register_next_step_handler(call.message, checkname)

@bot.message_handler(content_types=['text'])
def checkname(message):
    if message.text == 'Завершить':
        ending(message)
    else:
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
                bot.send_message(message.chat.id, f"{person} не создавал(а) у нас свой вишлист. \U0001F914 "
                                                       "\nПроверь, нет ли ошибок в имени или фамилии, и попробуй снова")
                bot.register_next_step_handler(message, checkname)
            else:
                global receiver_id
                receiver_id = check_name.fetchone()[0] #получили id

                def present_on_but(receiver_id):
                    connect = sqlite3.connect('wishlist.db', check_same_thread=False)
                    cursor = connect.cursor()

                    cursor.execute("SELECT present FROM wish_list WHERE id = ?",(receiver_id,))
                    all_res = cursor.fetchall()
                    connect.commit()

                    list_of_present = []
                    for i in range(len(all_res)):
                        list_of_present.append(str(all_res[i][0]))
                    button_list = []
                    for each in list_of_present:
                        button_list.append(InlineKeyboardButton(each, callback_data=each))
                    reply_markup = InlineKeyboardMarkup(
                        build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
                    bot.send_message(message.chat.id, text='Какой подарок из предложенных ты хочешь подарить?',
                                        reply_markup=reply_markup)

                present_on_but(receiver_id)

            @bot.callback_query_handler(func=lambda c: True)
            def choice_reaction(c: types.CallbackQuery):
                bot.answer_callback_query(c.id)
                cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
                if cid_call not in ["yes", "no"]:
                    keyboard = InlineKeyboardMarkup()
                    bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}",
                                     reply_markup=keyboard)
                    # удаляем из базы данных
                    req = "Delete from wish_list where present = ?"
                    cursor.execute(req, (cid_call,))
                    connect.commit()
                    # спрашиваем хочет ли он еще что-то выбрать
                    markup = InlineKeyboardMarkup()
                    but_yes = InlineKeyboardButton("\U00002705",
                                                   callback_data="yes")
                    but_no = InlineKeyboardButton("\U0000274C",
                                                  callback_data="no")
                    markup.add(but_yes, but_no)

                    bot.send_message(c.message.chat.id, "Хочешь еще что-то выбрать?", reply_markup=markup)

                elif cid_call == "yes":
                    present_on_but(receiver_id)

                elif cid_call == "no":
                    bot.send_message(c.message.chat.id, "\U0001F389 Готово! \U0001F389"
                                                        "\nЕсли захочешь вернуться, просто нажми на /start")

         except IndexError:
            bot.send_message(message.chat.id, "Будь внимательнее: чтобы найти вишлист, нам нужны имя и фамилия. Попробуй ещё раз \U0001F917")
            bot.register_next_step_handler(message, checkname)

#строим меню из множества кнопочек
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

# # чтобы получать список подарков
# def list_of_presents(req, id):
#     connect = sqlite3.connect('wishlist.db', check_same_thread=False)
#     cursor = connect.cursor()
#
#     cursor.execute(req, (id,))
#
#     all_res = cursor.fetchall()
#     connect.commit()
#
#     # добавляем подарки в список, чтобы было корректно для кнопок
#     list_of_present = []
#     for i in range(len(all_res)):
#         list_of_present.append(str(all_res[i][0]))
#
#     return list_of_present


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
