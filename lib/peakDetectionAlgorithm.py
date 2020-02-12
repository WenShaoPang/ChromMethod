# coding: utf-8
import numpy as np
if __name__ == '__main__':
    import sys
    from os import path
    sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from lib.DebugLog import logging 

def ifCrossZero( fragment):
    mid_index = round( len(fragment) )-1
    front_check = True
    back_check = True
    for i in fragment[:mid_index]:
        if i > 0:
            front_check = False
            break
    for i in fragment[ mid_index: ]:
        if i < 0:
            back_check = False
            break
    return front_check and back_check

@logging
def peakSearchAlgorithm(
    data, 
    deriv_data, 
    up_frt_threshold, 
    down_frt_threshold,
    down_snd_threshold, 
    offset=10,
    MAX_TIME_WIDTH = 0.5
    ):
    """
    Peak Search Algorithm:
    使用訊號的一階二階與三階微分進行訊號peak的搜尋。
    一階微分用於大略判斷可能有peakk存在的位置，當發現可能有peak存在時，
    接著使用三階微分判斷peak精確位置與數量, 最後在使用二階微分作為閾值過濾不需要的小peaks
    Input:
        data : [ Time:list, signal:list ]
        deriv_data : [ first deriv signal:list, seconnd deriv signal:list , third deriv signal:lsit ]
        up_frt_threshold
        down_frt_threshold
        down_snd_threshold
        offset
        MAX_TIME_WIDTH

    Return Boundary table
    格式:
    +---------------+---------------+---------------+---------------------+
    |  start_index  | highest index |   end index   |  apex_index (list)  |
    +---------------+---------------+---------------+---------------------+
    |  start_index  | highest index |   end index   |  apex_index (list)  |
    +---------------+---------------+---------------+---------------------+
    + ....................................................................+

    """
    # -----------------------------------------------------------------
    print( 
        "In peakSearchAlgorithm , up_snd_threshold : ",up_frt_threshold,
        ", down_snd_threshold : ", down_frt_threshold 
        )
    time, signal = data[0], data[1]
    frt_deriv, snd_deriv, trd_deriv = deriv_data[0], deriv_data[1], deriv_data[2]
    index = 0
    # 用於儲存 peaks 的list
    peaks_list = []
    # 考慮到有 共析 peaks, 故 apex_index 以 list 的形式, 儲存單靠斜率無法區分的peak
    start_index, apex_index, end_index = 0, [], 0
    # 控制演算法進行何者步驟
    MODE = 'Search Start Point'
    PEAK_SREACH_WINDOW = 3
    snd_step_start_index = 0
    # 用於第三步驟的退出機制
    # MAX_TIME_WIDTH = 0.5

    while index < len( trd_deriv )-offset :
        # 搜尋 peak 的起始點 ( 表示接下來可能有peak的存在 ) 
        if MODE == 'Search Start Point':
            if frt_deriv[index] >= up_frt_threshold:
                start_index =  int(index - offset/2)
                MODE = 'Pre Search Apex'

        elif MODE == 'Pre Search Apex':
            # 搜尋是否有 apex ( 三次微分 cross 0 )
            #if ( trd_deriv[ index ] == 0 ) or ( trd_deriv[ index-1 ]<0 and trd_deriv[ index ]>0 ):
            if ifCrossZero( trd_deriv[ index -PEAK_SREACH_WINDOW: index +PEAK_SREACH_WINDOW ]):
                if snd_deriv[index] < down_snd_threshold:
                    apex_index.append( index )
            if frt_deriv[ index ] <= up_frt_threshold:
                MODE = 'Back Search Apex'
                snd_step_start_index = index

        elif MODE == 'Back Search Apex':
            # 檢查第三步驟是否過長( cross 0 後, 訊號是否有往低於下閥值的趨勢 ), 則退出peak搜尋
            if time[ index ] - time[ snd_step_start_index ] > MAX_TIME_WIDTH:
                apex_index = []
                MODE = 'Search Start Point'
            # 若此時出現一階微分高於一階微分的上閾值時, 表示前面的訊號可能只是baseline的起伏,故重新第二步驟
            if frt_deriv[index] >= up_frt_threshold:
                start_index =  int(index - offset/2) #重新設定起始點
                MODE = 'Pre Search Apex'

            #if ( trd_deriv[ index ] == 0 ) or ( trd_deriv[ index-1 ]<0 and trd_deriv[ index ]>0 ):
            if ifCrossZero( trd_deriv[ index -PEAK_SREACH_WINDOW: index +PEAK_SREACH_WINDOW ]):
                if snd_deriv[index] < down_snd_threshold:
                    apex_index.append( index )
            if frt_deriv[ index ] <= down_frt_threshold:
                MODE = 'Search End Point'

        elif MODE == 'Search End Point':
            #if ( trd_deriv[ index ] == 0 ) or ( trd_deriv[ index-1 ]<0 and trd_deriv[ index ]>0 ):
            if ifCrossZero( trd_deriv[ index -PEAK_SREACH_WINDOW: index +PEAK_SREACH_WINDOW ]):
                if snd_deriv[index] < down_snd_threshold:
                    apex_index.append( index )
            if frt_deriv[index] >= down_frt_threshold :
                # 檢查 peak 的終點是否會超出訊號最後一筆的index
                # 並令一個window大小的範圍中之最小值為 peak 的終點
                if int(index + offset/2) <= len( trd_deriv ):
                    min_value = min( signal[ index-int(offset/2):index+int(offset/2) ] )
                    sub_index = signal[ index-int(offset/2):index+int(offset/2) ].index( min_value )
                    end_index = sub_index + index-int(offset/2)
                else:
                    min_value = min( signal[ index-int(offset/2):index ] )
                    sub_index = signal[ index-int(offset/2):index ].index( min_value )
                    end_index = sub_index + index-int(offset/2)
                print( "Peak : len(apex)={0}, start time={1}, end time={2} ".format( len(apex_index), time[start_index], time[end_index] ) )
                # 把成功搜尋到的peak儲存起來
                # 若一個 peak 找不到 apex, 則不儲存
                if len(apex_index) > 0:
                    # 以 peak 範圍內的最高點作為 apex 位置
                    highest_index = signal[start_index:end_index].index( max( signal[start_index:end_index] ) ) + start_index
                    peaks_list.append(  [ start_index, highest_index, end_index, apex_index ]  )
                apex_index = []
                MODE = 'Search Start Point'
        else:
            print( "peakSearchAlgorithm Error : MODE '{0}' error".format( MODE ) )
        # 預防 index 超出訊號長度大小之退出機制
        if index + 1 >= len( trd_deriv ):
            print("Error : index = ",index)
            break
        index += 1
    return peaks_list

@logging
def adjustPeaksBoundary( time, signal, peak_table, baseline, MIN_PEAK_INTERVAL = 0.4 ):
    """
    尋找是否有共析的peaks, 若有, 則調整該peaks的邊界
    Return Boundary table
    格式:
    +--------------+--------------+--------------+--------------+
    |  start_time  | start_signal |   end_time   |  end_signal  |
    +--------------+--------------+--------------+--------------+
    |  start_time  | start_signal |   end_time   |  end_signal  |
    +--------------+--------------+--------------+--------------+
    """
    # 作為 peaks 間最小時間間距, 若小於此值, 則peaks間可能共析, 並需要調整其 boundary
    # MIN_PEAK_INTERVAL = 0.4
    boundary_table = []
    # 尋找 coelution peak, 並建立 peak_cluster
    # 其中 peak_cluster 儲存的數值為 peak table 的index
    table_index = 0
    peak_cluster = [ [table_index] ]
    while table_index < len(peak_table)-1:
        if (time[ peak_table[table_index+1][0] ] - time[ peak_table[table_index][1] ] ) < MIN_PEAK_INTERVAL:
            # ----------- 共析的情況 -----------
            while (time[ peak_table[table_index+1][0] ] - time[ peak_table[table_index][1] ] ) < MIN_PEAK_INTERVAL:
                # 找尋哪些peaks共析在一起
                peak_cluster[-1].append( table_index+1 )
                table_index += 1
                if table_index >= len(peak_table)-1:
                    break
        else:
            # ----------- 未有共析的情況 -----------
            peak_cluster.append( [table_index+1 ] )
            table_index += 1

    index, start_index, end_index =0,0,0
    boundary_table =[]
    for i in range( len( peak_cluster ) ):
        if len( peak_cluster[i] ) > 1:
            # ---------- 為共析 peak 的情況 ----------
            temp_copeak_boundary = []
            # 建立初始 peak index boundary 
            for peak_table_index in peak_cluster[i] :
                # peak : [ start index, apex index, end index, [colution] ]
                peak = peak_table[ peak_table_index ]
                temp_copeak_boundary.append( [peak[0], peak[2]] )
            # 調整共析peak的 index boundary
            cut_time, cut_signal = [], []
            for j in range( len(temp_copeak_boundary)-1 ):
                interval = [
                    min( temp_copeak_boundary[j][1], temp_copeak_boundary[j+1][0] ),
                    max( temp_copeak_boundary[j][1], temp_copeak_boundary[j+1][0] )
                ]
                cut_signal = signal[ interval[0]:interval[1] ]
                if cut_signal != []:
                    min_location = cut_signal.index( min( cut_signal ) ) + interval[0]
                else:
                    min_location = temp_copeak_boundary[j][1]
                temp_copeak_boundary[j][1] = min_location
                temp_copeak_boundary[j+1][0] = min_location
            # ------ 計算 bseline line 一元一次線性方程式 ------
            # cut_time, cut_signal 用於後面程式碼縮短之用途( 非必要 )
            cut_time = time[ temp_copeak_boundary[0][0]: temp_copeak_boundary[-1][1] ]
            cut_signal = signal[ temp_copeak_boundary[0][0]: temp_copeak_boundary[-1][1] ]
            a = ( cut_signal[-1] - cut_signal[0] ) / ( cut_time[-1] - cut_time[0] )
            b = ( cut_time[-1]*cut_signal[0] - cut_time[0]*cut_signal[-1] ) / ( cut_time[-1] - cut_time[0] )
            # 把新的peak boundary 加入 boundary table中
            for peak_boundary_index in temp_copeak_boundary:
                # 以原始訊號, 基線, 積分基線三者中的最小值作為 peak 的 boundary
                start_signal = min( 
                    a*( time[ peak_boundary_index[0] ] )+b, 
                    signal[peak_boundary_index[0]],
                    baseline[ peak_boundary_index[0] ]
                    )
                end_signal = min( 
                    a*( time[ peak_boundary_index[1] ] )+b, 
                    signal[peak_boundary_index[1]],
                    baseline[ peak_boundary_index[0] ]
                    )
                boundary_table.append(
                    [ time[peak_boundary_index[0]], start_signal, time[peak_boundary_index[1]], end_signal ]  
                    )

        elif len( peak_cluster[i] ) == 1:
            # ---------- 為單根 peak 的情況 ----------
            index = peak_cluster[i][0]
            start_index = peak_table[index][0]
            end_index = peak_table[index][2]
            boundary_table.append( [ time[start_index], signal[start_index], time[end_index], signal[end_index] ] )
        else:
            print( "Error : peak_clustrt[{i}] : {content}".format(i=i,content=peak_cluster[i]) )
    return boundary_table

#=====================================================================================

# 尋找peak
def peakDetectionAlgorithm( third_derivate=[], windowsize=5  ):
    # 使用三次微分來對peak做搜尋 

    num = int( (windowsize/2) )
    peak_index, front_window, back_window = [], [], []
    index = 0 + num 
    startPoint =0,

    print('max length = {0}'.format( len( third_derivate) -num*2))
    for i in range( len( third_derivate )-num*2 ):
        if(index - num  < 0):
            startPoint = 0
        else:
            startPoint = index - num

        front_window = third_derivate[ startPoint:index ]
        back_window = third_derivate[ index+1 : index+num+1 ]
        
        a = False
        for j in range( len(front_window)):
            if front_window[j] < 0:
                continue
            elif front_window[j] > 0:
                a = True
                break

        b = False
        for k in range( len(back_window)):
            if back_window[k] > 0:
                continue
            elif back_window[k] < 0:
                b = True
                break
            
        if a == False :
            if b == False:
                # peak 符合條件
                # 注意 ( +1 ) 影響到 peak 的重覆判定
                # 情況 ( --- +++) 由於沒有不一定有0的資料, 導致在+-交界的前一筆與後一筆都被判斷成peak
                peak_index.append(index)
                index += 1  
        if index > len( third_derivate)-1:
            # 如果迴圈次數大於資料大小, 則跳出迴圈
            break            
        index += 1
    return peak_index 


def peakFilter( peak_index=[], second_derivate=[], threshold=0 ):
    # 使用二次微分與其閥值來對所找到的peak做篩選

    newPeakIndex = []
    for i in range( len( peak_index) ):
        
        index = peak_index[i]

        try:
            sd = second_derivate[ index ]
        except:
            print("list index ot of range")
            print("len(second_derivate) = {0}, index = {1}".format(len(second_derivate), index))
            sd = 0
        if( sd < threshold ):
            newPeakIndex.append( index )
    return newPeakIndex


def PeakDetectionAlgorithm( time=[], signal=[], second_derivate=[], third_derivate=[], windowsize=5, sd_threshold=0 ):
    # 主方法介面

    peakTime, peakSignal, peakIndex = [], [], []
    peakIndex = peakDetectionAlgorithm( third_derivate, windowsize)
    peakIndex = peakFilter( peakIndex, second_derivate, sd_threshold)
    
    for i in range( len( peakIndex)):
        index = peakIndex[i]
        peakTime.append( time[index] )
        peakSignal.append( signal[index] )
    return peakTime, peakSignal, peakIndex

