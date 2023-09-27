from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout, QSizePolicy, QSpacerItem,QScrollArea,QTextEdit,QTextBrowser,QFrame
from PyQt5.QtGui import QFont,QIcon,QPixmap,QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import hostUtility_1
import time
from intelhex import IntelHex

class COMPortSelectionWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()

        comLayout = QHBoxLayout()
        comLabel = QLabel("Select a COM Port  :")
        comLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        comLayout.addWidget(comLabel)
        comLayout.setContentsMargins(100, 50, 150, 0)  # Adjust the bottom margin to a smaller value

        self.comComboBox = QComboBox()
        self.comComboBox.setStyleSheet("font-size: 14px;")
        self.comComboBox.setFixedWidth(350)
        comLayout.addWidget(self.comComboBox)

        mainLayout.addLayout(comLayout)

        baudLayout = QHBoxLayout()
        baudLabel = QLabel("Selected Baud Rate:   115200")
        baudLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        baudLayout.addWidget(baudLabel)
        baudLayout.setContentsMargins(100, -50, 150, 100)  # Remove the bottom margin

        mainLayout.addSpacing(5)  # Add a small spacing between the two lines
        mainLayout.addLayout(baudLayout)

        buttonLayout = QHBoxLayout()

        self.goBackButton = QPushButton("Go Back")
        self.goBackButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.goBackButton.setStyleSheet("background-color: #3f51b5; color: white; text-align: center;")
        self.goBackButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.goBackButton.clicked.connect(self.goBack)
        buttonLayout.addWidget(self.goBackButton)

        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.refreshButton.setStyleSheet("background-color: #f44336; color: white; text-align: center;")
        self.refreshButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.refreshButton.clicked.connect(self.refreshCOMPorts)
        buttonLayout.addWidget(self.refreshButton)

        self.SelectButton = QPushButton("Select")
        self.SelectButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.SelectButton.setStyleSheet("background-color: #2196F3; color: white; text-align: center;")
        self.SelectButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.SelectButton.clicked.connect(self.moveTo_NextWindow)
        buttonLayout.addWidget(self.SelectButton)

        mainLayout.addLayout(buttonLayout)

        # Add one line of space after the buttons
        spaceLabel = QLabel()
        spaceLabel.setFixedHeight(20)  # Adjust the height as needed
        mainLayout.addWidget(spaceLabel)

        self.setLayout(mainLayout)


    def populateCOMPorts(self):
        self.comComboBox.clear()
        self.com_ports =hostUtility_1.comPortSelection()
        if len(self.com_ports) == 0:
            QMessageBox.warning(self, "No Ports", "No active COM ports available. Please connect a port.")
            
        else:
            self.comComboBox.clear()
            self.comComboBox.setPlaceholderText("Click here to select COM port")
            self.comComboBox.setStyleSheet("color: black;")
            for port in self.com_ports:
                self.comComboBox.addItem(port.device + " - " + port.description)

    def selectCOMPort(self):
        selectedCOMIndex = self.comComboBox.currentIndex()
        if selectedCOMIndex == -1:
            QMessageBox.warning(self, "No Port Selected", "Please select a COM port.")
            return

        selectedPort = self.com_ports[selectedCOMIndex].device
        self.main_window.selectedCOMPort = selectedPort  # Store the selected COM port

    def goBack(self):
        self.main_window.selectedCOMPort = "" 
        self.main_window.hexFileSelectionWindow.fileComboBox.setCurrentIndex(-1)  
        self.main_window.hexFileSelectionWindow.fileComboBox.clear() 
        self.main_window.hexFileSelectionWindow.populateHexFiles() 
        self.main_window.activateWindow(0)  


    def refreshCOMPorts(self):
        self.populateCOMPorts()

    def moveTo_NextWindow(self):
        self.selectCOMPort()
        self.main_window.HandshakeWindow.hexFileValueLabel.setText(self.main_window.selectedHexFile)
        self.main_window.HandshakeWindow.comPortValueLabel.setText(self.main_window.selectedCOMPort)
        if self.main_window.selectedHexFile == "":
            QMessageBox.warning(self, "No HEX File Selected", "Please select a HEX file.")
        elif self.main_window.selectedCOMPort == "":
            QMessageBox.warning(self, "No COM Port Selected", "Please select a COM port.")
        else:
            try:
                self.main_window.targetArduino=hostUtility_1.setupSerialComm(
                COMport=self.main_window.selectedCOMPort,
                baudRate=115200,
                timeOut=10)
                if self.main_window.targetArduino is not None:
                    self.main_window.activateWindow(2)  # Go to Serial Setup window
            except hostUtility_1.SerialConnectionError as error:

                error_message = f"Oops! Trouble initiating communication with Arduino.\n"
                error_message += f"Make sure Arduino is connected to the same COM-port that you mentioned.\n"
                error_message += f"Error: {str(error)}"

                message_box = QMessageBox(self)
                message_box.setIcon(QMessageBox.Warning)
                message_box.setWindowTitle("Serial Communication Error")
                message_box.setText(error_message)
                try_again_button = message_box.addButton("Try Again", QMessageBox.AcceptRole)
                exit_button = message_box.addButton("Exit", QMessageBox.RejectRole)
                message_box.exec_()

                if message_box.clickedButton() == try_again_button:
                    message_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
                    self.main_window.selectedCOMPort = ""  # Reset the selected COM port
                    self.main_window.comPortSelectionWindow.comComboBox.setCurrentIndex(-1)  # Clear the selected hex file
                    self.main_window.comPortSelectionWindow.comComboBox.clear()  # Clear the combo box items
                    self.main_window.comPortSelectionWindow.populateCOMPorts()  # Repopulate HEX files
                    self.main_window.activateWindow(1)  # Try again
                    
                else:
                    message_box.done(QMessageBox.RejectRole)
                    self.main_window.close()
                    return None  # Exit the method or handle the case as needed