# -*- coding: utf-8 -*-

from PyQt5.QtGui import QStandardItemModel, QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import QWidget, QMainWindow, QAction, QFileDialog
import pyqtgraph as pg
import sys
from os import path

from mainWindowUI import Ui_MainWindow as MainUI
if __name__ == '__main__':
    sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from lib.Chrom import ChromData, ChromOperation
from conf.ChromAlgoSetting import ChromSetting
from UI.SettingWindow import SettingWindow
from lib.OpenChromFile import FileOpenClass, SavePeakTable
from lib.DebugLog import logging 



class MainMenuBar(QWidget):
    show_ChromData_Signal = pyqtSignal()
    set_ChromData_Signal = pyqtSignal( str )
    
    def __init__(self, parent=None):
        # 先初始化父類別, 否則在 connect event的時候會出錯
        super(MainMenuBar, self).__init__(parent)
        

    def initSetting(self, obj:object, root=None):
        self.menu = obj
        if type(root).__name__ == "MainWindow":
            self.root = root
        self.menu.triggered[QAction].connect(self.menuActionEvent)
        
    @logging
    def menuActionEvent(self, menuBarObject):
        print( menuBarObject.text() )
        if menuBarObject.text() == "Open File":
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                'Open File', 
                path.dirname( path.dirname( path.abspath(__file__) ) )+'\\example'
                )
            if file_path == "":
                return

            self.set_ChromData_Signal.emit( file_path )
            #----------------------------------------------------
            # 發送繪圖訊號到 ChromGraph.show() 
            # 於 MainWindow class 進行signal & slot 的連接
            #----------------------------------------------------
            self.show_ChromData_Signal.emit() 

        elif menuBarObject.text() == "Setting":
            settingwindow = SettingWindow()
            settingwindow.LoadSetting( self.root.chromOperation.chrom_Setting )
            settingwindow.show()

        elif menuBarObject.text() == "Export Excel":
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                'Save File', 
                path.dirname( path.dirname( path.abspath(__file__) ) )
                )
            apt = SavePeakTable()
            apt.setData( self.root.chromOperation.chrom_info.Peaks, file_path )
            


class MainToolBar(QWidget):
    clear_peakTable_signal = pyqtSignal()
    start_integral_signal = pyqtSignal()
    show_baseline_signal = pyqtSignal( object )
    show_peaks_signal = pyqtSignal( object )
    show_graph_signal = pyqtSignal()
    reloadData_signal = pyqtSignal()
    def __init__(self, parent=None):
        # 先初始化父類別, 否則在 connect event的時候會出錯
        super(MainToolBar, self).__init__(parent)

    def initSetting(self, obj, root):
        self.root = root
        self.tool = obj
        self.tool.setIconSize( QSize(40,40) )
        # toolbar上的任意 QAction 點擊事件
        self.tool.actionTriggered[QAction].connect(self.toolActionEvent)
        # 點擊 BaselineView 去啟動 chart class 中的 showBaseline()
        #self.root.actionBaselineView.toggled.connect( self.root.chart.showBaseline )
        #self.root.actionPeaksView.toggled.connect( self.root.chart.showPeaks )

    def toolActionEvent(self, toolBarObject):
        print( toolBarObject.text() )
        if toolBarObject.text() == "Home":
            pass
        elif toolBarObject.text() == "Start":
            self.start_integral_signal.emit()
        elif toolBarObject.text() == "BaselineView":
            #print( " BaselineView : ",toolBarObject.isChecked() )
            self.show_baseline_signal.emit( toolBarObject.isChecked()  )
        elif toolBarObject.text() == "PeaksView":
            #print( " PeaksView : ",toolBarObject.isChecked() )
            self.show_peaks_signal.emit( toolBarObject.isChecked()  )
        elif toolBarObject.text() == "Reload":
            #print( " PeaksView : ",toolBarObject.isChecked() )
            self.reloadData_signal.emit()
            self.show_graph_signal.emit()
            self.clear_peakTable_signal.emit()
        else:
            print( " The '{0}' be pressed ".format( toolBarObject.text() ) )

    def ActionRefresh(self):
        pass


class ChromGraph:
    chrom = None 
    info = None
    def __init__(self, obj:object):
        self.plotWidget = obj
        # 用於顯示積分底線 之 data class
        self.Integralbaseline = self.plotWidget.getPlotItem().plot()
        self.Integralbaseline.setData()

        # 顯示層析圖譜用之data class
        self.spectrum = self.plotWidget.getPlotItem().plot()
        self.spectrum.setData()

        # 用於顯示baseline 之 data class
        self.baseline = self.plotWidget.getPlotItem().plot()
        self.baseline.setData()

        # 用於顯示 peak 之 data class
        self.scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='r'), symbol='o', size=10)
        self.plotWidget.getPlotItem().addItem( self.scatter )
        self.scatter.setData()

    def connectInfo(self, info):
        self.info = info

    def clearDraw(self):
        self.Integralbaseline.setData([],[])
        self.spectrum.setData([],[])
        self.baseline.setData([],[])
        self.scatter.setData([],[])

    def refresh(self):
        pass

    def showData(self):
        self.clearDraw()
        # width 不能超過 1,  程式的 performance 會很差 
        # self.spectrum.setData(self.chrom.time, self.chrom.signal, pen=pg.mkPen('b',width=1))
        if self.info.rawData != None:
            self.spectrum.setData(self.info.rawData.time, self.info.rawData.signal, pen=pg.mkPen('b',width=1))
        else:
            self.spectrum.setData([],[])
        #self.addRect()

    def showBaseline(self,checked=None):
        # 由 MainToolBar class上 BaselineView事件作觸發, 並依該 QAction狀態決定是否顯示 baseline
        if checked == False:
            self.baseline.setData([],[])
            
        else:
            if self.info.baseline != []:
                self.baseline.setData( self.info.rawData.time,self.info.baseline, pen=pg.mkPen('r',width=1))    

    def showPeaks(self,checked):
        if checked == False:
            self.scatter.setData()
        else:
            time, signal = [], []
            print( " peak data # = ", len( self.info.Peaks ) )
            for peak in self.info.Peaks:
                time.append( peak.apex.time )
                signal.append( peak.apex.signal )
            self.scatter.setData( time,signal, pen=pg.mkPen('r',width=1))

    @logging
    def showIntegralBase(self, base_time, base_signal):
        self.Integralbaseline.setData( base_time, base_signal, pen=pg.mkPen('r',width=1) )


    def addRect(self):
        pass

    def updateRect(self):
        pass

    def closeRect(self):
        pass
        
class PeakTable(QWidget):
    title = [ "#", "Ret.Time", "Height", "Area", "Width", "Coelution #", 
        "As", "Tf", "N", "Sigma","W0.5","W0.1","W0.05" ]
    NUM, RETTIME, HEIGHT, AREA, WIDTH, COELUTION = range(6)
    def __init__(self, parent=None):
        # 先初始化父類別, 否則在 connect event的時候會出錯
        super(PeakTable, self).__init__(parent)

    def initSetting(self, obj:object):
        self.treeView = obj
        self.setHeader()

    def setHeader(self):
        '''
        self.model = QStandardItemModel(0, 6, self)
        self.model.setHeaderData(self.NUM, Qt.Horizontal, "#")
        self.model.setHeaderData(self.RETTIME, Qt.Horizontal, "Ret.Time")
        self.model.setHeaderData(self.HEIGHT, Qt.Horizontal, "Height")
        self.model.setHeaderData( self.AREA, Qt.Horizontal, "Area" )
        self.model.setHeaderData(self.WIDTH, Qt.Horizontal, "Width")
        self.model.setHeaderData( self.COELUTION, Qt.Horizontal, "Coelution #" )
        '''
        self.model = QStandardItemModel(0, len( self.title ), self)
        i=0
        for element in self.title:
            self.model.setHeaderData(i, Qt.Horizontal, element)
            i += 1

        self.treeView.setModel( self.model )

    def clear(self):
        self.model.clear()
        self.setHeader()

    def setData(self, peakList=[]):
        try:
            #self.treeView.clear()
            self.setHeader()
            i = 0
            for peak in peakList:
                #print( i, " paek ",peak.tr,", ",peak.start_time,", ",peak.end_time, )
                self.model.insertRow(i)
                element = [ i+1, peak.tr, peak.height, peak.area, peak.width, len(peak.coelution_list),
                    peak.As, peak.tf, peak.N, peak.sigma, peak.w05, peak.w01, peak.w005 ]
                j = 0
                for e in element:
                    if j == 0 or j == 5:
                        self.model.setData(self.model.index(i, j), "%.0f" % (e) )
                    elif j == 1 or j == 4:
                        self.model.setData(self.model.index(i, j), "%.2f" % (e) )
                    else:
                        self.model.setData(self.model.index(i, j), "%.4f" % (e) )
                    j += 1
                '''
                self.model.setData(self.model.index(i, self.NUM), "%.0f" % (i+1) )
                self.model.setData(self.model.index(i, self.RETTIME), "%.2f" % (peak.tr) )
                self.model.setData(self.model.index(i, self.HEIGHT), "%.4f" % (peak.height))
                self.model.setData(self.model.index(i, self.AREA), "%.4f" % (peak.area))
                self.model.setData(self.model.index(i, self.WIDTH), "%.2f" % (peak.width))
                self.model.setData(self.model.index(i, self.COELUTION), "%.0f" % ( len(peak.coelution_list) ))
                '''
                i += 1
        except Exception as e:
            print(e)

class MainWindow(MainUI, QMainWindow):
    chromOperation = None
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # ------------------------------------------------------------------------------------#
        # 進行 pyqtgraph的初始化, 
        # 需要再 PlotWidget 實體化前進行( self.setupUi(self) 前 ), 否則會出錯
        # ------------------------------------------------------------------------------------#
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # gui 初始化
        self.setupUi(self)
        # 物件初始化
        self.initObject()
        self.connectEvent()
        self.initIcon()

    def initIcon(self):
        print("set icon")
        p = path.dirname( path.abspath(__file__) )
        print(p)
        icon = QIcon()
        icon.addPixmap(QPixmap(p +"/icon/showBaseline.png"), QIcon.Normal, QIcon.Off)
        self.actionBaselineView.setIcon(icon)
        icon = QIcon()
        icon.addPixmap(QPixmap(p+"/icon/showPeaks.png"), QIcon.Normal, QIcon.Off)
        self.actionPeaksView.setIcon(icon)
        icon = QIcon()
        icon.addPixmap(QPixmap(p+"/icon/Start.png"), QIcon.Normal, QIcon.Off)
        self.actionstartAction.setIcon(icon)
        icon = QIcon()
        icon.addPixmap(QPixmap(p+"/icon/Reload.png"), QIcon.Normal, QIcon.Off)
        self.reloadAction.setIcon(icon)
        
    def initObject(self):
        # ------------------------------------------------------------------------------------#
        # GUI上之元件物件之建立
        # 新建新的 CLASS, 把與該元件相關的方法與屬性和事件封裝在一起
        # ------------------------------------------------------------------------------------#
        self.menu = MainMenuBar()
        self.tool = MainToolBar()
        self.chart = ChromGraph( self.chromView )

        self.chromOperation = ChromOperation() # 圖譜計算方法之 class

        self.peakTable = PeakTable()
        # ------------------------------------------------------------------------------------#
        # 物件之初始化, 於物件皆實體化後再執行, 有些物件彼此間進行相依  ( 待刪除 )
        # ------------------------------------------------------------------------------------#
        self.menu.initSetting( self.menubar, self )
        self.tool.initSetting( self.toolBar, self )
        self.peakTable.initSetting( self.peakTreeView )

        self.chart.connectInfo(self.chromOperation.chrom_info)
        self.chart.showData()

    def connectEvent(self):
        # ------------------------------------------------------------------------------------#
        # menu 的 signal & slot 連接
        # ------------------------------------------------------------------------------------#
        self.menu.show_ChromData_Signal.connect( self.chart.showData )
        self.menu.set_ChromData_Signal.connect( self.chromOperation.openChrom )
        
        # ------------------------------------------------------------------------------------#
        # toolbar 的 signal & slot 連接
        # ------------------------------------------------------------------------------------#
        self.tool.show_baseline_signal.connect( self.chart.showBaseline )
        self.tool.show_peaks_signal.connect( self.chart.showPeaks )
        self.tool.start_integral_signal.connect( self.startIntegral )
        self.tool.reloadData_signal.connect( self.chromOperation.reloadData )
        self.tool.reloadData_signal.connect( self.peakTable.clear )
        self.tool.show_graph_signal.connect( self.chart.showData )

    def startIntegral(self):
        # ------------------------------------------------------------------------------------#
        # 開始進行層析圖譜的積分演算法
        # ------------------------------------------------------------------------------------#
        print('start treating chromatograph')
        self.chromOperation.IntegralAlgo()
        try:
            self.peakTable.setData( self.chromOperation.chrom_info.Peaks )
        except Exception as e:
            print(e)
        base_time, base_signal = self.chromOperation.getIntegralBaseLine()
        self.chart.showIntegralBase( base_time, base_signal )
        
        
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)

    form = MainWindow()
    form.show()
    app.exec_()