from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QPushButton, QComboBox, QLabel, QMessageBox, QFormLayout, QSizePolicy, QSpacerItem,QScrollArea,QTextEdit,QTextBrowser,QFrame
from PyQt5.QtGui import QFont,QIcon,QPixmap,QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import hostUtility_1
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
        hexFiles=hostUtility_1.selectHexFile()
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