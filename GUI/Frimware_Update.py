from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout, QSizePolicy, QSpacerItem,QScrollArea,QTextEdit,QTextBrowser,QFrame
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import hostUtility_1
import time
from intelhex import IntelHex

class FirmwareUpdateWorker(QThread):
    update_signal = pyqtSignal(str)
    firmware_flashed = pyqtSignal(bool)  # Corrected signal name
    firmware_failed=pyqtSignal(str)

    def __init__(self, parent, selected_hex_file, target_arduino):
        super().__init__(parent)
        self.selected_hex_file = selected_hex_file
        self.target_arduino = target_arduino

    def run(self):
        try:
            HexFileName = self.selected_hex_file
            HexFileData = IntelHex()
            HexFileData.fromfile(HexFileName, format='hex')
            HexPyDictionary = HexFileData.todict()
            segmentList = HexFileData.segments()

            numberOfSegments = 0
            firmwareFlashedSuccessfully = True
            for segment in reversed(segmentList):
                firmwareFlashedSuccessfully, message, numberOfSegments = hostUtility_1.flashFirmware(
                    numberOfSegments, segment, HexPyDictionary, self.target_arduino, firmwareFlashedSuccessfully)
                numberOfSegments = numberOfSegments
                if firmwareFlashedSuccessfully:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    message = f"[{timestamp}] {numberOfSegments}: Segment written successfully."
                    self.update_signal.emit(message)
                    continue
                else:
                    self.update_signal.emit(f"VCU communication! {message}")
                    break

            self.firmware_flashed.emit(firmwareFlashedSuccessfully)  # Emit the corrected signal name

        except hostUtility_1.SerialConnectionError as error:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            message = str(error) + "VCU communication error!"
            message_1 = f"[{timestamp}] {message}"
            self.update_signal.emit(message_1)
            self.firmware_failed.emit(message)  # Emit error message
            

class FirmwareUpdateWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        self.segmentStatusLabel = QLabel("<b><font size='5'>Uploading&nbsp;Firmware:</font></b>")
        self.segmentStatusLabel.setWordWrap(True)
        mainLayout.addWidget(self.segmentStatusLabel, alignment=Qt.AlignLeft)

        # Create a scroll area for firmware update status
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)  # Remove the frame around the scroll area
        self.contentWidget = QWidget()

        # Create a QTextBrowser for firmware update status
        self.firmwareStatusLabel = QTextBrowser()
        self.firmwareStatusLabel.setReadOnly(True)

        contentLayout = QVBoxLayout()
        contentLayout.addWidget(self.firmwareStatusLabel)
        self.contentWidget.setLayout(contentLayout)

        self.scrollArea.setWidget(self.contentWidget)
        mainLayout.addWidget(self.scrollArea)

        # Message label aligned to the center
        self.messageLabel = QLabel("Please click on 'Upload' to start uploading firmware...")
        self.messageLabel.setStyleSheet("font-size: 14px; font-weight;")
        mainLayout.addWidget(self.messageLabel, alignment=Qt.AlignCenter)

        # Upload button aligned to the center
        buttonLayout = QHBoxLayout()
        buttonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.uploadButton = QPushButton("Upload")
        self.uploadButton.setFont(QFont("Arial", 10, QFont.Bold))
        self.uploadButton.setStyleSheet("background-color: #4CAF50; color: white; text-align: center;")
        self.uploadButton.setFixedSize(100, 30)
        self.uploadButton.clicked.connect(self.flash_firmware)
        buttonLayout.addWidget(self.uploadButton, alignment=Qt.AlignCenter)
        buttonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def flash_firmware(self):
        self.messageLabel.setVisible(False)
        self.uploadButton.setVisible(False)

        self.worker_thread = FirmwareUpdateWorker(self, self.main_window.selectedHexFile, self.main_window.targetArduino)
        self.worker_thread.update_signal.connect(self.update_status_label)
        self.worker_thread.firmware_flashed.connect(self.firmware_status)
        self.worker_thread.firmware_failed.connect(self.firmware_failed)
        self.worker_thread.start()

    def update_status_label(self, message):
        formatted_message = f"<p style='text-align:justify; margin-left: 50px; font-size: 14px;'>{message}</p>"
        self.firmwareStatusLabel.append(formatted_message)



    def firmware_status(self, firmwareFlashedSuccessfully):  # Corrected signal name
        if firmwareFlashedSuccessfully:
            time.sleep(3)
            message_box = QMessageBox(self)
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Firmware flashed successfully!")
            message_box.setText("Do you want to flash firmware again?")
            yes_button = message_box.addButton("Yes", QMessageBox.AcceptRole)
            exit_button = message_box.addButton("No", QMessageBox.RejectRole)
            message_box.exec_()

            if message_box.clickedButton() == yes_button:
                message_box.done(QMessageBox.AcceptRole)
                self.main_window.restart_application()
            else:
                message_box.done(QMessageBox.RejectRole)
                self.main_window.close()
                return
        else:
            QMessageBox.information(self, "Flashing error", "Firmware flashing unsuccessful! Please restart the utility.")
            time.sleep(3)
            self.main_window.close()

    def firmware_failed(self,message):
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Warning)
        message_box.setWindowTitle("VCU communication error!")
        message_box.setText(message)
        yes_button = message_box.addButton("Try again", QMessageBox.AcceptRole)
        exit_button = message_box.addButton("No", QMessageBox.RejectRole)
        message_box.exec_()

        if message_box.clickedButton() == yes_button:
            message_box.done(QMessageBox.AcceptRole)  # Set the result and close the message box
            self.main_window.restart_application()
        else:
            message_box.done(QMessageBox.RejectRole)
            self.main_window.close()
