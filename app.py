import telebot
import sqlite3
import config

bot = telebot.TeleBot(config.token)


def db_car_number(message):
    bot.send_message(message.from_user.id, "Прикрепите фотографию автомобиля с буквой Z")
    global car_number
    car_number = message.text.upper()
    bot.register_next_step_handler(message, db_car_photo)


def db_car_photo(message):
    print(car_number)
    file_info = bot.get_file(message.photo[0].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with sqlite3.connect("KRSK.db") as con:
        binary = sqlite3.Binary(downloaded_file)
        cur = con.cursor()
        cur.execute("INSERT INTO cars (car_number, photo) VALUES (?, ?)", (car_number, binary))


@bot.message_handler(content_types=['text'])
def messages(message):
    if message.text.lower() == "/start":
        bot.send_message(message.from_user.id, "Привет! Я предназначен для сбора данных об автовладельцах, "
                                               "поддерживающих войну в Украине. Чтобы открыть FAQ, введите команду "
                                               "/help")
    elif message.text.lower() == "/help":
        bot.send_message(message.from_user.id, "FAQ пока не готов")
    elif message.text.lower() == "сделать запись":
        bot.send_photo(message.from_user.id, photo='https://upload.wikimedia.org/wikipedia/commons/thumb/1/14'
                                                   '/License_plate_in_Russia_2.svg/1920px-License_plate_in_Russia_2'
                                                   '.svg.png', caption='Введите серию, регистрационный номер и код '
                                                                       'региона регистрации, как на картинке. Пример '
                                                                       '"C065MK78"')
        bot.register_next_step_handler(message, db_car_number)


bot.polling(none_stop=True, interval=0)
