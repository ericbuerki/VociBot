# Enthält alle Strings, die für den Chatbot benötigt werden

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

aborttext = 'Suche abgebrochen'

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

options = ['*weiter*','*abbrechen*']