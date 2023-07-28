from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QFont,QIcon,QPixmap,QPainter, QColor
from PyQt5.QtCore import Qt
import os.path
import sys
import serial
import serial.tools.list_ports
from datetime import datetime

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
        self.nextButton.clicked.connect(self.moveToNext_Window)
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

    def refreshHexFiles(self):
        self.populateHexFiles()

    def moveToNext_Window(self):
        selectedHexIndex = self.fileComboBox.currentIndex()
        if selectedHexIndex == -1:
            QMessageBox.warning(self, "No File Selected", "Please select a HEX file.")
            return

        selectedHexFile = self.fileComboBox.itemText(selectedHexIndex)
        self.main_window.selectedHexFile = selectedHexFile  # Store the selected hex file name
        
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

        self.setLayout(mainLayout)

    def populateCOMPorts(self):
        self.com_ports = serial.tools.list_ports.comports()
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
            # QMessageBox.warning(self, "No Port Selected", "Please select a COM port.")
            return

        selectedPort = self.com_ports[selectedCOMIndex].device
        self.main_window.selectedCOMPort = selectedPort  # Store the selected COM port

    def goBack(self):
        self.main_window.activateWindow(0)  # Go back to Hex File Selection window

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
            self.main_window.targetArduino=self.setupSerialComm(
            COMport=self.main_window.selectedCOMPort,
            baudRate=115200,
            timeOut=10)
            if self.main_window.targetArduino!=None:
                self.main_window.activateWindow(2)  # Go to Serial Setup window
        
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
                    self.main_window.activateWindow(1)  # Try again
                    
                else:
                    message_box.done(QMessageBox.RejectRole)
                    self.main_window.close()
                    return None  # Exit the method or handle the case as needed

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

        self.handshakeStatusLabel = QLabel()
        self.handshakeStatusLabel.setWordWrap(True)  # Enable multiline display
        formLayout.addRow("Handshake Status:", self.handshakeStatusLabel)

        mainLayout.addLayout(formLayout)

        buttonLayout = QHBoxLayout()

        # Create a layout to hold the "Click here" button and message label in the same line
        messageButtonLayout = QHBoxLayout()
        self.messageLabel = QLabel("Please click on 'Click here' to start handshake ....")
        self.messageLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.messageLabel.setFixedSize(300, 30)  # Set the size as desired
        messageButtonLayout.addWidget(self.messageLabel)

        self.clickButton = QPushButton("Click here")
        self.clickButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.clickButton.setStyleSheet("background-color: #3f51b5; color: white; text-align: Center;")
        self.clickButton.setFixedSize(100, 30)  # Adjust the size as desired
        self.clickButton.clicked.connect(self.handshake)
        messageButtonLayout.addWidget(self.clickButton)

        # Add spacer to center the "Click here" button
        messageButtonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        buttonLayout.addLayout(messageButtonLayout)
        self.arduinohandshakeLabel = QLabel(" please wait...")
        self.arduinohandshakeLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.arduinohandshakeLabel.setFixedSize(300, 30)  # Set the size as desired
        self.arduinohandshakeLabel.setVisible(False)  # Initially, hide the label
        buttonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        buttonLayout.addWidget(self.arduinohandshakeLabel)
        buttonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
       
        self.handshakeInProgressLabel = QLabel("MEW Handshake in progress please wait...")
        self.handshakeInProgressLabel.setStyleSheet("font-size: 14px; font-weight;")
        self.handshakeInProgressLabel.setFixedSize(250, 30)  # Set the size as desired
        self.handshakeInProgressLabel.setVisible(False)  # Initially, hide the label
        buttonLayout.addWidget(self.handshakeInProgressLabel)

        
        

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        
    def handshake(self):
        self.messageLabel.setVisible(False)
        self.clickButton.setVisible(False)
        self.clickButton.deleteLater()
        self.arduinohandshakeLabel.setVisible(True)

        HexFileName = self.main_window.selectedHexFile
        HexFileData = IntelHex()
        HexFileData.fromfile(HexFileName,format='hex')
        HexPyDictionary = HexFileData.todict()
        programMemoryStartAddress = HexFileData.minaddr()
        totalSize = HexFileData.maxaddr() - HexFileData.minaddr() +1
        programExecutionStartAddress = HexFileData.start_addr['EIP']
        segmentList = HexFileData.segments()
        numberOfDataSegments = len(segmentList) 

        self.arduinoHandshakeflag = self.Arduinohandshake()
        self.main_window.communicationOkayFlag = 0

        if self.arduinoHandshakeflag == 1:
            
            self.arduinohandshakeLabel.setVisible(False)
            self.handshakeInProgressLabel.setVisible(False)

            self.main_window.targetArduino.flushInput()

            startTimeForVCUhandshake = time.time()
            
            while (1):
                try:
                    if ((time.time() - startTimeForVCUhandshake) < 60): #Check for VCU availability for 60 seconds
                        arduinoResponse = self.main_window.targetArduino.read(size=10)
                        if arduinoResponse != b'':
                            if arduinoResponse[0] == 0x51 and arduinoResponse[1] == 0x08:
                                print("Mew bootloader detected!\n")
                                self.updateStatusLabel("Mew bootloader detected!")
                                break
                    else:
                        self.updateStatusLabel("Mew bootloader detection timeout!")
                        # print("Mew bootloader detection timeout!\n")
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

                except Exception as error:
                    QMessageBox.information(self,"Arduino connection problem.", "Arduino connection problem. Please restart utility.")
                    time.sleep(5)
                    self.main_window.close()
            try:
                startAddressBytes = programMemoryStartAddress.to_bytes(4, byteorder='big', signed=False)
                vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
                writtenBytes = self.sendArduinoCANframe(self.main_window.targetArduino, vcuInitList, startAddressBytes)

                executionStartAddressBytes = programExecutionStartAddress.to_bytes(4, byteorder='big', signed=False)
                vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
                writtenBytes = self.sendArduinoCANframe(self.main_window.targetArduino, vcuInitList, executionStartAddressBytes)

                numberOfDataSegmentsBytes = numberOfDataSegments.to_bytes(2, byteorder='big', signed=False)
                totalSizeBytes = totalSize.to_bytes(4, byteorder='big', signed=False)
                vcuInitList = [0x50, 0x08, 0xB0, 0x00]
                writtenBytes = self.sendArduinoCANframe(self.main_window.targetArduino, vcuInitList, numberOfDataSegmentsBytes, totalSizeBytes)

                arduinoResponse = self.main_window.targetArduino.read(size=10)


                if arduinoResponse != b'':
                    if arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x01:
                        self.main_window.communicationOkayFlag = 1
                        message = f"Mew handshake successful!\nNumber of memory segments in hex file: {numberOfDataSegments}"
                        self.updateStatusLabel(message)
                        QMessageBox.information(self, "Mew handshake", message)
                        self.handshakeInProgressLabel.setVisible(False)
                        
                        self.clickButton.hide()
                        self.layout().removeWidget(self.clickButton)
                        self.clickButton.deleteLater()
                        # self.uploadInProgressLabel.setVisible(True)  # Initially, hide the label

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

                    elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x10:
                        self.main_window.communicationOkayFlag = 0
                else:
                    message = "Mew handshake timeout! Please restart the utility."
                    self.updateStatusLabel(message)
                    QMessageBox.information(self, "Mew handshake error", message)
                    time.sleep(2)
                    self.main_window.close()

            except Exception as error:
                message = "Arduino connection problem. Please restart utility."
                self.updateStatusLabel(message)
                QMessageBox.information(self, "Arduino connection error", message)
                time.sleep(5)
                self.main_window.close()

            if self.main_window.communicationOkayFlag != 1:
                message = "Mew denied communication! Please restart the utility."
                self.updateStatusLabel(message)
                QMessageBox.information(self, "Mew denied communication", message)
                time.sleep(5)
                self.main_window.close()
                

    def updateStatusLabel(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        formatted_message = f"<p style='text-align:justify;'>[{timestamp}] {message}</p>"
        current_text = self.handshakeStatusLabel.text()
        updated_text = f"{current_text}{formatted_message}"
        self.handshakeStatusLabel.setText(updated_text)


    def sendArduinoCANframe(self,targetArduino = [], listOfBytes = [], byteFrame1 = [], byteFrame2 = []):
        writtenBytes = 0
        if listOfBytes != []:
            for byteIndex in range(len(listOfBytes)):
                writtenBytes = writtenBytes + targetArduino.write(listOfBytes[byteIndex].to_bytes(1, byteorder='big'))
        if byteFrame1 != []:
            for byte in byteFrame1:
                writtenBytes = writtenBytes + targetArduino.write(byte.to_bytes(1, byteorder='big'))
        if byteFrame2 != []:
            for byte in byteFrame2:
                writtenBytes = writtenBytes + targetArduino.write(byte.to_bytes(1, byteorder='big'))

        time.sleep(0.01)

        return writtenBytes

    def Arduinohandshake(self):
        self.arduinoHandshakeFlag = 0
        arduinoHandshakeList = [0x0B, 0xA0]

        while 1: #Arduino handshake loop            
            time.sleep(3)
            startTimeForArduinoHandshake = time.time()
            while ((time.time() - startTimeForArduinoHandshake) < 30):
                try:
                    self.main_window.targetArduino.write(arduinoHandshakeList[0].to_bytes(1, byteorder='big'))               
                except Exception as error:
                    break
                arduinoResponse = self.main_window.targetArduino.read(size=1)
                if arduinoResponse == b'\xB0':
                    self.main_window.targetArduino.write(arduinoHandshakeList[1].to_bytes(1, byteorder='big'))
                    arduinoResponse = self.main_window.targetArduino.read(size=1)
                    if arduinoResponse == b'\x0A':
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
                        message = f"[{timestamp}]: Arduino handshake successful! "
                        self.handshakeStatusLabel.setText(message)  # Set the handshake message label
                        QMessageBox.information(self,"Arduino handshake successful", "Arduino handshake successful!")
                        print("\nArduino Handshake successful!\n")
                        self.arduinoHandshakeFlag = 1
                        break

            if self.arduinoHandshakeFlag == 1:
                return self.arduinoHandshakeFlag
                
            else:
                self.main_window.targetArduino.close()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
                message = f"{timestamp}: Arduino handshake unsuccessful! "
                self.handshakeStatusLabel.setText(message)  # Set the handshake message label
                error_message="Arduino Handshake unsuccessful!"
                # print("\nArduino Handshake unsuccessful!\n")
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
    
    def move_ToNextWindow(self):
        self.main_window.activateWindow(3)  # Go to Serial Setup window


class Frimware_updateWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        formlayout = QFormLayout()

        self.segmentStatusLabel = QLabel()
        self.segmentStatusLabel.setWordWrap(True)  # Enable multiline display
        formlayout.addRow("Uploading frimware", self.segmentStatusLabel)
        mainLayout.addLayout(formlayout)


        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch() # Add stretch before the button to center it
        doneButton = QPushButton("Upload")
        doneButton.setFont(QFont("Arial", 10, QFont.Bold))
        doneButton.setStyleSheet("background-color: #4CAF50; color: white; text-align: center;")
        doneButton.setFixedSize(100, 30)
        doneButton.clicked.connect(self.flashFirmware)
        buttonLayout.addWidget(doneButton)
        buttonLayout.addStretch()  # Add stretch after the button to center it
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
    
    def sendArduinoCANframe(self,targetArduino = [], listOfBytes = [], byteFrame1 = [], byteFrame2 = []):
        writtenBytes = 0
        if listOfBytes != []:
            for byteIndex in range(len(listOfBytes)):
                writtenBytes = writtenBytes + targetArduino.write(listOfBytes[byteIndex].to_bytes(1, byteorder='big'))
        if byteFrame1 != []:
            for byte in byteFrame1:
                writtenBytes = writtenBytes + targetArduino.write(byte.to_bytes(1, byteorder='big'))
        if byteFrame2 != []:
            for byte in byteFrame2:
                writtenBytes = writtenBytes + targetArduino.write(byte.to_bytes(1, byteorder='big'))

        time.sleep(0.01)

        return writtenBytes

    def flashFirmware(self):
        HexFileName = self.main_window.selectedHexFile
        HexFileData = IntelHex()
        HexFileData.fromfile(HexFileName, format='hex')
        HexPyDictionary = HexFileData.todict()
        segmentList = HexFileData.segments()

        numberOfSegments = 0
        firmwareFlashedSuccessfully = True

        for segment in reversed(segmentList):
            try:
                numberOfSegments = numberOfSegments+1
                segmentStartAddress = segment[0]
                segmentEndAddress = segment[1] - 1
                segementMemory = segmentEndAddress - segmentStartAddress + 1

                CANdataBytes = [0x50, 0x08, 0xB0, 0x01, 0x00, 0x00]
                segmentStartAddressBytes = segmentStartAddress.to_bytes(4, byteorder='big', signed=False)
                writtenBytes = self.sendArduinoCANframe(self.main_window.targetArduino, CANdataBytes, segmentStartAddressBytes)

                pageByteCount = 0 #Reset when reaches 128
                fourByteCount = 0
                dataByteList = []
                for byteAddres in range(segmentStartAddress, segmentEndAddress+1):
                    dataByteList = dataByteList + [HexPyDictionary[byteAddres]]
                    fourByteCount = fourByteCount+1
                    
                    if fourByteCount == 4 or byteAddres == segmentEndAddress:
                        if byteAddres == segmentEndAddress:
                            CANdataBytes = [0x50, 0x08, 0xB0, 0x03, 0x00, 0x00] + dataByteList
                            if fourByteCount < 4:
                                CANdataBytes = CANdataBytes + [0xFF] * (4 - fourByteCount)

                        else:
                            CANdataBytes = [0x50, 0x08, 0xB0, 0x02, 0x00, 0x00] + dataByteList
                        
                        pageByteCount = pageByteCount+4
                        fourByteCount = 0
                        dataByteList = []

                        self.main_window.targetArduino.flushInput()
                        writtenBytes =self.sendArduinoCANframe(self.main_window.targetArduino, CANdataBytes)
                        
                    if (pageByteCount == 128) or byteAddres == segmentEndAddress:
                        arduinoResponse = self.main_window.targetArduino.read(size=10)
                        if arduinoResponse == b'':
                            QMessageBox.information(self,"VCU communication!","VCU communication time out")
                            # print("\nVCU comm. timeout!\n")
                            firmwareFlashedSuccessfully = False
                            break
                        elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x10:
                            QMessageBox.information(self,"VCU communication!","VCU communication error")
                            # print("\nVCU comm. error!\n")
                            firmwareFlashedSuccessfully = False
                            break
                        elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x04:
                            pageByteCount = 0
                            continue

            except Exception as error:
                firmwareFlashedSuccessfully = False

            if firmwareFlashedSuccessfully:
                message = f"{numberOfSegments}: Segment written successfully."
                self.updateStatusLabel(message)
                QApplication.processEvents()  # Force the GUI to update
                print(str(numberOfSegments) + ": Segment written successfully.\n")
                continue
            else:
                break

        if firmwareFlashedSuccessfully:
            time.sleep(5)
            message_box = QMessageBox(self)
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Firmware flashed successfully!")
            message_box.setText("Do you want to Flash firmware again")
            yes_button = message_box.addButton("Yes", QMessageBox.AcceptRole)
            exit_button = message_box.addButton("No", QMessageBox.RejectRole)
            message_box.exec_()

            if message_box.clickedButton() == yes_button:
                message_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
                self.main_window.targetArduino.close()
                self.main_window.activateWindow(0)  # Try again
                
            else:
                message_box.done(QMessageBox.RejectRole)
                self.main_window.close()
                return None  # Exit the method or handle the case as needed
        else:
            QMessageBox.information(self,"Flashing error","Firmware flashing unsuccessful! Please restart the utility.")
            print("\nFirmware flashing unsuccessful! Please restart the utility.\n")
            time.sleep(5)
            self.main_window.close()
            

    
    def updateStatusLabel(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        formatted_message = f"<p style='text-align:justify;'>[{timestamp}] {message}</p>"
        current_text = self.segmentStatusLabel.text()
        updated_text = f"{current_text}{formatted_message}"
        self.segmentStatusLabel.setText(updated_text)



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # Disable maximize button
        self.selectedHexFile = ""
        self.selectedCOMPort = ""
        self.selectedBaudRate = ""
        self.targetArduino = ""
        self.communicationOkayFlag = 0

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

        self.serialSetupButton = QPushButton("Handshake", self)
        self.serialSetupButton.setFixedSize(115, 30)
        self.serialSetupButton.clicked.connect(self.HandshakeClicked)
        buttonLayout.addWidget(self.serialSetupButton)

        self.vcuHandshakeButton = QPushButton("Frimware update", self)
        self.vcuHandshakeButton.setFixedSize(115, 30)
        self.vcuHandshakeButton.clicked.connect(self.Frimware_updateClicked)
        buttonLayout.addWidget(self.vcuHandshakeButton)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.stack = QStackedWidget()

        self.hexFileSelectionWindow = HexFileSelectionWindow(self)
        self.comPortSelectionWindow = COMPortSelectionWindow(self)
        self.HandshakeWindow = HandshakeWindow(self)
        self.Frimware_updateWindow = Frimware_updateWindow(self)

        self.stack.addWidget(self.hexFileSelectionWindow)
        self.stack.addWidget(self.comPortSelectionWindow)
        self.stack.addWidget(self.HandshakeWindow)
        self.stack.addWidget(self.Frimware_updateWindow)

        mainLayout.addWidget(self.stack)

        self.activateWindow(0)  # Start with Hex File Selection window

    def hexFileSelectionClicked(self):
        self.activateWindow(0)

    def comPortSelectionClicked(self):
        if not self.selectedHexFile:
            self.showWarning("No HEX File Selected", "Please select a HEX file first.")
        else:
            self.activateWindow(1)

    def HandshakeClicked(self):
        if not self.selectedHexFile:
            self.showWarning("No HEX File Selected", "Please select a HEX file first.")
        elif not self.selectedCOMPort:
            self.showWarning("No COM Port Selected", "Please select a COM port first.")
        else:
            # Set the selected baud rate (you can update this with the actual baud rate value)
            self.selectedBaudRate = "115200"
            self.activateWindow(2)

    def Frimware_updateClicked(self):
        if not self.selectedHexFile:
            self.showWarning("No HEX File Selected", "Please select a HEX file first.")
        elif not self.selectedCOMPort:
            self.showWarning("No COM Port Selected", "Please select a COM port first.")
        elif not self.communicationOkayFlag:
            self.showWarning("New handshake problem", "Please do New handshake first.")
        else:
            self.activateWindow(3)

    def showWarning(self, title, message):
        QMessageBox.warning(self, title, message)

    def activateWindow(self, index):
        if index == 1:  # COM Port Selection window
            if self.selectedHexFile == "":
                self.showWarning( "No HEX File Selected", "Please select a HEX file first.")
                return
        elif index == 2:  # Serial Setup window
            if self.selectedHexFile == "":
                self.showWarning("No HEX File Selected", "Please select a HEX file first.")
                return
            if self.selectedCOMPort == "":
                self.showWarning("No COM Port Selected", "Please select a COM port first.")
                return
        elif index==3:
            if self.selectedHexFile == "":
                self.showWarning("No HEX File Selected", "Please select a HEX file first.")
                return
            if self.selectedCOMPort == "":
                self.showWarning("No COM Port Selected", "Please select a COM port first.")
                return
            if self.communicationOkayFlag==0:
                self.showWarning("Mew handshake problem", "Please do Mew handshake first.")
                return

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
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    