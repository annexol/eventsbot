import requests
from bs4 import BeautifulSoup
from lxml import html
import datetime
from date_base import *

urls = [['theatre', 'https://afisha.relax.by/theatre/minsk/'],
        ['concerts', 'https://afisha.relax.by/conserts/minsk/'],
        ['expo', 'https://afisha.relax.by/expo/minsk/'],
        ['other', 'https://afisha.relax.by/event/minsk/'],
        ['education', 'https://afisha.relax.by/education/minsk/'],
        ['stand_up', 'https://afisha.relax.by/stand-up/minsk/']
        ]

'''getting the day of the month'''
'''parsing events'''


def get_amount(url):
    def get_date(figure):
        day = datetime.datetime.today() + datetime.timedelta(days=figure)
        date = day.strftime("%d_%m_%Y")
        return date

    list_date = []
    for item in range(6):
        list_date.append(get_date(item))

    '''parsing events'''

    r = requests.get(url[1]).text
    soup = BeautifulSoup(r, 'lxml')  # getting soup object
    html_events = (soup.find_all('div', class_='schedule__list'))[
                  :6]  # getting html of page

    html_event = {}  # date is key, html of day is value

    for number in range(len(html_events)):

        number_event = html_events[number].find('h5', class_='h5 h5--compact h5--bolder u-mt-6x').text.strip().split()[
            0]
        if len(number_event) == 1:
            number_event = '0' + number_event

        number_event += (datetime.datetime.today()+ datetime.timedelta(days=number)).strftime("_%m_%Y")

        if number_event in list_date:
            html_event[number_event] = html_events[number]

        else:
            html_event[number_event] = False

    for number_of_days, html in html_event.items():
        if html:
            list_place = []  # places of events
            list_name = []  # names of events
            list_href = []  # links of events
            list_time = []  # time of events
            lis_href_text = []  # [text](link)
            events = html.find_all('div', class_='schedule__table--movie__item')  # string of events

            '''function filters symbols that are reserved by MarkdownV2'''

            def data_edit(text):
                list_symb = ['(', ')', '.', ',', '/', '<', '>', '?', '|', '!', '@', '#', '$', '%', '^', '&', '*', '+',
                             '-', "'"]
                text_2 = text.text
                text_3 = text_2.split()
                text_4 = ' '.join(text_3)
                for i in list_symb:
                    text_4 = text_4.replace(i, ' ')
                return text_4

            for number in range(len(events)):
                try:
                    place = (events[number].find('a', class_='schedule__place-link link'))
                    place_edit = data_edit(place)
                    list_place.append(place_edit)  # appending places in list
                except:
                    list_place.append(list_place[-1])

                name = events[number].find('a', class_='schedule__event-link link')
                name_edit = data_edit(name)
                list_name.append(name_edit)  # appending names in list

                hrev = name.get('href')
                list_href.append(hrev)  # appending links in list

                time = events[number].find(class_='schedule__seance-time')
                try:
                    time_edit = data_edit(time)
                    list_time.append(time_edit)  # appending time in list
                except:
                    list_time.append(' ')

            '''inserting events into database'''

            for i in range(len(list_name)):
                lis_href_text.append('[{text}]({url})'.format(text=list_name[i], url=list_href[i]))

            insert_data = DataBase()
            insert_data.connection()
            insert_data.insert_events(number_of_days, list_name, list_place, list_time, list_href, lis_href_text,
                                      url[0])
            insert_data.close_db()


'''updating database'''


def get_events(url_events):
    for url_event in url_events:
        get_amount(url_event)
