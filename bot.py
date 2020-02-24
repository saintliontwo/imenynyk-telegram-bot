import calendar
from datetime import datetime
import json
import random
import re
import telebot
from telebot import types
from name_list import _NAME_LIST


#  ================================ PRESETS ================================
TODAY = datetime.now()
commands = {
    "start": "начати користуватися ботом",
    "help": "побачити доступні команди",
    "date": "подивитися іменини за датою",
    "name": "дізнатися коли іменини по імені",
    "subscribe": "управління підписками",
}
known_user = []  # user state. Need to implement


def day_checker(check_day: int, check_month: int):
    """Check data"""
    try:
        datetime(TODAY.year, check_month, check_day)
    except Exception:
        return False
    else:
        return True


def get_name_list(input_day: int, input_month=datetime.now().month):
    """
        :return: markdowned name-day list in str representation
        Need to refactor
    """
    if day_checker(input_day, input_month):
        day, month = input_day, input_month
    with open('fete_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return "*" + ", ".join(data[str(int(month))][str(int(day))]) + "*"                          # Markdown


def random_congrat(when: str):
    """
        :param when is state like: today, yesterday, tomorrow
        :return random congratulation
    """
    congrat_list = {"today": ["Сьогодні іменини у людей с цими іменами: ",
                              "Не забудьте привітати сьогодні:",
                              "Якщо ви знайомі з людиною яка має однє з цих імен, привітайте її ",
                              "Вітаємо! ",
                              "Подивіться на свій записничок, можливо вам варто привітати колег з іменами: "],
                    "tomorrow": ["Завтра святкують:"],
                    "yesterday": ['Вчора були іменини', "Ви встигли привітати? Вчора були іменини"]}
    res = random.choice(congrat_list[when])
    return res + "\n\n"


# ================================ TELEGRAM HANDLERS ================================
@bot.message_handler(commands=['start'])
def command_start(message):
    """Send start page"""
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id,
                     text="Вітаємо!\nЦей бот підкаже коли та в кого іменини. "
                          "Для початку ознайомтись з командами.\nНатисніть */help*",
                     parse_mode="Markdown")


@bot.message_handler(commands=['help'])
def command_help(message):
    """Send help page"""
    chat_id = message.chat.id
    help_text = "Наступні команди доступні:\n\n"
    for key in commands:
        help_text += f"*/{key}* - {commands[key]}\n"
    bot.send_message(chat_id=chat_id,
                     text=help_text + "\nЯкщо ви знайшли помилку або у вас є питання "
                                      "напишить за адресою *saintliontwo@gmail.com*",
                     parse_mode="Markdown")


@bot.message_handler(commands=['date'])
def date_command(message):
    """Recommend date buttons"""
    chat_id = message.chat.id
    date_keyboard = types.InlineKeyboardMarkup(row_width=3)
    yesterday_button = types.InlineKeyboardButton(text="вчора",
                                                  callback_data="yesterday")
    today_button = types.InlineKeyboardButton(text="сьогодні",
                                              callback_data="today")
    tomorrow_button = types.InlineKeyboardButton(text="завтра",
                                                 callback_data="tomorrow")
    another_button = types.InlineKeyboardButton(text="інакший день",
                                                callback_data="another")
    date_keyboard.add(yesterday_button, today_button, tomorrow_button, another_button)
    bot.send_message(chat_id=chat_id,
                     text="Бажаєте побачити список іменин на сьогодні або на інший день? ",
                     reply_markup=date_keyboard)


@bot.callback_query_handler(lambda query: query.data == "another")
def ask_date(query):
    """Ask about fete date"""
    bot.send_message(chat_id=query.message.chat.id,
                     text="Вкажіть дату яка вас цікавить (наприклад, _12.01_): ",
                     parse_mode="Markdown")


@bot.callback_query_handler(func=lambda query: query.data != "another")
def date_inline_callback(query):
    """Send results of date_command buttons. Need to refactor"""
    if query.data == 'today':
        text_data = get_name_list(input_day=TODAY.day, input_month=TODAY.month)
    elif query.data == 'tomorrow':
        text_data = get_name_list(input_day=TODAY.day+1, input_month=TODAY.month)
    elif query.data == 'yesterday':
        text_data = get_name_list(input_day=TODAY.day-1, input_month=TODAY.month)
    text_phrase = random_congrat(query.data)
    generated_text = ''.join([text_phrase, text_data])
    bot.send_message(chat_id=query.message.chat.id,
                     text=generated_text,
                     parse_mode="Markdown")


@bot.message_handler(regexp=r"(\d{1,2}[\._ -/]\d{1,2})")
def current_date(message):
    """Send results of current date. Need to refactor"""
    day, month = [int(x) for x in re.split(r"[\._ -/]", message.text)]
    if not day_checker(day, month):
        bot.send_message(chat_id=message.chat.id,
                         text=f"*Неправильно вказана дата!*\nСпробуйте ще раз в форматі \"день.місяц\" "
                              f"(наприклад, _{TODAY.day}.{TODAY.month}_)",
                         parse_mode="Markdown")
    else:
        if month == TODAY.month and day in range(TODAY.day - 1, (TODAY.day + 1) + 1):
            if day == TODAY.day:
                text_phrase = random_congrat("today")
            elif day + 1 == TODAY.day:
                text_phrase = random_congrat("yesterday")
            elif day - 1 == TODAY.day:
                text_phrase = random_congrat("tomorrow")
        else:
            text_phrase = f"*{day}.{month}* іменини мають: \n\n"  # Markdown
        text_data = get_name_list(day, month)
        generated_text = ''.join([text_phrase, text_data])
        bot.send_message(chat_id=message.chat.id,
                         text=generated_text,
                         parse_mode="Markdown")


@bot.message_handler(commands=["name"])
def command_name(message):
    """Send name page"""
    bot.send_message(chat_id=message.chat.id,
                     text="Укажіть і'мя людини яке вас цікавить(наприклад, _\"Іван\"_): ",      # _Markdown_
                     parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text.lower() in _NAME_LIST)
def name_checked(message):
    """Show current(!) month calendar with chosen name. Need to extended"""
    name = message.text.capitalize()
    date_list = []
    with open('fete_data.json', 'r', encoding='utf-8') as file:                                # open json file with name days
        data = json.load(file)
    for days in range(TODAY.day, calendar._monthlen(year=TODAY.year, month=TODAY.month) + 1):  # remaining days in month
        for day in data[str(TODAY.month)][str(days)]:
            if name in day:
                date_list.append(str(days))
    if len(date_list) >= 1:
        text_phrase = f"*{message.text}* має іменини в цьому місяці в наступних днях:\n\n"      # *Markdown*
        text_data = "*" + ', '.join(date_list) + "*"  # Markdown
        generated_text = text_phrase + text_data
        bot.send_message(chat_id=message.chat.id,
                         text=generated_text,
                         parse_mode="Markdown")
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f"В цьому місяці *{message.text}* більше немає іменин",
                         parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text.lower() not in _NAME_LIST)
def name_not_checked(message):
    """Send mistake message. Need to refactor"""
    print(f"{message.date} - {message.from_user.id} - send name witch is not in DB: {message.text}")
    bot.send_message(chat_id=message.chat.id,
                     text=f"Якщо імя - *{message.text}*, його немає в нашій базі\n/help",
                     parse_mode="Markdown")


@bot.message_handler(commands=['subscribe'], func=lambda message: message.text == '/subscribe')
def command_subscribe(message):
    """Send subscribe page. Need to implement"""
    bot.send_message(chat_id=message.chat.id,
                     text="Ця функція ще нереалізована\n*/help*",
                     parse_mode="Markdown")

    
if __name__ == '__main__':
    TOKEN = <telegram token place>
    bot = telebot.TeleBot(TOKEN)
    bot.polling(none_stop=True, interval=0.5)
