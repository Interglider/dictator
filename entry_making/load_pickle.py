# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 02:38:44 2015

@author: misha

PRIMER KAKO IZVLACITI ODREDNICE IZ PICKLE-A
"""

import pywikibot
import pickle
from sinonimi_reader import *

ignore = set(['импресиван', 'мезетити', 'навала', 'хеј', 'да', 'а', 'врло'])
exist = set([])

def main(*argv):
    infile = open('data/synonyms', 'rb')
    out = open('data/to_wikiX.txt', 'w')
    site = pywikibot.Site()
    syn_dict = pickle.load(infile, fix_imports=True, encoding="ASCII", errors="strict")
    if len(argv) == 1:    
        synonyms = syn_dict.keys()
    else:
        synonyms = [x for x in syn_dict.keys() if x in argv]
    for i, title in enumerate(synonyms):
        fin = i/float(len(synonyms))
        if i % 100 == 0:
            print('Finished %0.4f' % (fin))
        if title not in ignore:
            page = pywikibot.Page(site, title)
            if page.exists() and 'Iglbot' not in page.contributors():
                exist.add(title)
            else:
                out.write('\n{{-start-}}\n')
                out.write('\'\'\'%s\'\'\'\n' % (title))
                if isinstance(syn_dict[title], list):
                    string = []
                    for i, e in enumerate(syn_dict[title]):
                        if i == 0:
                            string.extend(e.to_wiki(True, False))
                        elif i == (len(syn_dict[title]) - 1):
                            string.extend(e.to_wiki(False, True))
                        else:
                            string.extend(e.to_wiki())
                    
                    string = concat_entry(string)
                    string = string.replace("]]  ","]] ")
                    out.write(string)
                elif isinstance(syn_dict[title], object):
                    string = concat_entry(syn_dict[title].to_wiki(True, True))
                    string = string.replace("]]  ","]] ")
                    out.write(string)
                out.write('\n{{-stop-}}\n')
    out.close()
    out_ex = open('existing.txt', 'w')
    for e in list(exist):
        out_ex.write(e + '\n')
    out_ex.close()

if __name__ == "__main__":
    main(*argv)