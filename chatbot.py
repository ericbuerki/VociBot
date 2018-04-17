import sys
import time
import telepot
import telepot.helper
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)

import urllib3

import suche
import strings

with open('../keytesting.txt') as f:
    TOKEN = f.read().replace('\n', '')

s = suche.Searcher()


#class VociBot(telepot.helper.InlineUserHandler, telepot.helper.AnswererMixin):
class VociBot(telepot.helper.ChatHandler):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=strings.options[0],
                             callback_data='continue'),
        InlineKeyboardButton(text=strings.options[1],
                             callback_data='abort')

    ]])

    def __init__(self, *args, **kwargs):
        super(VociBot, self).__init__(*args, **kwargs)

        # True, wenn neue Sitzung initialisiert wird
        self._newsession = True

        # Index in convohandler.messages, die gesendet wurden
        # self._messages_ind = 0

        # Objekt für die Bearbeitung von Konversationen
        self.convohandler = None

        # Zeugs für Callback-Handler
        self._edit_msg_ident = None
        self._editor = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('content_type:  %s' % content_type)
        print('chat_type:  %s' % chat_type)
        print('chat_id:  %s' % chat_id)
        print('msg[\'text\']:  %s' % msg['text'])

        if msg['text'].startswith('/'):
            self.funhandler(msg['text'])
        if self._newsession:
            # Initialisiert ConvoHandler bei neuer Sitzung neu
            self.convohandler = ConvoHandler(msg['text'])
            self._newsession = False
            self.sendwrapper(self.convohandler.next())
            # self.sendoptions()
        elif self.convohandler.done:
            print('self.convohandler: %s' % self.convohandler.done)
            # Initialisiert ConvoHandler nach Abschluss der
            # Suchanfrage neu
            self.convohandler = ConvoHandler(msg['text'])
            self.sendwrapper(self.convohandler.next())
        elif not self.convohandler.done:
            # self.convohandler.feed(msg['text'])
            self.funhandler(msg['text'])

    def _cancel_last(self):
        if self._editor:
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self._editor = None
            self._edit_msg_ident = None

    def on_callback_query(self, msg):
        print('self.on_callback_query')
        query_id, from_id, query_data = telepot.glance(msg,
                                                       flavor='callback_query')

        if query_data == 'continue':
            self._cancel_last()
            self.sendwrapper(self.convohandler.next())
        else:
            self.bot.answerCallbackQuery(query_id,
                                         text=strings.abort_inline)
            self._cancel_last()
            self.convohandler.done = True

    def funhandler(self, msgtext):
        if '/help' in msgtext:
            print('funhandler(): Zeige Hilfe an')
            self.sender.sendMessage(strings.helptext,
                                    parse_mode='Markdown')
        elif '/info' in msgtext:
            print('funhandler(): Zeige Infos an')
            self.sender.sendMessage(strings.infotext,
                                    parse_mode='Markdown')
        else:
            self.sender.sendMessage(strings.invalid_command % msgtext,
                                    parse_mode='Markdown')
            self.sender.sendMessage(strings.helptext,
                                    parse_mode='Markdown')


    def sendwrapper(self, messages):
        print('sendwrapper: aufgerufen')
        # Sendet mehrere Nachrichten auf einmal.
        if isinstance(messages, list):
            print('sendwrapper: messages ist list')
            for message in messages[:-1]:
                self.sender.sendMessage(message,
                                        parse_mode='Markdown')
            if not self.convohandler.done:
                # Es gibt noch weitere Ergebnisse
                self.sendquerymessage(messages[-1])
            else:
                # Letzter Eintrag
                self.sender.sendMessage(messages[-1],
                                        parse_mode='Markdown')
        elif isinstance(messages, str):
            print('sendwrapper: messages ist str')
            if not self.convohandler.done:
                self.sendquerymessage(messages)
            else:
                self.sender.sendMessage(messages,
                                        parse_mode='Markdown')
        else:
            print('Fehler: message muss str oder list sein, ist %s.' %
                  type(messages))
            raise TypeError

    def sendquerymessage(self, message):
        sent = self.sender.sendMessage(message,
                                       parse_mode='Markdown',
                                       reply_markup=self.keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_msg_ident = telepot.message_identifier(sent)


# Klasse, die die Konversation übernimmt
class ConvoHandler(object):
    def __init__(self, msgtext):

        print('ConvoHandler initialisiert')

        # True, wenn alle Nachrichten geschickt wurden
        self.done = False

        # Eingabequery
        self._msgtext = msgtext

        # Argumente, wird von preprocess definiert ['suche','mod']
        self._args = None

        # Nachrichten, bereit zum Senden,
        # wird von preprocess oder processquery definiert
        self._messages = None
        self._nextind = 0

        # True, wenn Parsen abgeschlossen ist
        self._finparse = False

        self.preprocess()
        if not self._finparse:
            self.processquery()

    def preprocess(self):
        args = self._msgtext.split(' ')
        if len(args) > 2:
            self._messages = [strings.unknown_warning % self._msgtext]
            self._finparse = True
        else:
            if len(args) == 1:
                args.append('all')
            self._args = [x.lower() for x in args]

    def processquery(self):
        start = time.time()
        s.search(self._args[0], self._args[1])
        m = suche.Matches(s.matches, self._args[0], self._args[1])
        self._messages = suche.parsematches(m.matches_fin)
        end = time.time()
        self._messages.append('%s Treffer in %.4f s' %
                              (sum((len(x) for x in m.matches_fin)),
                               end - start))
        self._finparse = True

    def next(self):
        tmp = self._messages[self._nextind]
        self._nextind += 1
        if len(self._messages) == self._nextind:
            self.done = True
        return tmp


bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(), create_open, VociBot, timeout=60),
])

MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)
