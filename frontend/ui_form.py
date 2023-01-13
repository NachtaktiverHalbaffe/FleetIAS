# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridViewRobotinoManager = QGridLayout()
        self.gridViewRobotinoManager.setObjectName(u"gridViewRobotinoManager")
        self.buttonStopCommandServer = QPushButton(self.centralwidget)
        self.buttonStopCommandServer.setObjectName(u"buttonStopCommandServer")
        self.buttonStopCommandServer.setAutoDefault(False)

        self.gridViewRobotinoManager.addWidget(self.buttonStopCommandServer, 2, 1, 1, 1)

        self.lableTitleRobotinoManager = QLabel(self.centralwidget)
        self.lableTitleRobotinoManager.setObjectName(u"lableTitleRobotinoManager")
        self.lableTitleRobotinoManager.setTextFormat(Qt.MarkdownText)

        self.gridViewRobotinoManager.addWidget(self.lableTitleRobotinoManager, 0, 0, 1, 1)

        self.buttonStartCommandServer = QPushButton(self.centralwidget)
        self.buttonStartCommandServer.setObjectName(u"buttonStartCommandServer")
        self.buttonStartCommandServer.setCheckable(False)
        self.buttonStartCommandServer.setAutoDefault(False)
        self.buttonStartCommandServer.setFlat(False)

        self.gridViewRobotinoManager.addWidget(self.buttonStartCommandServer, 2, 0, 1, 1)

        self.tableViewRobotinos = QTableWidget(self.centralwidget)
        if (self.tableViewRobotinos.columnCount() < 5):
            self.tableViewRobotinos.setColumnCount(5)
        font = QFont()
        font.setBold(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font);
        self.tableViewRobotinos.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font);
        self.tableViewRobotinos.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font);
        self.tableViewRobotinos.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font);
        self.tableViewRobotinos.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font);
        self.tableViewRobotinos.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tableViewRobotinos.setObjectName(u"tableViewRobotinos")
        self.tableViewRobotinos.setGridStyle(Qt.SolidLine)
        self.tableViewRobotinos.setRowCount(0)
        self.tableViewRobotinos.setColumnCount(5)
        self.tableViewRobotinos.horizontalHeader().setCascadingSectionResizes(True)
        self.tableViewRobotinos.horizontalHeader().setMinimumSectionSize(80)
        self.tableViewRobotinos.horizontalHeader().setProperty("showSortIndicator", True)
        self.tableViewRobotinos.horizontalHeader().setStretchLastSection(True)

        self.gridViewRobotinoManager.addWidget(self.tableViewRobotinos, 1, 0, 1, 2)


        self.verticalLayout.addLayout(self.gridViewRobotinoManager)

        self.gridViewMES = QGridLayout()
        self.gridViewMES.setObjectName(u"gridViewMES")
        self.buttonStartMesClient = QPushButton(self.centralwidget)
        self.buttonStartMesClient.setObjectName(u"buttonStartMesClient")
        self.buttonStartMesClient.setAutoDefault(False)

        self.gridViewMES.addWidget(self.buttonStartMesClient, 2, 0, 1, 1)

        self.tableViewMes = QTableWidget(self.centralwidget)
        if (self.tableViewMes.columnCount() < 4):
            self.tableViewMes.setColumnCount(4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFont(font);
        self.tableViewMes.setHorizontalHeaderItem(0, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setFont(font);
        self.tableViewMes.setHorizontalHeaderItem(1, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setFont(font);
        self.tableViewMes.setHorizontalHeaderItem(2, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setFont(font);
        self.tableViewMes.setHorizontalHeaderItem(3, __qtablewidgetitem8)
        self.tableViewMes.setObjectName(u"tableViewMes")
        self.tableViewMes.setTextElideMode(Qt.ElideRight)
        self.tableViewMes.setWordWrap(True)
        self.tableViewMes.setRowCount(0)
        self.tableViewMes.setColumnCount(4)
        self.tableViewMes.horizontalHeader().setCascadingSectionResizes(True)
        self.tableViewMes.horizontalHeader().setMinimumSectionSize(60)
        self.tableViewMes.horizontalHeader().setDefaultSectionSize(130)
        self.tableViewMes.horizontalHeader().setProperty("showSortIndicator", True)
        self.tableViewMes.horizontalHeader().setStretchLastSection(True)
        self.tableViewMes.verticalHeader().setCascadingSectionResizes(False)

        self.gridViewMES.addWidget(self.tableViewMes, 1, 0, 1, 2)

        self.buttonStopMesClient = QPushButton(self.centralwidget)
        self.buttonStopMesClient.setObjectName(u"buttonStopMesClient")
        self.buttonStopMesClient.setAutoDefault(False)

        self.gridViewMES.addWidget(self.buttonStopMesClient, 2, 1, 1, 1)

        self.labelMES = QLabel(self.centralwidget)
        self.labelMES.setObjectName(u"labelMES")
        self.labelMES.setTextFormat(Qt.MarkdownText)

        self.gridViewMES.addWidget(self.labelMES, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridViewMES)

        self.gridViewManual = QGridLayout()
        self.gridViewManual.setObjectName(u"gridViewManual")
        self.labelRobotinoId = QLabel(self.centralwidget)
        self.labelRobotinoId.setObjectName(u"labelRobotinoId")
        self.labelRobotinoId.setTextFormat(Qt.MarkdownText)

        self.gridViewManual.addWidget(self.labelRobotinoId, 2, 0, 1, 1)

        self.inputResourceId = QSpinBox(self.centralwidget)
        self.inputResourceId.setObjectName(u"inputResourceId")

        self.gridViewManual.addWidget(self.inputResourceId, 2, 3, 1, 1)

        self.buttonDock = QPushButton(self.centralwidget)
        self.buttonDock.setObjectName(u"buttonDock")
        self.buttonDock.setAutoDefault(False)

        self.gridViewManual.addWidget(self.buttonDock, 4, 2, 1, 1)

        self.buttonSetAutomatic = QPushButton(self.centralwidget)
        self.buttonSetAutomatic.setObjectName(u"buttonSetAutomatic")

        self.gridViewManual.addWidget(self.buttonSetAutomatic, 5, 2, 1, 1)

        self.buttonSetManual = QPushButton(self.centralwidget)
        self.buttonSetManual.setObjectName(u"buttonSetManual")

        self.gridViewManual.addWidget(self.buttonSetManual, 5, 3, 1, 1)

        self.labelManualOp = QLabel(self.centralwidget)
        self.labelManualOp.setObjectName(u"labelManualOp")
        self.labelManualOp.setTextFormat(Qt.MarkdownText)

        self.gridViewManual.addWidget(self.labelManualOp, 1, 0, 1, 2)

        self.buttonLoadCarrier = QPushButton(self.centralwidget)
        self.buttonLoadCarrier.setObjectName(u"buttonLoadCarrier")

        self.gridViewManual.addWidget(self.buttonLoadCarrier, 4, 0, 1, 1)

        self.inputRobtinoId = QSpinBox(self.centralwidget)
        self.inputRobtinoId.setObjectName(u"inputRobtinoId")

        self.gridViewManual.addWidget(self.inputRobtinoId, 2, 1, 1, 1)

        self.buttonUndock = QPushButton(self.centralwidget)
        self.buttonUndock.setObjectName(u"buttonUndock")
        self.buttonUndock.setAutoDefault(False)

        self.gridViewManual.addWidget(self.buttonUndock, 4, 3, 1, 1)

        self.buttonUnloadCarrier = QPushButton(self.centralwidget)
        self.buttonUnloadCarrier.setObjectName(u"buttonUnloadCarrier")
        self.buttonUnloadCarrier.setAutoDefault(False)

        self.gridViewManual.addWidget(self.buttonUnloadCarrier, 4, 1, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setTextFormat(Qt.MarkdownText)

        self.gridViewManual.addWidget(self.label, 2, 2, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.xSpinBox = QSpinBox(self.centralwidget)
        self.xSpinBox.setObjectName(u"xSpinBox")

        self.horizontalLayout_2.addWidget(self.xSpinBox)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.ySpinBox = QSpinBox(self.centralwidget)
        self.ySpinBox.setObjectName(u"ySpinBox")

        self.horizontalLayout_2.addWidget(self.ySpinBox)


        self.gridViewManual.addLayout(self.horizontalLayout_2, 1, 3, 1, 1)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setTextFormat(Qt.MarkdownText)

        self.gridViewManual.addWidget(self.label_4, 1, 2, 1, 1)

        self.buttonDriveTo = QPushButton(self.centralwidget)
        self.buttonDriveTo.setObjectName(u"buttonDriveTo")

        self.gridViewManual.addWidget(self.buttonDriveTo, 5, 0, 1, 1)

        self.buttonDriveToPos = QPushButton(self.centralwidget)
        self.buttonDriveToPos.setObjectName(u"buttonDriveToPos")

        self.gridViewManual.addWidget(self.buttonDriveToPos, 5, 1, 1, 1)

        self.buttonSetDockingPos = QPushButton(self.centralwidget)
        self.buttonSetDockingPos.setObjectName(u"buttonSetDockingPos")

        self.gridViewManual.addWidget(self.buttonSetDockingPos, 6, 0, 1, 1)

        self.buttonEndTask = QPushButton(self.centralwidget)
        self.buttonEndTask.setObjectName(u"buttonEndTask")

        self.gridViewManual.addWidget(self.buttonEndTask, 6, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridViewManual)

        self.gridViewROS = QGridLayout()
        self.gridViewROS.setObjectName(u"gridViewROS")
        self.label_add_offset = QLabel(self.centralwidget)
        self.label_add_offset.setObjectName(u"label_add_offset")
        self.label_add_offset.setTextFormat(Qt.MarkdownText)

        self.gridViewROS.addWidget(self.label_add_offset, 1, 0, 1, 1)

        self.labelRos = QLabel(self.centralwidget)
        self.labelRos.setObjectName(u"labelRos")
        self.labelRos.setTextFormat(Qt.MarkdownText)

        self.gridViewROS.addWidget(self.labelRos, 0, 0, 1, 1)

        self.label_topic = QLabel(self.centralwidget)
        self.label_topic.setObjectName(u"label_topic")

        self.gridViewROS.addWidget(self.label_topic, 2, 0, 1, 1)

        self.topic_comboBox = QComboBox(self.centralwidget)
        self.topic_comboBox.setObjectName(u"topic_comboBox")

        self.gridViewROS.addWidget(self.topic_comboBox, 2, 1, 1, 1)

        self.label_offset = QLabel(self.centralwidget)
        self.label_offset.setObjectName(u"label_offset")
        self.label_offset.setLayoutDirection(Qt.LeftToRight)
        self.label_offset.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridViewROS.addWidget(self.label_offset, 2, 2, 1, 1)

        self.offset_value_input = QDoubleSpinBox(self.centralwidget)
        self.offset_value_input.setObjectName(u"offset_value_input")

        self.gridViewROS.addWidget(self.offset_value_input, 2, 3, 1, 1)

        self.label_activate_feature = QLabel(self.centralwidget)
        self.label_activate_feature.setObjectName(u"label_activate_feature")
        self.label_activate_feature.setTextFormat(Qt.MarkdownText)

        self.gridViewROS.addWidget(self.label_activate_feature, 6, 0, 1, 1)

        self.label_feature = QLabel(self.centralwidget)
        self.label_feature.setObjectName(u"label_feature")

        self.gridViewROS.addWidget(self.label_feature, 7, 0, 1, 1)

        self.feature_comboBox = QComboBox(self.centralwidget)
        self.feature_comboBox.setObjectName(u"feature_comboBox")

        self.gridViewROS.addWidget(self.feature_comboBox, 7, 1, 1, 1)

        self.pushButton_offset = QPushButton(self.centralwidget)
        self.pushButton_offset.setObjectName(u"pushButton_offset")

        self.gridViewROS.addWidget(self.pushButton_offset, 2, 4, 1, 1)

        self.pushButton_feature = QPushButton(self.centralwidget)
        self.pushButton_feature.setObjectName(u"pushButton_feature")

        self.gridViewROS.addWidget(self.pushButton_feature, 7, 4, 1, 1)

        self.useCustomNavigationCB = QCheckBox(self.centralwidget)
        self.useCustomNavigationCB.setObjectName(u"useCustomNavigationCB")
        self.useCustomNavigationCB.setFont(font)

        self.gridViewROS.addWidget(self.useCustomNavigationCB, 0, 1, 1, 1)

        self.checkBox_feature = QCheckBox(self.centralwidget)
        self.checkBox_feature.setObjectName(u"checkBox_feature")

        self.gridViewROS.addWidget(self.checkBox_feature, 7, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridViewROS)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.buttonStartCommandServer.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"FleetIAS", None))
#if QT_CONFIG(whatsthis)
        self.buttonStopCommandServer.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.buttonStopCommandServer.setText(QCoreApplication.translate("MainWindow", u"Stop Server", None))
        self.lableTitleRobotinoManager.setText(QCoreApplication.translate("MainWindow", u"## Robotino Manager", None))
        self.buttonStartCommandServer.setText(QCoreApplication.translate("MainWindow", u"Start Server", None))
        ___qtablewidgetitem = self.tableViewRobotinos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"id", None));
        ___qtablewidgetitem1 = self.tableViewRobotinos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"mode", None));
        ___qtablewidgetitem2 = self.tableViewRobotinos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Battery", None));
        ___qtablewidgetitem3 = self.tableViewRobotinos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Error", None));
        ___qtablewidgetitem4 = self.tableViewRobotinos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"State", None));
        self.buttonStartMesClient.setText(QCoreApplication.translate("MainWindow", u"Connect to MES", None))
        ___qtablewidgetitem5 = self.tableViewMes.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Start", None));
        ___qtablewidgetitem6 = self.tableViewMes.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Target", None));
        ___qtablewidgetitem7 = self.tableViewMes.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Assigned Robotino", None));
        ___qtablewidgetitem8 = self.tableViewMes.horizontalHeaderItem(3)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"State", None));
        self.buttonStopMesClient.setText(QCoreApplication.translate("MainWindow", u"Disconnect from MES", None))
        self.labelMES.setText(QCoreApplication.translate("MainWindow", u"## MES", None))
        self.labelRobotinoId.setText(QCoreApplication.translate("MainWindow", u"#### Id of robotino", None))
        self.buttonDock.setText(QCoreApplication.translate("MainWindow", u"Dock", None))
        self.buttonSetAutomatic.setText(QCoreApplication.translate("MainWindow", u"Change to automatic operation", None))
        self.buttonSetManual.setText(QCoreApplication.translate("MainWindow", u"Change to manual operation", None))
        self.labelManualOp.setText(QCoreApplication.translate("MainWindow", u"## Manual Operation & Settings", None))
        self.buttonLoadCarrier.setText(QCoreApplication.translate("MainWindow", u"Load Carrier", None))
        self.buttonUndock.setText(QCoreApplication.translate("MainWindow", u"Undock", None))
        self.buttonUnloadCarrier.setText(QCoreApplication.translate("MainWindow", u"Unload Carrier", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"#### Id of target resource", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"y", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"x", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"#### Coordinate of target", None))
        self.buttonDriveTo.setText(QCoreApplication.translate("MainWindow", u"Drive to resource", None))
        self.buttonDriveToPos.setText(QCoreApplication.translate("MainWindow", u"Drive to coordinate", None))
        self.buttonSetDockingPos.setText(QCoreApplication.translate("MainWindow", u"Set docking position", None))
        self.buttonEndTask.setText(QCoreApplication.translate("MainWindow", u"End Task/Reset Error", None))
        self.label_add_offset.setText(QCoreApplication.translate("MainWindow", u"#### Add Offset", None))
        self.labelRos.setText(QCoreApplication.translate("MainWindow", u"## ROS", None))
        self.label_topic.setText(QCoreApplication.translate("MainWindow", u"Topic", None))
        self.topic_comboBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Name of topic", None))
        self.label_offset.setText(QCoreApplication.translate("MainWindow", u"Offset ", None))
        self.label_activate_feature.setText(QCoreApplication.translate("MainWindow", u"#### Activate Feature", None))
        self.label_feature.setText(QCoreApplication.translate("MainWindow", u"Feature", None))
        self.feature_comboBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Name of feature", None))
        self.pushButton_offset.setText(QCoreApplication.translate("MainWindow", u"Send Command", None))
        self.pushButton_feature.setText(QCoreApplication.translate("MainWindow", u"Send Command", None))
        self.useCustomNavigationCB.setText(QCoreApplication.translate("MainWindow", u"Use ROS", None))
        self.checkBox_feature.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
    # retranslateUi

