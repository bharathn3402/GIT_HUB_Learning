import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout
from PyQt5.QtGui import QFont,QIcon,QPixmap,QPainter, QColor
from PyQt5.QtCore import Qt
import os.path


import serial
import serial.tools.list_ports
import time
from intelhex import IntelHex

arduinoTimeOut = 10     # Value in seconds, None for infinite wait



class HexFileSelectionWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):


        mainLayout = QVBoxLayout()

        fileLayout = QHBoxLayout()
        hexLabel = QLabel("Select a HEX file:")
        hexLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        fileLayout.addWidget(hexLabel)
        fileLayout.setContentsMargins(120, 10, 250, 10)  # Add top and bottom padding


        self.fileComboBox = QComboBox()
        self.fileComboBox.setStyleSheet("font-size: 14px;")
        self.fileComboBox.setFixedWidth(250)
        fileLayout.addWidget(self.fileComboBox)

        mainLayout.addLayout(fileLayout)

        buttonLayout = QHBoxLayout()

        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.refreshButton.setStyleSheet("background-color: #f44336; color: white; text-align: center;")
        self.refreshButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.refreshButton.clicked.connect(self.refreshHexFiles)
        buttonLayout.addWidget(self.refreshButton)


        self.nextButton = QPushButton("Select")
        self.nextButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.nextButton.setStyleSheet("background-color: #4CAF50; color: white; text-align: center;")
        self.nextButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.nextButton.clicked.connect(self.moveToNextWindow)

        buttonLayout.addWidget(self.nextButton)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        self.populateHexFiles()  # Populate HEX files

    def populateHexFiles(self):
        presentFiles = [file for file in os.listdir() if os.path.isfile(file)]
        hexFiles = [file for file in presentFiles if file.endswith(".hex")]

        if len(hexFiles) == 0:
            QMessageBox.warning(self, "No HEX Files", "No HEX files found in the current directory.")
        else:
            self.fileComboBox.clear()
            self.fileComboBox.setPlaceholderText("Select a HEX file")
            self.fileComboBox.addItems(hexFiles)

    def selectHexFile(self):
        selectedHexIndex = self.fileComboBox.currentIndex()
        if selectedHexIndex == -1:
            QMessageBox.warning(self, "No File Selected", "Please select a HEX file.")
            return

        selectedHexFile = self.fileComboBox.itemText(selectedHexIndex)
        self.main_window.selectedHexFile = selectedHexFile  # Store the selected hex file name

        print("Selected HEX File:", selectedHexFile)

    def refreshHexFiles(self):
        self.populateHexFiles()

    def moveToNextWindow(self):
        selectedHexIndex = self.fileComboBox.currentIndex()
        if selectedHexIndex == -1:
            QMessageBox.warning(self, "No File Selected", "Please select a HEX file.")
            return

        selectedHexFile = self.fileComboBox.itemText(selectedHexIndex)
        self.main_window.selectedHexFile = selectedHexFile  # Store the selected hex file name

        print("Selected HEX File:", selectedHexFile)

        self.main_window.comPortSelectionWindow.populateCOMPorts()  # Populate COM ports
        self.main_window.activateWindow(1)  # Go to COM Port Selection window




class COMPortSelectionWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):


        mainLayout = QVBoxLayout()

        comLayout = QHBoxLayout()
        comLabel = QLabel("Select a COM Port:")
        comLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        comLayout.addWidget(comLabel)
        comLayout.setContentsMargins(100,10,150,10)

        self.comComboBox = QComboBox()
        self.comComboBox.setStyleSheet("font-size: 14px;")
        self.comComboBox.setFixedWidth(350)
        comLayout.addWidget(self.comComboBox)

        mainLayout.addLayout(comLayout)

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

        self.nextButton = QPushButton("Select")
        self.nextButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.nextButton.setStyleSheet("background-color: #2196F3; color: white; text-align: center;")
        self.nextButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.nextButton.clicked.connect(self.moveToNextWindow)
        buttonLayout.addWidget(self.nextButton)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def populateCOMPorts(self):
        self.com_ports = serial.tools.list_ports.comports()
        if len(self.com_ports) == 0:
            QMessageBox.warning(self, "No Ports", "No active COM ports available. Please connect a port.")
        else:
            self.comComboBox.clear()
            self.comComboBox.setPlaceholderText("Click here to select COMport")
            self.comComboBox.setStyleSheet("color: black;")
            for port in self.com_ports:
                self.comComboBox.addItem(port.device + " - " + port.description)

    def selectCOMPort(self):
        selectedCOMIndex = self.comComboBox.currentIndex()
        if selectedCOMIndex == -1:
            QMessageBox.warning(self, "No Port Selected", "Please select a COM port.")
            return

        selectedPort = self.comComboBox.itemText(selectedCOMIndex)
        # selectedPort= self.com_ports[selectedCOMIndex].device

        print("Selected COM Port:", selectedPort)

        self.main_window.selectedCOMPort = selectedPort  # Store the selected COM port

    def enableWindow(self):
        self.comComboBox.setEnabled(True)
        self.nextButton.setEnabled(True)

    def disableWindow(self):
        self.comComboBox.setEnabled(False)
        self.nextButton.setEnabled(False)

    def goBack(self):
        self.main_window.activateWindow(0)  # Go back to Hex File Selection window

    def refreshCOMPorts(self):
        self.populateCOMPorts()

    def moveToNextWindow(self):
        self.selectCOMPort()
        self.main_window.serialSetupWindow.hexFileValueLabel.setText(self.main_window.selectedHexFile)
        self.main_window.serialSetupWindow.comPortValueLabel.setText(self.main_window.selectedCOMPort)

        if self.main_window.selectedHexFile == "":
            QMessageBox.warning(self, "No HEX File Selected", "Please select a HEX file.")
        elif self.main_window.selectedCOMPort == "":
            QMessageBox.warning(self, "No COM Port Selected", "Please select a COM port.")
        else:
            self.main_window.activateWindow(2)  # Go to Serial Setup window





class SerialSetupWindow(QWidget):
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

        baudRateLabel = QLabel("Baud Rate:")
        self.baudRateComboBox = QComboBox()
        self.baudRateComboBox.setStyleSheet("font-size: 14px;")
        self.baudRateComboBox.setFixedWidth(200)
        self.baudRateComboBox.addItems(["9600", "115200"])  # Add available baud rates
        self.baudRateComboBox.setCurrentIndex(-1)
        formLayout.addRow(baudRateLabel, self.baudRateComboBox)

        mainLayout.addLayout(formLayout)

        buttonLayout = QHBoxLayout()

        self.goBackButton = QPushButton("Go Back")
        self.goBackButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.goBackButton.setStyleSheet("background-color: #3f51b5; color: white; text-align: center;")
        self.goBackButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.goBackButton.clicked.connect(self.goBack)
        buttonLayout.addWidget(self.goBackButton)

        self.startButton = QPushButton("Start")
        self.startButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.startButton.setStyleSheet("background-color: #4CAF50; color: white; text-align: center;")
        self.startButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.startButton.clicked.connect(self.startSerialComm)
        buttonLayout.addWidget(self.startButton)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def startSerialComm(self):
        baudRateIndex = self.baudRateComboBox.currentIndex()
        if baudRateIndex == -1:
            QMessageBox.warning(self, "No Baud Rate Selected", "Please select a baud rate.")
            return

        selectedBaudRate = self.baudRateComboBox.itemText(baudRateIndex)

        print("Selected Baud Rate:", selectedBaudRate)

        self.main_window.selectedBaudRate = selectedBaudRate  # Store the selected baud rate
        self.main_window.serialArduino=self.setupSerialComm(
            COMport=self.main_window.selectedCOMPort,
            baudRate=self.main_window.selectedBaudRate,
            timeOut=10
        )
        
        self.main_window.close()

   
    def setupSerialComm(self, COMport, baudRate, timeOut):
        """Setup serial communication"""
        while True:
            try:
                targetArduino = serial.Serial(
                    COMport, baudRate, timeout=timeOut, write_timeout=timeOut, bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE
                )
                return targetArduino
            except Exception as error:
                error_message = f"Oops! Trouble initiating communication with Arduino.\n"
                error_message += f"Make sure Arduino is connected to the same COM-port that you mentioned.\n"
                error_message += f"Error: {str(error)}"
                message_box = QMessageBox(self)
                message_box.setIcon(QMessageBox.Warning)
                message_box.setWindowTitle("Serial Communication Error")
                message_box.setText(error_message)
                message_box.addButton("Try Again", QMessageBox.AcceptRole)
                message_box.addButton("Exit", QMessageBox.RejectRole)
                
                result = message_box.exec_()
                message_box.close()
                
                if result == QMessageBox.AcceptRole:
                    self.main_window.activateWindow(1)  # Try again
                    

                else:
                    return None  # Exit the method or handle the case as needed
            break
     

    def goBack(self):
        self.main_window.activateWindow(1)  # Go back to Hex File Selection window




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # Disable maximize button
        self.selectedHexFile = ""
        self.selectedCOMPort = ""
        self.selectedBaudRate = ""
        self.serialArduino=""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("BOSON VCU")
        self.setGeometry(590, 340, 500, 350)  # Set the window's position and size (x, y, width, height)

        mainLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(5)  # Set the spacing between buttons

        self.hexFileSelectionButton = QPushButton("Select HEX File", self)
        self.hexFileSelectionButton.setFixedSize(115, 30)
        self.hexFileSelectionButton.clicked.connect(self.hexFileSelectionClicked)
        buttonLayout.addWidget(self.hexFileSelectionButton)

        self.comPortSelectionButton = QPushButton("Select COM Port", self)
        self.comPortSelectionButton.setFixedSize(115, 30)
        self.comPortSelectionButton.clicked.connect(self.comPortSelectionClicked)
        buttonLayout.addWidget(self.comPortSelectionButton)

        self.startButton = QPushButton("Serial setup", self)
        self.startButton.setFixedSize(115, 30)
        self.startButton.clicked.connect(self.Serial_setup)
        buttonLayout.addWidget(self.startButton)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)


        self.stack = QStackedWidget()

        self.hexFileSelectionWindow = HexFileSelectionWindow(self)
        self.comPortSelectionWindow = COMPortSelectionWindow(self)
        self.serialSetupWindow = SerialSetupWindow(self)

        self.stack.addWidget(self.hexFileSelectionWindow)
        self.stack.addWidget(self.comPortSelectionWindow)
        self.stack.addWidget(self.serialSetupWindow)

        mainLayout.addWidget(self.stack)

        self.setLayout(mainLayout)

        self.activateWindow(0)  # Start with Hex File Selection window

    def hexFileSelectionClicked(self):
        self.activateWindow(0)

    def comPortSelectionClicked(self):
        if self.selectedHexFile == "":
            QMessageBox.warning(self, "No HEX File Selected", "Please select a HEX file first.")
        else:
            self.activateWindow(1)

    def Serial_setup(self):
        if self.selectedHexFile == "":
            QMessageBox.warning(self, "No HEX File Selected", "Please select a HEX file first.")
        elif self.selectedCOMPort == "":
            QMessageBox.warning(self, "No COM Port Selected", "Please select a COM port first.")
        else:
            self.activateWindow(2)

    def activateWindow(self, index):
        if index == 1:  # COM Port Selection window
            if self.selectedHexFile == "":
                QMessageBox.warning(self, "No HEX File Selected", "Please select a HEX file first.")
                return
            self.comPortSelectionWindow.populateCOMPorts()
            self.startButton.setEnabled(True)
        elif index == 2:  # Serial Setup window
            if self.selectedHexFile == "":
                QMessageBox.warning(self, "No HEX File Selected", "Please select a HEX file first.")
                return
            if self.selectedCOMPort == "":
                QMessageBox.warning(self, "No COM Port Selected", "Please select a COM port first.")
                return
            
            self.hexFileSelectionButton.setEnabled(True)
            self.comPortSelectionButton.setEnabled(True)
            self.startButton.setEnabled(True)

        self.stack.setCurrentIndex(index)


    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Quit', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()




# if __name__ == '__main__':
app = QApplication(sys.argv)
pixmap = QPixmap(64, 64)  # Set the size of the pixmap
pixmap.fill(Qt.white)  # Set the background color to white
painter = QPainter(pixmap)
font = QFont("Arial", 40, QFont.Bold)
font.setItalic(True)  # Set font style to italic
painter.setFont(font)
painter.setPen(QColor(Qt.red))  # Set text color to red
painter.drawText(pixmap.rect(), Qt.AlignCenter, "B")  # Replace "B" with the desired letter
painter.end()
icon = QIcon(pixmap)
app.setWindowIcon(icon)
mainWindow = MainWindow()
mainWindow.show()
app.exec_()
print("\n\nWelcome to Mew utility.\n")
while 1:
    HexFileName = mainWindow.selectedHexFile
    # print("Selected HEX file:", HexFileName)
    #hexFileRawData = open(HexFileName, 'r')
    HexFileData = IntelHex()
    
    HexFileData.fromfile(HexFileName,format='hex')
    HexPyDictionary = HexFileData.todict()
    
    programMemoryStartAddress = HexFileData.minaddr()
    
    totalSize = HexFileData.maxaddr() - HexFileData.minaddr() +1
    programExecutionStartAddress = HexFileData.start_addr['EIP']
    segmentList = HexFileData.segments()
    numberOfDataSegments = len(segmentList)


    arduinoHandshakeFlag = 0
    arduinoHandshakeList = [0x0B, 0xA0]
    while 1: #Arduino handshake loop
        COMport = mainWindow.selectedCOMPort
        targetArduino =mainWindow.serialArduino
        time.sleep(3)
        startTimeForArduinoHandshake = time.time()
        # print(startTimeForArduinoHandshake)
        while((time.time() - startTimeForArduinoHandshake) < 30):
            try:
                targetArduino.write(arduinoHandshakeList[0].to_bytes(1, byteorder='big'))
            except Exception as error:
                break
            arduinoResponse = targetArduino.read(size=1)
            if arduinoResponse == b'\xB0':
                targetArduino.write(arduinoHandshakeList[1].to_bytes(1, byteorder='big'))
                arduinoResponse = targetArduino.read(size=1)
                if arduinoResponse == b'\x0A':
                    print("\nArduino Handshake successful!\n")
                    arduinoHandshakeFlag = 1
                    break
        if arduinoHandshakeFlag == 1:
            break
        else:
            targetArduino.close()
            print("\nArduino Handshake unsuccessful!\n")
            userChoice = int(input("Do you want to \n1> Try again or 2> Exit? "))
            if userChoice == 1:
                continue
            else:
                exit()


    communicationOkayFlag = 0

    break
print("END")






