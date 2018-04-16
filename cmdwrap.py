#!/usr/bin/env python3

import sys
import time

import search

print('Voci-Suche\n\tSuche\tvon Eric Bürki\n\tDaten\tvon Lucius Hartmann')
# print(sys.argv)

start_time = time.time()
matches = search.voci_search(sys.argv[1])
end_time = time.time()

for match in matches:
    print(match[1:])

print('%s Treffer in %.4f s' % (len(matches),
                                (end_time - start_time)))
