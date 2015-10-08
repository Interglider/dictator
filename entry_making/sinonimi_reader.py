# -*- coding: utf-8 -*-
"""
SINONIMI JSON convert to wiki format

Created on Tue Aug 11 17:16:06 2015

@author: misha
"""

import json, re, os, pickle, codecs
from sys import argv
from sr_lat2cyr2lat import transliterate
from collections import OrderedDict, Counter

SHORT = 'out/sinonimi_cyr_short.json'
FULL = 'out/sinonimi_cyr.json'

TAGS = {'narrow meaning':'суж.', 'regional':'рег.', 'similar meaning':'сл.', 'eufemizam':'еуф.',
        'familiarly':'фам.', 'expression':'изр.', 'rare':'рет.', 'archaic':'арх.', 'figurative':'фиг.',
        'popularly':'нар.', 'jargon':'жарг.'}
            
TYPES = {'ž': 'Именица', 'm': 'Именица', 'prid.': 'Придев', 's': 'Именица',
         'svrš. prel.': 'Глагол', 'nesvrš. prel.': 'Глагол', 
         'nesvrš. neprel.': 'Глагол', 'pril.': 'Прилог', 'nesvrš.': 'Глагол', 
         'svrš.': 'Глагол', 'svrš. neprel.': 'Глагол', 'm ž': 'Именица',
         'ž mn.': 'Именица', 'nesvrš. neprel. prel.': 'Глагол',
         'uzv.': 'Узвик', 'vzn.': 'Везник', 'm mn.': 'Именица',
         'pred.': 'Предлог', 'svrš. nesvrš. prel.': 'Глагол', 
         'svrš. neprel. prel.': '', 'm i ž': 'Именица', 'rčc.': 'Речца',
         'prid. neprom.': 'Придев', 'm s': 'Именица', 's mn.': 'Именица',
         'svrš. nesvrš.': 'Глагол', 'svrš. prel. neprel.': 'Глагол', 
         's ž': 'Именица', 'svrš. bezl.': 'Глагол', 
         'svrš. nesvrš. neprel. prel.': 'Глагол',
         'nesvrš. prel. neprel.': 'Глагол', 'nesvrš. bezl.': 'Глагол',
         'svrš. prel. i neprel.': 'Глагол', 'nesvrš. svrš. neprel.': 'Глагол',
         'svrš. prel. prel.': 'Глагол', 'zam.': 'Заменица', 'm i s': 'Именица',
         'nesvrš. neprel. i neprel.': 'Глагол', 'ž s': 'Именица', 'vezn.': 'Везник', 
         'nesvrš. i svrš. prel.': 'Глагол',  'nesvrš. neprel. i prel.': 'Глагол',
         'pril. neprom.': 'Прилог', 'svrš. neprel. neprel.': 'Глагол',
         'svrš. i nesvrš. neprel.': 'Глагол',
         'nesvrš. neprel. neprel. prel.': 'Глагол', 
         'svrš. i nesvrš. neprel': 'Глагол', 
         'nesvrš. i svrš. neprel. i prel.': 'Глагол', 
         'nesvrš. prel. i neprel': 'Глагол', 'nesvrš. prel. i neprel.': 'Глагол',
         'nesvrš. svrš. prel.': 'Глагол', 'ž i m': 'Именица'}
         
LINKS = {"фам." : " ''[[Викиречник:Фамилијарне речи|фам.]]''",
        "непром." : " ''[[Викиречник:Непромењиве речи|непром.]]''",
        "жарг.": " ''[[Викиречник:Жаргонске речи|жарг.]]''",
        "форм.": " ''[[Викиречник:Формалне речи|форм.]]''",
        "арх.": " ''[[Викиречник:Архаичне речи|арх.]]''",
        "рет.": " ''[[Викиречник:Ретке речи|рет.]]''",
        "хрв.": " ''[[Викиречник:Речи из хрватског стандарда|хрв.]]''",
        "рег.": " ''[[Викиречник:Дијалекатске речи|рег.]]''",
        "фиг.": " ''[[Викиречник:Фигуративне речи|фиг.]]''",
        "арх.": " ''[[Викиречник:Архаичне речи|арх.]]''",
        "рет.": " ''[[Викиречник:Ретке речи|рет.]]''",
        "изр.": " ''[[Викиречник:Изрази|изр.]]''",
        "нар.": " ''[[Викиречник:Народске речи|нар.]]''",
        "пог.": " ''[[Викиречник:Погрдне речи|пог.]]''",
        "рег.": " ''[[Викиречник:Регионализми|рег.]]''",
        "археол.": " ''[[Викиречник:Археолошки појмови|археол.]]''",
        "биол.": " ''[[Викиречник:Биолошки појмови|биол.]]''",
        "ауг.": " ''[[Викиречник:Аугментатив|ауг.]]''",
        "безл.": " ''[[Викиречник:Безлични глагол|безл.]]''",
        "бот.": " ''[[Викиречник:Ботанички појмови|бот.]]''",
        "вет.": " ''[[Викиречник:Ветеринарски појмови|вет.]]''",
        "взн.": " ''[[Викиречник:Везник|взн.]]''",
        "вој.": " ''[[Викиречник:Војни појмови|вој.]]''",
        "геог.": " ''[[Викиречник:Географски појмови|геог.]]''",
        "грађ.": " ''[[Викиречник:Грађевински појмови|грађ.]]''",
        "грам.": " ''[[Викиречник:Граматички појмови|грам.]]''",
        "дем.": " ''[[Викиречник:Деминутив|дем.]]''",
        "деч.": " ''[[Викиречник:Дечији говор|деч.]]''",
        "екон.": " ''[[Викиречник:Економски појмови|екон.]]''",
        "експр.": " ''[[Викиречник:Екпресивно|експр.]]''",
        "енг.": " ''[[Викиречник:Речи из енглеског језика|енг.]]''",
        "еуф.": " ''[[Викиречник:Еуфемизми|еуф.]]''",
        "ж": " ''[[Викиречник:Именице женског рода|ж]]''",
        "зам.": " ''[[Викиречник:Замнице|зам.]]''",
        "зоол.": " ''[[Викиречник:Зоолошки|зоол.]]''",
        "ирон.": " ''[[Викиречник:Иронично|ирон.]]''",
        "ист.": " ''[[Викиречник:Историјски|ист.]]''",
        "мат.": " ''[[Викиречник:Математички појмови|мат.]]''",
        "мед.": " ''[[Викиречник:Медицински појмови|мед.]]''",
        "мет.": " ''[[Викиречник:Метеоролошки појмови|мет.]]''",
        "м": " ''[[Викиречник:Именице мушког рода|м]]''",
        "мит.": " ''[[Викиречник:Митолошки појмови|мит.]]''",
        "мн.": " ''[[Викиречник:Именице у множини|мн.]]''",
        "муз.": " ''[[Викиречник:Музички појмови|муз.]]''",
        "непрел.": " ''[[Викиречник:Непрелазни глаголи|непрел.]]''",
        "несврш.": " ''[[Викиречник:Несвршени глаголи|несврш.]]''",
        "песн.": " ''[[Викиречник:Песничке речи|песн.]]''",
        "пол.": " ''[[Викиречник:Политички појмови|пол.]]''",
        "правн.": " ''[[Викиречник:Правнички појмови|правн.]]''",
        "пред.": " ''[[Викиречник:Предлози|пред.]]''",
        "прел.": " ''[[Викиречник:Прелазни глаголи|прел.]]''",
        "прид.": " ''[[Викиречник:Придеви|прид.]]''",
        "прил.": " ''[[Викиречник:Прилози|прил.]]''",
        "псих.": " ''[[Викиречник:Психологизми|псих.]]''",
        "рчц.": " ''[[Викиречник:Речце|рчц.]]''",
        "сврш.": " ''[[Викиречник:Свршени глаголи|сврш.]]''",
        "сл.": " ''[[Викиречник:Речи сличног значења|сл.]]''",
        "спорт.": " ''[[Викиречник:Спортски појмови|спорт.]]''",
        "струч.": " ''[[Викиречник:Стручни појмови|струч.]]''",
        "техн.": " ''[[Викиречник:Технолошки појмови|техн.]]''",
        "узв.": " ''[[Викиречник:Узвици|узв.]]''",
        "физ.": " ''[[Викиречник:Физички појмови|физ.]]''",
        "филоз.": " ''[[Викиречник:Филозофски појмови|филоз.]]''",
        "фил.": " ''[[Викиречник:Филолошки појмови|фил.]]''",
        "форм.": " ''[[Викиречник:Формализми|форм.]]''",
        "хип.": " ''[[Викиречник:Хипокористици|хип.]]''",
        "цркв.": " ''[[Викиречник:Црквени појмови|цркв.]]''",
        "шаљ.": " ''[[Викиречник:Шаљиви појмови|шаљ.]]''",
        "шах.": " ''[[Викиречник:Шаховски појмови|шах.]]''"}

class Entry():
    """
    Entry class contains all entry data split into base constituents.
    We use set methods fill them in. Additionally, we use 'unique' attribute
    to mark that entry is standalone or not (i.e, does it need to be combined
    with other entries bearing the same name).
    We use get methods to receive synthesize data in desired format for 
    Wiktionary. Finally, we use to_wiki method to get the all the data
    contained in the instance of the entry formatted and ready for upload
    to Wiktionary.
    """
    def __init__(self, name, lat = False):
        if lat == True:
            self.name = transliterate(name, lat)
            self.script = 'lat'
        else:
            self.name = name
            self.script = 'cyr'
        self.original_name = name
        self.type = []
        self.keys = 0
        self.unique = True
        self.syn = {}
        self.des = {}
        self.asc = {}
    def increase_key(self):
        self.keys += 1
    def set_type(self, typ):
        if self.type != []: self.type = [typ]
        else: self.type.append(typ)
    def not_unique(self):
        self.unique = False
    def set_syn(self, syn, key):
        if syn.startswith('*'):
            self.set_des(syn, key)
        else:
            if self.syn == {}: self.syn = {key: [syn]}
            else:
                if key in self.syn.keys():
                    self.syn[key].append(syn)
                else:
                    self.syn[key] = [syn]
    def set_des(self, des, key):
        if self.des == {}: self.des = {key: [des]}
        else:
            if key in self.des.keys():
                self.des[key].append(des)
            else:
                self.des[key] = [des]
    def set_asc(self, asc, key):
        if self.asc == {}: self.asc = {key: [asc]}
        else:
            if key in self.asc.keys():
                self.asc[key].append(asc)
            else:
                self.asc[key] = [asc]
    def isUnique(self):
        return self.unique
        
    def get_type(self):
        return self.type       
        
    def get_wiki_type(self):
        cand = re.sub("[\[\]'\,]", "", ''.join(self.type))
        return TYPES[cand]
        
    def get_description(self, key):
        if key in self.des.keys():
            return ', '.join(list(set([x for x in self.des[key]])))
        return ''
        
    def get_synonyms(self, key):
        if key in self.syn.keys():
            if self.script == 'lat':
                return format_syn_asc(self.syn[key], True)
            return format_syn_asc(self.syn[key])
        return ''
        
    def get_assoc(self, key):
        if key in self.asc.keys():
            if self.script == 'lat':
                return format_syn_asc(self.asc[key], True)
            return format_syn_asc(self.asc[key])
        return ''
        
    def debug(self):
        print(self.name)
        print(self.get_type())
        print(self.keys)
        print(self.syn)
        print(self.des)
        print(self.asc)
        
    def to_wiki(self, begin = False, end = False):
        """
        Calls appropriate methods and add them in order to a list of strings.
        Then it makes a single string which is formatted and ready to be
        published on Wiktionary.
        Parameters 'begin' and 'end' if True make to_wiki return beginning and
        end of the entry. In cases when the Entry is not unique (i.e, there are
        entries with the same name from which we need to make a single 
        Wiktionary entry), we use begin and/or end set to False depending on 
        in which order the current entry is going to appear in the final 
        combined entry.
        """
        string = []        
        
        """
        Beginning of Wiktionary entry
        """
        if begin:
            if self.script == 'lat':
                string.append('== %s ([[Викиречник:Српски|српски]], [[Викиречник:Ћирилица|ћир.]] [[%s]]) ==\n\n' % (self.name, self.original_name))
            else:
                string.append('== %s ([[Викиречник:Српски|српски]]) ==\n\n' % (self.name))
        
        """
        Loop through all meanings.
        """
        string.append('=== %s ===\n' % (self.get_wiki_type()))
        string.append(format_type(self.get_type(), self.get_wiki_type()))
        
        rng = [str(x) for x in range(1, self.keys + 1)]
        
        string.append('{{Значење|')
        for k in rng:
            if self.get_synonyms(k) or self.get_description(k): 
                string.append('\n# ')
            if self.get_description(k):
                string.extend([self.get_description(k), '$'])
            elif self.get_synonyms(k):
                string.extend([' {{значење преко синонима|' + self.get_synonyms(k), '$', '}}']) 
        string.append('\n}}\n\n')

        string.append('{{Синоними|')
        for k in rng:
            if self.get_synonyms(k):
                string.append('\n# ')
                string.append(self.get_synonyms(k) + ' ')
                string.append('$')
        string.append(' \n}}\n\n')
        
        if self.get_assoc(k) != '':
            string.append('{{Асоцијације|')
            for k in rng:            
                if self.get_assoc(k):
                    string.append('\n# ')
                    string.append(self.get_assoc(k) + ' ')
                    string.append('$')
            string.append(' \n}}\n\n')
                
        """
        End of Wiktionary entry
        """
        if end:
            string.append('== Референце ==\n{{reflist}}\n\n== Напомене ==\n{{reflist|group="н"}}')
        return string

def format_type(lst, string):
    """
    Formats word type for a Wiktionary page. Takes lst as unformatted raw list of
    words describing the word type and string which represents formatted 
    simple word type (without any other qualifications). 
    The function handles the special cases when word type is a noun or verb
    and adds additional data such as gender and type of verb.
    Returns formatted word type block as a string.
    
    """
    formatted = ['{{српски-']
    formatted.append(string.lower())
    if string == 'Именица':
        gender = []
        if "['m']" in lst:
            if gender == []:
                gender.append('|род=м')
            else:
                gender.append(' м') 
        if "['ž']" in lst:
            if gender == []:
                gender.append('|род=ж')
            else:
                gender.append(' ж') 
        if "['s']" in lst:
            if gender == []:
                gender.append('|род=с')
            else:
                gender.append(' с')
        formatted.append(''.join(gender))
    elif string == 'Глагол':        
        asp = ''.join([x for x in lst if x in ["['svrš.']", "['nesvrš.']"]])
        asp = transliterate(re.sub("[\[\]'\,]", "", asp))
        gen = ''.join([x for x in lst if x in ["['prel.']", "['neprel.']"]])
        gen = transliterate(re.sub("[\[\]'\,]", "", gen))
        if asp:
            formatted.append('|вид=' + asp)
        if gen:
            formatted.append('|род=' + gen)
    formatted.append('}}\n')
    return ''.join(formatted)

def concat_entry(strings):
    """
    Takes a list of strings, inserts reference and concatenates it.
    """
    ref_long_des = ' <ref name="П. Ћосић и сарадници, Речник синонима">' + \
            'Павле Ћосић и сарадници, ''Речник синонима'', Београд 2008, ' + \
            'ISBN 978-86-86673-0901</ref>|облик=пун'
    ref_short_des = ' <ref name="П. Ћосић и сарадници, Речник синонима" />|облик=скраћен'
    ref_long = '<ref name="П. Ћосић и сарадници, Речник синонима">Павле ' + \
    'Ћосић и сарадници, ''Речник синонима'', Београд 2008, ISBN 978-86-86673-0901</ref>'
    ref_short = ' <ref name="П. Ћосић и сарадници, Речник синонима" />'    
    
    refd_des = True
    refd = True
    for i,s in enumerate(strings):
        if s == '$':
            end = strings[i+1]
            if '}}' in end:
                if refd_des:
                    strings[i] = ref_long_des
                    refd_des = False
                else:
                    strings[i] = ref_short_des
            else:
                if refd:
                    strings[i] = ref_long
                    refd = False
                else:
                    strings[i] = ref_short
    return ''.join(strings)

def format_syn_asc(word_list, lat = False):
    """
    Formats the sysnonyms and associations block of the entry by finding their 
    appropriate references and inserting words and categories in tags.
    """
    string = []
    flip = {x:False for x in LINKS.keys()}
    for k in word_list:
        s = k.split()
        if s[-1].endswith('.') and s[-1] in LINKS.keys() and flip[s[-1]] == False:
            flip[s[-1]] = True
            string.append(LINKS[s[-1]] + ' ') 
        string.append(' [[' + ' '.join([transliterate(x, lat) for x in s if x.endswith('.') == False]) + ']]')
        for i in range(len(s)):
            if s[i].endswith('.'):
                string.append(' [['+s[i]+']]')
        if k != word_list[-1]:
            string.append(',')
    return ''.join(string)

def find_duplicate_keys(d, no_of_dup):
    """
    Read dictionary keys and figure out which are duplicates. Store them in a
    txt file. If the file exists it skips this step and reads the file.
    """
    if os.path.isfile("duplicates.txt"):
        duplicates = open("duplicates.txt", "r", encoding="utf8").read().split()
        return duplicates
    else:
        all_keys = d["Rečnik sinonima"].keys()
        all_keys_list = [re.sub(r'\([^)]*\)', '', x).strip() for x in all_keys]
        ordered_keys = Counter(all_keys_list).most_common(no_of_dup)
        duplicates = ([x[0] for x in ordered_keys if x[1] > 1])
        outfile = open("duplicates.txt", "w", encoding="utf8")
        outfile.write("\n".join(duplicates))
        return duplicates

def load_dict(source):
    """
    Load Recnik Sinonima from JSON.
    """
    file = open(source, 'r', encoding="utf8")
    sinonimi = json.load(file, object_pairs_hook=OrderedDict)
    return sinonimi

def count_nums(lst):
    """
    Count all digits in a list.
    """
    return len([x for x in lst if x.isdigit()])
    
def check_see(d):
    """
    For a given submeaning of the entry look if there is one that is not 
    refering to the other entries. Returns False immediately after it finds
    such case and return True if we don't find any.
    """
    for k in d.keys():
      for sk in d[k].keys(): 
        if 'categories' in d[k][sk]:
            if 'в.' not in d[k][sk]['categories']:
                return False
    return True

def strip_numbers(string):
    """
    Strips numbers from the word which mark reference entries and their 
    meanings that current word is related to. 
    """
    if string[0].isdigit() == False:
        return string
    for i in range(len(string)):
        if string[i].isalpha():
            return string[i:]
            
def process_description(word, desc, new_entry, skey):
    """
    Strip parathesis from description and insert it if it concerns
    entire entry and not just the particluar meaning (in original JSON file
    such particluar descriptions begin with space character immediatelly 
    after opening paranthesis).
    """
    if desc.startswith('( '):
        word = word + '(' + desc[2:]
    else:
        new_entry.set_des(desc.strip('()'), skey)
    return word
            
def process_form(description, word, tag):
    """
    Remove numbers from unit of meaning and append description and any tags
    """
    if description != '':
        if tag:
            word = strip_numbers(word) + ' ' + description + ' ' + tag
        else:
            word = strip_numbers(word) + ' ' + description
    else:
        if tag:
            word = strip_numbers(word) + ' ' + tag
        else:
            word = strip_numbers(word)
    return word
    
def proces_categories(word, key, element, meaning):
    """
    Get categories and append them to the word. First remove reference tag
    because we directly incorporate synonyms of the reference into the meaning
    of the word.
    """
    cat_list = [x for x in meaning[key][element] if x != 'в.']
    return word + ' ' + ' '.join(cat_list)    

def check_ref(d, new_entry, sinonimi, skey, mode = 'syn'):
    """
    Check if unit of meaning contains reference to the other entry 
    """
    if d['form'][0].isdigit():
        return True
    elif 'categories' in d.keys():
        if 'в.' in d['categories']:
            return True
    return False
    
def only_alpha(string):
    """
    Remove numbers from the string.
    """
    string = [re.sub(r'\([^)]*\)', '', x) for x in string.split() if not x[0].isdigit()]
    return ''.join(string)

def extract_meaning(meaning, entry, sinonimi, skey, mode = 'syn', tag = None, secondary = False):
    """
    Take meaning of the entry and process each word in it. The purpose of this
    function is to distinguish if meaning contains any submeaning which we
    need to deal with recursively calling this function. For words in meaning,
    we look inside their dictionary and look for three key value pairs:
    description, form, and categories. We use helper functions to format them
    and put the data into entry object instance accordingly. 
    
    Parameters
    ----------
        meaning: dict
            Meaning unit of the dictionary entry.
        entry: object
            Instance of the entry we are working with.
        sinonimi: dict
            Entire dictionary containing all entries.
        skey: dict
            This shall contain any original meaning dictionary if we are 
            recursively using this function.
        mode: string
            Default: 'syn'. Determines wether we treat words from meaning as
            synonyms or associations.
        tag: None or string
            Default: None. Contains any global tag that we need to add to all
            words contained in the meaning.
        secondary: boolean
            Default False. True if recursive call, otherwise False. 
    """
    for key in meaning.keys():
        if (key == 'compare' or key == 'similar meaning'):
            if not secondary:
                for comp in meaning[key]:
                    if check_ref(meaning[key][comp], entry, sinonimi, skey, 'asc'):
                        add_from_other(entry, meaning, meaning[key][comp]["form"], sinonimi, skey, mode)
                        continue
                    if 'categories' in meaning[key][comp]:
                        cats = proces_categories('', key, comp, meaning)
                    else:
                        cats = ''
                    entry.set_asc(meaning[key][comp]['form'] + cats, skey)
        elif key in TAGS.keys():
            extract_meaning(meaning[key], entry, sinonimi, skey, mode = 'syn', tag = TAGS[key])
        else:
            word = ''
            if check_ref(meaning[key], entry, sinonimi, skey) and not secondary: 
                add_from_other(entry, meaning, meaning[key]["form"], sinonimi, skey, mode)
                continue
            for element in meaning[key]:
                if element == 'description':
                    word = process_description(word, meaning[key][element], entry, skey)                    
                if element == 'form':
                    # don't add synonym if it's equal to the entry name
                    if only_alpha(meaning[key][element]) == entry.name:
                        break
                    word = process_form(word, meaning[key][element], tag)
                if element == 'categories':
                    cats = proces_categories(word, key, element, meaning)
                    if cats != None:
                        word = cats
            if word != '':
                if word[0].isdigit():
                    add_from_other(entry, meaning, meaning[key]['form'], sinonimi, skey)
                    continue
                if mode == 'syn':
                    entry.set_syn(word, skey)
                elif mode == 'asc':
                    entry.set_asc(word, skey)
#                debugging
#                print (word)
                
def add_from_other(entry, d, lookup, sinonimi, skey, mode='syn'):
    """
    Adding synonyms from other entries into the original entry that refers
    to them. There are two basic cases. First case when the entry of the 
    refered synonym specifies submeanings, or when it specifies one of the
    entries who share the same term, and the second case when this is not the
    case and we can simply take all synonyms of the refered entry.
    
    Parameters:
    ----------
        entry: Object
            instance of Entry class which holds dictionary entry formatted data.
        d: dict
            meaning of entry as dictionary.
        lookup: string
            the name of the other entry that the word from the meaning is refering to.
        sinonimi: dict
            entire dictionary which contains all of the entries
        skey: dict
            This shall contain any original meaning dictionary if we are 
            recursively using this function.
        mode: string
            Default: 'syn'. Determines wether we treat words from meaning as
            synonyms or associations.
            
    """
#    print(lookup)
    if re.search(r'\d', lookup):
        lookup = [x.strip('.()') for x in lookup.split()]
        name = ' '.join([x for x in lookup if x[0].isalpha()])
        sub = []
        if lookup[-1].isdigit():
            sub.append(lookup.pop())
        if sub:
            term = name + ' (%s) ' % (sub[0])
        else:
            term = name
        term = term.strip()
        if term:
            for typ in sinonimi["Rečnik sinonima"][term]:
                for s in sinonimi["Rečnik sinonima"][term][typ][0]:
                    if lookup:
                        if s in lookup:
                            extract_meaning(dict(sinonimi["Rečnik sinonima"][term][typ][0][s]), entry, sinonimi, skey, mode, None, True)
                    extract_meaning(dict(sinonimi["Rečnik sinonima"][term][typ][0][s]), entry, sinonimi, skey, mode, None, True)

    else:
        for typ in sinonimi["Rečnik sinonima"][lookup]:
            for s in (dict(sinonimi["Rečnik sinonima"][lookup][typ][0])):
                extract_meaning(dict(sinonimi["Rečnik sinonima"][lookup][typ][0][s]), entry, sinonimi, skey, mode, None, True)
               
                    
def make_entries(sinonimi, to_text, to_pickle, debug, breakpoint, lat = False):
    """
    Iterate over dictionary in order of entries. If entry is a duplicate, put 
    the object that represents it in the list which contains all objects with
    the same duplicate name. 
    """
    if debug:
        names = []
    entries = {}
    duplicates = find_duplicate_keys(sinonimi, len(sinonimi["Rečnik sinonima"]))
    for i, s in enumerate(sinonimi["Rečnik sinonima"].keys()):
        if debug:        
            names.append(" ".join([x for x in sinonimi["Rečnik sinonima"][s].keys()]))
        entry_name = re.sub(r'\([^)]*\)', '', s).strip()
        entry = Entry(entry_name, lat)
        if entry_name in duplicates:
            entry.not_unique()
            if entry_name in entries:
                entries[entry_name].append(entry)                
            else:
                entries[entry_name] = [entry]
        else:
            entries[s] = entry       
        
        """
        Getting the type of the word
        """
        typ = list(sinonimi["Rečnik sinonima"][s].keys())[0] 
        entry.set_type(typ)
        """
        Iterate over the meanings of the dictionary entry. Only 'reference'
        subdictionary is not ordered, so we use this fact to distinguish
        between them. Pass submeaning for further processing.
        """
        for j, body in enumerate(sinonimi["Rečnik sinonima"][s][typ]):
            if isinstance(body, OrderedDict):
                for meaning in sinonimi["Rečnik sinonima"][s][typ][0]:
                    entry.increase_key()
                    extract_meaning(sinonimi["Rečnik sinonima"][s][typ][0][meaning], entry, sinonimi, skey = meaning)
            else:
#                it's reference which is not needed because it contains no data
                pass

        
        """
        Enable for debugging
    
        """
        if breakpoint:
            if i == breakpoint:
                break

    """
    To print the entries to a text file.
    """
    if to_text:
        out = codecs.open('out/test0.txt', 'w', encoding = 'utf8')
        for k in entries:
            out.write('\n{{-start-}}\n')
            out.write('\'\'\'%s\'\'\'\n' % (transliterate(k, lat)))
            if isinstance(entries[k], list):
                string = []
                for i, e in enumerate(entries[k]):
                    if i == 0:
                        string.extend(e.to_wiki(True, False))
                    elif i == (len(entries[k]) - 1):
                        string.extend(e.to_wiki(False, True))
                    else:
                        string.extend(e.to_wiki())
                
                string = concat_entry(string)
                out.write(string)
            elif isinstance(entries[k], object):
                string = concat_entry(entries[k].to_wiki(True, True))
                out.write(string)
            out.write('\n{{-stop-}}\n')
    """
    To print the entries to the console.
    """
    if debug:
        print (Counter(names))
        for k in entries:
            if isinstance(entries[k], list):
                for i in range(len(entries[k])):
                    entries[k][i].debug()
            else:
                entries[k].debug()
    """
    To Pickle
    """
    if to_pickle:
        pickle.dump(entries, open('out/synonymsX', 'wb')) 
    
    print('Finish')

def main(argv):
    to_text = to_pickle = to_json = debug = lat = False
    print(argv)
    if 't' in argv:
        to_text = True
    if 'p' in argv:
        to_pickle = True
    if 'j' in argv:
        to_json = True
    if 'd' in argv:
        debug = True
    if 'l' in argv:
        lat = True
    if 's' in argv:
        source = SHORT
    else:
        source = FULL
    print(source, to_text, debug, lat)
    breakpoint = None
    for a in argv:
        if a.isdigit():
            breakpoint = a
    sinonimi = load_dict(source)
    if debug:
        print (len(sinonimi["Rečnik sinonima"]))
    make_entries(sinonimi, to_text, to_pickle, debug, breakpoint, lat)

if __name__ == "__main__":
    main(argv)