# Enthält alle Strings, die für den Chatbot benötigt werden

helptext = "Schicke deine Suchanfrage dem VociBot als Nachricht und " \
           "erhalte sogleich Antwort.\n" \
           "*Benutzung:*\n" \
           "  'suche' 'parameter' _(ohne Anführungszeichen)_\n" \
           "*Beispiel:*\n" \
           "  vox lat\n" \
           "  König ger\n" \
           "  caesar all\n" \
           "  timere\n" \
           "_(ohne Parameter wird 'all' angenommen)_"

aborttext = 'Suche abgebrochen'

infotext = '*VociBot* 📖\n' \
           'Lateinvokabelsuche von Eric Bürki\n' \
           'Erstellt mit der unwissentlichen ' \
           'Unterstützung von ' \
           '[Lucius Hartmann](http://www.lucius-hartmann.ch/).'

fb_text = 'Äussern Sie Ihr Feedback hier.\nFügen Sie bitte Ihre ' \
          'e-Mail-Adresse hinzu, damit der Entwickler ' \
          'Sie kontaktieren kann.\n' \
          '_"abbrechen"_ bricht den Vorgang ab.'

fb_success = 'Feedback erfolgreich gesendet.\nVielen Dank!'

fb_error = '*🚨 Fehler 🚨:* Feedback konnte nicht gesendet werden. ' \
           'Kontaktiere bitte den Entwickler unter ericbuerki@gmail.com'

fb_abort = 'Feedback abgebrochen'

tl_warning = '*🚧 Warnung 🚧:* Suche zu unscharf. Eventuell werden nicht alle ' \
             'Suchergebnisse angezeigt. Bitte verfeinere deine Suche.\n' \
             '_(%s Ergebnisse in %s Nachrichten)_'

lm_warning = '*🚨 Fehler 🚨:* Nachricht ist länger als 4096 Zeichen und kann ' \
             'nicht gesendet werden. Benachrichtigen Sie bitte den Entwickler.'

unknown_warning = '🚧 Unbekanntes Kommando \'%s\'\n' \
                  '/info gibt dir weitere Infos,\n' \
                  '/help zeigt dir, wie die Suche funktioniert,\n' \
                  'Feedback kann mit /feedback angebracht werden.'
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

options = ['*weiter*', '*abbrechen*']
