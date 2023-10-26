"""
BOSON VCU Application

This module serves as the core of the BOSON VCU application, 
providing a graphical user interface for managing the process of selecting HEX files, COM ports, 
and performing firmware updates with Arduino devices. It comprises the primary window and
user interface for the application.

Attributes:
    selected_hex_file (str): The currently selected HEX file.
    selected_com_port (str): The currently selected COM port for serial communication.
    selected_baud_rate (int): The baud rate for the serial communication (default: 115200).
    target_arduino: A reference to the connected Arduino device.
    communication_okay_flag (int): An indicator of the communication status (0: Not okay, 1: Okay).

Classes:
    MainWindow (QWidget): The main application window, 
    managing the user interface and window transitions.

Usage:
    This module contains the primary application window.
"""

from __future__ import annotations

__author__ = "Bharath"
__modified_by__ = "Bharath"
__modified_date__ = "19-10-2023"

# Standard Library Imports
import sys

# Third-party Imports
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QPushButton,
    QMessageBox
)
from PyQt5.QtCore import Qt

# local module imports
from hexfile_selection_window import HexFileSelectionWindow
from comport_selection_window import COMPortSelectionWindow
from handshake_window import HandshakeWindow
from frimware_update_window import FirmwareUpdateWindow

class MainWindow(QWidget):
    """
    This class represents the main window of the BOSON VCU application.

    It provides the user interface for selecting HEX files, COM ports,
    and performing firmware updates with an Arduino device.

    Attributes:
        selected_hex_file (str): The currently selected HEX file.
        selected_com_port (str): The currently selected COM port.
        selected_baud_rate (int): The selected baud rate (default: 115200).
        target_arduino: A reference to the target Arduino device.
        communication_okay_flag (int): It indicates the communication status (0: Not okay, 1: Okay).
    """
    def __init__(self):
        """Initialize the main window of the BOSON VCU application."""
        super().__init__()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.selected_hex_file = None
        self.selected_com_port = None
        self.selected_baud_rate = 115200
        self.target_arduino = None
        self.arduino_handshake_flag = None
        self.communication_okay_flag = 0
        self.bootloader_version = None
        self.checksum_unique = False
        self.firmware_flashed_successfully = False
        self.init_ui()

    def init_ui(self):
        """Initialize the main user interface."""
        self.setWindowTitle("BOSON VCU")
        self.setGeometry(590, 340, 500, 350)

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        self.hex_file_selection_button = QPushButton("Select HEX File", self)
        self.hex_file_selection_button.setFixedSize(115, 30)
        self.hex_file_selection_button.clicked.connect(self.hex_file_selection_clicked)
        button_layout.addWidget(self.hex_file_selection_button )

        self.comport_selection_button = QPushButton("Select COM Port", self)
        self.comport_selection_button.setFixedSize(115, 30)
        self.comport_selection_button.clicked.connect(self.com_port_selection_clicked)
        button_layout.addWidget(self.comport_selection_button)

        self.serial_setup_button = QPushButton("Handshake", self)
        self.serial_setup_button.setFixedSize(115, 30)
        self.serial_setup_button.clicked.connect(self.handshake_clicked)
        button_layout.addWidget(self.serial_setup_button )

        self.firmware_update_button = QPushButton("Frimware update", self)
        self.firmware_update_button.setFixedSize(115, 30)
        self.firmware_update_button.clicked.connect(self.firmware_update_clicked)
        button_layout.addWidget(self.firmware_update_button )

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.stack =  QStackedWidget()

        self.hex_file_selection_window = HexFileSelectionWindow(self)
        self.com_port_selection_window = COMPortSelectionWindow(self)
        self.handshake_window = HandshakeWindow(self)
        self.firmware_update_window = FirmwareUpdateWindow(self)

        self.stack.addWidget(self.hex_file_selection_window)
        self.stack.addWidget(self.com_port_selection_window)
        self.stack.addWidget(self.handshake_window )
        self.stack.addWidget(self.firmware_update_window )

        main_layout.addWidget(self.stack)

        self.activate_window(0)  # Start with Hex File Selection window

    def hex_file_selection_clicked(self):
        """Handle the click event for the HEX file selection button."""
        # self.hex_file_selection_window.next_button.setDisabled(True)
        # self.hex_file_selection_window.refresh_button.setDisabled(True)
        self.activate_window(0)

    def com_port_selection_clicked(self):
        """Handle the click event for the COM Port selection button."""
        if not self.selected_hex_file :
            self.show_warning("No HEX File Selected", "Please select a HEX file first.")
        else:

            self.activate_window(1)

    def handshake_clicked(self):
        """Handle the click event for the Handshake button."""
        if not self.selected_hex_file :
            self.show_warning("No HEX File Selected", "Please select a HEX file first.")
        elif not self.selected_com_port :
            self.show_warning("No COM Port Selected", "Please select a COM port first.")
        else:
            self.activate_window(2)

    def firmware_update_clicked(self):
        """Handle the click event for the Firmware Update button."""
        if not self.selected_hex_file :
            self.show_warning("No HEX File Selected", "Please select a HEX file first.")
        elif not self.selected_com_port :
            self.show_warning("No COM Port Selected", "Please select a COM port first.")
        elif not self.communication_okay_flag :
            self.show_warning("Mew handshake problem", "Please do Mew handshake first.")
        elif not self.checksum_unique:
            self.show_warning("Checksum Not Unique", "The checksum is not unique.")
        else:
            self.activate_window(3)

    def show_warning(self, title, message):
        """Display a warning message dialog."""
        QMessageBox.warning(self, title, message)

    def activate_window(self, index):
        """Activate the specified window in the stack."""
        if index == 1:  # COM Port Selection window
            if self.selected_hex_file is None:
                self.show_warning( "No HEX File Selected", "Please select a HEX file first.")
                return
        elif index == 2:  # Serial Setup window
            if self.selected_hex_file is None:
                self.show_warning("No HEX File Selected", "Please select a HEX file first.")
                return
            if self.selected_com_port is None:
                self.show_warning("No COM Port Selected", "Please select a COM port first.")
                return
        elif index==3:
            if self.selected_hex_file is None:
                self.show_warning("No HEX File Selected", "Please select a HEX file first.")
                return
            if self.selected_com_port is None:
                self.show_warning("No COM Port Selected", "Please select a COM port first.")
                return
            if self.communication_okay_flag == 0:
                self.show_warning("Mew handshake problem", "Please do Mew handshake first.")
                return
            if not self.checksum_unique:
                self.show_warning("Checksum Not Unique", "The checksum is not unique. Please resolve the issue.")
                return
        self.stack.setCurrentIndex(index)


    def closeEvent(self,event):
        """Handle the close event of the main window."""
        reply = QMessageBox.question(
            self,
            'Quit', 
            'Are you sure you want to quit?',  
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit()
        else:
            event.ignore()

    def restart_application(self):
        """Restart the application and reset its state."""
        self.selected_hex_file = None
        self.hex_file_selection_window.file_combo_box.setCurrentIndex(-1)
        self.hex_file_selection_window.file_combo_box.clear()
        self.hex_file_selection_window.populate_hex_files()
        self.hex_file_selection_window.refresh_button.setDisabled(False)
        self.hex_file_selection_window.next_button.setDisabled(False)
        self.selected_com_port  = None
        self.com_port_selection_window.com_combo_box.setCurrentIndex(-1)
        self.com_port_selection_window.com_combo_box.clear()
        self.com_port_selection_window.populate_com_ports()
        self.target_arduino  = None
        self.com_port_selection_window.select_button.setDisabled(False)
        self.com_port_selection_window.refresh_button.setDisabled(False)
        self.com_port_selection_window.go_back_button.setDisabled(False)
        self.communication_okay_flag  = 0
        self.arduino_handshake_flag = None
        self.bootloader_version = None
        self.checksum_unique = False
        self.firmware_flashed_successfully = False
        self.handshake_window.message_label.setVisible(True)
        self.handshake_window.click_button.setVisible(True)
        self.handshake_window.arduino_handshake_label.setVisible(False)
        self.handshake_window.handshake_in_progress_label.setVisible(False)
        self.handshake_window.handshake_status_label.clear()
        self.handshake_window.upload_in_progress_label.setVisible(False)
        self.handshake_window.start_button.setDisabled(False)
        self.handshake_window.start_button.setVisible(False)
        self.firmware_update_window.message_label.setVisible(True)
        self.firmware_update_window.upload_button.setVisible(True)
        self.firmware_update_window.firmware_status_label.clear()
        self.activate_window(0)
