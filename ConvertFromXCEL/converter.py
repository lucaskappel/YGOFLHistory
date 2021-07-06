# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 18:59:31 2021

@author: Lucas
"""

import xlrd, io, os, re, datetime,sqlite3
filepath = "C:\\Users\\Lucas\\source\\Python\\YGO\\FL_List\\ConvertFromXCEL\\TCG Forbidden_Limited List.xlsx"
months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
FLStatus = ['Forbidden', 'Limited', 'Semi-Limited']
dbpath = "C:\\Users\\Lucas\\source\\Python\\YGO\\FL_List\\FL_List.db"

wb = xlrd.open_workbook(filepath)
ws = wb.sheet_by_index(0)

def PrintTextFile(FilePath: str, FileContents: str, OverwritePrevious = False):
    
    ## Submethod to rename a duplicate file
    def Rename_Duplicate(Savepath):
        
        ## Sub-Submethod to get current working directory of the parent
        def Get_Parent_Directory(path = os.getcwd()): return path.split('\\')[:-1]
        
        duplicate_copy_counter = []
        file_array = Savepath.split('\\')[-1].split('.')
        
        if len(file_array) <= 1: 
            raise Exception(message = 'Error in \'Rename_Duplicate\'; \'Savepath\' must be splittable by \'.\'')
            
        filename_regex = re.compile(file_array[0] + '\d*')
        
        for list_file in os.listdir('\\'.join(Savepath.split('\\')[:-1])):
            if re.match(filename_regex, list_file.split('.')[0]): 
                duplicate_copy_counter.append(list_file)
                
        return '\\'.join(Get_Parent_Directory(Savepath)) + '\\' + file_array[0] + str(len(duplicate_copy_counter)) + '.' + file_array[1]
    
    ## Rename the duplicate file if we don't want to overwrite
    if(not OverwritePrevious): FilePath = Rename_Duplicate(FilePath)
    
    ## Write the file contents
    with io.open(FilePath, "w+", encoding="utf-8") as TargetFile: TargetFile.write(FileContents)
    
    return

class FL_Entry:
    Type = None
    Name = None
    Status_Advanced = None
    Status_Traditional = None
    Remarks = None
    Link = None
    Effective_From = None
    
    def ToTuple(self):
        return(
            self.Type,
            self.Name,
            self.Status_Advanced,
            self.Status_Traditional,
            self.Remarks,
            self.Link,
            self.Effective_From.isoformat()
            )
    
    def ToPropertyTuple(self):
        for(index, property) in self.Properties:
            yield(self.Name, index, property)
    
    def ToString(self):
        return "Type: {cTyp}\nName: {cNam}\nAdvanced: {cAdv}\nTraditional: {cTra}\nRemarks: {cRem}\nLink: {cLnk}\nEffective From: {cEff}\n".format(
            cTyp = self.Type, 
            cNam = self.Name, 
            cAdv = self.Status_Advanced, 
            cTra = self.Status_Traditional,
            cRem = self.Remarks,
            cLnk = self.Link,
            cEff = self.Effective_From
            )

def GetEffectiveDate(wksheet, col):
    daymonth = wksheet.cell_value(1, col).split(' ')
    eday = re.search('(\d*)', daymonth[0]).group(1)
    emonth = months.index(daymonth[1])
    eyear = wksheet.cell_value(0, col)
    return datetime.date(year = int(eyear), month = int(emonth), day = int(eday))

def GetFLEntries():
    FL_List = []
    for row in range(3, ws.nrows):
        for col in range(2, ws.ncols):
            ## Create the FLE for each cell in the grid
            FLE = FL_Entry()
            FLE.Type = ws.cell_value(row, 0)
            FLE.Name = ws.cell_value(row, 1)
            SAdv = ws.cell_value(row, col)
            if SAdv in FLStatus:
                FLE.Status_Advanced = FLStatus.index(SAdv)
                if FLStatus.index(SAdv) == 0:
                    FLE.Status_Traditional = 1
                else:
                    FLE.Status_Traditional = FLStatus.index(SAdv)
            else: 
                FLE.Status_Advanced = 3
                FLE.Status_Traditional = 3

            FLE.Effective_From = GetEffectiveDate(ws, col)
            FL_List.append(FLE)
    return FL_List

def UpdateDB(records):
    SQLConnection = sqlite3.connect(dbpath)
    SQLCursor = SQLConnection.cursor()
    
    for record in records:
        if record.Name == '' or record.Name is None: pass
        else:
            Create_Entries = '''
            INSERT INTO
                Master_List_Backup(Card_Type, Card_Name, Status_Advanced, Status_Traditional, Remarks, Database_Link, Effective_From)
            VALUES
                (?,?,?,?,?,?,?);
            '''
            SQLCursor.execute(Create_Entries, record.ToTuple())
    SQLConnection.commit()
    SQLConnection.close()

def PrintTextFile(FilePath: str, FileContents: str, OverwritePrevious = False):
    
    ## Submethod to rename a duplicate file
    def Rename_Duplicate(Savepath):
        
        ## Sub-Submethod to get current working directory of the parent
        def Get_Parent_Directory(path = os.getcwd()): return path.split('\\')[:-1]
        
        duplicate_copy_counter = []
        file_array = Savepath.split('\\')[-1].split('.')
        
        if len(file_array) <= 1: 
            raise Exception(message = 'Error in \'Rename_Duplicate\'; \'Savepath\' must be splittable by \'.\'')
            
        filename_regex = re.compile(file_array[0] + '\d*')
        
        for list_file in os.listdir('\\'.join(Savepath.split('\\')[:-1])):
            if re.match(filename_regex, list_file.split('.')[0]): 
                duplicate_copy_counter.append(list_file)
                
        return '\\'.join(Get_Parent_Directory(Savepath)) + '\\' + file_array[0] + str(len(duplicate_copy_counter)) + '.' + file_array[1]
    
    ## Rename the duplicate file if we don't want to overwrite
    if(not OverwritePrevious): FilePath = Rename_Duplicate(FilePath)
    
    ## Write the file contents
    with io.open(FilePath, "w+", encoding="utf-8") as TargetFile: TargetFile.write(FileContents)
    
    return

UpdateDB(GetFLEntries())
pass