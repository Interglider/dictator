# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 20:39:01 2015

As the name says - get all Wiktionary entries in Serbian
and save them to a JSON file

requires pywikibot installed and configured

@author: misha
"""

import pywikibot
import json, re, json
from collections import OrderedDict

def get_pages():
    site = pywikibot.Site()
    pages = site.allpages()
    if site.sitename() == 'wiktionary:sr':
        found_entries = {}
        for i, p in enumerate(pages):
            if i % 100 == 0:
                print(i)
            if not p.isRedirectPage(): 
                found_entries[p.title()] = p.get()
    #    to get page url
    #    print(p.full_url())
        outfile = open('wiktionary_sr_entries.json', 'w')
        json.dump(found_entries, outfile, ensure_ascii=False, indent=4, separators=(',', ': '))

def main():
    get_pages()

if __name__ == "__main__":
    main()