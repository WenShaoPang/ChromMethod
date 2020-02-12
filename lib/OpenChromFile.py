import sys
from os import path
import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
if __name__ == '__main__':
    sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
#from lib.Chrom import Peak

class FileOpenClass:
    filepath = ""
    filename = ""
    fileExtention = ""
    time = []
    signal = []
    def __init__(self, filepath=""):
        self.filepath = filepath
        self.filename = filepath.split("/")[-1]
        self.fileExtention = path.splitext(filepath)[1][1:]
        if self.fileExtention == "txt":
            self.time, self.signal = openTXT(filepath)
        elif self.fileExtention == "csv" or self.fileExtention == "CSV":
            self.time, self.signal = openCSV(filepath)
        else:
            print("Error : File Extention Error - {0}".format( self.fileExtention ) )
            print("File Name : ", filepath)
    def getFileData(self):
        return self.time, self.signal, self.filename, self.filepath

def openTXT(path=""):
    X, Y = [],[]
    # ------------------------------------------------------------------------------------#
    # 如果 路徑為空的, 則跳出函式
    # ------------------------------------------------------------------------------------#
    if path == "":
        return X, Y
    # ------------------------------------------------------------------------------------#
    # 開啟 txt 檔案
    # ------------------------------------------------------------------------------------#
    with open( path, 'r') as f:
        X, Y = zip(*[[float(s) for s in line.split()] for line in f])
    return list(X),list(Y)   

def openCSV(path=""):
    ''' 開啟 csv 檔案 '''
    X,Y = [],[]
    # ------------------------------------------------------------------------------------#
    # 如果 路徑為空的, 則跳出函式
    # ------------------------------------------------------------------------------------#
    if path == "":
        return X,Y
    # ------------------------------------------------------------------------------------#
    # 開啟 csv 檔案, 若失敗, 則跳入 except
    # ------------------------------------------------------------------------------------#
    try:
        with open( path, 'r', encoding="GB2312") as f:
            rows = csv.reader(f)
            for row in rows:
                X.append( float( row[0] ))
                Y.append( float( row[1] ))
    except Exception as e :
        print( getattr(e, 'message', repr(e)) )
    return list(X), list(Y)



class SavePeakTable:
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(["Ret. Time", "Height", "Area", 
            "Width", "Asymmetry", "Tailing Factor", "N", "Sigma", "W0.5","W0.1", "W0.05"])
    def setData(self, peaklist=[], path=""):
        for peak in peaklist:
            self.ws.append( [ float("%.2f"%(peak.tr)), float("%.4f"%(peak.height)), 
                float("%.4f"%(peak.area)), float("%.4f"%(peak.width)), peak.As, peak.tf, 
                peak.N, peak.sigma, peak.w05, peak.w01, peak.w005  ] )
        self.setStyle( path, len(peaklist) )

    def setStyle(self, path="", num=0):
        tab = Table(displayName="Table1", ref= "A1:K{0}".format( num+1 )  )
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=True)
        tab.tableStyleInfo = style
        self.ws.add_table(tab)
        #self.wb.save("C:\\Users\\gogho\\OneDrive\\桌面\\Chrom\\test\\create_sample.xlsx")
        self.wb.save( path + ".xlsx" )

if __name__ == "__main__":
    a = FileOpenClass("C:/Users/gogho/OneDrive/桌面/Chrom/example/2MIN100ML(A1)-1.csv")
    time, signal, filename, filepath = a.getFileData()
    print( "len(time) : {0}\nlen(signal) : {1}\nFile Name : {2}\nFile Path : {3}".format(
         len(time), len(signal), filename, filepath ) 
         )

