import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('Threading in GUI')

        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 300, 30)
        self.label.setText("Waiting for task to complete...")

        self.button = QPushButton('Start Task', self)
        self.button.setGeometry(10, 50, 100, 30)
        self.button.clicked.connect(self.start_task)

    def start_task(self):
        self.label.setText("Task in progress...")
        self.button.setEnabled(False)  # Disable the button during task execution

        # Create a thread to perform the time-consuming task
        task_thread = threading.Thread(target=self.time_consuming_task)
        task_thread.start()

    def time_consuming_task(self):
        # Simulate a time-consuming task
        for i in range(5):
            time.sleep(1)
            # Update the label with the progress information
            self.label.setText(f"Task is running: {i + 1}")

        # Update the GUI when the task is complete
        self.label.setText("Task completed.")
        self.button.setEnabled(True)  # Re-enable the button

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
