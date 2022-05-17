import telebot
import sqlite3
import config

bot = telebot.TeleBot(config.token)


def db_car_number(message):
    if message.content_type == 'text' and 7 < len(message.text) < 10:
        startkboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        catalog = telebot.types.KeyboardButton(text="Сделать запись")
        info = telebot.types.KeyboardButton(text="Отмена")
        startkboard.add(catalog, info)
        global car_number
        car_number = message.text.upper()
        bot.send_message(message.from_user.id, "Прикрепите фотографию автомобиля с буквой Z.", reply_markup=startkboard)
        bot.register_next_step_handler(message, db_car_photo)
    elif message.content_type == 'text' and message.text.lower() == "отмена":
        bot.send_message(message.from_user.id, "Ввод отменен")
        pass
    else:
        bot.send_message(message.from_user.id,
                         'Мне нужен номер в текстовом виде, как на примере "C065MK78" без кавычек.')
        bot.send_message(message.from_user.id,
                         'Попробуйте ещё раз.')
        bot.register_next_step_handler(message, db_car_number)


def db_car_photo(message):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with sqlite3.connect("KRSK.db") as con:
            binary = sqlite3.Binary(downloaded_file)
            cur = con.cursor()
            cur.execute("INSERT INTO cars (car_number, photo, date) VALUES (?, ?, DATE())", (car_number, binary))
        bot.send_message(message.from_user.id, "Номер и фото успешно добавлены в таблицу")
    elif message.content_type == 'text' and message.text.lower() == "отмена":
        bot.send_message(message.from_user.id, "Ввод отменен")
        pass
    else:
        bot.send_message(message.from_user.id, 'Мне нужна фотография автомобиля.')
        bot.send_message(message.from_user.id, 'Попробуйте ещё раз.')
        bot.register_next_step_handler(message, db_car_photo)


@bot.message_handler(commands=['start'])
def keyboard_start(message):
    startkboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    catalog = telebot.types.KeyboardButton(text="Сделать запись")
    info = telebot.types.KeyboardButton(text="Помощь")
    startkboard.add(catalog, info)
    bot.send_message(message.chat.id,
                     "Привет! Я предназначен для сбора данных об автовладельцах, поддерживающих войну в Украине. "
                     "Чтобы открыть справку, введите команду \n\n/help",
                     reply_markup=startkboard)


@bot.message_handler(content_types=['text'])
def messages(message):
    if message.text.lower() == "/help" or message.text.lower() == "помощь":
        bot.send_message(message.from_user.id, 'Доступные команды: \n🔸 /start'
                                               '\n🔸 /help')
    elif message.text.lower() == "сделать запись":
        bot.send_photo(message.from_user.id, photo='https://upload.wikimedia.org/wikipedia/commons/thumb/1/14'
                                                   '/License_plate_in_Russia_2.svg/1920px-License_plate_in_Russia_2'
                                                   '.svg.png', caption='Введите серию, регистрационный номер и код '
                                                                       'региона регистрации, как на картинке. Пример '
                                                                       '"C065MK78" без кавычек')
        bot.register_next_step_handler(message, db_car_number)


bot.polling(none_stop=True, interval=0)
