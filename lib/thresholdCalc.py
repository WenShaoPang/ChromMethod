# coding: utf-8

import numpy as np


def get_median(data = []):
    #計算數據的中位數

    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2


def threshold(data =[], rate = 10):
    # 計算數值中的閥值

    median = get_median(data)
    D = get_median( [ abs( median - data[i]) for i in range( len( data)) ])
    return [ median - rate*D, median + rate*D]


def thresholdCalc( data = [] , mode = "D1D2", p1 = 10, p2 = 10):
    if( mode == "D1" ):
        try:
            return threshold( data, p1)
        except:
            print( "mode({0} error".format(mode) )
    
    elif( mode == "D1D2" ):
        try:
            FD = threshold( data[0], p1)
            SD = threshold( data[1], p2)
            return [ FD, SD]
        except:
            print( "mode({0} error".format(mode) )

    else:
        print( "mode error")

