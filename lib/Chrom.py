# -*- coding: utf-8 -*-
import numpy as np
from scipy.signal import savgol_filter
if __name__ == '__main__':
    import sys
    from os import path
    sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from conf.ChromAlgoSetting import ChromSetting
from lib.OpenChromFile import FileOpenClass
from lib.Smoother import Moving_average, data_Bunching
from lib import AirPLS
from lib.peakDetectionAlgorithm import adjustPeaksBoundary, peakSearchAlgorithm
from lib.thresholdCalc import threshold
from lib.DebugLog import logging

def ViewInMatplotlib(time, signal):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot( time, signal )
    plt.scatter( time, signal )
    plt.show()


class ChromData:
    file_path=''
    file_name=''
    time , signal = [], []
    def __init__(self, x=[], y=[], path="", filename=""):
        self.time=x
        self.signal=y
        self.file_path=path
        self.file_name = filename

    def setData(self, x=[], y=[], path="", filename=""):
        self.time=x
        self.signal=y
        self.file_path=path
        self.file_name = filename

class Point:
    time=0
    signal=0 
    def __init__(self, time, signal):
        self.time = time
        self.signal = signal

class Boundary:
    front = None # class Point (儲存起始點的資訊)
    end = None # class Point (儲存終點的資訊)
    def __init__(self, start_time, start_signal, end_time, end_signal):
        self.front = Point(start_time, start_signal)
        self.end = Point( end_time, end_signal )

class Peak:
    # peak 的直接資訊
    apex_index = None # 最高頂點的time index
    height,tr, width ,area = None,None,0,None # peak 的積分面積 ( 減去基線 )
    # peak 的非對稱資訊
    w05,w01,w005,tf,As,N= 0,0,0,1,1,0
    # peak 的 model 資訊
    detrand_height, sigma, model = None, None, None
    
    # peak 的點的資訊
    apex =None # class Point (儲存最高頂點的參數)
    boundary=None # class Boundary (儲存 peak boundary的資訊)
    coelution_list=None # list (儲存高度共析而不可分的apex index)
    
    def __init__(self, t, h, data_index, area):

        self.apex_index = data_index
        self.apex = Point(t,h)
        self.height = h
        self.tr = t
        self.area = area

    def setBoundary(self, boundary:Boundary):
        self.boundary = boundary
        self.width = self.boundary.end.time - self.boundary.front.time

class ChromInfo:
    baseline = []
    Peaks = []
    # ChromData Class
    rawData = ChromData
    def __init__(self):
        self.baseline = []
        self.Peaks = []
        self.rawData = ChromData()

    def clearData(self):
        self.baseline = []
        self.Peaks = []
        self.rawData = ChromData()

class ChromAlgorithm:
    setting = ChromSetting
    def __init__(self,setting:ChromSetting):
        self.setting = setting

    def dataBunch(self, chrom_info:ChromInfo):
        chrom_info.rawData.time, chrom_info.rawData.signal = data_Bunching( 
            chrom_info.rawData.time, 
            chrom_info.rawData.signal, 
            self.setting.setting["Smooth_Filter"]["Bunching Point"] 
            )
        return chrom_info

    def detrand(self, chrom_info:ChromInfo, method='airPLS'):
        # ----- return baseline ------
        if method == 'airPLS':
            chrom_info.baseline = AirPLS.airPLS( 
            np.array( chrom_info.rawData.signal), lambda_= self.setting.setting["Detrand"]
            )
        else:
            chrom_info.baseline = []

    def preProcess(self, chrom_info:ChromInfo):
        '''
        Return:
            [ first deriv signal, second deriv signal, third deriv signal ]
            [ first theshold[down,up], second threshold[down,up] ]
        '''
        Diff_Window_Length = self.setting.setting["Differential"]["Window Length"]
        Smooth_Window_Length = self.setting.setting["Smooth_Filter"]["Window Length"]
        Threshold_Rate = self.setting.setting["Peak_Detection"]["Threshold Rate"]

        process_signal = savgol_filter( chrom_info.rawData.signal, window_length=Smooth_Window_Length, polyorder=2 )
        process_signal = Moving_average( process_signal, Smooth_Window_Length )
        
        frt_deriv = savgol_filter(process_signal, window_length=Diff_Window_Length, polyorder=2,deriv=1 )
        frt_deriv = Moving_average( frt_deriv, Smooth_Window_Length )
        
        snd_deriv = savgol_filter(process_signal, window_length=Diff_Window_Length, polyorder=2,deriv=2 )
        snd_deriv = Moving_average( snd_deriv, Smooth_Window_Length )
        #snd_deriv = savgol_filter(snd_deriv, window_length=7, polyorder=3,deriv=2 )

        third_deriv = savgol_filter( snd_deriv, window_length=Diff_Window_Length, polyorder=2,deriv=1 )
        third_deriv = Moving_average( third_deriv, Smooth_Window_Length )
        third_deriv = savgol_filter( third_deriv, window_length=Smooth_Window_Length, polyorder=2 )

        updown_frt_threshold = threshold( frt_deriv.copy(), Threshold_Rate )
        updown_snd_threshold = threshold( snd_deriv.copy(), Threshold_Rate )
        return [frt_deriv,snd_deriv,third_deriv ], [updown_frt_threshold, updown_snd_threshold]

    def PeakSearch(self, chrom_info:ChromInfo, deriv=[], threshold=[]):
        peak_table = peakSearchAlgorithm(
            [ chrom_info.rawData.time, chrom_info.rawData.signal ],
            deriv, 
            threshold[0][1], 
            threshold[0][0],
            threshold[1][0], 
            offset = self.setting.setting["Peak_Detection"]["Peaks Search Offset"],
            MAX_TIME_WIDTH = self.setting.setting["Peak_Detection"]["MAX_TIME_WIDTH"]
        )
        return peak_table

    def adjustPeaksBoundary(self, peak_table:list, chrom_info:ChromInfo):
        boundary_table = adjustPeaksBoundary(
            chrom_info.rawData.time, chrom_info.rawData.signal, peak_table, chrom_info.baseline,
            MIN_PEAK_INTERVAL = self.setting.setting["Peak_Detection"]["MIN_PEAK_INTERVAL"]
            )
        return boundary_table

    def build_Peak_List(self, peak_table:list, boundary_table:list, chrom_info:ChromInfo):
        i = 0
        for peak in peak_table:
            # 把
            boundary = Boundary( boundary_table[i][0], boundary_table[i][1], boundary_table[i][2], boundary_table[i][3])
            front_index = chrom_info.rawData.time.index( boundary.front.time )
            end_index = chrom_info.rawData.time.index( boundary.end.time )
            area_1 = np.trapz(
                chrom_info.rawData.signal[ front_index:end_index ], 
                chrom_info.rawData.time[ front_index:end_index ] )
            base = (
                ( boundary.front.signal + boundary.end.signal ) * 
                ( chrom_info.rawData.time[ end_index ] - chrom_info.rawData.time[ front_index ])/2 
                )
            area = area_1 -base
            '''
            print( i, " peak ", peak[1], ", ",
                self.chromdata.time[ front_index ],", ",
                self.chromdata.time[ end_index ],", ",
                area_1,
                base,
                area_1-base
                )
            '''
            p = Peak( chrom_info.rawData.time[ peak[1] ], chrom_info.rawData.signal[ peak[1] ], peak[1], area )
            p.setBoundary( boundary )
            p.coelution_list = peak[3]
            chrom_info.Peaks.append( p )
            i += 1

    def getIntegralBaseline(self, info:ChromInfo):
        if len(info.Peaks) == 0:
            return
        index, peak_index = 0, 0
        base_time, base_signal = [],[]
        while index < len( info.rawData.time ):
            test_peak = info.Peaks[peak_index]
            if test_peak.boundary.front.time <= info.rawData.time[index] <= test_peak.boundary.end.time:
                print( "peak # : {0}".format(peak_index) )
                base_time.append( test_peak.boundary.front.time )
                base_time.append( test_peak.boundary.front.time )
                base_time.append( test_peak.boundary.front.time )
                base_time.append( test_peak.boundary.end.time )
                base_time.append( test_peak.boundary.end.time )
                base_time.append( test_peak.boundary.end.time )
                

                base_signal.append( test_peak.boundary.front.signal )
                base_signal.append( 
                    info.rawData.signal[ info.rawData.time.index( test_peak.boundary.front.time ) ]
                )
                base_signal.append( test_peak.boundary.front.signal )
                base_signal.append( test_peak.boundary.end.signal )
                base_signal.append( 
                    info.rawData.signal[ info.rawData.time.index( test_peak.boundary.end.time ) ]
                )
                base_signal.append( test_peak.boundary.end.signal )

                peak_index += 1
                index = info.rawData.time.index( test_peak.boundary.end.time )
            else:
                base_time.append( info.rawData.time[index] )
                base_signal.append( info.rawData.signal[index] )
                index += 1
            if peak_index >= len( info.Peaks ):
                break
        return base_time, base_signal

    def peaksHeightFilter(self,info:ChromInfo):
        baseline = info.rawData.signal[0]
        new_peak_list=[]
        for peak in info.Peaks:
            if peak.apex.signal > baseline*1.1:
                new_peak_list.append( peak )
        info.Peaks = new_peak_list

    def calcPeakSymmetry(self,peak:Peak,info:ChromInfo):
        signal, time = info.rawData.signal, info.rawData.time
        front_index, back_index=0,0
        # 求 w0.5, sigma
        goal_height = ( peak.height - peak.boundary.front.signal )*0.5 + peak.boundary.front.signal
        front_index = self.__searchTargetHeight( 
            signal, peak.apex_index,goal_height, time.index( peak.boundary.front.time ), mode="-" )
        back_index = self.__searchTargetHeight( 
            signal, peak.apex_index,goal_height, time.index( peak.boundary.end.time ), mode="+" )
        w05 = time[back_index] - time[front_index]
        sigma = w05/2.355
        N = 5.54 * ( peak.tr*peak.tr ) / ( w05*w05 )
        # 求 w0.1 & As
        goal_height = ( peak.height - peak.boundary.front.signal )*0.1 + peak.boundary.front.signal
        front_index = self.__searchTargetHeight( 
            signal, peak.apex_index,goal_height, time.index( peak.boundary.front.time ), mode="-" )
        back_index = self.__searchTargetHeight( 
            signal, peak.apex_index,goal_height, time.index( peak.boundary.end.time ), mode="+" )
        w01 = time[back_index] - time[front_index]
        As = ( time[back_index] - peak.tr )/ ( peak.tr - time[front_index] )
        # 求 w0.05 & tf
        goal_height = ( peak.height - peak.boundary.front.signal )*0.05 + peak.boundary.front.signal
        front_index = self.__searchTargetHeight( 
            signal, peak.apex_index,goal_height, time.index( peak.boundary.front.time ), mode="-" )
        back_index = self.__searchTargetHeight( 
            signal, peak.apex_index,goal_height, time.index( peak.boundary.end.time ), mode="+" )
        w005 = time[back_index] - time[front_index]
        a = peak.tr - time[front_index]
        b = time[back_index] - peak.tr
        tf = ( a+b ) / ( 2*a )

        peak.w05 = w05
        peak.sigma = sigma 
        peak.N = N
        peak.w01 = w01
        peak.As = As
        peak.w005 = w005
        peak.tf = tf
        return peak


    def __searchTargetHeight(self, signal=[], start_index=0, goal_signal=0,end_index=0 ,mode="+"):
        now_index = start_index
        while signal[now_index] > goal_signal:
            if now_index == end_index:
                break
            if mode == "+":
                now_index += 1
            elif mode == "-":
                now_index -= 1
            else:
                print("mode error : {0}".format( mode ) )
                break
        return now_index



class ChromOperation:
    chrom_Setting = None
    chrom_info = None
    def __init__(self):
        self.chrom_info = ChromInfo()
        self.chrom_Setting = ChromSetting()
        self.algorithm = ChromAlgorithm( self.chrom_Setting )

    @logging
    def openChrom(self, path="", ifDataBunch=True):
        print(path)
        chromFileObj = FileOpenClass(path)
        x,y, filename, filepath = chromFileObj.getFileData()
        self.chrom_info.rawData = ChromData(x,y,filepath,filename)
        if ifDataBunch:
            self.algorithm.dataBunch( self.chrom_info )

    def clearInfo(self):
        self.chrom_info.clearData()

    def reloadData(self):
        filepath = self.chrom_info.rawData.file_path
        self.clearInfo()
        self.openChrom( filepath )

    def getRawData(self):
        return self.chrom_info.rawData


    def getIntegralBaseLine(self):
        time, signal = self.algorithm.getIntegralBaseline( self.chrom_info )
        return time, signal
        
    @logging
    def IntegralAlgo(self):
        self.algorithm.detrand( self.chrom_info )
        deriv, threshold = self.algorithm.preProcess( self.chrom_info )
        peak_table = self.algorithm.PeakSearch( self.chrom_info, deriv, threshold )
        boundary_table = self.algorithm.adjustPeaksBoundary( peak_table, self.chrom_info )
        
        self.chrom_info.Peaks = []
        print( "Result # of peaks : ",len(peak_table) )
        self.algorithm.build_Peak_List( peak_table, boundary_table,self.chrom_info )
        self.algorithm.peaksHeightFilter(self.chrom_info)

        for i in range( len(self.chrom_info.Peaks) ):
            peak = self.algorithm.calcPeakSymmetry( self.chrom_info.Peaks[i], self.chrom_info )
            self.chrom_info.Peaks[i] = peak
        
        



            