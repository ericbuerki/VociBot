#!/usr/bin/env python3

import sys
import time
import csv

from unidecode import unidecode
import pyexcel

import pprint

csvpath = 'data/voci_escapd.csv'


class Searcher(object):
    def __init__(self):

        # Lese Voci-Tabelle ein
        with open(csvpath) as f:
            reader = csv.reader(f)
            self.voci_list = list(reader)

        # Suchstring (bleibt bis zur nächsten Suche)
        self._query = ''

        # Treffer (Zeilen in self.voci_list)
        self.match_ind = []

        # Treffer
        self.matches = []

    def search(self, query, mod):
        # query:    Suchstring
        self._query = query
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
                    if unidecode(self._query) in unidecode(self.voci_list[i][j])\
                            .lower():
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
        self._matches_raw = matches

        # Liste mit Treffern, sortiert
        self._matches_list = []

        # Liste mit 2 Dicts,
        self.matches_fin = []

        # Suchstring
        self._query = query
        self._mod = mod

        self._columns = {'lat': [1, 2, 3, 4, 13],
                         'ger': [7, 9],
                         'all': [1, 2, 3, 4, 7, 9, 13]}
        '''
        # Art der Suche
        if mod == 'lat':
            print('%s == \'lat\'' % mod)
            self.gc = [1, 2, 3, 4, 13]
        elif mod == 'ger':
            print('%s == \'ger\'' % mod)
            self.gc = [7, 9]
        else:
            print('%s == \'all\'' % mod)
            self.gc = [1, 2, 3, 4, 7, 9, 13]
        '''

        self._matches_a = []    # Exakte Treffer
        self._matches_b = []    # Treffer (Anfang/Ende von Wort)
        self._matches_c = []    # Weniger Exakte Treffer (in Wort)

        self._matches = {'exact': [],               # Exakter Treffer
                         'in_expression': [],       # Wort (exakt) in Ausdruck
                         'startsends': [],          # beginnt/endet mit Query
                         'startsends_inexpr': [],   # wie oben, nur in Ausdruck
                         'unsharp': []}             # Wort in Ausdruck

        self.order()
        self.dedup()

    def order(self):
        '''
        for entry in self._matches_raw:
            matched = False
            splittable = False
            matched_dict = {}

            for j in self._columns[self._mod]:
                if not matched:

                    if ',' in entry[j] or ' ' in entry[j]:

                        if ',' in entry[j]:
                            subentries = entry[j].split(', ')
                        else:
                            subentries = entry[j].split(' ')

                        matched_a = False
                        matched_b = False

                        for subentry in subentries:
                            if unidecode(subentry).lower() == unidecode(self._query):
                                matched_a = True
                            elif unidecode(subentry).lower() \
                                    .startswith(unidecode(self._query)) or \
                                    unidecode(subentry).lower() \
                                    .endswith(unidecode(self._query)):
                                matched_b = True

                        if matched_a:
                            self._matches['in_expression'].append(entry)
                        elif matched_b:
                            self._matches['startsends'].append(entry)
                        else:
                            self._matches['unsharp'].append(entry)

                    else:
                        if self.transform(entry[j], j) == self._query:
                            self._matches['exact'].append(entry)
                            break
                        elif self.transform(entry[j], j) \
                                .startswith(self._query) or \
                                self.transform(entry[j], j) \
                                .endswith(self._query):
                            self._matches['startsends'].append(entry)
                        else:
                            self._matches['unsharp'].append(entry)
        '''
        
        for entry in self._matches_raw:
            matched = {'exact': False,
                       'in_expression': False,
                       'startsends': False,
                       'startsends_inexpr': False,
                       'unsharp': False}

            for j in self._columns[self._mod]:
                if not matched['exact']:
                    if ',' in entry[j] or ' ' in entry[j]:
                        if ',' in entry[j]:
                            subentries = entry[j].split(', ')
                        else:
                            subentries = entry[j].split(' ')

                        for subentry in subentries:
                            if self.transform(subentry, j) == self._query:
                                matched['in_expression'] = True
                            elif self.transform(subentry, j) \
                                    .startswith(self._query) or \
                                    self.transform(subentry, j) \
                                    .endswith(self._query):
                                matched['startsends_inexpr'] = True
                            else:
                                matched['unsharp'] = True
                else:
                    if self.transform(entry[j], j) == self._query:
                        matched['exact'] = True
                    elif self.transform(entry[j], j) \
                            .startswith(self._query) or \
                            self.transform(entry[j], j) \
                            .endswith(self._query):
                        matched['startsends'] = True
                    else:
                        matched['unsharp'] = True



            matched_tot = False     # Ob schon einem Dict zugewiesen
            for key, value in matched.items():
                if not matched_tot and value:
                    self._matches[key].append(entry)
                    matched_tot = True





        # for i in (x for x in ind if x not in taken):
        #    matches_c.append(self._matches_raw[i])

        pprint.pprint(self._matches)
        self._matches_list = [x for _, x in self._matches.items()]
        # print(matches_a)

    '''
    def _check_field(self, entry, j, subentry=None):
        if not subentry:
            field = entry[j]
        else:
            field = subentry

        if unidecode(field).lower() == unidecode(self._query):
            self._matches_a.append(entry)
        elif unidecode(field).lower() \
                .startswith(unidecode(self._query)) or \
                unidecode(field).lower() \
                .endswith(unidecode(self._query)):
            self._matches_b.append(entry)
        else:
            self._matches_c.append(entry)
    '''

    def transform(self, field, j):
        if j in self._columns['lat']:
            return unidecode(field).lower()
        elif j in self._columns['ger']:
            return field.lower()
        else:
            raise ValueError('%s nicht in self._colums (%s)' % (j,
                                                                self._columns))

    def dedup(self):

        fin_temp = []

        for matches in self._matches_list:

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

                for a, mm_temp in enumerate(zip(*temp)):
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
                if (len(str_temp) - lastlen) > 1500:
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
        # parsedstr += '--  '
        parsedstr += '-  '
        ptemp = '%s _(%s)_' % (bedeutung[0],
                               ', '.join([x for x in bedeutung[1]]))
        parsedstr += ptemp
        parsedstr += '\n'
    for beispiel in match['ger'][1]:
        if beispiel != '':
            parsedstr += '_%s_\n' % beispiel
    parsedstr += '\n'
    # parsedstr += ('-'*10+'\n')

    return parsedstr


if __name__ == '__main__':

    mod = 'all'
    query = 'gott'

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
    '''
    # print('Anzahl Nachrichten: %s' % len(ltemp))
    print('Anzahl Zeichen')
    print(ltemp)
    # print('Durchschnit:\t%.2f' % (sum(ltemp)/len(ltemp)))
    print('Maximum:\t%s\nMinimum:\t%s' % (max(ltemp), min(ltemp)))
    toomuch = [x for x in ltemp if x>4000]
    print('%s Nachrichten zu gross:' % len(toomuch))
    print(toomuch)
    '''
    print('m.matches_fin')
    pprint.pprint(m.matches_fin)
