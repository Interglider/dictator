# -*- coding: utf-8 -*-
"""
Find if dictionary entries already exist on Wiktionary.
If on Wiktionary, find if certain author or bot have edited it.

Created on Wed Aug 26 20:35:18 2015

@author: misha

26.08.2015:
505 entries from 'Recnik sinonima' already on SR Wiktionary
12410 entries not on Wiktionary

10.09.2015:
484 entries from 'Recnik sinonima' already on SR Wiktionary
1 entries not on Wiktionary
13091 pages made by Iglbot

"""
import pywikibot
from sinonimi_reader import *
import pickle, codecs
from collections import OrderedDict

AUTHOR = 'Iglbot'
DATA = 'data/synonyms'

def find_wiki_entries(data, author):   
    site = pywikibot.Site()
    infile = open(data, 'rb')
    for_edit = codecs.open('data/to_editXXX.txt', 'w', encoding = 'utf8')
    syn_dict = pickle.load(infile, fix_imports=True, encoding="ASCII", errors="strict")
    infile.close()
    
    no_page = set([])
    exist = set([])
    remain = set([])
    
    for i, entry in enumerate(syn_dict.keys()):
        fin = (i/float(len(syn_dict.keys()))) * 100.0
        if i % 100 == 0:
            print('Finished %0.2f' % (fin))
        page = pywikibot.Page(site, entry)
        if page.exists():
            if author in page.contributors():
                exist.add(page.title())
            else:
                p = page.title()
                remain.add(p)
                for_edit.write(p + '\n')
        else:
            no_page.add(page.title())
            
    for_edit.close()
    print ("Pages already created by %s " % (author), len(exist)) 
    print ("Following pages are not created yet: ", len(no_page))
    print ("Pages already created by other author/bot:", remain)
    

def main(argv):
    if len(argv) == 3:
        data = argv[1]
        data = argv[2]
    else:
        data = DATA
        author = AUTHOR
    find_wiki_entries(data, author)   
        
if __name__ == "__main__":
    main(argv)