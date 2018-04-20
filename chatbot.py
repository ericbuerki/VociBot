import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardRemove
from telepot.delegate import per_chat_id, create_open, pave_event_space

import urllib3

import suche
import strings
import helpers
import private


s = suche.Searcher()


class VociBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(VociBot, self).__init__(*args, **kwargs)

        # True, wenn neue Sitzung initialisiert wird
        self._newsession = True

        # Index in convohandler.messages, die gesendet wurden
        # self._messages_ind = 0

        # Objekt für die Bearbeitung von Konversationen
        self.convohandler = None

        self.buttons = {'keyboard': [strings.options]}

        # True, wenn Feedback erwartet wird
        self._await_feedback = False

        # LoggingHandler-Objekt
        self.logginghandler = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('content_type:  %s' % content_type)
        print('chat_type:  %s' % chat_type)
        print('chat_id:  %s' % chat_id)
        print('msg[\'text\']:  %s' % msg['text'])

        if self._await_feedback:
            # Stellt sicher, dass Feedback eingelesen wird
            if not 'abbrechen' in msg['text']:
                helpers.sendfeedback(msg)
                self.sender.sendMessage(strings.fb_success,
                                        parse_mode='Markdown')
                self.logginghandler.add_event_data(
                    {'aborted': False,
                     'feedback': msg['text']}
                )
            else:
                self.sender.sendMessage(strings.fb_abort,
                                        parse_mode='Markdown')
                self.logginghandler.add_event_data(
                    {'aborted': True})
            self._await_feedback = False
            self.logginghandler.close_event()
        elif msg['text'].startswith('/') or msg['text'].startswith('*'):

            if not self.logginghandler:
                self.logginghandler = helpers.LoggingHandler(msg)

            # Liest Kommandos und MarkupKeyboardeingaben aus
            self.funhandler(msg['text'])
        elif self._newsession:

            # Initialisiert ConvoHandler bei neuer Sitzung neu
            self.convohandler = ConvoHandler(msg['text'])

            self._newsession = False
            self.sendwrapper(self.convohandler.next())

            # Initialisiert den LoggingHandler
            self.logginghandler = helpers.LoggingHandler(msg)
            print(self.logginghandler)
            self.logging_add_query(msg['text'])

        elif self.convohandler.done:
            # Initialisiert ConvoHandler nach Abschluss der
            # Suchanfrage neu
            print('self.convohandler.done: %s' % self.convohandler.done)

            self.convohandler = ConvoHandler(msg['text'])
            self.sendwrapper(self.convohandler.next())

            self.logging_add_query(msg['text'])

    def funhandler(self, msgtext):
        self.logginghandler.open_event()
        if '/help' in msgtext:
            print('funhandler(): Zeige Hilfe an')
            self.sender.sendMessage(strings.helptext, parse_mode='Markdown')

            self.logginghandler.add_event_data({'type': 'show_help'})
        elif '/info' in msgtext:
            print('funhandler(): Zeige Infos an')
            self.sender.sendMessage(strings.infotext, parse_mode='Markdown')

            self.logginghandler.add_event_data({'type': 'show_info'})
        elif '/feedback' in msgtext:
            print('funhandler() Feedback')
            self.sender.sendMessage(strings.fb_text, parse_mode='Markdown')
            self._await_feedback = True

            self.logginghandler.add_event_data({'type': 'send_feedback'})
        elif strings.options[0] == msgtext:     # Weiter
            self.logginghandler.add_event_data(
                {'type': 'query_continue',
                 'successful': False})
            if not self._newsession and self.convohandler:
                if not self.convohandler.done:
                    self.sendwrapper(self.convohandler.next())
                    self.logginghandler.add_event_data(
                        {'successful': True}
                    )
        elif strings.options[1] == msgtext:     # Abbrechen
            self.logginghandler.add_event_data(
                {'type': 'query_abort',
                 'successful': False}
            )
            if self.convohandler:
                if not self.convohandler.done:
                    self.convohandler.done = True
                    self.sender.sendMessage(strings.aborttext,
                                            parse_mode='Markdown',
                                            reply_markup=ReplyKeyboardRemove())
                    self.logginghandler.add_event_data(
                        {'successful': True}
                    )
        else:
            self.sender.sendMessage(strings.unknown_warning,
                                    parse_mode='Markdown',
                                    reply_markup=ReplyKeyboardRemove())
            self.logginghandler.add_event_data(
                {'type': 'unknown_command',
                 'raw_query': msgtext}
            )

        self.logginghandler.add_event_data({'time': int(time.time())})
        if not self._await_feedback:
            self.logginghandler.close_event()

    def sendwrapper(self, messages):
        buttons = {'keyboard': [strings.options]}
        print('sendwrapper: Aufruf')
        # Sendet mehrere Nachrichten auf einmal.
        if isinstance(messages, list):
            print('sendwrapper: list')
            for message in messages[:-1]:
                self.sender.sendMessage(message,
                                        parse_mode='Markdown',
                                        reply_markup=ReplyKeyboardRemove())
            if not self.convohandler.done:
                print('convohanler not done')
                self.sender.sendMessage(messages[-1],
                                        parse_mode='Markdown',
                                        reply_markup=buttons)
                # self.sendoptions()
            else:
                self.sender.sendMessage(messages[-1],
                                        parse_mode='Markdown',
                                        reply_markup=ReplyKeyboardRemove())
        elif isinstance(messages, str):
            print('sendwrapper: str')
            if not self.convohandler.done:
                print('convohanler not done')
                self.sender.sendMessage(messages,
                                        parse_mode='Markdown',
                                        reply_markup=buttons)
                # self.sendoptions()
            else:
                self.sender.sendMessage(messages,
                                        parse_mode='Markdown',
                                        reply_markup=ReplyKeyboardRemove())
        else:
            print('Fehler: message muss str oder list sein, ist %s.' %
                  type(messages))
            raise TypeError

    def logging_add_query(self, msgtext):
        # self.logginghandler.open_event()
        print(self.logginghandler)
        with self.logginghandler as lh:
            # self.logginghandler.add_event_data(
            lh.add_event_data(
                {'type': 'query',
                 'raw_query': msgtext,
                 'args': {'query': self.convohandler.args[0],
                          'mod': self.convohandler.args[1]},
                 'duration': self.convohandler.elapsed_time,
                 'time': int(time.time()),
                 'results': self.convohandler.results,
                 'messages': len(self.convohandler.messages)})
            # self.logginghandler.close_event()

    def logging_add_interaction(self, _type):
        self.logginghandler.open_event()
        self.logginghandler.add_event_data(
            {'type': _type,
             'time': int(time.time())
             }
        )

    def on_close(self, ex):
        print('Sitzung geschlossen')
        if self.logginghandler:
            self.logginghandler.close_session()


class ConvoHandler(object):
    """
    Übernimmt die Kommunikation während des Suchprozesses.
    Portioniert die Nachrichten fürs Senden.
    """
    def __init__(self, msgtext):

        print('ConvoHandler initialisiert')

        # True, wenn alle Nachrichten geschickt wurden
        self.done = False

        # Eingabequery
        self._msgtext = msgtext

        # Argumente, wird von _preprocess definiert ['suche','mod']
        self.args = None

        # Nachrichten, bereit zum Senden,
        # wird von _preprocess oder _processquery definiert
        self.messages = None
        self._nextind = 0

        # True, wenn Parsen abgeschlossen ist
        self._finparse = False

        # Zeit, die für Verarbeitung von Query benötigt wird
        self.elapsed_time = 0
        # Anzahl Resultate
        self.results = 0

        self._preprocess()
        if not self._finparse:
            self._processquery()

    def _preprocess(self):
        args = self._msgtext.split(' ')
        if len(args) > 2:
            self.messages = [strings.unknown_warning % self._msgtext]
            self._finparse = True
        else:
            if len(args) == 1:
                args.append('all')
            self.args = [x.lower() for x in args]

    def _processquery(self):
        start = time.time()
        s.search(self.args[0], self.args[1])
        m = suche.Matches(s.matches, self.args[0], self.args[1])
        self.messages = suche.parsematches(m.matches_fin)
        end = time.time()
        self.elapsed_time = end-start
        self.results = sum((len(x) for x in m.matches_fin))
        self.messages.append('%s Treffer in %.4f s' %
                             (self.results,
                               self.elapsed_time))
        self._finparse = True

    def next(self):
        print('self.done: %s\nself._nextind: %s' % (self.done, self._nextind))
        if len(self.messages) <= 4:
            tmp = [x for x in self.messages]
            self.done = True
        elif len(self.messages)-1 == self._nextind:
            tmp = self.messages[-2:]
            self.done = True
        else:
            tmp = self.messages[self._nextind]
            self._nextind += 1
        return tmp


bot = telepot.DelegatorBot(private.TOKEN_TESTING, [
    pave_event_space()(
        per_chat_id(), create_open, VociBot, timeout=300
    ),
])

MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)
