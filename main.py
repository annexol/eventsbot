import bot
import events
import threading
import time


def new_events():
    while True:
        time.sleep(5)
        print('start')
        events.get_events(events.urls)
        print('++++++++++++++++')
        time.sleep(14440)





if __name__ == '__main__':
    t_1 = threading.Thread(target=new_events)
    t_1.start()
    bot.bot.polling()



