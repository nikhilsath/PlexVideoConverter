from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QPushButton, QTabWidget, QLabel, QSizePolicy
import sys

class WorkerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Worker UI - Plex Video Converter")
        self.setGeometry(200, 200, 800, 600)
        
        main_layout = QHBoxLayout(self)
        
        # Left Panel - Job Queue and Logs
        left_panel = QVBoxLayout()
        
        self.job_queue_label = QLabel("Job Queue")
        self.job_queue_list = QListWidget()
        
        self.tabs = QTabWidget()
        self.logs_tab = QTextEdit()
        self.logs_tab.setReadOnly(True)
        self.errors_tab = QTextEdit()
        self.errors_tab.setReadOnly(True)
        
        self.tabs.addTab(self.logs_tab, "Logs")
        self.tabs.addTab(self.errors_tab, "Errors")
        
        left_panel.addWidget(self.job_queue_label)
        left_panel.addWidget(self.job_queue_list)
        left_panel.addWidget(self.tabs)
        
        # Right Panel - Controls and Worker Data
        right_panel = QVBoxLayout()
        
        self.worker_status_label = QLabel("Worker Status: Idle")
        self.worker_info_label = QLabel("Worker Info: Not Connected")
        
        self.start_button = QPushButton("Start Processing")
        self.stop_button = QPushButton("Stop Processing")
        self.refresh_button = QPushButton("Refresh Queue")
        
        # Disable buttons initially
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        
        right_panel.addWidget(self.worker_status_label)
        right_panel.addWidget(self.worker_info_label)
        right_panel.addWidget(self.start_button)
        right_panel.addWidget(self.stop_button)
        right_panel.addWidget(self.refresh_button)
        
        # Add Panels to Main Layout
        main_layout.addLayout(left_panel, 2)  # Left panel takes 2/3 of space
        main_layout.addLayout(right_panel, 1)  # Right panel takes 1/3 of space
        
        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkerUI()
    window.show()
    sys.exit(app.exec())
