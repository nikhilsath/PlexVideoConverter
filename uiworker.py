import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QTextEdit, QPushButton, QTabWidget, QLabel
)
from db_handler import get_queue
from PyQt6.QtCore import Qt

class WorkerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Worker UI - Plex Video Converter")
        self.setGeometry(200, 200, 800, 600)
        
        main_layout = QHBoxLayout(self)
        
        # Left Panel - Job Queue and Logs/Errors
        left_panel = QVBoxLayout()
        
        self.job_queue_label = QLabel("Job Queue")
        
        # Replace QListWidget with QTableWidget for a table-like format
        self.job_queue_table = QTableWidget()
        self.job_queue_table.setColumnCount(4)
        self.job_queue_table.setHorizontalHeaderLabels(["File Name", "Size (GB)", "Status", "Order"])
        self.job_queue_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.job_queue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.job_queue_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Tabs for Logs and Errors
        self.tabs = QTabWidget()
        self.logs_tab = QTextEdit()
        self.logs_tab.setReadOnly(True)
        self.errors_tab = QTextEdit()
        self.errors_tab.setReadOnly(True)
        
        self.tabs.addTab(self.logs_tab, "Logs")
        self.tabs.addTab(self.errors_tab, "Errors")
        
        left_panel.addWidget(self.job_queue_label)
        left_panel.addWidget(self.job_queue_table)
        left_panel.addWidget(self.tabs)
        
        # Right Panel - Controls and Worker Data
        right_panel = QVBoxLayout()
        
        self.worker_status_label = QLabel("Worker Status: Idle")
        self.worker_info_label = QLabel("Worker Info: Not Connected")
        
        self.start_button = QPushButton("Start Processing")
        self.stop_button = QPushButton("Stop Processing")
        self.refresh_button = QPushButton("Refresh Queue")
        
        # Connect the refresh button to our update method
        self.refresh_button.clicked.connect(self.update_queue_table)
        
        # Enable the refresh button, disable start/stop initially
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.refresh_button.setEnabled(True)
        
        right_panel.addWidget(self.worker_status_label)
        right_panel.addWidget(self.worker_info_label)
        right_panel.addWidget(self.start_button)
        right_panel.addWidget(self.stop_button)
        right_panel.addWidget(self.refresh_button)
        
        # Add Panels to Main Layout
        main_layout.addLayout(left_panel, 2)  # Left panel takes 2/3 of space
        main_layout.addLayout(right_panel, 1)  # Right panel takes 1/3 of space
        
        self.setLayout(main_layout)
        
        # Update the queue table when the UI loads
        self.update_queue_table()

    def update_queue_table(self):
        """
        Fetches queued items from the database and displays them in the QTableWidget,
        matching the table format in ui.py.
        """
        jobs = get_queue()
        
        # Clear current rows
        self.job_queue_table.setRowCount(0)
        
        # Populate rows
        for row_index, (file_name, file_size, job_status, queue_position) in enumerate(jobs):
            self.job_queue_table.insertRow(row_index)
            
            # Column 0: File Name
            self.job_queue_table.setItem(row_index, 0, QTableWidgetItem(str(file_name)))
            
            # Column 1: Size (GB) - convert bytes to GB
            size_gb = file_size / (1024**3) if file_size else 0
            self.job_queue_table.setItem(row_index, 1, QTableWidgetItem(f"{size_gb:.2f} GB"))
            
            # Column 2: Status
            self.job_queue_table.setItem(row_index, 2, QTableWidgetItem(str(job_status)))
            
            # Column 3: Order
            if queue_position is None:
                queue_str = "—"
            else:
                queue_str = str(queue_position)
            self.job_queue_table.setItem(row_index, 3, QTableWidgetItem(queue_str))
        
        print(f"Queue table updated with {len(jobs)} items.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkerUI()
    window.show()
    sys.exit(app.exec())
