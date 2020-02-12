# coding: utf-8
import numpy as np

def data_Bunching(time=[], signal = [], bunching_point=3):
    if bunching_point == 1 :
        return time, signal
    else:
        lng = len(time)
        i,j = 0, 0
        b_time, b_signal = [], []
        while i <= lng-1:
            sub_time, sub_signal = [], []
            for j in range( bunching_point ):
                if i == lng-1:
                    break
                sub_time.append( time[i] )
                sub_signal.append( signal[i] )
                i += 1
            if i == lng-1:
                    break
            b_time.append( np.mean( sub_time ) )
            b_signal.append( np.mean( sub_signal ) )
        return b_time, b_signal


def pseudo_gaussian_smooth(signal=[],sigma=7,mode="nearest"):
    # pseudo_gaussian_smooth / haystack smooth 
    from scipy.ndimage.filters import gaussian_filter as gaussian_filter
    smooth = gaussian_filter(signal, sigma, 0, None, mode)
    smoothdata = smooth.tolist()
    return smoothdata

def Savitzky_Golay_Smooth(signal=[], windowsize=5, order=3, mode="nearest"):
    from scipy.signal import savgol_filter
    smooth = savgol_filter(np.array(signal), windowsize, order, 0, 1.0, -1, mode="nearest")
    smoothdata = smooth.tolist()
    return smoothdata

def Moving_average(Signal=[],windowsize=3):
    """
    移動平均法：
    輸入：
        Signal ：1-D array訊號
        windowsize：平滑區間大小, 整數, 最小值為3
    輸出：
        smooth：1-D array訊號(平滑數據)
    參考資料：
    https://stackoverflow.com/questions/14313510/how-to-calculate-moving-average-using-numpy
    """
    smooth = np.cumsum(Signal, dtype=float)
    smooth[windowsize:] = smooth[windowsize:] - smooth[:-windowsize]
    smooth = smooth[windowsize - 1:] / windowsize
    smoothdata = smooth.tolist()
    #使平滑後的數據長度與初始數據長度能一致
    for n in range( windowsize-1 ):
        smoothdata.insert(0,smooth[0])
    
    return smoothdata