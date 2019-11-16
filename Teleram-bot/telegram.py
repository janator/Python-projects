import requests
import psycopg2
from constants import *


class Telegram:
    def __init__(self, TOKEN):
        self.url_for_telegram = 'https://api.telegram.org/bot' + TOKEN + '/'
        db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        db.autocommit = True
        self.cursor = db.cursor()
        self.cursor.execute('Create Table if not exists ALREADY_USED(ID INTEGER PRIMARY KEY )')
        self.cursor.execute('Create Table if not exists DIARY(CHAT_ID INTEGER, TEXT VARCHAR(1000), '
                            'PRIMARY KEY (ChaT_ID, TEXT))')

    def process(self, message):
        message_text = message['text'].split(' ')
        chat_id = message['chat']['id']

        if len(message_text) > 1 and message_text[0] == '/add':
            case = u' '.join(message_text[1:]).encode('utf-8')
            try:
                self.cursor.execute('Insert into diary values(%s, %s)', (chat_id, case))
                self.send_message(chat_id, 'Added successfully: ' + str(case))
            except Exception:
                self.send_message(chat_id, 'This case already exists')

        elif len(message_text) > 1 and message_text[0] == '/delete':
            case = u' '.join(message_text[1:]).encode('utf-8')
            try:
                self.cursor.execute('Select chat_id from diary where chat_id = %s and text = %s',
                                    (chat_id, case))

                if self.cursor.rowcount:
                    self.cursor.execute('Delete from diary where chat_id = %s and text = %s',
                                        (chat_id, case))
                    self.send_message(chat_id, 'Deleted: ' + str(case))
                else:
                    pass
                    raise ValueError('No such case')
            except Exception:
                self.send_message(chat_id, 'Error. There\'s no such case in your list.')

        elif message_text and message_text[0] == '/list':
            self.cursor.execute('Select TEXT from diary where chat_id = %s', (chat_id,))
            string = []
            q = 1
            for i in self.cursor:
                string.append('\nCase ' + str(q) + ':\n')
                string.append(i[0])
                q += 1

            if len(string) != 0:
                self.send_message(chat_id, ''.join(string))
            else:
                self.send_message(chat_id, 'You have no cases.')

        elif message_text and message_text[0] == '/start':
            self.send_message(chat_id,
                              'Hello, I\'m yout bot-schedule. \n'
                              'With my help you will always have your to-do list with you. \n'
                              '/add _your_case_ - add new case in list, \n'
                              '/delete _your_case_ - delete case from list, \n'
                              '/list - show your to-do list, \n'
                              '/help - show all available commands.')
        elif message_text and message_text[0] == '/help':
            self.send_message(chat_id, 'Avaliable commands: \n'
                                       '/add _your_case_ - add new case in list, \n'
                                       '/delete _your_case_ - delete case from list, \n'
                                       '/list - show your to-do list, \n'
                                       '/help - show all available commands.')
        else:
            self.send_message(chat_id, 'Wrong command.')

    def get_updates(self):
        ans = requests.get(self.url_for_telegram + 'getUpdates').json()

        for i in ans['result']:
            self.cursor.execute('Select * from already_used where ID = %s', (str(i['update_id']),))
            if not self.cursor.rowcount:
                self.process(i['message'])
                self.cursor.execute('Insert into already_used values(%s)', (str(i['update_id']),))

    def send_message(self, chat_id, text):
        ans = requests.get(self.url_for_telegram + 'sendMessage?text='
                           + str(text) + '&chat_id=' + str(chat_id))
