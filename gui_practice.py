from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
import serial.tools.list_ports
import hostUtility_1  # Import your hostUtility module

class COMPortSelectionWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()
        self.populateCOMPorts()  # Call to populate COM ports initially

    def initUI(self):
        mainLayout = QVBoxLayout()

        comLayout = QHBoxLayout()
        comLabel = QLabel("Select a COM Port:")
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
        self.SelectButton.clicked.connect(self.selectCOMPort)
        buttonLayout.addWidget(self.SelectButton)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def populateCOMPorts(self):
        # Call the imported comPortSelection function and get the COM ports
        self.com_ports = hostUtility_1.comPortSelection()

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

if __name__ == "__main__":
    app = QApplication([])
    main_window = COMPortSelectionWindow(None)
    main_window.show()
    app.exec_()
