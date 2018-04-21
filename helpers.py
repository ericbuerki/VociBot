import os
import os.path

import time
import datetime

import json

import telepot

import private

'''
with open('../keyfeedback.txt') as f:
    TOKEN = f.read().replace('\n', '')

DEV_ID = '415691257'
'''

bot = telepot.Bot(private.TOKEN_FB)
print('FeedbackBot läuft.')


def sendfeedback(message):
    """
    Sendet Feedback an den Entwickler
    :param message:
    :return True/False:
    """
    print('sendfeedback() Name: %s %s' % (message['from']['first_name'],
                                          message['from']['last_name']))
    # String für die Feedbacknachricht
    msgstring = ''

    msgstring += '%s %s ' % (message['from']['first_name'],
                             message['from']['last_name'])
    msgstring += 'schrieb:\n'

    msgstring += message['text']

    bot.sendMessage(private.DEV_ID, msgstring)

"""
{'message_id': 851,
     'from': {'id': 999999999, 'is_bot': False,
              'first_name': 'Eric', 'last_name': 'Bürki',
               'username': 'xxx', 'language_code': 'de'},
     'chat': {'id': 999999999,
              'first_name': 'Eric', 'last_name': 'Bürki',
              'username': 'xxx', 'type': 'private'},
     'date': 1524149831, 'text': 'hallo'}
"""


class LoggingHandler(object):
    """
    Speichert Daten zu den Nutzerinteraktionen.
    Wird bei Schliessung der Session beendet

    self_data = {'id':              ID
                 'first_name':      Vorname
                 'last_name':       Nachname
                 'start_session':   Beginn der Sitzung  (Unix-Zeit)
                 'end_session':     Ende der Sitzung    (Unix-Zeit)
                 'queries':         {0:     query,
                                     1:     query,
                                     2:     query,
                                     ...
                                     }

    query = {'type':        Typ des Ereignis,
             'raw_query':   Unverarbeitetes Query,
             'args':        {'query':   Query
                             'mod':     Modifikator},
             'duration':    Zeit, die für Verarbeitung des Queries gebraucht
                            wurde,
             'time:         Zeitpunkt   (Unix-Zeit)
             'results':     Anzahl Ergebnisse bei Query}

    """
    def __init__(self, message):
        # Wichtige Nutzerdaten
        self._data = {'id': message['from']['id'],
                      'first_name': message['from']['first_name'],
                      'last_name': message['from']['last_name'],
                      'st   art_session': int(time.time()),
                      'end_session': None,
                      'events': {}
                      }
        # Pfad, für die dateien
        self._path = None

        self._current_query = {}

        self._collected_events = []

        self._create_logging_env()

        # Backup, falls Sammeln im Kontextmanager Fehlschlägt
        self._backup = None

    def __enter__(self):
        print('%s: Kontextmanager geöffnet' % self.__repr__())
        self._backup = [self._current_query,
                        self._collected_events]
        self.open_event()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._current_query, self._collected_events = self._backup
            print('Fehler, Daten wurden vom Backup wiederhergestellt')
            print('Fehler passierte in %s (%s)' % (exc_type.__name__,
                                                   exc_val))
        else:
            self.close_event()
        print('%s: Kontextmanager geschlossen' % self.__repr__())

    def __repr__(self):
        return 'LoggingHandler (%s %s)' % (self._data['first_name'],
                                           self._data['last_name'])

    def _create_logging_env(self):
        loggingpath = 'logs/%s' % self._data['id']
        if not os.path.exists(loggingpath):
            os.makedirs(loggingpath)
        self._path = loggingpath

    def open_event(self):
        self._current_query = {}
        print('%s: Neues Query geöffnet' % self.__repr__())

    def add_event_data(self, data):

        self._current_query = merge_two_dicts(self._current_query,
                                              data)

    def close_event(self):
        print('%s: Query geschlossen' % self.__repr__())
        self._collected_events.append(self._current_query)

    def close_session(self):
        self._data['end_session'] = int(time.time())

        print('%s: Sitzung geschlossen' % self.__repr__())

        self._write_data()

    def _write_data(self):
        for i, query in enumerate(self._collected_events):
            self._data['events'][i] = query

        # Konvertiert dict zu json
        json_data = json.dumps(self._data, ensure_ascii=False, indent=4)

        date_temp = datetime.datetime.fromtimestamp(self._data['end_session'])\
                                            .isoformat().split('T')
        fn = date_temp[0]
        time_temp = date_temp[1].split(':')[:2]
        fn += '-%s-%s' % tuple(time_temp)

        print(self._path)
        exact_path = os.path.join(self._path, '.'.join((fn,'json')))

        with open(exact_path,'w') as f:
            f.write(json_data)

        print('%s: Logs erfolgreich gespeichert in\n\t%s' % (self.__repr__(),
                                                             exact_path))


def merge_two_dicts(dict0, dict1):
    dict2 = dict0.copy()
    dict2.update(dict1)
    return dict2


if __name__ == "__main__":
    msg = {'message_id': 708,
           'from': {'id': 415691257, 'is_bot': False,
                    'first_name': 'Eric', 'last_name': 'Bürki',
                    'language_code': 'de'},
           'chat': {'id': 415691257,
                    'first_name': 'Eric', 'last_name': 'Bürki',
                    'type': 'private'},
           'date': 1524069498,
           'text': 'hallo'}
    sendfeedback(msg)