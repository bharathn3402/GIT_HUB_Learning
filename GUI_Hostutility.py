from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout
from PyQt5.QtGui import QFont,QIcon,QPixmap,QPainter, QColor
from PyQt5.QtCore import Qt
import os.path


import sys
import serial
import serial.tools.list_ports
import time
from intelhex import IntelHex


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
        comLabel = QLabel(" Select a COM Port :")
        comLabel.setStyleSheet("font-size: 16px; font-weight: bold;")
        comLayout.addWidget(comLabel)
        comLayout.setContentsMargins(100, 50, 150, 0)  # Adjust the bottom margin to a smaller value

        self.comComboBox = QComboBox()
        self.comComboBox.setStyleSheet("font-size: 14px;")
        self.comComboBox.setFixedWidth(350)
        comLayout.addWidget(self.comComboBox)

        mainLayout.addLayout(comLayout)

        baudLayout = QHBoxLayout()
        baudLabel = QLabel("Selected Baud Rate:    115200")
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

        # selectedPort = self.comComboBox.itemText(selectedCOMIndex)
        selectedPort= self.com_ports[selectedCOMIndex].device

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

        baudRateLabel = QLabel("Selected Baud Rate:")
        self.baudRatevalueLabel = QLabel("115200")
        formLayout.addRow(baudRateLabel, self.baudRatevalueLabel)

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
        

        selectedBaudRate = 115200

        print("Selected Baud Rate:", selectedBaudRate)
        self.main_window.selectedBaudRate = selectedBaudRate  # Store the selected baud rate
        
        targetArduino=self.setupSerialComm(
            COMport=self.main_window.selectedCOMPort,
            baudRate=115200,
            timeOut=10
            
        )
        if targetArduino == None:
            return
        else:
            self.Arduinohandshakeflag=self.Arduinohandshake()
            if self.Arduinohandshakeflag == 1:
                self.bootloader()
                print("exit")
                sys.exit()
    
    
        

    def bootloader(self):
        while 1:
            self.communicationOkayFlag = 0

            if self.Arduinohandshakeflag == 1:
                self.targetArduino.flushInput()
                startTimeForVCUhandshake = time.time() 
                  
                while (1):
                    try:
                        
                        if ((time.time() - startTimeForVCUhandshake) < 60): #Check for VCU availability for 60 seconds
                            arduinoResponse = targetArduino.read(size=10)
                            if arduinoResponse != b'':                              
                                if arduinoResponse[0] == 0x51 and arduinoResponse[1] == 0x08:
                                    QMessageBox.information(self,"Mew bootloader detected!\n", "Mew bootloader detected!\n")
                                    print("Mew bootloader detected!\n")
                                    break                          
                        else:
                            bootloader_box = QMessageBox(self)
                            bootloader_box.setIcon(QMessageBox.Warning)
                            bootloader_box.setWindowTitle("Bootloader Error")
                            bootloader_box.setText("Mew bootloader detection timeout!\n")
                            try_again_button = bootloader_box.addButton("Try Again", QMessageBox.AcceptRole)
                            exit_button = bootloader_box.addButton("Exit", QMessageBox.RejectRole)
                            bootloader_box.exec_()

                            if bootloader_box.clickedButton() == try_again_button:
                                bootloader_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
                                startTimeForVCUhandshake = time.time()
                                continue  # Try again
                                
                            else:
                                bootloader_box.done(QMessageBox.RejectRole)
                                self.main_window.close()
                                return None  # Exit the method or handle the case as needed

                    except Exception as error:
                        QMessageBox.information(self, "Error in  connection ","Arduino connection problem. Please restart utility.")   
                        time.sleep(2)
                        self.main_window.close()
                        sys.exit()
                try:
                    startAddressBytes = programMemoryStartAddress.to_bytes(4, byteorder='big', signed=False)
                    vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
                    writtenBytes = self.sendArduinoCANframe(self.targetArduino, vcuInitList, startAddressBytes)
                   
                    executionStartAddressBytes = programExecutionStartAddress.to_bytes(4, byteorder='big', signed=False)
                    vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
                    writtenBytes = self.sendArduinoCANframe(self.targetArduino, vcuInitList, executionStartAddressBytes)
                    numberOfDataSegmentsBytes = numberOfDataSegments.to_bytes(2, byteorder='big', signed=False)
                    totalSizeBytes = totalSize.to_bytes(4, byteorder='big', signed=False)
                    vcuInitList = [0x50, 0x08, 0xB0, 0x00]
                    writtenBytes = self.sendArduinoCANframe(self.targetArduino, vcuInitList, numberOfDataSegmentsBytes, totalSizeBytes)

                    self.arduinoResponse = self.targetArduino.read(size=10)
                    print(arduinoResponse) 
                    print(self.arduinoResponse)
                    if self.arduinoResponse != b'':
                        print(self.arduinoResponse[0],self.arduinoResponse[3])
                        if self.arduinoResponse[0] == 0x51 and self.arduinoResponse[3] == 0x01:
                            self.communicationOkayFlag = 1
                            print("\nMew handshake successful!  Uploading firmware.\nNumber of memory segments in hex file: " + str(numberOfDataSegments) + "\n\n")
                        elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x10:

                            self.communicationOkayFlag = 0
                    else:
                        print("Mew handshake timeout! Please restart the utility.")
                        time.sleep(10)
                        exit()

                except Exception as error:
                        print("Arduino connection problem. Please restart utility.")
                        time.sleep(10)
                        exit()
                
                if self.communicationOkayFlag != 1:
                    print("Mew denied communication! Please restart the utility.")
                    time.sleep(10)
                    exit()

    def sendArduinoCANframe(self,targetArduino = [], listOfBytes = [], byteFrame1 = [], byteFrame2 = []):
        writtenBytes = 0
        if listOfBytes != []:
            for byteIndex in range(len(listOfBytes)):
                writtenBytes = writtenBytes + targetArduino.write(listOfBytes[byteIndex].to_bytes(1, byteorder='big'))
        if byteFrame1 != []:
            for byte in byteFrame1:
                writtenBytes = writtenBytes +targetArduino.write(byte.to_bytes(1, byteorder='big'))
        if byteFrame2 != []:
            for byte in byteFrame2:
                writtenBytes = writtenBytes +targetArduino.write(byte.to_bytes(1, byteorder='big'))

        time.sleep(0.01)

        return writtenBytes
                    
                        
                
                        
                           
    def setupSerialComm(self, COMport, baudRate, timeOut):
        """Setup serial communication"""
        while 1:
            try:
                targetArduino = serial.Serial(COMport, baudRate, timeout=timeOut, write_timeout=timeOut, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
                
                return targetArduino
                
            except Exception as error:
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
                    self.main_window.comPortSelectionClicked()  # Try again
                    
                else:
                    message_box.done(QMessageBox.RejectRole)
                    self.main_window.close()
                    return None  # Exit the method or handle the case as needed
                
            break
    


    def Arduinohandshake(self):
        arduinoHandshakeFlag = 0
        arduinoHandshakeList = [0x0B, 0xA0]

        while 1: #Arduino handshake loop            
            time.sleep(3)
            startTimeForArduinoHandshake = time.time()
            while ((time.time() - startTimeForArduinoHandshake) < 30):
                try:
                    self.targetArduino.write(arduinoHandshakeList[0].to_bytes(1, byteorder='big'))               
                except Exception as error:
                    break
                arduinoResponse = self.targetArduino.read(size=1)
                if arduinoResponse == b'\xB0':
                    self.targetArduino.write(arduinoHandshakeList[1].to_bytes(1, byteorder='big'))
                    arduinoResponse = self.targetArduino.read(size=1)
                    if arduinoResponse == b'\x0A':
                        QMessageBox.information(self,"Arduino handshake successful", "Arduino handshake successful!")
                        print("\nArduino Handshake successful!\n")
                        arduinoHandshakeFlag = 1
                        break
            if arduinoHandshakeFlag == 1:
                return arduinoHandshakeFlag
                
            else:
                self.targetArduino.close()
                # QMessageBox.information(self,"Arduino handshake unsuccessful", "Arduino handshake unsuccessful!")
                error_message="\nArduino Handshake unsuccessful!\n"
                print("\nArduino Handshake unsuccessful!\n")
                Handshake_box = QMessageBox(self)
                Handshake_box.setIcon(QMessageBox.Warning)
                Handshake_box.setWindowTitle("Serial Communication Error")
                Handshake_box.setText(error_message)
                try_again_button = Handshake_box.addButton("Try Again", QMessageBox.AcceptRole)
                exit_button = Handshake_box.addButton("Exit", QMessageBox.RejectRole)
                Handshake_box.exec_()

                if Handshake_box.clickedButton() == try_again_button:
                    Handshake_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
                    continue # Try again
                    
                else:
                    Handshake_box.done(QMessageBox.RejectRole)
                    self.main_window.close()
                    return None  # Exit the method or handle the case as needed
            

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




if __name__ == '__main__':
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
    # hexWindow=HexFileSelectionWindow()
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    # print("\n\nWelcome to Mew utility.\n")