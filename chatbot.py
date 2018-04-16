import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space

import urllib3

import suche


with open('key.txt') as f:
    TOKEN = f.read().replace('\n', '')

s = suche.Searcher()

helptext = "Schicken Sie Ihre Suchanfrage dem VociBot als Nachricht und " \
           "erhalten Sie sogleich Antwort.\n" \
           "*Benutzung:*\n" \
           "  'suche' 'parameter' _(ohne Anführungszeichen)_\n" \
           "*Beispiel:*\n" \
           "  vox lat\n" \
           "  König ger\n" \
           "  caesar all\n" \
           "  timere\n" \
           "_(ohne Parameter wird 'all' angenommen)_"

infotext = '*VociBot* 📖 Lateinvokabelsuche\n' \
           'von Eric Bürki\n_Erstellt mit der unwissentlichen ' \
           'Unterstützung von Lucius Hartmann._'

tl_warning = '*🚧 Warnung 🚧:* Suche zu unscharf. Eventuell werden nicht alle ' \
             'Suchergebnisse angezeigt. Bitte verfeinern Sie ihre Suche.\n' \
             '_(%s Ergebnisse in %s Nachrichten)_'

lm_warning = '*🚨 Fehler 🚨:* Nachricht ist länger als 4096 Zeichen und kann ' \
             'nicht gesendet werden. Benachrichtigen Sie bitte den Entwickler.'

unknown_warning = '🚧 Unbekanntes Kommando \'%s\'\n' \
                  'Verwenden Sie /help oder /info für weitere Informationen.'
'''
tm_error = '*🚨 Fehler 🚨:* Bot wurde wegen Überlastung der Telegram-Server ' \
           'pausiert. Warten Sie noch %s s und versuchen Sie dann, ihre ' \
           'Suche enger einzugrenzen.'
'''
tm_error = '*🚨 Fehler 🚨:* Die Verbindung zu den Telegram-Servern wurde ' \
           'abgebrochen, da zu viele Nachrichten aufs Mal gesendet wurden.\n' \
           'Bitte warten Sie %s m %s s und versuchen Sie anschliessend, ' \
           'ihre Suche zu verfeinern.'

ready_again = '*VociBot* kann wieder benutzt werden.\n' \
              'Vielen Dank fürs Warten.'

rtm_error = '*🚨 Fehler 🚨:* Zeitüberschreitung beim Lesen.\n' \
            'Wiederholen Sie ihre Anfrage in %s s. Ich bitte vielmals um ' \
            'Entschuldigung.'


class VociBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(VociBot, self).__init__(*args, **kwargs)
        self._count = 0

    '''
    def on_chat_message(self, msg):
        #print(msg)

        content_type, chat_type, chat_id = telepot.glance(msg)

        print('content_type:  %s' % content_type)
        print('chat_type:  %s' % chat_type)
        print('chat_id:  %s' % chat_id)

        self._count += 1
        self.sender.sendMessage('Hallo zum %s. Mal' % self._count)
    

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('content_type:  %s' % content_type)
        print('chat_type:  %s' % chat_type)
        print('chat_id:  %s' % chat_id)
        print('text:  %s' % msg['text'])

        if content_type == 'text':
            print(type(msg['text']))
            query_raw = msg['text'].split(' ')
            print(query_raw)
            start = time.time()
            s.search(query_raw[0], query_raw[1])
            m = suche.Matches(s.matches, query_raw[1], query_raw[0])
            m.dedup()
            self.sender.sendMessage('*Antworten*', parse_mode='Markdown')
            matches_tot = 0
            for match_type in m.matches_fin:
                self.sender.sendMessage(str(match_type))
                matches_tot += len(match_type)
            self.sender.sendMessage('%s Treffer in %.4f s' %(matches_tot,
                                                             time.time()-start))
    '''

    '''
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('content_type:  %s' % content_type)
        print('chat_type:  %s' % chat_type)
        print('chat_id:  %s' % chat_id)

        if content_type == 'text':
            print('text:  %s' % msg['text'])
            args_raw = msg['text'].split(' ')
            _args = [x.lower() for x in args_raw]
            if len(_args) == 1:
                _args.append('all')
            print(_args)
            start = time.time()
            s.search(_args[0], _args[1])
            m = suche.Matches(s.matches, _args[0], _args[1])
            p_list = suche.parsematches(m.matches_fin)
            end = time.time()
            print('Anzahl Nachrichten: %s' % len(p_list))
            for m_type in p_list:
                self.sender.sendMessage(m_type, parse_mode='Markdown')
                time.sleep(1)
            match_tot = sum([len(x) for x in m.matches_fin])
            self.sender.sendMessage('%s Treffer in %.4f s' % (match_tot,
                                                              end-start))
    '''

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('content_type:  %s' % content_type)
        print('chat_type:  %s' % chat_type)
        print('chat_id:  %s' % chat_id)

        if content_type == 'text':
            try:
                self.queryhandler(msg['text'])
            except telepot.exception.TooManyRequestsError as err:
                print('Err: Nachricht zu lang.')
                print(err.args)
                retry_after = err.args[2]['parameters']['retry_after']
                #time.sleep(retry_after/2)
                time.sleep(10)
                self.sender.sendMessage(tm_error % (retry_after // 60,
                                                    retry_after % 60),
                                        parse_mode='Markdown')
                time.sleep(retry_after)
                self.sender.sendMessage(ready_again,
                                        parse_mode='Markdown')
            except urllib3.exceptions.ReadTimeoutError as err:
                print('Err: Zeitüberschreitung beim Lesen')
                print(err.args)
                time.sleep(10)
                tm = 30
                self.sender.sendMessage(rtm_error % tm,
                                        parse_mode='Markdown')
                time.sleep(tm)
                self.sender.sendMessage(ready_again,
                                        parse_mode='Markdown')

    def queryhandler(self, msgtext):
        print('Text: %s' % msgtext)
        if '/help' in msgtext:
            self.sender.sendMessage(helptext, parse_mode='Markdown')
        elif '/info' in msgtext:
            self.sender.sendMessage(infotext, parse_mode='Markdown')
        elif len(msgtext.split(' ')) <= 2:
            args = msgtext.split(' ')
            args = [x.lower() for x in args]
            if len(args) == 1:
                args.append('all')
            print(args)

            start = time.time()
            s.search(args[0], args[1])
            m = suche.Matches(s.matches, args[0], args[1])
            p_list = suche.parsematches(m.matches_fin)
            end = time.time()
            anz_matches = sum([len(x) for x in m.matches_fin])
            print('%s Matches in %.4f s' % (anz_matches,
                                            end-start))
            print('%s Nachrichten' % len(p_list))
            if len(p_list) > 15:
                self.sender.sendMessage(tl_warning % (anz_matches,
                                                      len(p_list)),
                                        parse_mode='Markdown')
                time.sleep(10)
            for message in p_list:
                if len(message) > 4096:
                    self.sender.sendMessage(lm_warning,
                                            parse_mode='Markdown')
                self.sender.sendMessage(message, parse_mode='Markdown')
                if len(p_list) > 20:
                    print('p_list: %s > 20' % len(p_list))
                    time.sleep(3)
                else:
                    print('p_list: %s < 20' % len(p_list))
                    #time.sleep(0.2)

            self.sender.sendMessage('%s Treffer in %.4f s' % (anz_matches,
                                                              end-start))
        else:
            self.sender.sendMessage(unknown_warning % msgtext,
                                    parse_mode='Markdown')




bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, VociBot, timeout=600
    ),
])

MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)

##  TODO
#   Handler-Klasse implementieren, die Zunächst nur den ersten Eintrag
#   zeigt.