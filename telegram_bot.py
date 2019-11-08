#!/usr/bin/env py

import telebot
import pandas as pd
import random
import datetime
from telebot import types
import mongodb
import logging
import keys

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO,
                    filename=u'botlog.log')

logging.info(u'It`s work')

token = keys.telegram_token
bot = telebot.TeleBot(token)

money = ['money', 'buy', 'tickets', 'bought', 'kupic', 'купить', 'билеты', 'где купить']

origin_cities = {'kiev': 'Kyiv', 'kyiv': 'Kyiv', 'киев': 'Kyiv', 'київ': 'Kyiv',
                 'moscow': 'Moscow', 'moskow': 'Moscow', 'москва': 'Moscow', 'масква': 'Moscow',
                 'krakow': 'Krakow', 'kraków': 'Krakow', 'краков': 'Krakow', 'краків': 'Krakow',
                 'санкт-петербург': 'Saint Petersburg', 'saint petersburg': 'Saint Petersburg',
                 'спб': 'Saint Petersburg', 'saint-petersburg': 'Saint Petersburg', 'prague': 'Prague',
                 'прага': 'Prague'}
language_choosed = {'eng': 'Now I speak English', 'ru': 'Теперь я говорою по-русски'}

emoji = ['\U00002708', '\U0001F680', '\U0001F304', '\U0001F307', '\U0001F305', '\U0001F303', '\U0001F3A0', '\U000026F2']

origin_city = 'Krakow'
iata = {'Kyiv': 'IEV', 'Krakow': 'KRK', 'Moscow': 'MOW', 'Saint Petersburg': 'LED', 'Prague': 'PRG'}


@bot.message_handler(commands=['start'])
def start(message):
    data = mongo(message)
    bot.send_message(message.chat.id,
                     'Write the max price of the tickets in USD by using keyboard or choose one below to find the best offer.\n'
                     + 'To change your language /language\n'
                     + 'To change your city /city',
                     reply_markup=starting_keyboard())


@bot.message_handler(commands=['buy'])
def buy(message):
    data = mongo(message)
    lang = data['language']
    if lang == 'eng':
        bot.send_message(message.chat.id, 'You can buy tickets here \nhttp://jetradar.com/?marker=242680',
                         reply_markup=starting_keyboard())
    else:
        bot.send_message(message.chat.id, 'Купить билеты вы можете тут\nhttp://www.aviasales.ru/?marker=242680',
                         reply_markup=starting_keyboard())


@bot.message_handler(commands=['help'])
def help(message):
    data = mongo(message)
    lang = data['language']
    if lang == 'eng':
        bot.send_message(message.chat.id,
                         'Type the max price of the tickets in USD by using keyboard or choose one below to find the best offer.\n'
                         + 'To change your language /language\n'
                         + 'To change your city /city',
                         reply_markup=help_keyboard())
    else:
        bot.send_message(message.chat.id,
                         'Укажите максимальную цену для билета в USD используя клавиатуру, либо выберите из списка ниже\n'
                         + 'Для смены языка /language\n'
                         + 'Для смены города отправки /city',
                         reply_markup=help_keyboard())


@bot.message_handler(commands=['status'])
# Status of creating csv files script
def status_message(message):
    if message.chat.id == 408454739:
        bot.send_message(message.chat.id, status('mylog.log'))
    else:
        bot.send_message(message.chat.id, 'Sorry you must be an administrator',
                         reply_markup=starting_keyboard())


@bot.message_handler(commands=['botstatus'])
# Bot status
def bot_status_message(message):
    if message.chat.id == 408454739:
        bot.send_message(message.chat.id, status('botlog.log'))
    else:
        bot.send_message(message.chat.id, 'Sorry you must be an administrator',
                         reply_markup=starting_keyboard())


@bot.message_handler(commands=['time'])
def local_time(message):
    if message.chat.id == 408454739:
        bot.send_message(message.chat.id, datetime.datetime.now())
    else:
        bot.send_message(message.chat.id, 'Sorry you must be an administrator',
                         reply_markup=starting_keyboard())


@bot.message_handler(commands=['download'])
# Download creat_avia logs
def download(message):
    if message.chat.id == 408454739:
        directory = '/home/ec2-user/'
        document = open(directory + 'mylog.log', 'rb')
        try:
            bot.send_document(message.chat.id, document)
        except:
            bot.send_message(message.chat.id, 'Ups, some error')
        document.close()
    else:
        bot.send_message(message.chat.id, 'Sorry you must be an administrator',
                         reply_markup=starting_keyboard())


@bot.message_handler(commands=['botdownload'])
# Download bot logs
def bot_download(message):
    if message.chat.id == 408454739:
        directory = '/home/ec2-user/'
        document = open(directory + 'botlog.log', 'rb')
        try:
            bot.send_document(message.chat.id, document)
        except:
            bot.send_message(message.chat.id, 'Ups, some error')
        document.close()
    else:
        bot.send_message(message.chat.id, 'Sorry you must be an administrator',
                         reply_markup=starting_keyboard())


@bot.message_handler(commands=['language'])
def language_changer(message):
    data = mongo(message)
    lang = data['language']
    if lang == 'eng':
        bot.send_message(message.chat.id, 'Please choose a language',
                         reply_markup=language_keyboard())
    else:
        bot.send_message(message.chat.id, 'Пожалуйста выберите язык',
                         reply_markup=language_keyboard())


@bot.message_handler(commands=['city'])
def origin_changer(message):
    data = mongo(message)
    lang = data['language']
    origin = data['origin']
    if lang == 'eng':
        bot.send_message(message.chat.id,
                         'Your current city is ' + origin + "\nChoose a city below if you'd like to change it.",
                         reply_markup=origin_en_keyboard())
    else:
        bot.send_message(message.chat.id,
                         'Ваш нынешний город отправки ' + origin + '\nДля смены города, выберите из списка ниже.',
                         reply_markup=origin_ru_keyboard())


@bot.message_handler(commands=['profile'])
def profile(message):
    data = mongo(message)
    lang = data['language']
    origin = data['origin']

    if lang == 'eng':
        bot.send_message(message.chat.id, 'Language: ' + lang.title() + '\nHometown: ' + origin,
                         reply_markup=starting_keyboard())
    else:
        bot.send_message(message.chat.id, 'Язык: ' + lang.title() + '\nГород отбытия: ' + origin,
                         reply_markup=starting_keyboard())


@bot.message_handler(content_types=['text'])
def handle_text(message):
    data = mongo(message)
    lang = data['language']
    origin = data['origin']
    file_name = 'avi_result_' + iata[origin] + '.csv'
    df_tickets = pd.read_csv(file_name)
    text = message.text

    if text.lower() == 'eng' or text.lower() == 'ru':
        bot.send_message(message.chat.id, language_choosed[text.lower()],
                         reply_markup=starting_keyboard())
        mongodb.lang_updater(message.chat.id, text.lower())
    # Administrator function
    elif text == '\U00002699':
        bot.send_message(message.chat.id, 'You must be an administrator to use it', reply_markup=setings_keyboard())
    elif text.isdigit():
        try:
            bot.send_message(message.chat.id, compare_message(df_tickets[df_tickets['price'] <= int(text)], origin),
                             reply_markup=starting_keyboard())
        except:
            if int(text) < 100:
                if lang == 'eng':
                    bot.send_message(message.chat.id, "Unfortunately, I don't have such cheap tickets." + u'\U0001F614',
                                     reply_markup=starting_keyboard())
                else:
                    bot.send_message(message.chat.id, "Упс, у меня нет таких дешёвых билетов." + u'\U0001F614',
                                     reply_markup=starting_keyboard())
            else:
                if lang == 'eng':
                    bot.send_message(message.chat.id,
                                     "Wow, there are too many tickets at this price, so Telegram isn’t useful for it. Maybe try to check some lower prices.",
                                     reply_markup=starting_keyboard())
                else:
                    bot.send_message(message.chat.id,
                                     "Ого, слишком много билетов с такой ценой, Telegram будет не очень удобен для использования. Может быть попробуешь цену пониже.",
                                     reply_markup=starting_keyboard())
    # If some one want to buy a tickets
    elif money.count(text.lower()) > 0:
        if lang == 'eng':
            bot.send_message(message.chat.id, 'You can buy tickets here \nhttp://jetradar.com/?marker=242680',
                             reply_markup=starting_keyboard())
        else:
            bot.send_message(message.chat.id, 'Купить билеты вы можете тут\nhttp://www.aviasales.ru/?marker=242680',
                             reply_markup=starting_keyboard())
    else:
        # Try to change origin city
        try:
            if lang == 'eng':
                mongodb.origin_updater(message.chat.id, origin_cities[text.lower()])
                bot.send_message(message.chat.id, 'Now your city is ' + origin_cities[text.lower()],
                                 reply_markup=starting_keyboard())
            else:
                mongodb.origin_updater(message.chat.id, origin_cities[text.lower()])
                bot.send_message(message.chat.id, 'Теперь ваш город отправки ' + origin_cities[text.lower()],
                                 reply_markup=starting_keyboard())
        except:
            if lang == 'eng':
                bot.send_message(message.chat.id, 'Sorry I don`t get it. Write /help to check out what I can do.',
                                 reply_markup=starting_keyboard())
            else:
                bot.send_message(message.chat.id,
                                 'Извини, но я не понял. Напиши /help для того что-бы узнать, что я умею.',
                                 reply_markup=starting_keyboard())


def help_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('20')
    btn2 = types.KeyboardButton('40')
    btn3 = types.KeyboardButton('60')
    btn4 = types.KeyboardButton('/language')
    btn5 = types.KeyboardButton('/city')
    btn6 = types.KeyboardButton('/buy')
    btn7 = types.KeyboardButton('/profile')
    btn8 = types.KeyboardButton('\U00002699')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    markup.add(btn7, btn8)
    return markup


def setings_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('/status')
    btn2 = types.KeyboardButton('/time')
    btn3 = types.KeyboardButton('/download')
    btn4 = types.KeyboardButton('/botstatus')
    btn5 = types.KeyboardButton('/botdownload')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    return markup


def starting_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('20')
    btn2 = types.KeyboardButton('40')
    btn3 = types.KeyboardButton('60')
    btn4 = types.KeyboardButton('/language')
    btn5 = types.KeyboardButton('/city')
    btn6 = types.KeyboardButton('/help')
    btn7 = types.KeyboardButton('/buy')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5, btn6)
    markup.add(btn7)
    return markup


def language_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Ru')
    btn2 = types.KeyboardButton('Eng')
    markup.add(btn1, btn2)
    return markup


def origin_en_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Krakow')
    btn2 = types.KeyboardButton('Moscow')
    btn3 = types.KeyboardButton('Prague')
    btn4 = types.KeyboardButton('Kyiv')
    btn5 = types.KeyboardButton('Saint Petersburg')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    return markup


def origin_ru_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Краков')
    btn2 = types.KeyboardButton('Москва')
    btn3 = types.KeyboardButton('Прага')
    btn4 = types.KeyboardButton('Киев')
    btn5 = types.KeyboardButton('Санкт-Петербург')
    markup.add(btn1, btn2, btn3)
    markup.add(btn4, btn5)
    return markup


# Looking for a tickets in opened csv
def tickets(data, origin):
    result = []
    data_len = len(data)
    for i in range(0, data_len):
        origin_city = origin
        price = data.iloc[i]['price']
        dest_city = data.iloc[i]['destinaton citi']
        airline = data.iloc[i]['airline name']
        departure_date = (data.iloc[i]['departure_at']).split('T')[0]
        return_date = (data.iloc[i]['return_at']).split('T')[0]
        result.append(str(origin_city) + ' — ' + str(dest_city) + ' — ' + str(origin_city) + '\nPrice: ' +
                      str(price) + ' USD\n' + str(
            departure_date) + ' — ' + str(return_date) + ' by ' + str(airline))
    return result


# Compare tickets into a message
def compare_message(data, origin):
    result = ''
    for i in tickets(data, origin):
        result += i + '\n\n'
    if len(result) < 5:
        return result
    else:
        return random.choice(emoji) + '\n' + result


# Opening log files
def status(file):
    log = open(file, 'r')
    log_list = [line for line in log]
    number = len(log_list) - 20
    log_list = log_list[number:]
    mes = ''
    for i in log_list:
        mes += i
    log.close()
    return mes


# Read info from MongoDB
def mongo(message):
    try:
        # Try to read user data
        data = (mongodb.reader(message.chat.id))
        lang = data['language']
        return data
    except:
        # If no user with this id, create new user with this id
        mongodb.writer(message.chat.id)
        data = {'id': message.chat.id, 'lang': 'eng', 'origin': 'Krakow'}
        return data


bot.polling(none_stop=True, interval=0)

