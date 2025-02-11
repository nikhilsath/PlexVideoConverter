from PyQt6.QtWidgets import QTableWidgetItem, QVBoxLayout, QTableWidget, QPushButton, QWidget
from db_handler import get_conversion_jobs, update_job_status_to_queued
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class JobListUI:
    def __init__(self, main_ui):
        """Initialize Job List UI component."""
        self.main_ui = main_ui
        self.job_list_tab = None 
        self.setup_job_list()

    def setup_job_list(self):
        """Creates and manages the Job List UI component."""
        layout = QVBoxLayout()

        self.main_ui.job_list = QTableWidget()
        self.main_ui.job_list.setColumnCount(3)
        self.main_ui.job_list.setHorizontalHeaderLabels(["File Name", "Size (GB)", "Status"])

        # Load Job List Button
        self.main_ui.refresh_jobs_button = QPushButton("Load Job List")
        self.main_ui.refresh_jobs_button.clicked.connect(self.load_jobs)

        # Add to Queue Button
        self.main_ui.add_to_queue_button = QPushButton("Add Selected to Queue")
        self.main_ui.add_to_queue_button.clicked.connect(self.add_selected_to_queue)

        layout.addWidget(self.main_ui.job_list)
        layout.addWidget(self.main_ui.refresh_jobs_button)
        layout.addWidget(self.main_ui.add_to_queue_button)

        container = QWidget()
        container.setLayout(layout)
        self.job_list_tab = container

    def load_jobs(self):
        """Load job records from ConversionQueue into the Job List table."""
        logging.info("Loading jobs from the database...")
        jobs = get_conversion_jobs()
        logging.info(f"Retrieved {len(jobs)} jobs from ConversionQueue.")

        # Clear existing rows
        self.main_ui.job_list.setRowCount(0)

        # Populate table with database data
        for row_idx, (file_name, file_size, job_status) in enumerate(jobs):
            self.main_ui.job_list.insertRow(row_idx)
            self.main_ui.job_list.setItem(row_idx, 0, QTableWidgetItem(file_name))
            self.main_ui.job_list.setItem(row_idx, 1, QTableWidgetItem(f"{file_size / (1024**3):.2f} GB"))  # Convert bytes to GB
            self.main_ui.job_list.setItem(row_idx, 2, QTableWidgetItem(job_status))

    def add_selected_to_queue(self):
        """Update the selected jobs in the list to 'queued' and refresh the UI."""
        selected_rows = self.main_ui.job_list.selectedItems()

        if not selected_rows:
            logging.info("No rows selected.")
            return

        # Extract file names from selected rows
        file_names = set()
        for item in selected_rows:
            row = item.row()
            file_name = self.main_ui.job_list.item(row, 0).text()  # File name is in the first column
            file_names.add(file_name)

        logging.info(f"Queuing {len(file_names)} jobs: {file_names}")

        # Update the database
        update_job_status_to_queued(list(file_names))

        # Refresh the job list
        self.load_jobs()
