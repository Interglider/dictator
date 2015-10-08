# -*- coding: utf-8 -*-
"""
igl_addition

Program to add data from our dataset to existing Wiktionary entries. It adds
meaning of the entry if there is none in the Wiktionary entry and appends
to synonyms and associations fields. It can also ingore certain entries if 
their titles are provided.   

Dependencies (beside common modules):
- pywikibot - to get data from Wiktionary
    https://www.mediawiki.org/wiki/Manual:Pywikibot
- sinonimi_reader and pickle - to read, manage and process our data which we 
want to add to Wiktionary entries.

Created on Tue Sep 15 16:50:53 2015

@author: misha
"""

import pywikibot
import pickle
import re
import itertools
from sinonimi_reader import *

# empty fields as constants, we need them to check if fields are empty
EMP_M = '{{Значење\n:\n}}'
EMP_S = '{{Синоними\n:\n}}'
EMP_A = '{{Асоцијације\n:\n}}'

# Here we can specify entries to ignore
ignore = set(['абдомен', 'абдицирати', 'Сунце'])

def find_element(content, mode):
    """
    Extracts field from the entry, whether it is a meaning field, synonyms 
    or assications field.
    Parameters:
    ----------
        content: String
            Wiktionary entry represented as a single string.
        mode: String
            parameter that determines what element are we looking for.
            'des' - meaning or description of the entry
            'syn' - synonyms
            'asc' - associations
        lookup: string
    """
    mode_dict = {'des':'Значење','syn':'Синоними','asc':'Асоцијације'}
    search = r'{{%s(.*?){{' % (mode_dict[mode])
    res = re.search(search, content, re.DOTALL)
    if res:
        res = res.group(0)[:-2]
    return res    
    
def wiki_format_element(syn_dict, entry, mode, head = True, tail = True):
    """
    This function adds data to a field specified in the parameters. It can
    return the whole filed with opening and closing tags, or without it,
    determined by head and tail booleans. Returns None if there is no data
    to be added. 
    Parameters:
    ----------
        syn_dict: Dictionary
            contains all entries from the parsed dictionary as objects
        entry: String
            name of the entry (key from the dictionary) which is the 
            Wiktionary entry to be added to.
        mode: String 
            element of the entry that we are trying to add.
        head: Boolean
            if True generate entry with starting tags and name of the field.
            Else skip tag and name of the field.
        tail: Boolean
            if True generate entry with ending tags.
            Else skip ending tags.
    """
    content = False
    mode_dict = {'des':'{{Значење|', 'syn':'{{Синоними|', 'asc':'{{Асоцијације|'}
    method_dict = {'des': syn_dict[entry].des.keys(), 'syn':syn_dict[entry].syn.keys(), 'asc': syn_dict[entry].asc.keys()}    
    if len(method_dict[mode]) == 0:
        return None
    if head:
        string = [mode_dict[mode]]
    else:
        string = []
    for k in method_dict[mode]:
        if mode == 'des':
            if syn_dict[entry].get_description(k) != '':
                string.append('\n# ' + syn_dict[entry].get_description(k))
                content = True
            else:
                continue
        elif mode == 'syn':
            if syn_dict[entry].get_synonyms(k) != '':
                string.append('\n# ' + syn_dict[entry].get_synonyms(k))
                content = True
            else:
                continue
        elif mode == 'asc':
            if syn_dict[entry].get_assoc(k) != '':
                string.append('\n# ' + syn_dict[entry].get_assoc(k))
                content = True
            else:
                continue
        string.append('$')
    if content == False:
        return None
    if tail:
        string.append('\n}}\n')
    return string
    
def is_empty(lst):
    """
    Find out if there is any content in the field.
    Takes list of words as an input and determines if any of those start with
    tags. If any of them do, returns False, if none start with tags,
    it returns True.
    """
    for l in lst:
        if re.search('\[\[', l, re.M):
            return False
    return True
    
def compare_words(addition, lst):
    """
    Filter out words that are already in the Wiktionary entry in order
    to get rid of duplicate words.
    Parameters:
    ----------
        addition: List
            data from dictionary to be added
        lst: List
            existing data from the entry field 
    """
    syn_words = [re.findall(r'\[\[[\w\s]+\]\]', x) for x in addition]
    syn_words = list(itertools.chain(*syn_words))
    syn_words = [x for x in syn_words if x != '']
    wiki_words = ''.join(lst)
    for w in syn_words:
        if w in wiki_words:
            for i in range(len(addition)):
                if w in addition[i]:
                    addition[i] = re.sub("\[\[.*\]\]|\'\'\[.*\]\]\'\'", "", addition[i])
    addition = [x + ',' for x in addition if x.strip() != '']
    if addition:
        addition[-1] = addition[-1].replace(',', ' ')
    return addition   
    
def addition_to_el_list(syn_dict, entry, lst, mode):
    """
    Adds new entries to the list representing the entry field. It adds 
    numeration using # format and calls a function that filters out duplicate 
    words from the words to be added. Additions, if there are any, are added
    to the list representing the new, modified field of the entry.
    Parameters:
    -----------
        syn_dict: Dictionary
            contains all entries from the parsed dictionary as objects
        entry: String
            name of the entry (key from the dictionary) which is the 
            Wiktionary entry to be added to.
        lst: List
            list which contains existing entry.
        mode: String 
            element of the entry that we are trying to add.
    """
    for i in range(len(lst)):
        lst[i] = re.sub('\:\[\d\]|\:\'\'\'\[\d\]\'\'\'|\:\*|\'\'\'\[\d\]\'\'\'|\[\d\]','\#', lst[i])
    addition = wiki_format_element(syn_dict, entry, mode, False)
    if addition:
        addition = compare_words(addition, lst)
        if '[[' in ''.join(addition):
            lst.extend(addition)
        else:
            lst.append('\n}}\n')
    return lst
        
def add_meaning(content, entry, syn_dict):
    """
    Adds meaning to the entry if the field is empty.
    """
    meaning = find_element(content, 'des')
    if meaning:
        if meaning.startswith(EMP_M):
            mean_add = wiki_format_element(syn_dict, entry, 'des')
            if mean_add:
                content = content.replace(EMP_M, concat_entry(mean_add))
    else:
        mean_add = wiki_format_element(syn_dict, entry, 'des')
        if mean_add:
            content = content + '\n' + concat_entry(mean_add)
    return content        
        
def add_syns(content, entry, syn_dict):    
    """
    Adds or appends to the synonyms field of the entry.
    """
    synonyms = find_element(content, 'syn')
    if synonyms:
        if synonyms.startswith(EMP_S):
            syn_add = wiki_format_element(syn_dict, entry, 'syn')  
            if syn_add:
                content = content.replace(EMP_S, concat_entry(syn_add))
        else:
            syn_lst = synonyms.splitlines()[:-1]
            if is_empty(syn_lst):
                syn_add = wiki_format_element(syn_dict, entry, 'syn')
            else:
                syn_add = addition_to_el_list(syn_dict, entry, syn_lst, 'syn')
            if syn_add:
                content = content.replace(synonyms, concat_entry(syn_add))                
    else:
        syn_add = wiki_format_element(syn_dict, entry, 'syn')
        if syn_add:
            content = content + '\n' + concat_entry(syn_add)
    return content
    
def add_associations(content, entry, syn_dict):
    """
    Adds or appends to the associations field of the entry.
    """
    assoc = find_element(content, 'asc')
    if assoc:
        if assoc.startswith(EMP_A):
            assoc_add = wiki_format_element(syn_dict, entry, 'asc')
            if assoc_add:
                content = content.replace(EMP_A, concat_entry(assoc_add))
        else:
            asc_list = assoc.splitlines()[:-1]
            if is_empty(asc_list):
                asc_add = wiki_format_element(syn_dict, entry, 'asc')
            else:
                asc_add = addition_to_el_list(syn_dict, entry, asc_list, 'asc')

            if asc_add:
                content = content.replace(assoc, concat_entry(asc_add))
    else:
        asc_list = wiki_format_element(syn_dict, entry, 'asc')
        if asc_list:
            content = content + '\n' + concat_entry(asc_list)
    return content
    
def has_changed(content, old_content):
    """
    Returns True if new content generated is different from the old one, i.e,
    check if we are adding anything to the entry.
    """
    return content == old_content
        
def call_add_funcs(content, entry, syn_dict):
    """
    Calls functions to add or append to the entry fields and checks if we 
    have added anything.
    """
    meaning = False
    synonyms = False
    associations = False
    old_content = content
    content = add_meaning(content, entry, syn_dict)
    if has_changed(content, old_content):
        meaning = True
    content = add_syns(content, entry, syn_dict)
    if has_changed(content, old_content):
        synonyms = True
    content = add_associations(content, entry, syn_dict)
    if has_changed(content, old_content):
        associations = True
    return content, meaning, synonyms, associations     
        
def prepare_str_for_file(content, title, mean, syn, asc):  
    """
    Prepares entry string to be uploaded to Wiktionary (in overwrite mode).
    It checks if there is title in the string because Pywikibot won't allow
    saving the entry that has no title.
    It also cleans formatting or adjusts it to our own.
    Returns string ready to be uploaded to Wiktionary.
    """
    if re.search("\'\'\'[A-Za-z]+\'\'\'", content):
        title = "'''%s'''\n" % (title) 
        content = title + content
    if asc or syn or mean:
        content = re.sub(':::', '', content, re.M)
        content = re.sub('Значење\|#', r'Значење|\n#', content, re.M)
        content = re.sub('Синоними\|#', r'Синоними|\n#', content, re.M)
        content = re.sub('Асоцијације\|#', r'Асоцијације|\n#', content, re.M)
        content = re.sub('\]#', r']\n#', content, re.M)
        content = re.sub('\.#', r'.\n#', content, re.M)
        content = re.sub('\}\}#', '|\n#', content, re.M)
    content = '{{-start-}}\n' + content + '\n{{-stop-}}\n\n\n'
    return content 

"""
We can, if we prefer, get the list of entries to be ignored from the file,
instead of using a set of entries.
"""
if os.path.isfile('data/added.txt'):  
    ignore = open('data/added.txt', 'r+').read().splitlines()
print(ignore)
       
"""
Read from the list of entries to be appended to. Remove unwanted ones and sort
the final version of the list.
"""
append_to = open('data/to_edit 14092015.txt', 'r').read().splitlines()
#append_to = [x for x in append_to if x not in ignore]
append_to.sort()

"""
Open files where modified entries will be written to and open dictionary data
stored using Pickle. Load data into Python's dictionary.
"""
additions = open('data/additions3.txt', 'w')
infile = open('data/synonyms', 'rb')
syn_dict = pickle.load(infile, fix_imports=True, encoding="ASCII", errors="strict")

"""
These lists are for used for tracking status of the entries and pages.
Lists - stores entries that we have as a list of objects and not just a single
object as is most often the case (that is the case when we have a entry as word
which is in multiple word types).
Redirect - if page is redirect we cannot edit it and we want to know about
that, so we keep these entries in a separate set.
Modified - set of entries that were modified (but not yet uploaded!) to 
Wiktionary. 
"""
lists = []
redirect = set([])
modified = set([])
site = pywikibot.Site()

"""
Loop through all the entries that need to be appended to.
We skip lists of objects because such entries require different approach. 
"""
for i, entry in enumerate(append_to):
    page = pywikibot.Page(site, entry)
    if page.isRedirectPage():
        redirect.add(page.title())
        continue
    if isinstance(syn_dict[entry], list):
        lists.append(entry)      
        continue
    # nice to have some feedback what the program is doing 
    print(page.title())
    content = page.get()
    original_content = content
    content, mean, syn, asc = call_add_funcs(content, entry, syn_dict)
    """
    If original content is changed we will write it to a file, ready to be
    uploaded to Wiktionary.
    """
    if content != original_content:
        modified.add(page.title())
        content = prepare_str_for_file(content, page.title(), mean, syn, asc)
        additions.write(content)
# We can break the loop early if we are only testing.
    if i == 12:
        break

"""
Here we can write entries which consist of multiple objects. We are writing
them to a file as if there is no existing entry on Wiktionary. 
To do for a future is to make functions which will enable automatic 
generation of such entries, but as they are not that frequent, on this
occasion I added them by hand. 
"""
print(lists, sorted(modified))
print ([x for x in modified if x not in append_to])
for multientry in lists:
    for e in range(len(syn_dict[multientry])):
        content = []
        if e == 0:
            content.extend(syn_dict[multientry][e].to_wiki(True, False))
        elif e == (len(multientry) - 1):
            content.extend(syn_dict[multientry][e].to_wiki(False, True))
        else:
            content.extend(syn_dict[multientry][e].to_wiki())
                
        content = concat_entry(content)
        additions.write(content)
        
additions.close()
infile.close()
