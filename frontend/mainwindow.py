# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from guimanager import GUIManager


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(853, 674)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(MainWindow)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.titleView = QtWidgets.QHBoxLayout()
        self.titleView.setObjectName("titleView")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.titleView.addItem(spacerItem)
        self.labelTitle = QtWidgets.QLabel(MainWindow)
        self.labelTitle.setTextFormat(QtCore.Qt.MarkdownText)
        self.labelTitle.setObjectName("labelTitle")
        self.titleView.addWidget(self.labelTitle)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.titleView.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.titleView)
        self.gridViewRobotinoManager = QtWidgets.QGridLayout()
        self.gridViewRobotinoManager.setObjectName("gridViewRobotinoManager")
        self.buttonStopCommandServer = QtWidgets.QPushButton(MainWindow)
        self.buttonStopCommandServer.setAutoDefault(False)
        self.buttonStopCommandServer.setObjectName("buttonStopCommandServer")
        self.gridViewRobotinoManager.addWidget(
            self.buttonStopCommandServer, 2, 1, 1, 1)
        self.lableTitleRobotinoManager = QtWidgets.QLabel(MainWindow)
        self.lableTitleRobotinoManager.setTextFormat(QtCore.Qt.MarkdownText)
        self.lableTitleRobotinoManager.setObjectName(
            "lableTitleRobotinoManager")
        self.gridViewRobotinoManager.addWidget(
            self.lableTitleRobotinoManager, 0, 0, 1, 1)
        self.buttonStartCommandServer = QtWidgets.QPushButton(MainWindow)
        self.buttonStartCommandServer.setCheckable(False)
        self.buttonStartCommandServer.setAutoDefault(False)
        self.buttonStartCommandServer.setDefault(False)
        self.buttonStartCommandServer.setFlat(False)
        self.buttonStartCommandServer.setObjectName("buttonStartCommandServer")
        self.gridViewRobotinoManager.addWidget(
            self.buttonStartCommandServer, 2, 0, 1, 1)
        self.tableViewRobotinos = QtWidgets.QTableWidget(MainWindow)
        self.tableViewRobotinos.setRowCount(5)
        self.tableViewRobotinos.setColumnCount(5)
        self.tableViewRobotinos.setObjectName("tableViewRobotinos")
        item = QtWidgets.QTableWidgetItem()
        self.tableViewRobotinos.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableViewRobotinos.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableViewRobotinos.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableViewRobotinos.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableViewRobotinos.setHorizontalHeaderItem(4, item)
        self.gridViewRobotinoManager.addWidget(
            self.tableViewRobotinos, 1, 0, 1, 2)
        self.verticalLayout_2.addLayout(self.gridViewRobotinoManager)
        self.gridViewMES = QtWidgets.QGridLayout()
        self.gridViewMES.setObjectName("gridViewMES")
        self.labelMES = QtWidgets.QLabel(MainWindow)
        self.labelMES.setTextFormat(QtCore.Qt.MarkdownText)
        self.labelMES.setObjectName("labelMES")
        self.gridViewMES.addWidget(self.labelMES, 0, 0, 1, 1)
        self.buttonStartMesClient = QtWidgets.QPushButton(MainWindow)
        self.buttonStartMesClient.setAutoDefault(False)
        self.buttonStartMesClient.setObjectName("buttonStartMesClient")
        self.gridViewMES.addWidget(self.buttonStartMesClient, 2, 0, 1, 1)
        self.buttonStopMesClient = QtWidgets.QPushButton(MainWindow)
        self.buttonStopMesClient.setAutoDefault(False)
        self.buttonStopMesClient.setObjectName("buttonStopMesClient")
        self.gridViewMES.addWidget(self.buttonStopMesClient, 2, 1, 1, 1)
        self.tableViewMes = QtWidgets.QTableWidget(MainWindow)
        self.tableViewMes.setRowCount(5)
        self.tableViewMes.setColumnCount(4)
        self.tableViewMes.setObjectName("tableViewMes")
        item = QtWidgets.QTableWidgetItem()
        self.tableViewMes.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableViewMes.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableViewMes.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableViewMes.setHorizontalHeaderItem(3, item)
        self.gridViewMES.addWidget(self.tableViewMes, 1, 0, 1, 2)
        self.verticalLayout_2.addLayout(self.gridViewMES)
        self.gridViewManual = QtWidgets.QGridLayout()
        self.gridViewManual.setObjectName("gridViewManual")
        self.inputResourceId = QtWidgets.QSpinBox(MainWindow)
        self.inputResourceId.setObjectName("inputResourceId")
        self.gridViewManual.addWidget(self.inputResourceId, 2, 3, 1, 1)
        self.buttonUndock = QtWidgets.QPushButton(MainWindow)
        self.buttonUndock.setAutoDefault(False)
        self.buttonUndock.setObjectName("buttonUndock")
        self.gridViewManual.addWidget(self.buttonUndock, 3, 3, 1, 1)
        self.buttonDock = QtWidgets.QPushButton(MainWindow)
        self.buttonDock.setAutoDefault(False)
        self.buttonDock.setObjectName("buttonDock")
        self.gridViewManual.addWidget(self.buttonDock, 3, 2, 1, 1)
        self.inputRobtinoId = QtWidgets.QSpinBox(MainWindow)
        self.inputRobtinoId.setObjectName("inputRobtinoId")
        self.gridViewManual.addWidget(self.inputRobtinoId, 2, 1, 1, 1)
        self.labelManualOp = QtWidgets.QLabel(MainWindow)
        self.labelManualOp.setTextFormat(QtCore.Qt.MarkdownText)
        self.labelManualOp.setObjectName("labelManualOp")
        self.gridViewManual.addWidget(self.labelManualOp, 1, 0, 1, 1)
        self.labelRobotinoId = QtWidgets.QLabel(MainWindow)
        self.labelRobotinoId.setTextFormat(QtCore.Qt.MarkdownText)
        self.labelRobotinoId.setObjectName("labelRobotinoId")
        self.gridViewManual.addWidget(self.labelRobotinoId, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(MainWindow)
        self.label.setTextFormat(QtCore.Qt.MarkdownText)
        self.label.setObjectName("label")
        self.gridViewManual.addWidget(self.label, 2, 2, 1, 1)
        self.buttonUnloadCarrier = QtWidgets.QPushButton(MainWindow)
        self.buttonUnloadCarrier.setAutoDefault(False)
        self.buttonUnloadCarrier.setObjectName("buttonUnloadCarrier")
        self.gridViewManual.addWidget(self.buttonUnloadCarrier, 3, 1, 1, 1)
        self.buttonLoadCarrier = QtWidgets.QPushButton(MainWindow)
        self.buttonLoadCarrier.setObjectName("buttonLoadCarrier")
        self.gridViewManual.addWidget(self.buttonLoadCarrier, 3, 0, 1, 1)
        self.buttonDriveTo = QtWidgets.QPushButton(MainWindow)
        self.buttonDriveTo.setObjectName("buttonDriveTo")
        self.gridViewManual.addWidget(self.buttonDriveTo, 4, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridViewManual)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FleetIAS"))
        self.labelTitle.setText(_translate("MainWindow", "# FleetIAS"))
        self.buttonStopCommandServer.setWhatsThis(_translate(
            "MainWindow", "<html><head/><body><p><br/></p></body></html>"))
        self.buttonStopCommandServer.setText(
            _translate("MainWindow", "Stop Server"))
        self.lableTitleRobotinoManager.setText(
            _translate("MainWindow", "## Robotino Manager"))
        self.buttonStartCommandServer.setText(
            _translate("MainWindow", "Start Server"))
        item = self.tableViewRobotinos.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "id"))
        item = self.tableViewRobotinos.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "mode"))
        item = self.tableViewRobotinos.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Battery"))
        item = self.tableViewRobotinos.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Error"))
        item = self.tableViewRobotinos.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "State"))
        self.labelMES.setText(_translate("MainWindow", "## MES"))
        self.buttonStartMesClient.setText(
            _translate("MainWindow", "Connect to MES"))
        self.buttonStopMesClient.setText(
            _translate("MainWindow", "Disconnect from MES"))
        item = self.tableViewMes.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Start"))
        item = self.tableViewMes.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Target"))
        item = self.tableViewMes.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Assigned robotino"))
        item = self.tableViewMes.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "State"))
        self.buttonUndock.setText(_translate("MainWindow", "Undock"))
        self.buttonDock.setText(_translate("MainWindow", "Dock"))
        self.labelManualOp.setText(_translate(
            "MainWindow", "## Manual Operation"))
        self.labelRobotinoId.setText(_translate(
            "MainWindow", "#### Id of robotino"))
        self.label.setText(_translate(
            "MainWindow", "#### Id of target resource"))
        self.buttonUnloadCarrier.setText(
            _translate("MainWindow", "Unload Carrier"))
        self.buttonLoadCarrier.setText(
            _translate("MainWindow", "Load Carrier"))
        self.buttonDriveTo.setText(_translate(
            "MainWindow", "Drive to resource"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    guiManager = GUIManager(ui)
    guiManager.connectCallbackFunction()
    MainWindow.show()
    sys.exit(app.exec_())
