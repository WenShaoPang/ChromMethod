# -*- coding: utf-8 -*-
from os import path
class ChromSetting : 
    ''' 參數控制類別 '''
    # ------------------------------------------------------------------------------------#
    # 類別內參數
    # ------------------------------------------------------------------------------------#
    json_path = ""  # 檔案路徑
    setting = {} 

    def __init__(self):
        ''' Constructor '''
        self.load_ParFile()

    def load_ParFile(self):
        """ 開啟 json 參數檔案, 並匯入參數 """
        # ------------------------------------------------------------------------------------#
        # 開啟 json 參數檔案路徑 (( 不用絕對路徑, 以免換到其他電腦上時, 路徑失效
        # ------------------------------------------------------------------------------------#
        self.json_path =  path.dirname(path.abspath(__file__) )  + "//par.json"

        # ------------------------------------------------------------------------------------#
        # 讀取 json 參數檔案
        # ------------------------------------------------------------------------------------#
        import json
        with open( self.json_path , encoding='utf-8') as f:
            self.setting = json.loads( f.read() )
            print(self.setting)
            f.close()

    def save_ParFile(self):
        ''' 把 par 之資料寫入 json 檔案中 '''
        # ------------------------------------------------------------------------------------#
        # 把 par 寫入 json 參數檔案中
        # ------------------------------------------------------------------------------------#
        import json
        with open( self.json_path, 'w' , encoding='utf-8') as f:
            json.dump( self.setting , f, indent=4, separators=(',', ': ') )
            f.close()

if __name__ == '__main__':
    s = ChromSetting()
    print( s.setting['Smooth_Filter']['Data_Bunching'] )
