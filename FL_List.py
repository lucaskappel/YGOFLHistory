# -*- coding: utf-8 -*-
"""
Forbidden/Limited List
Created on Mon Jul 26 15:48:23 2021
@author: Lucas
"""

import File_IO, urllib, re


##########################
#### Module Variables ####
##########################

debug_text_file = "C:\\Users\\Lucas\\source\\Python\\YGO\\YGODB\\Debug\\debug_FL.txt"

locales = {
    'de' : 'TCG',
    'en' : 'TCG',
    'es' : 'TCG',
    'fr' : 'TCG',
    'it' : 'TCG',
    'ja' : 'OCG',
    'ko' : 'OCG',
    'pt' : 'TCG' }

Locales_DateFormat_RegexPattern = {
    'de' : '\(Status aktualisiert (?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\)',
    'en' : '\(Status Updated (?P<month>\d{2})\.(?P<day>\d{2})\.(?P<year>\d{4})\)',
    'es' : '\(Actualizado en (?P<day>\d{2})\/(?P<month>\d{2})\/(?P<year>\d{4})\)',
    'fr' : '\(Mise à jour le (?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\)',
    'it' : '\(Stato Aggiornato (?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\)',
    'ja' : '\((?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2}) 更新\)',
    'ko' : '\((?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2}) 갱신\)',
    'pt' : '\(Status Atualizado em (?P<day>\d{2})\/(?P<month>\d{2})\/(?P<year>\d{4})\)' }


########################
#### Module Methods ####
########################


def Validate_Locale(locale):
    if(locale not in locales):
        raise Exception('Locale "{locale}" not found in "locales" dictionary.'.format(locale))
        
def Get_FL_HTML(locale = 'en', live = True):
    HTML_Text = ''
    if(live):
        with urllib.request.urlopen("https://www.db.yugioh-card.com/yugiohdb/forbidden_limited.action?request_locale={locale}".format(locale = locale)) as URLReader:
            HTML_Text = URLReader.read().decode("utf8")
    else:
        with open("C:\\Users\\Lucas\\source\\Python\\YGO\\YGODB\\Debug\\FL test\\FL_Test_{locale}.htm".format(locale = locale), mode= "r", encoding = "utf-8") as TestFile:
            HTML_Text = TestFile.read()
    return HTML_Text

def HTML_Parse_Date(HTML_Text, locale = 'en'):    
    # Get the effective date of the banlist and standardize it as yyyy.mm.dd
    Regex_Matches = re.search(Locales_DateFormat_RegexPattern[locale], HTML_Text)
    return '{yyyy}.{mm}.{dd}'.format(
        yyyy = Regex_Matches.group('year'),
        mm = Regex_Matches.group('month'),
        dd = Regex_Matches.group('day'))

def FL_Parse_HTML(HTML_Text, locale = 'en'):
    # Get the list's effective date.
    Effective_Date = HTML_Parse_Date(HTML_Text, locale)
    
    # HTML tables 1-3 are the Forbidden, Limited, and Semi-Limited lists, respectively.
    FL_Tables = re.findall(r"<table.*?>(.*?)</table>", HTML_Text, flags = re.DOTALL)[1:4]
    
    # Create the FL List entries.
    FL_List = []
    for Table_Index in range(0, 3):
        
        #Get all the table entries, grouping the CID and Name
        Entries = re.finditer(r'<a href=".*?cid=(?P<cid>\d*)">(?P<cname>.*?)</a>', FL_Tables[Table_Index])
        
        # Create a tuple for each found entry with the CID, Name, and status (0-2, using the Table_Index).
        for Entry in Entries:
            FL_Entry_Tuple = (Entry.group('cid'), Entry.group('cname'), Table_Index, Effective_Date, locale)
            FL_List.append(FL_Entry_Tuple)

    return FL_List

def Get_FL_List(locale = 'en', live = True):
    # Validate that the locale entered exists
    Validate_Locale(locale)
    
    # Retreive the list's HTML text from the given source.
    HTML_Raw = Get_FL_HTML(locale, live)
    
    # Parse the HTML text into a list of tuples
    Forbidden_Limited_List = FL_Parse_HTML(HTML_Raw, locale)
    return Forbidden_Limited_List

def Full_Test(live = True):
    TCG_Lists = []
    OCG_Lists = []
    
    print('\n\n======== ======== ======== ========')
    print('== Retrieving live lists...\n')
    for locale in locales:
        FL_List = Get_FL_List(locale, live=live)
        if(locales[locale] == 'TCG'): TCG_Lists.append(FL_List)
        else: OCG_Lists.append(FL_List)
        print('==== Retrieved FL list for locale "{loc}".'.format(loc = locale))

    # Make sure the status of each cid matches by checking against the index 0 list
    print('\n== Checking OCG List equivalencies...')
    Reference_List = [(Entry[0], Entry[2]) for Entry in OCG_Lists[0]].sort()
    for OCG_List in OCG_Lists:
        CID_Status_List = [(Entry[0], Entry[2]) for Entry in OCG_List].sort()
        print("==== '{locale}' : {matches}".format(locale = OCG_List[0][len(OCG_List[0]) - 1], matches = Reference_List == CID_Status_List))

    print('\n== Checking TCG List equivalencies...')
    Reference_List = [(Entry[0], Entry[2]) for Entry in TCG_Lists[0]].sort()
    for TCG_List in TCG_Lists:
        CID_Status_List = [(Entry[0], Entry[2]) for Entry in TCG_List].sort()
        print("==== '{locale}' : {matches}".format(locale = TCG_List[0][len(TCG_List[0]) - 1], matches = Reference_List == CID_Status_List))
    
    print('\n== Forbidden/Limited Tests Complete.')
    print('======== ======== ======== ========\n')
    return
    
##########################
#### Module Execution ####
##########################

Full_Test(True)

#eof