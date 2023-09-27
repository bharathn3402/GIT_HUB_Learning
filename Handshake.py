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
        self.arduino_handshake_thread = None  # Store the thread instance
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

        self.clickButton = QPushButton("Click here")
        self.clickButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.clickButton.setStyleSheet("background-color: #3f51b5; color: white; text-align: Center;")
        self.clickButton.setFixedSize(100, 30)
        self.clickButton.clicked.connect(self.handshake)
        buttonLayout.addWidget(self.clickButton, alignment=Qt.AlignCenter)

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

        self.uploadInProgressLabel = QLabel("Please click on <b>\"Start button\"</b> to start Uploading...")
        self.uploadInProgressLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.uploadInProgressLabel.setFixedSize(250, 30)  # Set the size as desired
        self.uploadInProgressLabel.setVisible(False)  # Initially, hide the label
        self.uploadInProgressLabel.setAlignment(Qt.AlignCenter)
        buttonLayout.addWidget(self.uploadInProgressLabel, alignment=Qt.AlignCenter)

        self.startButton = QPushButton("Start")
        self.startButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.startButton.setStyleSheet("background-color: #4CAF50; color: white; text-align: center;")
        self.startButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.startButton.clicked.connect(self.move_ToNextWindow)
        self.startButton.setVisible(False)
        buttonLayout.addWidget(self.startButton, alignment=Qt.AlignCenter)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def handshake(self):
        self.messageLabel.setVisible(False)
        self.clickButton.setVisible(False)
        QApplication.processEvents()
        self.arduinohandshakeLabel.setVisible(True)
        QApplication.processEvents()
        self.arduino_handshake_thread = ArduinoHandshakeThread(self.main_window.targetArduino)
        self.arduino_handshake_thread.arduino_handshake_signal.connect(self.handle_arduino_handshake_result)
        self.arduino_handshake_thread.start()

    def handle_arduino_handshake_result(self, arduino_handshake_flag,handshake_message):
        if arduino_handshake_flag == 1:
            self.updateStatusLabel(handshake_message)
            QMessageBox.information(self, "Arduino handshake successful", handshake_message)
            self.arduinohandshakeLabel.setVisible(False)
            self.powerCycleLabel.setVisible(True)
            QApplication.processEvents()
            self.main_window.targetArduino.flushInput()
            self.mew_detect_thread = MewDetectThread(self.main_window.targetArduino)
            self.mew_detect_thread.mew_detect_signal.connect(self.handle_mew_detect_result)
            self.mew_detect_thread.start()
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
            else:
                Handshake_box.done(QMessageBox.RejectRole)
                self.main_window.close()
                return None  # Exit the method or handle the case as needed

    def updateStatusLabel(self, message):
        formatted_message = f"<p style='text-align:justify; font-size: 14px;'>{message}</p>"
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

    def handle_mew_handshake_result(self,mew_handshake_flag,number_of_data_segments):
        
        if mew_handshake_flag == 1:
            self.main_window.communicationOkayFlag = 1
            handshake_message = "Mew handshake successful!"
            segments_message = f"Number of memory segments in hex file: {number_of_data_segments}"
            self.updateStatusLabel(handshake_message)
            self.updateStatusLabel(segments_message)
            message = f"Mew handshake successful!\nNumber of memory segments in hex file: {number_of_data_segments}"
            QMessageBox.information(self, "Mew handshake", message)
            self.handshakeInProgressLabel.setVisible(False)
            self.uploadInProgressLabel.setVisible(True)
            self.startButton.setVisible(True)

        elif mew_handshake_flag==0:
            self.main_window.communicationOkayFlag = 0
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

    def handle_mew_detect_result(self, mew_detect_flag, message):
        if mew_detect_flag == 1:
            # Mew bootloader detected
            self.powerCycleLabel.setVisible(False)
            self.handshakeInProgressLabel.setVisible(True)
            self.updateStatusLabel(message)
            QApplication.processEvents()

            # Start the Mew handshake thread
            self.mew_handshake_thread = MewHandshakeThread(self.main_window.selectedHexFile, self.main_window.targetArduino)
            self.mew_handshake_thread.mew_handshake_signal.connect(self.handle_mew_handshake_result)
            self.mew_handshake_thread.start()
        else:
            # Mew bootloader not detected, handle the error or show a message to the user
            self.updateStatusLabel(message)
            message_box = QMessageBox(self)
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Bootloader Detection Error")
            message_box.setText("Mew bootloader not detected!")
            try_again_button = message_box.addButton("Try Again", QMessageBox.AcceptRole)
            exit_button = message_box.addButton("Exit", QMessageBox.RejectRole)
            message_box.exec_()
            if message_box.clickedButton() == try_again_button:
                message_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
                self.reset()
                self.main_window.activateWindow(1)
            else:
                message_box.done(QMessageBox.RejectRole)
                self.main_window.close()
                return None  # Exit the method or handle the case as needed

    
class MewDetectThread(QThread):
    mew_detect_signal = pyqtSignal(int, str)

    def __init__(self, target_arduino):
        super().__init__()
        self.target_arduino = target_arduino

    def run(self):
        startTimeForVCUhandshake=time.time()
        try:
            mew_detect_result, message = hostUtility_1.mew_detect(startTimeForVCUhandshake,self.target_arduino)
            print(mew_detect_result, message)
            self.mew_detect_signal.emit(mew_detect_result, message)
        except hostUtility_1.SerialConnectionError as error:
            self.mew_detect_signal.emit(0, f"Arduino connection problem: {error}")

class ArduinoHandshakeThread(QThread):
    arduino_handshake_signal = pyqtSignal(int, str)

    def __init__(self, target_arduino):
        super().__init__()
        self.target_arduino = target_arduino

    def run(self):
        arduino_handshake_flag, handshake_message = hostUtility_1.Arduinohandshake(self.target_arduino)
        print(arduino_handshake_flag, handshake_message)
        self.arduino_handshake_signal.emit(arduino_handshake_flag, handshake_message)

class MewHandshakeThread(QThread):
    mew_handshake_signal = pyqtSignal(int,int)

    def __init__(self, hex_file, target_arduino):
        super().__init__()
        self.hex_file = hex_file
        self.target_arduino = target_arduino

    def run(self):
        try:
            mew_handshake_result, number_of_data_segments = hostUtility_1.mew_Handshake(self.hex_file, self.target_arduino)
            self.mew_handshake_signal.emit(mew_handshake_result,number_of_data_segments)
        except hostUtility_1.SerialConnectionError as error:
            self.mew_handshake_signal.emit(0, f"Arduino connection problem: {error}")
