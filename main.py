import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot("7112275967:AAE3mPs-PIFUxAnTKNRnMWVvFLBOStF5FkU")

#'7112275967:AAE3mPs-PIFUxAnTKNRnMWVvFLBOStF5FkU'

@bot.message_handler(commands=['start']) #декоратор - функция, которая запускает другую функцию, чтобы запустился def
def send_keyboard(message, text="Привет! Давай запишем твои задачи на сегодня."):
    keyboard = types.ReplyKeyboardMarkup(row_width=2) #наша клавиатура (размер клавиатуры для ответа; 2- сколько клавиш будет отражаться в ряду)
    itembtn1 = types.KeyboardButton('Добавить дело в список')  #keyboardbutton делает подпись кнопке
    itembtn2 = types.KeyboardButton('Показать список дел')
    itembtn3 = types.KeyboardButton('Удалить дело из списка')
    itembtn4 = types.KeyboardButton('Удалить все дела из списка')
    itembtn5 = types.KeyboardButton('Другое')
    itembtn6 = types.KeyboardButton('Пока что всё')
    keyboard.add(itembtn1, itembtn2) #добавим кнопки 1 и 2 на первый ряд
    keyboard.add(itembtn3, itembtn4, itembtn5, itembtn6) #добавим кнопки 3, 4, 5 на второй ряд


    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard) #text= Привет! Давай запишем твои задачи на сегодня.


    bot.register_next_step_handler(msg, callback_worker) #msg- выбор юзера, нажавшего на одну из 6-ти кнопок


conn = sqlite3.connect('planner_hse.db') #Подключаем базу данных
cursor = conn.cursor() #Курсор для работы с таблицами

try:
    # sql
    query = "CREATE TABLE \"planner\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER, \"plan\" TEXT, PRIMARY KEY (\"ID\"))"
    cursor.execute(query)
except:
    pass #если возникает ошибка, то pass её игнорирует


def add_plan(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('INSERT INTO planner (user_id, plan) VALUES (?, ?)',
                       (msg.from_user.id, msg.text))
        con.commit()
    bot.send_message(msg.chat.id, 'Отлично! Я запомнил.')
    send_keyboard(msg, "Чем ещё могу помочь?")

    #функция, которая делает нам красивые строки для отправки пользователю
def get_plans_string(tasks):
        tasks_str = [] #изначально пустой список
        for val in list (enumerate(tasks)):
               tasks_str.append(str(val[0]+1) +')' + val[1][0]+ '\n')#чтобы не начиналось с нуля прибавляем 1
        return'' .join(tasks_str)  #выходит весь список дел


def show_plans(msg):
        with sqlite3.connect('planner_hse.db') as con:
            cursor = con.cursor()
            cursor.execute('SELECT plan FROM planner WHERE user_id=={}'.format(msg.from_user.id))
            tasks = get_plans_string(cursor.fetchall())
            bot.send_message(msg.chat.id, tasks)
            send_keyboard(msg, "Чем ещё могу помочь?")

    #выделяет одно дело, которое пользователь хочет удалить
def delete_one_plans(msg):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        with sqlite3.connect('planner_hse.db') as con:
            cursor = con.cursor()
            #достаём все задачи пользователя
            cursor.execute('SELECT plan FROM planner WHERE user_id={}'.format(msg.from_user.id))
            #достаём результат запроса
            tasks = cursor.fetchall()
            for value in tasks:
                markup.add(types.KeyboardButton(value[0]))
                msg = bot.send_message(msg.from_user.id,
                                       text= "Выбери одно дело из списка",
                                       reply_markup=markup)
                bot.register_next_step_handler(msg, delete_one_plan_)

#удаляет дело
def delete_one_plan_(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM planner WHERE user_id==? AND plan==?', (msg.from_user.id))
        bot.send_message(msg.chat.id, 'Поздравляю! Минус одна задача.')
        send_keyboard(msg, "Чем ещё могу помочь?")

#удаляет все планы пользователя
def delete_all_plans(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM planner WHERE user_id=={}'.format(msg.from_user.id))
        con.commit()
        bot.send_message(msg.chat.id, 'Удалены все дела. Хорошего отдыха!')
        send_keyboard(msg, "Чем ещё могу помочь?")

#привязываем функции к кнопкам на клавиатуре
def callback_worker(call):
    if call.text == 'Добавить дело в список':
        msg = bot.send_message(call.chat.id, "Давай добавим дело! Напиши его мне.")
        bot.register_next_step_handler(msg, add_plan)

    elif call.text == 'Показать список дел':
        try:
         show_plans(call)
        except:
            bot.send_message(call.chat.id, "На данный момент здесь пусто.")
            send_keyboard(call, "Чем ещё могу помочь?")
    elif call.text == "Удалить дело из списка":
        try:
            delete_one_plan_(call)
        except:
            bot.send_message(call.chat.id, 'На данный момент здесь пусто.')
            send_keyboard(call, "Чем ещё могу помочь?")
    elif call.text == "Удалить все дела из списка":
        try:
            delete_all_plans(call)
        except:
            bot.send_message(call.chat.id, 'На данный момент здесь пусто.')
            send_keyboard(call, 'Чем ещё могу помочь?')
    elif call.text == "Другое":
        bot.send_message(call.chat.id, "Больше я ничего не умею...")
        send_keyboard(call, "Чем ещё могу помочь?")
    elif call.text == "Пока что всё":
        bot.send_message(call.chat.id, 'Хорошего дня!')





@bot.message_handler(content_types=['text'])
def handle_docs_audio(message):
    send_keyboard(message, text="Я не понимаю. Выберите один из пунктов меню:")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, text='Чем я могу тебе помочь?')

bot.polling(none_stop=True) #Чтобы постоянно опрашивал/отвечал


