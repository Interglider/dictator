# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 17:13:53 2015

@author: misha
"""

AZBUKA = {u'a':u'а', u'b':u'б', u'v':u'в', u'g':u'г', u'd':u'д', 
          u'đ':u'ђ', u'e':u'е', u'ž':u'ж', u'z':u'з', u'i':u'и',
          u'j':u'ј', u'k':u'к', u'l':u'л', u'lj':u'љ', u'm':u'м',
          u'n':u'н', u'nj':u'њ', u'o':u'о', u'p':u'п', u'r':u'р',
          u's':u'с', u't':u'т', u'ć':u'ћ', u'u':u'у', u'f':u'ф',
          u'h':u'х', u'c':u'ц', u'č':u'ч', u'dž':u'џ', u'š':u'ш',
          u'A':u'А', u'B':u'Б', u'V':u'В', u'G':u'Г', u'D':u'Д',
          u'Đ':u'Ђ', u'E':u'Е', u'Ž':u'Ж', u'Z':u'З', u'I':u'И',
          u'J':u'Ј', u'K':u'К', u'L':u'Л', u'Lj':u'Љ', u'M':u'М',
          u'N':u'Н', u'Nj':u'Њ', u'O':u'О', u'P':u'П', u'R':u'Р',
          u'S':u'С', u'T':u'Т', u'Ć':u'Ћ', u'U':u'У', u'F':u'Ф',
          u'H':u'Х', u'C':u'Ц', u'Č':u'Ч', u'Dž':u'Џ', u'Š':u'Ш',
          u'LJ':u'Љ', u'NJ':u'Њ', u'DŽ':u'Џ'}


ABECEDA = {'з': 'z', 'Ж': 'Ž', 'К': 'K', 'Ш': 'Š', 'Ћ': 'Ć', 'Њ': 'Nj', 
           'ј': 'j', 'Д': 'D', 'ц': 'c', 'ж': 'ž', 'А': 'A', 'Е': 'E',
           'Б': 'B', 'ч': 'č', 'Л': 'L', 'Џ': 'DŽ', 'ш': 'š', 'с': 's',
           'к': 'k', 'З': 'Z', 'в': 'v', 'Ј': 'J', 'М': 'M', 'њ': 'nj',
           'у': 'u', 'б': 'b', 'И': 'I', 'Ђ': 'Đ', 'љ': 'lj', 'ђ': 'đ',
           'ф': 'f', 'п': 'p', 'л': 'l', 'д': 'd', 'У': 'U', 'Ф': 'F',
           'н': 'n', 'р': 'r', 'П': 'P', 'м': 'm', 'т': 't', 'џ': 'dž',
           'Љ': 'Lj', 'х': 'h', 'Т': 'T', 'Н': 'N', 'и': 'i', 'Ч': 'Č',
           'В': 'V', 'Ц': 'C', 'Х': 'H', 'О': 'O', 'а': 'a', 'С': 'S',
           'ћ': 'ć', 'Г': 'G', 'о': 'o', 'г': 'g', 'е': 'e', 'Р': 'R'}
          
def transliterate(string, to_latin = False):
    if to_latin == False:
        script = AZBUKA
    else:
        script = ABECEDA
    skip = False
    latin = False
    new = ''   
    for i, s in enumerate(string):
        if skip == True:
            skip = False
            continue  
        elif s == '#':
            latin = True
            continue
        elif latin == True:
            new = new + s
            latin == False
        elif s.isalpha() == False:
            new = new + s
        else:
            low_s = s.lower()
            if low_s == 'n' or low_s == 'd' or low_s == 'l': 
                try:
                    n = string[i+1]
                    low_n = n.lower()
                    if (low_s == 'n' and low_n == 'j')\
                    or (low_s == 'd' and low_n == 'ž')\
                    or (low_s == 'l' and low_n == 'j'):
                        if low_n == 'ž':
                            n = u'ž'
                        s = s + n
                        skip = True                        
                except:
                    pass
            if s in script.keys():
                new = new + script[s]
            elif s == '#':
                latin == True
            else:
                new = new + s
    return new