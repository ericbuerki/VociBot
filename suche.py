#!/usr/bin/env python3

import sys
import time
import csv

from unidecode import unidecode
import pyexcel

csvpath = 'processed/voci_escapd.csv'


class Searcher(object):
    def __init__(self):

        # Lese Voci-Tabelle ein
        with open(csvpath) as f:
            reader = csv.reader(f)
            self.voci_list = list(reader)

        # Suchstring (bleibt bis zur nächsten Suche)
        self.query = ''

        # Treffer (Zeilen in self.voci_list)
        self.match_ind = []

        # Treffer
        self.matches = []

    def search(self, query, mod):
        # query:    Suchstring
        self.query = query
        # mod:      'lat':  Lateinisch
        #           'ger':  Deutsch
        #           'all':  Alles

        print('query:\t%s' % query)
        print('mod:\t%s' % mod)

        if mod == 'lat':
            good_columns = [1, 2, 3, 4, 13]
        elif mod == 'ger':
            good_columns = [7, 9]
        # if mod == 'all':
        else:
            print('all')
            good_columns = [1, 2, 3, 4, 7, 9, 13]

        match_ind = []
        matches = []

        # matches_a = []

        start = time.time()

        for i in range(len(self.voci_list)):
            matched = False
            for j in good_columns:
                if not matched:
                    if unidecode(self.query) in unidecode(self.voci_list[i][j]).lower():
                        match_ind.append([i, j])
                        matches.append(self.voci_list[i])
                        matched = True

        print('%s Treffer in %.4f Sekunden' % (len(matches),
                                               time.time() - start))

        self.matches = matches
        self.save()

    def save(self):
        pyexcel.save_as(array=self.matches,
                        dest_file_name='matches.csv')


class Matches(object):
    def __init__(self, matches, query, mod):
        # Liste mit Treffern
        self.matches_raw = matches

        # Liste mit Treffern, sortiert
        self.matches_list = []

        # Liste mit 2 Dicts,
        self.matches_fin = []

        # Typ des Objekt
        #self.typ = typ

        # Suchstring
        self.query = query

        # Art der Suche

        if mod == 'lat':
            print('%s == \'lat\'' % mod)
            self.gc = [1, 2, 3, 4, 13]
        elif mod == 'ger':
            print('%s == \'ger\'' % mod)
            self.gc = [7, 9]
        #if mod == 'all':
        else:
            print('%s == \'all\'' % mod)
            self.gc = [1, 2, 3, 4, 7, 9, 13]

        self.order()
        self.dedup()

    def order(self):

        # Treffer mit ganz viel Scharf
        matches_top = []

        # Treffer (scharf)
        matches = []

        # Treffer (unscharf)
        matches_alt = []
        taken = []

        ind = list(range(len(self.matches_raw)))
        for i in ind:
            matched = False
            for j in self.gc:
                if not matched:
                    if unidecode(self.matches_raw[i][j]).lower() \
                            .startswith(unidecode(self.query)) or \
                            unidecode(self.matches_raw[i][j]).lower() \
                            .endswith(unidecode(self.query)):
                        if unidecode(self.matches_raw[i][j]).lower() == \
                                unidecode(self.query):
                            matches_top.append(self.matches_raw[i])
                        else:
                            matches.append(self.matches_raw[i])
                        taken.append(i)
                        matched = True

        good_ind = [x for x in ind if x not in taken]
        for i in good_ind:
            matches_alt.append(self.matches_raw[i])

        self.matches_list = [matches_top,
                             matches,
                             matches_alt]
        # print(matches_top)

    def dedup(self):

        fin_temp = []

        for matches in self.matches_list:

            m_temp = []

            defs = []
            for match in matches:
                defs.append(match[1])

            defset = list(set(defs))
            defset.sort()

            for defn in defset:

                d_temp = {'lat': [], 'ger': [],
                          'div': [], 'l': [],
                          'typ': ''}

                # lat:  inf /   N sg  / m,
                #       präs /  GenSg / f,
                #       perf /  genus / n,
                #       ppp

                # ger:  Bedeutung, ähnliche Wörter

                # div:  Ergänzungen

                # l:    Lektionen

                temp = []
                for match in matches:

                    if match[1] == defn:
                        temp.append(match)

                # Treffer, nach Zeile aufgeteilt
                # m_bc = list(zip(*temp))
                merkmale = []
                a = 0

                for mm_temp in zip(*temp):
                    if a is not 7:
                        merkmale.append(list(set(mm_temp)))
                    else:
                        inputtemp = []
                        for dt in set(mm_temp):
                            l_temp = []
                            for item in temp:
                                if dt == item[7]:
                                    l_temp.append(item[12])
                            inputtemp.append([dt, l_temp])

                        merkmale.append(inputtemp)

                    a += 1

                d_temp['l'].append(merkmale[12])
                d_temp['ger'].append(merkmale[7])
                d_temp['ger'].append(merkmale[9])
                d_temp['typ'] = merkmale[6][0]
                d_temp['div'].append(merkmale[5][0])

                if not isinstance(merkmale[6][0], str):
                    print(mm_temp)
                    raise ValueError

                if merkmale[6][0] == 'v':
                    # d_temp['lat'] = merkmale[1:5]
                    d_temp['lat'] = [x for x in list(zip(*merkmale[1:5]))[0]]
                    # d_temp['div'].append(merkmale[5])

                elif merkmale[6][0] == 's':
                    # d_temp['lat'] = merkmale[1:4]
                    d_temp['lat'] = [x for x in list(zip(*merkmale[1:4]))[0]]
                    # d_temp['div'].append(merkmale[5])

                # elif merkmale[6][0] == 'a' or merkmale[6][0] == 'pa':
                elif merkmale[6][0] in ['a', 'pa']:
                    # tmp = merkmale[1:3]+merkmale[13]
                    tmp = [merkmale[1][0],
                           merkmale[2][0],
                           merkmale[13][0]]

                    d_temp['lat'] = tmp
                    # d_temp['div'].append(merkmale[5])

                elif merkmale[6][0] in ['x', 'pr', 'p']:
                    d_temp['lat'] = merkmale[1]

                elif merkmale[6][0] == 'pa':
                    pass

                else:
                    d_temp['lat'].append(merkmale[1])
                    # d_temp['div'].append(merkmale[5])

                m_temp.append(d_temp)

            # print('m_temp')
            # print(m_temp)

            fin_temp.append(m_temp)

        self.matches_fin = fin_temp

'''
def parsematches(data):
    # data = [[{},{}, ...],
    #         [{},{}, ...],
    #         [{},{}, ...]]
    parseddata = []
    for subset in data:
        if not subset:
            continue
        else:
            str_temp = ''
            lentemp = []
            for _entry in subset:
                str_temp += parsedict(_entry)
                lentemp.append(len(str_temp))
        if max(lentemp) > 4000:         # Maximum 4096
            bool_temp = []
            for _len in lentemp:
                bool_temp.append(_len>4000)
            good_ind = lentemp[bool_temp.index(True)-1]
            parseddata.append(str_temp[:good_ind]+'\n(...)\n')
            parseddata.append('(...)\n\n'+str_temp[good_ind:])
        else:
            parseddata.append(str_temp)
        print(lentemp)

    return parseddata
'''

def parsematches(data):
    # data = [[{},{}, ...],
    #         [{},{}, ...],
    #         [{},{}, ...]]
    parseddata = []
    for subset in data:
        if not subset:
            continue
        else:
            str_temp = ''
            lentemp = []
            lastlen = 0
            splitted = False
            for _entry in subset:
                str_temp += parsedict(_entry)
                if (len(str_temp) - lastlen) > 3700:
                    splitted = True
                    parseddata.append(str_temp[lastlen:]+'\n(…)\n')
                    lastlen = len(str_temp)
                    lentemp.append(len(str_temp))
            if not splitted:
                parseddata.append(str_temp)
            if splitted:
                parseddata[-1] = parseddata[-1][:-5]
        # print(lentemp)

    return parseddata

def parsedict(match):
    # print('parsedict(match):')
    # print(match)
    parsedstr = ''
    '''
    if match['typ'] == 'v':                     # Verb
        i = 0
        for stammform in match['lat']:
            if i == 0:
                parsedstr += '*%s*' % stammform
            elif stammform != '':
                parsedstr += ', %s' % stammform
            i += 1
        parsedstr += '\n'

    elif match['typ'] == 's':                   # Substantiv
        i = 0
        for stammform in match['lat']:
            if i == 0:
                parsedstr += '*%s*' % stammform
            elif stammform != '':
                parsedstr += ', %s' % stammform
            i += 1
        parsedstr += '\n'

    elif match['typ'] == 'a':
        i = 0
        for stammform in match['lat']:
            if i == 0:
                parsedstr += '*%s*' % stammform
            elif stammform != '':
                parsedstr += ', %s' % stammform
            i += 1
        parsedstr += '\n'

    elif match['typ'] == 'x':
        pass
    '''
    i = 0
    for stammform in match['lat']:
        if i == 0:
            parsedstr += '*%s*' % stammform
        elif stammform != '':
            parsedstr += ', %s' % stammform
        i += 1
    parsedstr += '\n'

    for hilfe in match['div']:
        if hilfe != '':
            parsedstr += '_%s_ ' % hilfe
            parsedstr += '\n'

    for bedeutung in match['ger'][0]:
        parsedstr += '--  '
        ptemp = '%s _(%s)_' % (bedeutung[0],
                               ', '.join([x for x in bedeutung[1]]))
        parsedstr += ptemp
        parsedstr += '\n'
    for beispiel in match['ger'][1]:
        if beispiel != '':
            parsedstr += '_%s_\n' % beispiel
    # parsedstr += '\n'
    parsedstr += ('-'*10+'\n')

    return parsedstr


if __name__ == '__main__':

    mod = 'all'
    query = 'a'

    if len(sys.argv) > 1:
        mod = sys.argv[2]
        query = sys.argv[1]

    s = Searcher()
    start = time.time()
    s.search(query, mod)

    m = Matches(s.matches, query, mod)
    # m.dedup()
    end = time.time()

    '''
    for mf in m.matches_fin:
        for entry in mf:
            print(entry)
        print('='*25)
    '''

    print('Dauer: %.4f Sekunden' % (end-start))

    start1 = time.time()
    p_list = parsematches(m.matches_fin)
    end1 = time.time()

    ltemp = []
    for match in p_list:
        # print(match)
        ltemp.append(len(match))
        # print('Länge: %s' % len(match))
        # print('#'*15)

    print('%s Nachrichten generiert in %.4f s' % (len(ltemp),
                                                  end1-start1))
    # print('Anzahl Nachrichten: %s' % len(ltemp))
    print('Anzahl Zeichen')
    print(ltemp)
    print('Durchschnit:\t%.2f' % (sum(ltemp)/len(ltemp)))
    print('Maximum:\t%s\nMinimum:\t%s' % (max(ltemp), min(ltemp)))
    toomuch = [x for x in ltemp if x>4000]
    print('%s Nachrichten zu gross:' % len(toomuch))
    print(toomuch)
