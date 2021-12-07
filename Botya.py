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
                     'Привет! \nЭто виртуальный вишлист, куда ты можешь добавлять свои хотелки, а также узнавать чего '
                     'хотят твои друзья', reply_markup=markup)

    # создаем кнопки
    markup = InlineKeyboardMarkup()  # создаем клавиатуру
    but_1 = InlineKeyboardButton("Дарить подарки",
                                 callback_data="data_1")  # создаем кнопки, callback_data это что-то вроде id для кнопки
    but_2 = InlineKeyboardButton("Подарки",
                                 callback_data="data_2")
    markup.add(but_1)
    markup.add(but_2)
    bot.send_message(message.chat.id, "Ты здесь для того, чтобы", reply_markup=markup)




# именниник
@bot.callback_query_handler(lambda c: c.data == "data_2")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(
        call.id)  # мы указываем на какую кнопку бот должен отвечать, без этого работать не будет
    # bot.send_message(call.message.chat.id, "Напиши список своих подарков через Enter")
    whattodo = InlineKeyboardMarkup()  # создаем клавиатуру
    but_new = InlineKeyboardButton("Создать новый список",
                                   callback_data="new_wishlist")
    but_old = InlineKeyboardButton("Изменить готовый список",
                                   callback_data="old_wishlist")
    whattodo.add(but_new, but_old)
    bot.send_message(call.message.chat.id, "А теперь выбери, что нужно сделать", reply_markup=whattodo)

    # если создаем новый вишлист
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
            bot.send_message(call.message.chat.id, "Представься: напиши своё имя и фамилию"
                                                   "\nИменно по имени и фамилии твои друзья смогут найти твой вишлист")
            bot.register_next_step_handler(call.message, get_username)  # get_username берем имя фамилию в 78 строке
        else:
            goto_edit = InlineKeyboardMarkup()  # создаем клавиатуру
            but_go = InlineKeyboardButton("Перейти к редактированию",
                                          callback_data="old_wishlist")
            goto_edit.add(but_go)
            bot.send_message(call.message.chat.id, "У тебя уже есть действующий вишлист", reply_markup=goto_edit)

    @bot.message_handler(content_types=['text'])
    def get_username(message):  # получаем имя пользователя
        global username
        username = message.text.title()
        try:
            first_name = username.split(" ", 1)[0]  # чисто для обращения
            last_name = username.split(" ", 1)[1]  # имя уже выделили, поэтому лениво проверим на наличие второго

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
        if message.text == "Завершить":
            bot.send_message(call.from_user.id,
                             "Вишлист готов! Все, кто знает как тебя зовут, смогут найти его и выбрать подарок. "
                             "Если что, ты всегда можешь вернуться и изменить свой список, просто нажми на /start")
            # start(message)
        else:
            connect = sqlite3.connect('wishlist.db', check_same_thread=False)
            cursor = connect.cursor()

            id_wish = [message.chat.id, username, message.text]
            cursor.execute("INSERT INTO wish_list VALUES(?,?,?);", id_wish)
            connect.commit()
            bot.send_message(message.chat.id, 'Подарок добавлен в вишлист')

            # connect.commit()
            bot.register_next_step_handler(message, create_db)

    # если редачим старый вишлист
    @bot.callback_query_handler(lambda c: c.data == "old_wishlist")
    def oldbutton_reaction(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)

        connect = sqlite3.connect('wishlist.db', check_same_thread=False)
        cursor = connect.cursor()

        remember_check = cursor.execute('SELECT id FROM wish_list WHERE id=?', (call.message.chat.id,))
        connect.commit()
        if remember_check.fetchall() is None:  # если во второй раз заходить, не узнаёт. ,
            bot.send_message(call.message.chat.id,
                             "Кажется, для тебя список ещё не создавлся. Срочно исправляем!"
                             "\nПредставься: напиши своё имя и фамилию"
                             "\n Именно по имени и фамилии твои друзья смогут найти твой вишлист")
            bot.register_next_step_handler(call.message, get_username)

        else:
            markup = InlineKeyboardMarkup()  # создаем клавиатуру
            but_ch = InlineKeyboardButton("Изменить",
                                          callback_data="change")  # создаем кнопки, callback_data это что-то вроде id для кнопки
            but_add = InlineKeyboardButton("Добавить",
                                           callback_data="add")
            but_del = InlineKeyboardButton("Удалить", callback_data="delete")
            markup.add(but_ch, but_add, but_del)

            bot.send_message(call.message.chat.id, "Что ты хочешь сделать?", reply_markup=markup)

            connect = sqlite3.connect('wishlist.db', check_same_thread=False)
            cursor = connect.cursor()

            cursor.execute(f"SELECT present FROM wish_list where id = {call.message.chat.id}")
            all_res = cursor.fetchall()
            connect.commit()

            list_of_present = []
            for i in range(len(all_res)):
                list_of_present.append(str(all_res[i][0]))

        @bot.callback_query_handler(lambda c: c.data == "change")  # изменяем какой-то подарок на другой
        def button_reaction(call: types.CallbackQuery):
            if list_of_present is None:
                bot.send_message(call.message.chat.id,
                                 "Твоих подарков еще нет в списке\nНажми добавить, чтобы создать свой список желаний")
            else:
                # чтобы подарки кнопками выходили
                # def present_on_but():
                button_list = []
                for each in list_of_present:
                    button_list.append(InlineKeyboardButton(each, callback_data=each))
                reply_markup = InlineKeyboardMarkup(
                    build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
                bot.send_message(call.message.chat.id, text='Какой подарок ты хочешь изменить?',
                                 reply_markup=reply_markup)

            @bot.callback_query_handler(func=lambda c: True)
            @bot.message_handler(content_types=['text'])
            def reaction(c):
                global cid_call
                cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
                keyboard = types.InlineKeyboardMarkup()
                # cid = c.message.chat.id
                bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}", reply_markup=keyboard)

                # заменяем на новое значение
                msg = bot.send_message(c.message.chat.id, "На что ты хочешь его заменить?")
                bot.register_next_step_handler(msg, change_present)

                # @bot.message_handler(content_types=['text'])

            def change_present(message):

                cursor.execute("UPDATE wish_list SET present = ? where present = ?", (message.text, cid_call,))
                connect.commit()
                bot.send_message(message.chat.id, "Твой подарок изменен")


        @bot.callback_query_handler(lambda c: c.data == "add")
        def add_reaction(call: types.CallbackQuery):
            msg = bot.send_message(call.message.chat.id, "Напиши список своих подарков через Enter\nКак закончишь нажми на клаву внизу")
            bot.register_next_step_handler(msg, add_value_in_sql)

        def add_value_in_sql(message):

            cursor.execute(f"SELECT username FROM wish_list where id = {message.chat.id}")
            username = cursor.fetchone()[0]

            id_wish = [message.chat.id, username, message.text]

            cursor.execute("INSERT INTO wish_list VALUES(?,?,?);", id_wish)
            connect.commit()
            mes = bot.send_message(message.chat.id, "Твой подарок добавлен")

            bot.register_next_step_handler(mes, add_value_in_sql)


        @bot.callback_query_handler(lambda c: c.data == "delete")  # удаляем подарки
        def button_reaction(call: types.CallbackQuery):
            if list_of_present is None:
                bot.send_message(call.message.chat.id,
                                 "Твоих подарков еще нет в списке\nНажми добавить, чтобы создать свой список желаний")
            else:
                # чтобы подарки кнопками выходили
                # def present_on_but():
                button_list = []
                for each in list_of_present:
                    button_list.append(InlineKeyboardButton(each, callback_data=each))
                reply_markup = InlineKeyboardMarkup(
                    build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
                bot.send_message(call.message.chat.id, text='Какой подарок ты хочешь удалить?',
                                 reply_markup=reply_markup) \

                @bot.callback_query_handler(func=lambda c: True)
                def reaction(c):
                    cid_call = c.data  # получаем callback_data у кнопки, которая была нажата
                    keyboard = types.InlineKeyboardMarkup()
                    # cid = c.message.chat.id
                    bot.send_message(c.message.chat.id, f"Был выбран подарок: {cid_call}", reply_markup=keyboard)

                    req = "Delete from wish_list where present = ?"
                    cursor.execute(req, (cid_call,))
                    connect.commit()
                    bot.send_message(c.message.chat.id, "Этого подарка больше нет в базе")


@bot.callback_query_handler(lambda c: c.data == "data_1")
def button_reaction(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)  # мы указываем на какую кнопку бот должен отвечать, без этого работать не будет
    bot.send_message(call.message.chat.id, "Кому выбираем подарок? \nНапиши имя и фамилию счастливчика")
    bot.register_next_step_handler(call.message, checkname)

    # здесь будет исключение типо нет такого пользователя если скинули не корректную ссылку или фамилию и имя

@bot.message_handler(content_types=['text'])
def checkname(message):
        # global person
    person = message.text.title()
    try:
        first_name = person.split(" ", 1)[0]  # ограничители
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
            global receiver_id
            receiver_id = check_name.fetchone()[0]  # получили id


            def present_on_but(receiver_id):
                connect = sqlite3.connect(r'C:/Users/Adelina/PycharmProjects/WishList/wishlist.db',
                                      check_same_thread=False)
                cursor = connect.cursor()

                cursor.execute(f"SELECT present FROM wish_list where id = {receiver_id}")
                all_res = cursor.fetchall()
                connect.commit()
                # добавляем подарки в список, чтобы было корректно для кнопок
                list_of_present = []
                for i in range(len(all_res)):
                    list_of_present.append(str(all_res[i][0]))
                if list_of_present == []:
                    bot.send_message(message.chat.id, 'Уппс, похоже ты выбрал все подарки')
                # чтобы подарки кнопками выходили
                # def present_on_but():
                else:
                    button_list = []
                    for each in list_of_present:
                        button_list.append(InlineKeyboardButton(each, callback_data=each))
                    reply_markup = InlineKeyboardMarkup(
                        build_menu(button_list, n_cols=1))  # n_cols = 1 для одного столбца и нескольких строк
                    bot.send_message(message.chat.id, text='Какой подарок из предложенных ты хочешь подарить?', reply_markup=reply_markup)

            present_on_but(receiver_id)


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
                present_on_but(receiver_id)
            elif cid_call == "no":
                bot.send_message(c.message.chat.id, "Хорошего дарения\nЕсли захочешь вернуться просто нажми на /start")
                bot.stop_polling()

    except IndexError:
        bot.send_message(message.chat.id,
                             "Будь внимательнее: чтобы найти вишлист, нам нужны имя и фамилия. Попробуй ещё раз либо твоего другана нет в базе")
        bot.register_next_step_handler(message, checkname)


# строим меню из множества кнопочек для первого способа
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu



bot.polling()
