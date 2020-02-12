# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindowUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.chromView = PlotWidget(self.centralwidget)
        self.chromView.setObjectName("chromView")
        self.gridLayout.addWidget(self.chromView, 0, 0, 1, 2)
        self.peakTreeView = QtWidgets.QTreeView(self.centralwidget)
        self.peakTreeView.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.peakTreeView.sizePolicy().hasHeightForWidth())
        self.peakTreeView.setSizePolicy(sizePolicy)
        self.peakTreeView.setMaximumSize(QtCore.QSize(16777215, 250))
        self.peakTreeView.setStyleSheet("QTreeWidget {\n"
"   font-size: 24pt;\n"
"}\n"
"\n"
"")
        self.peakTreeView.setObjectName("peakTreeView")
        self.gridLayout.addWidget(self.peakTreeView, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSetting = QtWidgets.QMenu(self.menubar)
        self.menuSetting.setObjectName("menuSetting")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuReport = QtWidgets.QMenu(self.menubar)
        self.menuReport.setObjectName("menuReport")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.reloadAction = QtWidgets.QAction(MainWindow)
        self.reloadAction.setObjectName("reloadAction")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionstartAction = QtWidgets.QAction(MainWindow)
        self.actionstartAction.setObjectName("actionstartAction")
        self.actionBaselineView = QtWidgets.QAction(MainWindow)
        self.actionBaselineView.setCheckable(True)
        self.actionBaselineView.setObjectName("actionBaselineView")
        self.actionPeaksView = QtWidgets.QAction(MainWindow)
        self.actionPeaksView.setCheckable(True)
        self.actionPeaksView.setObjectName("actionPeaksView")
        self.actionSetting = QtWidgets.QAction(MainWindow)
        self.actionSetting.setObjectName("actionSetting")
        self.actionView_in_Matplotlib = QtWidgets.QAction(MainWindow)
        self.actionView_in_Matplotlib.setObjectName("actionView_in_Matplotlib")
        self.actionExport_Excel = QtWidgets.QAction(MainWindow)
        self.actionExport_Excel.setObjectName("actionExport_Excel")
        self.menuFile.addAction(self.actionOpen)
        self.menuSetting.addAction(self.actionSetting)
        self.menuView.addAction(self.actionView_in_Matplotlib)
        self.menuReport.addAction(self.actionExport_Excel)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSetting.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuReport.menuAction())
        self.toolBar.addAction(self.actionstartAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.reloadAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionBaselineView)
        self.toolBar.addAction(self.actionPeaksView)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuSetting.setTitle(_translate("MainWindow", "Setting"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuReport.setTitle(_translate("MainWindow", "Report"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.reloadAction.setText(_translate("MainWindow", "Reload"))
        self.reloadAction.setToolTip(_translate("MainWindow", "Reload Data"))
        self.actionOpen.setText(_translate("MainWindow", "Open File"))
        self.actionstartAction.setText(_translate("MainWindow", "Start"))
        self.actionBaselineView.setText(_translate("MainWindow", "BaselineView"))
        self.actionBaselineView.setToolTip(_translate("MainWindow", "show Baseline"))
        self.actionPeaksView.setText(_translate("MainWindow", "PeaksView"))
        self.actionPeaksView.setToolTip(_translate("MainWindow", "Show Peaks"))
        self.actionSetting.setText(_translate("MainWindow", "Setting"))
        self.actionView_in_Matplotlib.setText(_translate("MainWindow", "View in Matplotlib"))
        self.actionExport_Excel.setText(_translate("MainWindow", "Export Excel"))

from pyqtgraph import PlotWidget
