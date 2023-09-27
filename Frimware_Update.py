from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout, QSizePolicy, QSpacerItem,QScrollArea,QTextEdit,QTextBrowser,QFrame
from PyQt5.QtGui import QFont,QIcon,QPixmap,QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import hostUtility_1
import time
from intelhex import IntelHex

class Frimware_updateWindow(QWidget):
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
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setFrameShape(QFrame.NoFrame)  # Remove the frame around the scroll area
        contentWidget = QWidget()

        # Create a QTextBrowser for firmware update status
        self.firmwareStatusLabel = QTextBrowser()
        self.firmwareStatusLabel.setReadOnly(True)

        contentLayout = QVBoxLayout()
        contentLayout.addWidget(self.firmwareStatusLabel)
        contentWidget.setLayout(contentLayout)

        scrollArea.setWidget(contentWidget)
        mainLayout.addWidget(scrollArea)

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
        self.uploadButton.clicked.connect(self.flashfrimware)
        buttonLayout.addWidget(self.uploadButton, alignment=Qt.AlignCenter)
        buttonLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def flashfrimware(self):

        self.messageLabel.setVisible(False)
        self.uploadButton.setVisible(False)
        QApplication.processEvents()
        HexFileName = self.main_window.selectedHexFile
        HexFileData = IntelHex()
        HexFileData.fromfile(HexFileName, format='hex')
        HexPyDictionary = HexFileData.todict()
        segmentList = HexFileData.segments()

        numberOfSegments = 0
        firmwareFlashedSuccessfully = True
        try:
            for segment in reversed(segmentList):
                firmwareFlashedSuccessfully, message, numberOfSegments = hostUtility_1.flashFirmware(
                    numberOfSegments, segment, HexPyDictionary, self.main_window.targetArduino, firmwareFlashedSuccessfully)
                numberOfSegments = numberOfSegments
                if firmwareFlashedSuccessfully:
                    message = f"{numberOfSegments}: Segment written successfully."
                    self.updateStatusLabel(message)
                    QApplication.processEvents()  # Force the GUI to update
                    continue
                else:
                    QMessageBox.information(self, "VCU communication!", message)
                    break

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
                    return None  # Exit the method or handle the case as needed
            else:
                QMessageBox.information(self, "Flashing error", "Firmware flashing unsuccessful! Please restart the utility.")
                time.sleep(3)
                self.main_window.close()
        except hostUtility_1.SerialConnectionError as error:
            message = str(error)
            self.updateStatusLabel(message)
            QApplication.processEvents()
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
                # self.main_window.targetArduino.close()
                # self.move_ToNextWindow()
                # return
            else:
                message_box.done(QMessageBox.RejectRole)
                self.main_window.close()
                return None

    def updateStatusLabel(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        formatted_message = f"<p style='text-align:justify; margin-left: 50px; font-size: 14px;'>[{timestamp}] {message}</p>"
        self.firmwareStatusLabel.append(formatted_message)