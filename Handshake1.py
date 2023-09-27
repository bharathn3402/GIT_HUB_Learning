from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout, QSizePolicy, QSpacerItem,QScrollArea,QTextEdit,QTextBrowser,QFrame
from PyQt5.QtGui import QFont,QIcon,QPixmap,QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import hostUtility_1
import time
from intelhex import IntelHex

class HandshakeWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()

        hexFileLabel = QLabel("Selected HEX File:")
        self.hexFileValueLabel = QLabel(self.main_window.selectedHexFile)
        formLayout.addRow(hexFileLabel, self.hexFileValueLabel)

        comPortLabel = QLabel("Selected COM Port:")
        self.comPortValueLabel = QLabel(self.main_window.selectedCOMPort)
        formLayout.addRow(comPortLabel, self.comPortValueLabel)

        baudRateLabel = QLabel("Selected Baud Rate:")
        self.baudRatevalueLabel = QLabel("115200")
        formLayout.addRow(baudRateLabel, self.baudRatevalueLabel)

        self.handshakeStatusLabel = QTextBrowser()  # Use QTextBrowser for scrollable text
        self.handshakeStatusLabel.setReadOnly(True)
        self.handshakeStatusLabel.setOpenExternalLinks(True)  # Enable hyperlink clicking
        formLayout.addRow("Handshake Status:", self.handshakeStatusLabel)

        mainLayout.addLayout(formLayout)

        buttonLayout = QVBoxLayout()

        self.messageLabel = QLabel("Please click on 'Click here' to start handshake ....")
        self.messageLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.messageLabel.setAlignment(Qt.AlignCenter)
        buttonLayout.addWidget(self.messageLabel, alignment=Qt.AlignCenter)

        buttonRowLayout = QVBoxLayout()
        self.clickButton = QPushButton("Click here")
        self.clickButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.clickButton.setStyleSheet("background-color: #3f51b5; color: white; text-align: Center;")
        self.clickButton.setFixedSize(100, 30)
        self.clickButton.clicked.connect(self.handshake)
        buttonRowLayout.addWidget(self.clickButton, alignment=Qt.AlignCenter)
        buttonLayout.addLayout(buttonRowLayout)

        self.arduinohandshakeLabel = QLabel(" please wait Arduino Handshake is in progress...")
        self.arduinohandshakeLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.arduinohandshakeLabel.setFixedSize(300, 30)
        self.arduinohandshakeLabel.setVisible(False)
        buttonLayout.addWidget(self.arduinohandshakeLabel, alignment=Qt.AlignCenter)

        self.handshakeInProgressLabel = QLabel("MEW Handshake in progress please wait...")
        self.handshakeInProgressLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.handshakeInProgressLabel.setFixedSize(250, 30)
        self.handshakeInProgressLabel.setVisible(False)
        buttonLayout.addWidget(self.handshakeInProgressLabel, alignment=Qt.AlignCenter)

        self.powerCycleLabel = QLabel("Please give power cycle...")
        self.powerCycleLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.powerCycleLabel.setFixedSize(250, 30)
        self.powerCycleLabel.setVisible(False)
        self.powerCycleLabel.setAlignment(Qt.AlignCenter)
        buttonLayout.addWidget(self.powerCycleLabel, alignment=Qt.AlignCenter)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def handshake(self):
        self.messageLabel.setVisible(False)
        self.clickButton.setVisible(False)
        QApplication.processEvents()
        self.arduinohandshakeLabel.setVisible(True)
        QApplication.processEvents()
        time.sleep(2)
        self.arduinoHandshakeflag = self.Arduinohandshake()
        self.main_window.communicationOkayFlag = 0

        if self.arduinoHandshakeflag == 1:
            self.arduinohandshakeLabel.setVisible(False)
            self.powerCycleLabel.setVisible(True)
            QApplication.processEvents()
            self.main_window.targetArduino.flushInput()
            startTimeForVCUhandshake = time.time()
            
            while(1):
                try:
                    mew_detect,message=hostUtility_1.mew_detect(startTimeForVCUhandshake,self.main_window.targetArduino)
                    if mew_detect==1:
                        self.powerCycleLabel.setVisible(False)
                        self.handshakeInProgressLabel.setVisible(True)
                        self.updateStatusLabel(message)
                        QApplication.processEvents()
                        break
                    else:
                        self.updateStatusLabel(message)
                        message_box = QMessageBox(self)
                        message_box.setIcon(QMessageBox.Warning)
                        message_box.setWindowTitle("Bootloader detection timeout!")
                        message_box.setText("Mew bootloader detection timeout!")
                        try_again_button = message_box.addButton("Try Again", QMessageBox.AcceptRole)
                        exit_button = message_box.addButton("Exit", QMessageBox.RejectRole)
                        message_box.exec_()
                        if message_box.clickedButton() == try_again_button:
                                message_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
                                startTimeForVCUhandshake = time.time()
                                continue
                                
                        else:
                            message_box.done(QMessageBox.RejectRole)
                            self.main_window.close()
                            return None  # Exit the method or handle the case as needed
                except hostUtility_1.SerialConnectionError as error:
                    QMessageBox.information(self,"Arduino connection problem.", "Arduino connection problem. Please restart utility.")
                    time.sleep(1)
                    self.main_window.close()
            try:
                self.main_window.communicationOkayFlag,numberOfDataSegments=hostUtility_1.mew_Handshake(self.main_window.selectedHexFile,self.main_window.targetArduino)
                if self.main_window.communicationOkayFlag==1:
                    handshake_message = "Mew handshake successful!"
                    segments_message = f"Number of memory segments in hex file: {numberOfDataSegments}"
                    self.updateStatusLabel(handshake_message)
                    self.updateStatusLabel(segments_message)
                    message = f"Mew handshake successful!\nNumber of memory segments in hex file: {numberOfDataSegments}"
                    QMessageBox.information(self, "Mew handshake", message)
                    self.handshakeInProgressLabel.setVisible(False)

                    buttonLayout = QHBoxLayout()
                    buttonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
                    self.uploadInProgressLabel = QLabel("Click here to start Uploading...")
                    self.uploadInProgressLabel.setStyleSheet("font-size: 14px; font-weight;")
                    self.uploadInProgressLabel.setFixedSize(250, 30)  # Set the size as desired
                    self.uploadInProgressLabel.setVisible(False)  # Initially, hide the label
                    buttonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
                    buttonLayout.addWidget(self.uploadInProgressLabel)

                    self.startButton = QPushButton("Start")
                    self.startButton.setFont(QFont("Arial", 10, QFont.Bold))
                    self.startButton.setStyleSheet("background-color: #4CAF50; color: white; text-align: center;")
                    self.startButton.setFixedSize(100, 30)  # Adjust the size as desired
                    self.startButton.clicked.connect(self.move_ToNextWindow)
                    buttonLayout.addWidget(self.startButton)
                    self.layout().addLayout(buttonLayout)
                elif self.main_window.communicationOkayFlag==0:
                    message = "Mew denied communication! Please restart the utility."
                    self.updateStatusLabel(message)
                    QMessageBox.information(self, "Mew denied communication", message)
                    time.sleep(1)
                    self.main_window.close()
                else:
                    message = "Mew handshake timeout! Please restart the utility."
                    self.updateStatusLabel(message)
                    QMessageBox.information(self, "Mew handshake error", message)
                    time.sleep(1)
                    self.main_window.close()

            except hostUtility_1.SerialConnectionError as error:
                message = "connection problem. Please restart utility."+ str(error)
                self.updateStatusLabel(message)
                QMessageBox.information(self, " connection problem", message)
                time.sleep(1)
                self.main_window.close()
    
    def Arduinohandshake(self):
        QApplication.processEvents()
        try:
            arduinoHandshakeFlag, handshake_message = hostUtility_1.Arduinohandshake(self.main_window.targetArduino)
            if arduinoHandshakeFlag == 1:
                self.updateStatusLabel(handshake_message)
                QMessageBox.information(self,"Arduino handshake successful", "Arduino handshake successful!")
                return arduinoHandshakeFlag
            else:
                self.updateStatusLabel(handshake_message)
                Handshake_box = QMessageBox(self)
                Handshake_box.setIcon(QMessageBox.Warning)
                Handshake_box.setWindowTitle("Serial Communication Error")
                Handshake_box.setText(handshake_message)
                try_again_button = Handshake_box.addButton("Try Again", QMessageBox.AcceptRole)
                exit_button = Handshake_box.addButton("Exit", QMessageBox.RejectRole)
                Handshake_box.exec_()

                if Handshake_box.clickedButton() == try_again_button:
                    Handshake_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
                    self.reset()
                    self.main_window.activateWindow(1)
                    break
                    
                else:
                    Handshake_box.done(QMessageBox.RejectRole)
                    self.main_window.close()
                    return None  # Exit the method or handle the case as needed
        except hostUtility_1.SerialConnectionError as error:
            message = str(error)+" Please restart utility."
            self.updateStatusLabel(message)
            QMessageBox.information(self, " connection problem", message)
            time.sleep(1)
            self.main_window.close()

    def updateStatusLabel(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        formatted_message = f"<p style='text-align:justify; font-size: 14px;'>[{timestamp}] {message}</p>"
        self.handshakeStatusLabel.append(formatted_message)

    def reset(self):
        self.main_window.targetArduino.close()
        self.selectedCOMPort = ""
        self.main_window.comPortSelectionWindow.comComboBox.setCurrentIndex(-1)
        self.main_window.comPortSelectionWindow.comComboBox.clear()
        self.main_window.comPortSelectionWindow.populateCOMPorts()
        self.main_window.selectedBaudRate = ""
        self.main_window.targetArduino = ""
        self.main_window.communicationOkayFlag = 0
        self.main_window.HandshakeWindow.messageLabel.setVisible(True)
        self.main_window.HandshakeWindow.clickButton.setVisible(True)
        self.main_window.HandshakeWindow.arduinohandshakeLabel.setVisible(False)
        self.main_window.HandshakeWindow.handshakeInProgressLabel.setVisible(False)
        self.main_window.HandshakeWindow.handshakeStatusLabel.clear()  # Clear any previous messages

    def move_ToNextWindow(self):
        self.main_window.activateWindow(3)

