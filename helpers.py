
import telepot

with open('../keyfeedback.txt') as f:
    TOKEN = f.read().replace('\n', '')

DEV_ID = '415691257'

bot = telepot.Bot(TOKEN)
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

    #try:
    bot.sendMessage(DEV_ID, msgstring)
    return True
    # except as err:
    #    return False


class TelemetryHandler(object):
    """
    Speichert Daten zu den Nutzerinteraktionen.
    {'message_id': 851,
     'from': {'id': 415691257, 'is_bot': False,
              'first_name': 'Eric', 'last_name': 'Bürki',
               'username': 'ericbuerki', 'language_code': 'de'},
     'chat': {'id': 415691257,
              'first_name': 'Eric', 'last_name': 'Bürki',
              'username': 'ericbuerki', 'type': 'private'},
     'date': 1524149831, 'text': 'hallo'}

    """
    def __init__(self, message):
        pass


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