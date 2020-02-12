import sys
from os import path
import csv

from SettingWindowUI import Ui_Form as SettingUI
if __name__ == '__main__':
    sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from PyQt5.QtWidgets import QWidget
from conf.ChromAlgoSetting import ChromSetting
from lib.DebugLog import logging 

class SettingWindow(SettingUI, QWidget):
    data = None
    def __init__(self, parent=None):
        super(SettingWindow, self).__init__(parent)
        self.setupUi(self)
        self.save_pushButton.clicked.connect(self.SaveSetting)

    @logging
    def LoadSetting(self,settingData:ChromSetting):
        self.data = settingData
        if self.data == None:
            return

        self.sampling_spinBox.setValue(self.data.setting["Sampling Frequency"] )
        self.preprocess_window_spinBox.setValue( self.data.setting["Smooth_Filter"]["Window Length"] )
        self.bunching_spinBox.setValue( self.data.setting["Smooth_Filter"]["Bunching Point"] )

        self.threshold_doubleSpinBox.setValue( self.data.setting["Peak_Detection"]["Threshold Rate"] )
        self.offset_doubleSpinBox.setValue( self.data.setting["Peak_Detection"]["Peaks Search Offset"] )
        self.timewindow_doubleSpinBox.setValue( self.data.setting["Peak_Detection"]["MAX_TIME_WIDTH"] )
        self.peakInterval_doubleSpinBox.setValue( self.data.setting["Peak_Detection"]["MIN_PEAK_INTERVAL"] )

        self.detrand_lambda_SpinBox.setValue( self.data.setting["Detrand"] )
        self.differential_window_SpinBox.setValue( self.data.setting["Differential"]["Window Length"] )

    @logging
    def SaveSetting(self,*args, **kwargs):
        if self.data == None:
            return
        self.data.setting["Sampling Frequency"] = self.sampling_spinBox.value()
        self.data.setting["Smooth_Filter"]["Window Length"] = self.preprocess_window_spinBox.value()
        self.data.setting["Smooth_Filter"]["Bunching Point"] = self.bunching_spinBox.value()

        self.data.setting["Peak_Detection"]["Threshold Rate"] = self.threshold_doubleSpinBox.value()
        self.data.setting["Peak_Detection"]["Peaks Search Offset"] = self.offset_doubleSpinBox.value()
        self.data.setting["Peak_Detection"]["MAX_TIME_WIDTH"] = self.timewindow_doubleSpinBox.value()
        self.data.setting["Peak_Detection"]["MIN_PEAK_INTERVAL"] = self.peakInterval_doubleSpinBox.value()

        self.data.setting["Detrand"] = self.detrand_lambda_SpinBox.value()
        self.data.setting["Differential"]["Window Length"] = self.differential_window_SpinBox.value()
        self.data.save_ParFile()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    form = SettingWindow()

    chrom_setting = ChromSetting()
    form.LoadSetting(chrom_setting)

    form.show()
    app.exec_()