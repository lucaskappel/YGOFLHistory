# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 14:46:48 2021

@author: Lucas
"""
import datetime, urllib.request, re, sqlite3, html.parser
FL_Folder = "C:\\Users\\Lucas\\source\\Python\\YGO\\FL_List"
Test_Output = FL_Folder + "\\Output\\output.txt"
Test_Page = "C:\\Users\\Lucas\\source\\Python\\YGO\\FL_List\\Test\\Forbidden & Limited Card List Yu-Gi-Oh! TRADING CARD GAME.htm"
Status_Enumerable = ["Forbidden", "Limited", "Semi-Limited", "Unlimited"]
dbpath = "C:\\Users\\Lucas\\source\\Python\\YGO\\FL_List\\FL_List.db"
html_parser = html.parser.HTMLParser()

class FL_Entry:
    Type = None
    Name = None
    Status_Advanced = None
    Status_Traditional = None
    Remarks = None
    Link = None
    Effective_From = None
    
    def ToTuple(self):
        return (
            html_parser.unescape(self.Type),
            html_parser.unescape(self.Name),
            self.Status_Advanced,
            self.Status_Traditional,
            html_parser.unescape(self.Remarks) if self.Remarks is not None else self.Remarks,
            html_parser.unescape(self.Link),
            self.Effective_From.isoformat()
            )
    
    def ToPropertyTuple(self):
        for(index, property) in self.Properties:
            yield(self.Name, index, property)
    
    def ToString(self):
        return "Type: {cTyp}\nName: {cNam}\nAdvanced: {cAdv}\nTraditional: {cTra}\nRemarks: {cRem}\nLink: {cLnk}\nEffective From: {cEff}\n".format(
            cTyp = html_parser.unescape(self.Type), 
            cNam = html_parser.unescape(self.Name), 
            cAdv = self.Status_Advanced, 
            cTra = self.Status_Traditional,
            cRem = html_parser.unescape(self.Remarks) if len(self.Remarks) > 0 else self.Remarks,
            cLnk = html_parser.unescape(self.Link),
            cEff = self.Effective_From.isoformat()
            )

def GetCurrentListHTML():
    ## Get the HTML Page from the UK site and convert it from bytes to text
    PageHTML = ""
    with urllib.request.urlopen("https://img.yugioh-card.com/uk/gameplay/detail.php?id=1155") as URLReader:
        PageHTML = URLReader.read().decode("utf8")
    return PageHTML

def ReadListHTMLFromFilepath(Filepath):
    returnstring = ""
    with open(Filepath, encoding="utf8") as f:
        returnstring = f.read()
    return returnstring

def ParseHTML(PageHTML):
    ## Get the Effective Date (dd/mm/yy)
    EffectiveDateMatch = re.search("Effective from (?P<EffectiveFrom>\d{1,2}/\d{1,2}/\d{4})", PageHTML)
    EffectiveDateText = EffectiveDateMatch.group('EffectiveFrom').split('/')
    EffectiveDate = datetime.date(
        year = int(EffectiveDateText[2]), 
        month = int(EffectiveDateText[1]), 
        day = int(EffectiveDateText[0]))
    
    ## Cut out the table from the HTML and create an entry for each card on the list
    Card_Table = PageHTML[int(PageHTML.index("<tbody>") + len("<tbody>")):int(PageHTML.index("</tbody>"))].rstrip().split("</tr>")
    while('\n' in Card_Table): Card_Table.remove('\n')
    while('' in Card_Table): Card_Table.remove('')
    FL_List = []
    for Entry in Card_Table:
        EntryData = re.search("<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?", Entry, re.MULTILINE|re.DOTALL)

        ## Make sure the entry obtains a full set of data
        if(EntryData is None):
            raise Exception("EntryData is None\nEntries done: " + str(len(FL_List)) + "\n")
        elif(len(EntryData.groups()) < 6):
            raise Exception("EntryData is too small")
        elif(EntryData.group(1) == '&nbsp;' or 
             EntryData.group(1) == 'Card Type' or 
             EntryData.group(1) == '' or 
             EntryData.group(1) == '\xa0'):
            pass
        else:
            ## Replace '&nbsp;' with an empty string
            for g in EntryData.groups():
                g.replace('&nbsp;', '')
            
            ## Create the entry object
            FLE = FL_Entry()
            
            ## Type and Name
            FLE.Type = EntryData.group(1)
            FLE.Name = EntryData.group(2)
            
            ## Status, as integers
            if(EntryData.group(3) in Status_Enumerable): 
                FLE.Status_Advanced = Status_Enumerable.index(EntryData.group(3))
            else: FLE.Status_Advanced = 3
            if(EntryData.group(4) in Status_Enumerable): 
                FLE.Status_Traditional = Status_Enumerable.index(EntryData.group(4))
            else: FLE.Status_Traditional = 3
            
            ## Remarks column
            if "span" in EntryData.group(5):
                FilteredRemarks = re.search("<span>(?P<rem>.*?)<\/span>", EntryData.group(5))
                FLE.Remarks = FilteredRemarks.group('rem')
            else:
                FLE.Remarks = EntryData.group(5)
            
            ## Href Link
            hrefLink = re.search('href="(?P<hrefLink>.*?)"', EntryData.group(6))
            try:
                FLE.Link = hrefLink.group('hrefLink')
            except:
                print("Exception occurred when retrieving the card's database link.\n" +
                      "Card: " + EntryData.group(1) + "\n" +
                      "HTML: " + EntryData.group(6) + "\n"
                      )
                break
            
            ## Set effective date
            FLE.Effective_From = EffectiveDate
            
            ## Append the new entry to the list
            FL_List.append(FLE)

    ## Return the effective date and the list, cutting off the first entry
    return FL_List

def GetLatestFL(): return ParseHTML(GetCurrentListHTML())

def UpdateDB(DatabasePath, FL_List, Testing = True):
    if Testing:
        SQLTable = 'Master_List_Backup'
    else:
        SQLTable = 'Master_List'
        
    SQLConnection = sqlite3.connect(DatabasePath)
    SQLCursor = SQLConnection.cursor()
    for record in FL_List:
        
        ## Check to see if the record exists first
        Record_Exists = '''SELECT * FROM {Table} WHERE (
            Card_Type=? AND
            Card_Name=? AND 
            Status_Advanced=? AND 
            Status_Traditional=? AND
            Remarks=? AND
            Database_Link=? AND
            Effective_From=? 
            )'''.format(Table = SQLTable)
    
        RecordTuple = record.ToTuple()
        Entry = SQLCursor.execute(Record_Exists, RecordTuple).fetchone()
        if Entry is not None:
            raise Exception("Record already exists; this list has probably already been added.")
        else:
            Record_Insert = '''INSERT INTO {Table}(
                Card_Type, 
                Card_Name, 
                Status_Advanced, 
                Status_Traditional, 
                Remarks, 
                Database_Link, 
                Effective_From
                )
            VALUES
                (?,?,?,?,?,?,?);
            '''.format(Table = SQLTable)
            try:
                SQLCursor.execute(Record_Insert, record.ToTuple())
            except Exception as e:
                print(e)
                SQLConnection.close()
                quit()
    SQLConnection.commit()
    SQLConnection.close()
    
def DeleteRecentBanlist(DatabasePath, Testing = True):
    #Effective_From = '2021-07-01'
    if Testing:
        SQLTable = 'Master_List_Backup'
    else:
        SQLTable = 'Master_List'
        
    SQLConnection = sqlite3.connect(DatabasePath)
    SQLCursor = SQLConnection.cursor()
    Record_Delete = "DELETE FROM {Table} WHERE Effective_From = '2021-07-01'".format(Table = SQLTable)
    try:
        SQLCursor.execute(Record_Delete)
    except Exception as e:
        print(e)
        SQLConnection.close()
        quit()
    SQLConnection.commit()
    SQLConnection.close()

#DeleteRecentBanlist(dbpath)
UpdateDB(dbpath, GetLatestFL(), False)