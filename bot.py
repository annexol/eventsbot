import telebot  # pip install pytelegrambotapi
from telebot import types
from date_base import *
from telegram_bot_pagination import InlineKeyboardPaginator
import events
import datetime
# from telegram_token import telegram_token
import os

bot = telebot.TeleBot('1621525058:AAF3KHqupGjUydkUBIryL4jgdnAMHCVX8v8')

types_events = {'Концерт ♬': 'concerts',
                'Театр 🎭': 'theatre',
                'Выставки 🌉': 'expo',
                'Другое 🎨': 'other',
                'Стендап 🎤': 'stand_up',
                'Образование 📖': 'education'
                }

day_of_week = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}

'''creating the list that contains the days of the week for buttons'''
today = datetime.datetime.today().weekday()

'''getting numbers of the month'''


def get_number_day():
    list_date = []
    for item in range(6):
        day = datetime.datetime.today() + datetime.timedelta(days=item)
        date_of_day = day.strftime("%d_%m_%Y")
        list_date.append(date_of_day)
    return list_date


list_numbers_of_month = get_number_day()

type_event = None

user_name = []
person = {}

'''creating inline buttons'''


def day_buttons():
    days_for_buttons = [today + number if (today + number) < 7 else number + today - 7 for number in range(6)]
    keyboard_day = types.InlineKeyboardMarkup()
    i_today = types.InlineKeyboardButton(text='Сегодня', callback_data=list_numbers_of_month[0])
    i_today_and_1 = types.InlineKeyboardButton(text=day_of_week[days_for_buttons[1]],
                                               callback_data=list_numbers_of_month[1])
    i_today_and_2 = types.InlineKeyboardButton(text=day_of_week[days_for_buttons[2]],
                                               callback_data=list_numbers_of_month[2])
    i_today_and_3 = types.InlineKeyboardButton(text=day_of_week[days_for_buttons[3]],
                                               callback_data=list_numbers_of_month[3])
    i_today_and_4 = types.InlineKeyboardButton(text=day_of_week[days_for_buttons[4]],
                                               callback_data=list_numbers_of_month[4])
    i_today_and_5 = types.InlineKeyboardButton(text=day_of_week[days_for_buttons[5]],
                                               callback_data=list_numbers_of_month[5])

    keyboard_day.add(i_today,
                     i_today_and_1,
                     i_today_and_2,
                     i_today_and_3,
                     i_today_and_4,
                     i_today_and_5, )
    return keyboard_day


gender_user = types.InlineKeyboardMarkup()
i_men_gender = types.InlineKeyboardButton(text='Я парень 👨', callback_data='Парень')
i_woman_gender = types.InlineKeyboardButton(text='Я девушка 👩', callback_data='Девушка')
gender_user.add(i_men_gender, i_woman_gender)

gender_find_people = types.InlineKeyboardMarkup()
i_find_men_gender = types.InlineKeyboardButton(text='Пойду с парнем 👨', callback_data='find_men')
i_find_woman_gender = types.InlineKeyboardButton(text='Пойду с девушкой 👩', callback_data='find_woman')
i_find_people = types.InlineKeyboardButton(text='Неважно 👻', callback_data='find_people')
gender_find_people.add(i_find_men_gender, i_find_woman_gender)
gender_find_people.add(i_find_people)

show_people = types.InlineKeyboardMarkup()
i_list = types.InlineKeyboardButton(text='Показать людей', callback_data='show_people')
show_people.add(i_list)

'''creating keyboard buttons'''


def user_age(years):
    if str(years)[0] == '1' or str(years)[-1] == '0' or int(str(years)[1]) >= 5:
        return f'{years} лет'
    else:
        return f'{years} года'


'''function for working with callback'''


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == '*')
def answer_paginator(call):
    if call.data.split('#')[1] == 'show_people':
        current_page = int(call.data.split('#')[-1])
        show = DataBase()
        show.connection()
        persons = show.show_people(call.from_user.username)
        pages = len(persons)

        paginator = InlineKeyboardPaginator(
            pages,
            current_page=current_page,
            data_pattern=f'*#show_people#persons' + '#{page}'
        )
        date = str(persons[current_page - 1][5]).split()[0]
        text = f'Дата: {date}' + '\n' * 2 + f'💥{str(persons[current_page - 1][3])}: {str(persons[current_page - 1][1])}, ' + f'{user_age(persons[current_page - 1][4])}' + '\n' + f'Написать:@{str(persons[current_page - 1][2])}' + '\n' * 2

        photos_dir = os.listdir('photos/')
        name_users = {}
        for i in photos_dir:
            name_users[i.split('.')[0]] = i.split('.')[1]
        if persons[current_page - 1][2] in name_users:
            try:
                bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except Exception as e:
                print(e)

            with open(f'photos/{persons[current_page - 1][2]}.{name_users[persons[current_page - 1][2]]}',
                      'rb') as photo:
                bot.send_photo(call.from_user.id, photo=photo, caption=text, reply_markup=paginator.markup)
                photo.close()
        else:
            try:
                bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except Exception as e:
                print(e)

            with open(f'photos/no_photo.jpg', 'rb') as photo:
                bot.send_photo(call.from_user.id, photo=photo, caption=text, reply_markup=paginator.markup)
                photo.close()


    else:
        data = call.data.split('#')
        events = DataBase()
        events.connection()
        list_text = events.read_db(data[1], data[2])
        if len(list_text) / 10 > 1:  # 10 lines are displayed in the message
            if len(list_text) % 10 > 0:
                pages = int(len(list_text) / 10 + 1)
            else:
                pages = int(len(list_text) / 10)
        else:
            pages = 1

        paginator = InlineKeyboardPaginator(
            pages,
            current_page=int(data[3]),
            data_pattern=f'*#{data[1]}#{data[2]}' + '#{page}'
        )
        start_page = (int(data[3]) - 1) * 10
        ending = start_page + 10

        header = ''
        for i, j in types_events.items():
            if j == type_event:
                header = i
                break

        text = header + ' ' + call.data.split('#')[1].replace('_', '.') + ':' + '\n' * 2  # formation of text messages
        for event in list_text[start_page:ending]:
            text += ('💥 ' + event[5] + ' 🏛 ' + '*' + event[2] + '*' + ' 🕤 ' + event[3] + '\n' + '\n')

        try:
            bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
        except Exception as e:
            print(e)

        bot.send_message(call.from_user.id, text=text, parse_mode='Markdown',
                         reply_markup=paginator.markup)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard_event = types.ReplyKeyboardMarkup(resize_keyboard=True)
    i_concert = types.KeyboardButton(text='Концерт ♬')
    i_theatre = types.KeyboardButton(text='Театр 🎭')
    i_expo = types.KeyboardButton(text='Выставки 🌉')
    i_stand = types.KeyboardButton(text='Стендап 🎤')
    i_other = types.KeyboardButton(text='Другое 🎨')
    i_education = types.KeyboardButton(text='Образование 📖')
    i_find = types.KeyboardButton(text='Найти компанию 👫')
    keyboard_event.add(i_concert, i_theatre, i_expo, i_stand, i_other, i_education, i_find)
    bot.send_message(message.chat.id, text='Здравствуйте, выберете мероприятие', reply_markup=keyboard_event)


@bot.message_handler(content_types='text')
def weekday(event):
    try:
        if event.text == 'Найти компанию 👫':
            if event.from_user.username == None:  # checking the existence of the name in the telegram settings
                bot.reply_to(event, text='У Вас не задано имя пользователя в настройках...')
            else:
                person['first_name'] = event.from_user.first_name  # getting user data
                person['username'] = event.from_user.username  # getting user data
                if bot.get_user_profile_photos(event.from_user.id).photos:
                    photo = bot.get_user_profile_photos(event.from_user.id)
                    file_photo = bot.get_file(photo.photos[0][1].file_id)
                    file_name, file_extension = os.path.splitext(file_photo.file_path)
                    download_photo = bot.download_file(file_photo.file_path)
                    with open('photos/' + event.from_user.username + file_extension, 'wb') as new_photo:
                        new_photo.write(download_photo)
                        new_photo.close()

                bot.reply_to(event, text='Кто вы?', reply_markup=gender_user)

        elif event.text in types_events.keys():  # showing button keyboard_day
            global type_event, today, list_numbers_of_month
            list_numbers_of_month = get_number_day()
            type_event = types_events[event.text]
            today = datetime.datetime.today().weekday()

            bot.reply_to(event, text='Когда желаете пойти?', reply_markup=day_buttons())
        elif event.text == 'runparse':  # database update command
            events.get_events(events.urls)
            bot.reply_to(event, text='done')
        elif event.text == 'showall':  # command to display all users
            show_all = DataBase()
            show_all.connection()
            all_persons = show_all.show_all()
            text = ''
            for i in all_persons:  # formation of text messages
                text += '💥{}: {}, {} {}, написать:@{}'.format(str(i[3]), str(i[1]),
                                                               str(i[4]), 'лет', str(i[2]) + '\n' + '\n')
            bot.reply_to(event, text=text)

        elif event.text[0] == '%':  # command to delete the user from the database
            delete = DataBase()
            delete.connection()
            delete.delete_person(event.text[1:])



        else:  # checking the correctness of entering the user's age
            if 10 < int(event.text) < 100:
                person['age'] = event.text
                if len(person) >= 4:
                    add_person = DataBase()
                    add_person.connection()
                    status = add_person.insert_person(person)
                    if status == 'add':
                        bot.send_message(event.from_user.id, text='Нажмите на кнопку', reply_markup=show_people)
                    elif status == 'existed':
                        bot.send_message(event.from_user.id, text='Вы уже есть в списке... Данные обновлены...',
                                         reply_markup=show_people)
                else:
                    bot.reply_to(event, text='Вы ввели данные некорректно... Попробуйте заново... ')
            else:
                bot.reply_to(event, text='Вы ввели данные некорректно... Попробуйте заново... ')

    except Exception as error:
        print(error)
        bot.reply_to(event, text='Вы ввели данные некорректно... Попробуйте заново... ')





@bot.callback_query_handler(func=lambda call: True)
def answer(call):  # user gender detection
    if call.data == 'Парень' or call.data == 'Девушка':
        person['sex'] = call.data
        bot.send_message(call.from_user.id, text='Сколько Вам лет?')

    elif call.data == 'show_people':  # showing people who are looking for a company
        show = DataBase()
        show.connection()
        persons = show.show_people(call.from_user.username)
        if persons == 'empty':
            bot.send_message(call.from_user.id, text='Кроме Вас в списке пока никого нет...')
        else:

            pages = len(persons)

            paginator = InlineKeyboardPaginator(
                pages,
                current_page=1,
                data_pattern=f'*#{call.data}#persons' + '#{page}'
            )

            date = str(persons[0][5]).split()[0]
            text = f'Дата: {date}' + '\n' * 2 + f'💥{str(persons[0][3])}: {str(persons[0][1])}, ' + f'{user_age(persons[0][4])}' + '\n' + f'Написать:@{str(persons[0][2])}' + '\n' * 2
            photos_dir = os.listdir('photos/')
            name_users = {}
            for i in photos_dir:
                name_users[i.split('.')[0]] = i.split('.')[1]
            if persons[0][2] in name_users:
                with open(f'photos/{persons[0][2]}.{name_users[persons[0][2]]}', 'rb') as photo:
                    bot.send_photo(call.from_user.id, photo=photo, caption=text, reply_markup=paginator.markup)
                    photo.close()
            else:
                with open(f'photos/no_photo.jpg', 'rb') as photo:
                    bot.send_photo(call.from_user.id, photo=photo, caption=text, reply_markup=paginator.markup)
                    photo.close()

    else:  # showing events
        events = DataBase()
        events.connection()
        list_text = events.read_db(call.data, type_event)

        if len(list_text) / 10 > 1:  # 10 lines are displayed in the message
            if len(list_text) % 10 > 0:
                pages = int(len(list_text) / 10 + 1)
            else:
                pages = int(len(list_text) / 10)
        else:
            pages = 1

        paginator = InlineKeyboardPaginator(
            pages,
            current_page=1,
            data_pattern=f'*#{call.data}#{type_event}' + '#{page}'
        )

        header = ''
        for i, j in types_events.items():
            if j == type_event:
                header = i
                break

        text = header + ' ' + call.data.replace('_', '.') + ':' + '\n' * 2  # formation of text messages
        try:
            for event in list_text[:10]:
                text += ('💥 ' + event[5] + ' 🏛 ' + '*' + event[2] + '*' + ' 🕤 ' + event[3] + '\n' + '\n')

            bot.send_message(call.from_user.id, text=text, parse_mode='Markdown',
                             reply_markup=paginator.markup)
        except:
            bot.send_message(call.from_user.id, text='В выбранный день мероприятий не запланировано...')


if __name__ == '__main__':
    bot.polling()
