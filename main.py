# подключение библиотек
# В google colab добавить: !pip install pyTelegramBotAPI
# В google colab добавить: !pip install Faker
# для установки необходимо в файл requirements.text добавить строки
# 'PyTelegramBotApi'
# 'faker'
import json
import os
from dotenv import load_dotenv, find_dotenv
import time
from secrets import token_urlsafe

from faker import Faker
from telebot import TeleBot, types

load_dotenv(find_dotenv())

bot = TeleBot(os.getenv('TOKEN'), parse_mode='html')  # создание бота
faker = Faker()  # утилита для генерации номеров кредитных карт

# объект клавиатуры
card_type_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
card_type_kb.row(types.KeyboardButton(text='VISA'), types.KeyboardButton(text='Mastercard'))  # первый ряд кнопок
card_type_kb.row(types.KeyboardButton(text='Maestro'), types.KeyboardButton(text='JCB'))  # второй ряд кнопок
card_type_kb.add('Вернуться в начало')

# клавиатура меню
menu_kb = types.InlineKeyboardMarkup()
btn1 = types.InlineKeyboardButton('Кредитные карты', callback_data='cards')
btn2 = types.InlineKeyboardButton('Проверка JSON', callback_data='json')
menu_kb.add(btn1, btn2)
btn3 = types.InlineKeyboardButton('Тестовые данные', callback_data='data')
btn4 = types.InlineKeyboardButton('Тестовые файлы', callback_data='files')
menu_kb.add(btn3, btn4)

# клавиатура для тестовых данных
data_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
data_kb.row(types.KeyboardButton(text="1️⃣"), types.KeyboardButton(text="2️⃣"))
data_kb.row(types.KeyboardButton(text="5️⃣"), types.KeyboardButton(text="🔟"))
data_kb.add('Вернуться в начало')

# клавиатура для json
json_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
json_kb.row(types.KeyboardButton(text="Вернуться в начало"))

choose = ''
# Массив с доступными расширениями файлов. Можно изменить, и добавятся/удалятся кнопки выбора на клавиатуре.
formats = ['.jpg', '.png', '.svg', '.gif', '.ico', '.mp4', '.avi', '.webm', '.doc', '.docx', '.xls', '.xlsx', '.txt',
           '.pdf', '.css', '.html', '.js', '.json', '.zip', '.rar']


# обработчик команды '/start'
@bot.message_handler(commands=['start', 'menu'])
def start(message: types.Message):
    # отправляем ответ на команду '/start'
    bot.send_message(message.chat.id, 'Привет!', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Что будем делать? Выбирай', reply_markup=menu_kb)


def format_card_number(card_number):
    return " ".join([card_number[i:i + 4] for i in range(0, len(card_number) - 6, 4)])


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global choose
    if callback.data == 'cards':
        bot.send_message(callback.message.chat.id,
                         'Привет! Я умею генерировать номера тестовых банковских карт\nВыбери тип карты:',
                         reply_markup=card_type_kb)
        choose = 'cards'
    elif callback.data == 'json':
        bot.send_message(callback.message.chat.id,
                         'Привет! Ты выбрал <b>JSON</b>. \nЯ умею проверять JSON и форматировать его в красивый '
                         'текст\nВведи JSON в виде строки или вернись в начало:', reply_markup=json_kb)
        choose = 'json'
    elif callback.data == 'data':
        bot.send_message(callback.message.chat.id, "Привет! Ты выбрал <b>Тестовые данные</b>. \nДавай сгенерируем "
                                                   "тестовых пользователей. Выбери сколько пользователей тебе нужно 👇🏻",
                                                    reply_markup=data_kb)
        choose = 'data'
    elif callback.data == 'files':
        # Начальный шаг #1. Функция приветствия, приветствует пользователя и предлагает выбрать расширение файла.
        # С помощью хэндлера говорим, что данная функция будет запускаться при первом контакте с ботом командой /start.

        # Получаем имя пользователя Telegram, чтобы можно было обратиться к нему по имени.
        username = callback.message.from_user.first_name

        # Добавляем клавиатуру под поле ввода сообщения. Там отрисуются все кнопки из массива с расширениями.
        # Максимум будет 5 кнопок в ряд (параметр row_width=5).
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*formats, row_width=5)

        # Отправляем приветственное сообщение.
        reply = bot.send_message(callback.message.chat.id,
                                 f"Привет! Ты выбрал <b>Тестовые файлы</b>👋🏻\nЯ помогу тебе проверить граничные "
                                 f"значения при загрузке файлов разного веса в приложениях и на веб-сайтах. Я умею "
                                 f"генерировать файлы различных расширений размером от 1 байта до 45 мегабайт "
                                 f"включительно.\n\nЧтобы начать, выбери одно из доступных расширений в меню ниже ⬇️",
                                 reply_markup=markup)

        # Регистрируем переход на следующий шаг #2. Введенный пользователем ответ будет обрабатываться в функции
        # check_format().
        bot.register_next_step_handler(reply, check_format)
        choose = 'files'


# Шаг #2. Проверка выбранного расширения. Если всё хорошо, отправляется сообщение с выбором единицы измерения.
def check_format(message):
    # Проверим, если на данном шаге получаем от пользователя команду "Вернуться в начало" или "/start".
    if message.text == 'Вернуться в начало' or message.text == '/start':
        # То возвращаемся на первый начальный шаг.
        start(message)
    # Иначе, проверяем расширение из сообщения, есть ли такое в нашем массиве с расширениями.
    elif message.text in formats:
        # Добавляем клавиатуру с кнопками выбора единицы измерения.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("B (байты)", "KB (килобайты)", "MB (мегабайты)", "Вернуться в начало")

        # Отправляем сообщение с предложением выбрать единицу измерения.
        reply = bot.send_message(message.chat.id,
                                 f"🔹 Выбранное расширение — <b>{message.text}</b>\n\nТеперь выбери единицу измерения.\n<u>Небольшая памятка по размерам:</u>\n1 килобайт = 1 024 байта\n1 мегабайт = 1 024 килобайта = 1 048 576 байт",
                                 reply_markup=markup)

        # Регистрируем переход на следующий шаг #3. Введенный пользователем ответ будет обрабатываться в функции
        # check_unit(). Дополнительно передаем туда объект текущего обработанного сообщения от пользователя
        # (message). Это позволит сохранить выбранное расширение для дальнейших шагов.
        bot.register_next_step_handler(reply, check_unit, message)
    # Иначе, если такого расширения не оказалось в массиве, отправляем сообщение с ошибкой и предложением выбрать
    # корректное.
    else:
        # Добавляем клавиатуру с кнопками расширений из нашего массива, как на первом шаге.
        # Дополнительно в конце добавим кнопку "Вернуться в начало" для возврата на начальный шаг.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*formats, row_width=5)
        markup.add("Вернуться в начало")

        # Отправляем сообщение с ошибкой.
        reply = bot.send_message(message.chat.id,
                                 f"Выбрано неверное расширение файла, пожалуйста выбери одно из меню ниже 🙂⬇️",
                                 reply_markup=markup)
        # Регистрируем переход снова на шаг #2. Введенный пользователем ответ будет обрабатываться в функции
        # check_format().
        bot.register_next_step_handler(reply, check_format)


# Шаг #3. Проверка выбранной единицы измерения. Если всё хорошо, отправляется сообщение предложением ввести размер
# файла.
def check_unit(message, format):
    # Проверим, если на данном шаге получаем от пользователя команду "Назад".
    if message.text == 'Назад':
        # То возвращаемся на шаг #2 "Проверка расширения". Дополнительно передаем сообщение с выбранным расширением (
        # format), что оно сохранилось и не пришлось выбирать снова.
        check_format(format)

    # Иначе проверим, если на данном шаге получаем от пользователя команду "Вернуться в начало" или "/start".
    elif message.text == 'Вернуться в начало' or message.text == '/start':
        # То возвращаемся на первый начальный шаг.
        start(message)
    elif message.text in ['B (байты)', 'KB (килобайты)', 'MB (мегабайты)']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Назад', 'Вернуться в начало')

        # Отправляем сообщение с предложением ввести размер файла.
        reply = bot.send_message(message.chat.id,
                                 f"🔹 Выбранное расширение — <b>{format.text}</b>\n🔹 Единица измерения — <b>{message.text}</b>\n\nОстался последний шаг, напиши размер файла. Я принимаю только целые числа, без пробелов и прочих символов.\n⛔️ <u>Ограничения по размеру:</u>\n<b>Минимум</b> — 1 байт\n<b>Максимум</b> — 45 MB (это 46 080 KB или 47 185 920 байт)",
                                 reply_markup=markup)

        # Регистрируем переход на следующий шаг #4. Введенный пользователем ответ будет обрабатываться в функции
        # check_size(). Дополнительно передаем туда сообщение с выбранным расширением (format), чтобы сохранить его.
        # И также передаем туда сообщение с выбранной единицей измерения (message), чтобы сохранить её.
        bot.register_next_step_handler(reply, check_size, format, message)

    # Иначе, если единица измерения неверная, отправляем сообщение с ошибкой и предложением выбрать корректную.
    else:
        # Добавляем клавиатуру с кнопками выбора единицы измерения: байты, килобайты или мегабайты.
        # Также внизу добавляем кнопку "Вернуться в начало", она вернет на первый начальный шаг.
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('B (байты)', 'KB (килобайты)', 'MB (мегабайты)', 'Вернуться в начало')

        # Отправляем сообщение с ошибкой.
        reply = bot.send_message(message.chat.id, f"Неверная единица измерения. Пожалуйста, выбери одну из меню ниже 🙂",
                                 reply_markup=markup)

        # Регистрируем переход снова на шаг #3. Введенный пользователем ответ будет обрабатываться в функции
        # check_unit(). Дополнительно передаем туда сообщение с выбранным расширением (format), чтобы сохранить его.
        bot.register_next_step_handler(reply, check_unit, format)


# Шаг #4, последний шаг. Проверка введенного размера. Если всё хорошо, то генерируется и отправляется файл.
def check_size(message, format, unit):
    # Проверим, если на данном шаге получаем от пользователя команду "Назад".
    if message.text == 'Назад':
        # То возвращаемся на шаг #2 "Проверка расширения". Дополнительно передаем сообщение с выбранным расширением
        # (format), что оно сохранилось и не пришлось выбирать снова.
        check_format(format)

    # Иначе проверим, если на данном шаге получаем от пользователя команду "Вернуться в начало" или "/start".
    elif message.text == 'Вернуться в начало' or message.text == '/start':
        # То возвращаемся на первый начальный шаг.
        start(message)

    # Иначе проверим полученное сообщение на некорректность. Если оно некорректное, то выведем ошибку и попросим
    # ввести снова. Проходим 2 проверки. Первая isinstance() проверит, что текст сообщения None (по-простому,
    # что его нет). Это позволит отсеять все сообщения, которые не содержат текст (например, когда отправляешь стикер
    # или гифку). Вторая проверка проверяет что сообщение НЕ является числом (not isdigit()). Она отсеивает числа с
    # точками, знаками, буквами и прочими символами. Между двумя проверками используем оператор ИЛИ (or). Получается,
    # если наше сообщение не содержит текст ИЛИ наше сообщение не является числом, то выводим ошибку.
    elif isinstance(message.text, type(None)) or not message.text.isdigit():
        # Добавляем клавиатуру с кнопками "Назад" и "Вернуться в начало".
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Назад', 'Вернуться в начало')

        # Отправляем сообщение с ошибкой.
        reply = bot.send_message(message.chat.id,
                                 f"Неверный размер файла. Пожалуйста введи правильный, я принимаю только целые "
                                 f"положительные числа, без пробелов и прочих символов 🙂",
                                 reply_markup=markup)

        # Регистрируем переход снова на шаг #4. Введенный пользователем ответ будет обрабатываться в функции
        # check_size(). Дополнительно передаем туда сообщение с выбранным расширением (format) и единицей измерения
        # (unit), чтобы сохранить их.
        bot.register_next_step_handler(reply, check_size, format, unit)

    # Иначе, если всё ОК и было введено корректное число, то переходим к проверке размера и генерации файла.
    else:
        # Переводим текст сообщения с размером файла в число для удобства дальнейших манипуляций.
        size = int(message.text)

        # Посчитаем и сохраним размер в байтах, а также сохраним единицу измерения в более кратком виде для
        # финального сообщения.
        if unit.text == 'MB (мегабайты)':
            size_bytes = size * 1024 * 1024
            unit_result_text = 'MB'
        elif unit.text == 'KB (килобайты)':
            size_bytes = size * 1024
            unit_result_text = 'KB'
        else:
            size_bytes = size
            unit_result_text = 'B'

        # Добавим проверку на размер файла.
        # Если он меньше 1 байта или больше 45 мегабайт (47185920 байт), то выводим сообщение об ошибке.
        # Иначе переходим к генерации файла.
        if size_bytes < 1 or size_bytes > 47185920:
            reply = bot.send_message(message.chat.id,
                                     f"Размер файла выходит за границы моих возможностей.\n<u>Мои ограничения:</u>\n<b>Минимум</b> — 1 байт\n<b>Максимум</b> — 45 MB (это 46 080 KB или 47 185 920 байт)\n\nПожалуйста, введи подходящий размер 🙂")
            # Возвращаемся снова на шаг #4 "Проверка размера" (функция check_size). Не забываем передать туда
            # сообщение с выбранным расширением файла (format) и выбранной единицей измерения (unit).
            bot.register_next_step_handler(reply, check_size, format, unit)
        else:
            # Если всё ОК и размер файла соответствует ограничениям, то перейдем к его генерации. Для начала сделаем,
            # чтобы у файла всегда было уникальное имя. Для этого используя встроенный модуль time, получим текущий
            # timestamp и конвертируем в целое число. Имя файла будет содержать текущий timestamp, размер в байтах и
            # приписку bytes (будет выглядеть так - 1681568233-43521321-bytes.png).
            timestamp = int(time.time())
            filename = f'{timestamp}-{size_bytes}-bytes{format.text}'

            # Генерируем и сохраняем файл с заданным названием, записываем туда случайные байты в нужном количестве с
            # помощью os.urandom().
            f = open(filename, "wb")
            random_bytes = os.urandom(size_bytes)
            f.write(random_bytes)
            f.close()

            # Сделаем "умный" вывод финального сообщения, в зависимости от выбранных единиц измерения. Если выбраны
            # мегабайты или килобайты, выводим дополнительно в скобочках размер в байтах. Если выбраны байты,
            # то будем выводить только их. Дополнительно добавим форматирование чисел с помощью .format(),
            # чтобы большие числа красиво выглядели (пример - 2 330 200 байт).
            if unit_result_text == 'MB' or unit_result_text == 'KB':
                size_format = '{0:,}'.format(size).replace(',', ' ')
                size_bytes_format = '{0:,}'.format(size_bytes).replace(',', ' ')
                caption = f'🙌🏻 Ура, твой тестовый файлик с расширением <b>{format.text}</b> успешно сгенерирован!\n\nЕго размер — <b>{size_format} {unit_result_text}</b>\nВ байтах — <b>{size_bytes_format} B</b>'
            else:
                size_bytes_format = '{0:,}'.format(size_bytes).replace(',', ' ')
                caption = f'🙌🏻 Ура, твой тестовый файлик с расширением <b>{format.text}</b> успешно сгенерирован!\n\nЕго размер — <b>{size_bytes_format} {unit_result_text}</b>'

            # Открываем наш сгенерированный файл для чтения и отправляем его как документ.
            # Не забываем в подписи к нему (caption) добавить наш "умный" текст.
            # А также добавим клавиатуру с кнопкой "Вернуться в начало".
            f = open(filename, "rb")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Вернуться в начало')
            reply = bot.send_document(message.chat.id, f, caption=caption, reply_markup=markup)

            # Закрываем процедуру чтения файла и удаляем его, чтобы он не занимал место на диске.
            # После возвращаемся на первый начальный шаг "Приветствие".
            f.close()
            os.unlink(filename)
            bot.register_next_step_handler(reply, start)


# обработчик всех остальных сообщений
@bot.message_handler()
def message_handler(message: types.Message):
    global choose, card_type
    if choose == 'cards':
        # проверяем текст сообщения на совпадение с текстом какой-либо из кнопок
        # в зависимости от типа карты присваиваем значение переменной 'card_type'
        if message.text == 'VISA':
            card_type = 'visa'
        elif message.text == 'Mastercard':
            card_type = 'mastercard'
        elif message.text == 'Maestro':
            card_type = 'maestro'
        elif message.text == 'JCB':
            card_type = 'jcb'
        elif message.text == 'Вернуться в начало' or message.text == '/start':
            start(message)
            return
        else:
            # если текст не совпал ни с одной из кнопок выводим ошибку
            bot.send_message(message.chat.id, 'Не понимаю тебя :(')
            return

        # получаем номер тестовой карты выбранного типа
        # card_type может принимать одно из значений ['maestro', 'mastercard', 'visa13', 'visa16', 'visa19',
        # 'amex', 'discover', 'diners', 'jcb15', 'jcb16']

        card_info = faker.credit_card_full(card_type)

        list_card_info = card_info.split("\n")
        if card_type == 'maestro':
            card_number = format_card_number(list_card_info[2]) + "\n" + list_card_info[2][13:]
        else:
            card_number = format_card_number(list_card_info[2]) + "\n" + list_card_info[2][17:]
        list_card_info[2] = card_number
        format_card_info = "\n".join(list_card_info)

        # и выводим пользователю
        bot.send_message(message.chat.id, f'Тестовая карта:\n<code>{format_card_info}</code>')
    elif choose == 'json':
        if message.text == 'Вернуться в начало' or message.text == '/start':
            start(message)
            return
        try:
            # пытаемся распарсить JSON из текста сообщения
            payload = json.loads(message.text)
        except json.JSONDecodeError as ex:
            # при ошибке возникнет исключение 'json.JSONDecodeError'
            # преобразовываем исключение в строку и выводим пользователю
            bot.send_message(message.chat.id, f'При обработке произошла ошибка:\n<code>{str(ex)}</code>',
                             reply_markup=json_kb)
            # выходим из функции
            return

            # если исключения не возникло - значит был введен корректный JSON
            # форматируем его в красивый текст :) (отступ 2 пробела на уровень, сортировать ключи по алфавиту)
        text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        # и выводим пользователю
        bot.send_message(message.chat.id, f'JSON:\n<code>{text}</code>', reply_markup=json_kb)
    elif choose == 'data':
        # определяем количество тестовых пользователей
        # или отправляем ошибку
        payload_len = 0
        if message.text == "1️⃣":
            payload_len = 1
        elif message.text == "2️⃣":
            payload_len = 2
        elif message.text == "5️⃣":
            payload_len = 5
        elif message.text == "🔟":
            payload_len = 10
        elif message.text == 'Вернуться в начало' or message.text == '/start':
            start(message)
            return
        else:
            bot.send_message(message.chat.id, "Не понимаю тебя :(")
            return

        # генерируем тестовые данные для выбранного количества пользователей
        # при помощи метода simple_profile
        total_payload = []
        for _ in range(payload_len):
            user_info = faker.simple_profile()
            user_info['phone'] = f'+7{faker.msisdn()[3:]}'
            # при помощи библиотеки secrets генерируем пароль
            user_info['password'] = token_urlsafe(10)
            total_payload.append(user_info)

        # сериализуем данные в строку
        payload_str = json.dumps(
            obj=total_payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            default=str
        )

        # отправляем результат
        bot.send_message(message.chat.id, f"Данные {payload_len} тестовых пользователей:\n<code>"
                                          f"{payload_str}</code>")
        bot.send_message(message.chat.id, "Если нужны еще данные, можешь выбрать еще раз 👇🏻", reply_markup=data_kb)


# главная функция программы
def main():
    # запускаем нашего бота
    bot.infinity_polling()


if __name__ == '__main__':
    main()
