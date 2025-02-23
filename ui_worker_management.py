from PyQt6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QWidget
from db_handler import get_registered_workers
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class WorkerManagementUI:
    def __init__(self, main_ui):
        """Initialize Worker Management UI component."""
        self.main_ui = main_ui
        self.worker_tab = None
        self.setup_worker_ui()

    def setup_worker_ui(self):
        """Creates and manages the Worker Management UI component."""
        layout = QVBoxLayout()

        # ✅ Worker Table
        self.main_ui.worker_table = QTableWidget()
        self.main_ui.worker_table.setColumnCount(5)
        self.main_ui.worker_table.setHorizontalHeaderLabels(["Worker Name", "IP Address", "OS", "Status", "Last Check-in"])
        layout.addWidget(self.main_ui.worker_table)

        # ✅ Refresh Button
        self.main_ui.refresh_workers_button = QPushButton("Refresh Workers")
        self.main_ui.refresh_workers_button.clicked.connect(self.load_workers)
        layout.addWidget(self.main_ui.refresh_workers_button)

        container = QWidget()
        container.setLayout(layout)
        self.worker_tab = container
        


        # ✅ Load workers automatically when UI starts
        self.load_workers()
        self.worker_tab.setVisible(True)  # Force visibility
        self.worker_tab.show()
        print(f"Worker UI Object: {self.worker_tab}")



    def load_workers(self):
        """Loads worker details from the database into the worker table."""
        logging.info("Loading workers from the database...")
        workers = get_registered_workers()
        logging.info(f"Retrieved {len(workers)} workers from WorkerInfo.") #Log how many workers retrieved 

        self.main_ui.worker_table.setRowCount(0)  # Clear existing rows

        for row_idx, (worker_name, ip_address, os, status, last_checkin) in enumerate(workers):
            self.main_ui.worker_table.insertRow(row_idx)
            self.main_ui.worker_table.setItem(row_idx, 0, QTableWidgetItem(worker_name))
            self.main_ui.worker_table.setItem(row_idx, 1, QTableWidgetItem(ip_address))
            self.main_ui.worker_table.setItem(row_idx, 2, QTableWidgetItem(os))
            self.main_ui.worker_table.setItem(row_idx, 3, QTableWidgetItem(status))
            self.main_ui.worker_table.setItem(row_idx, 4, QTableWidgetItem(last_checkin))

        logging.info("Worker table updated successfully.")