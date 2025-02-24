from PyQt6.QtWidgets import QTableWidgetItem, QHBoxLayout, QTableWidget, QPushButton, QWidget, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt
from db_handler import get_conversion_jobs, update_jobs_queue_position_and_status, get_highest_queue_position, move_jobs_to_front, remove_jobs_from_queue
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class JobListUI:
    def __init__(self, main_ui):
        """Initialize Job List UI component."""
        self.main_ui = main_ui
        self.job_list_tab = None
        self.setup_job_list()

    def setup_job_list(self):
        """Creates and manages the Job List UI component with a search bar and button row."""
        
        # ✅ Define layout at the beginning
        layout = QVBoxLayout()

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search jobs...")
        self.search_bar.textChanged.connect(self.filter_jobs)  # Connect search event

        # Job List Table
        self.main_ui.job_list = QTableWidget()
        self.main_ui.job_list.setColumnCount(4)
        self.main_ui.job_list.setHorizontalHeaderLabels(["File Name", "Size (GB)", "Status", "Order"])

        # ✅ Define a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Reload Button
        self.main_ui.refresh_jobs_button = QPushButton("Reload")
        self.main_ui.refresh_jobs_button.clicked.connect(self.load_jobs)
        button_layout.addWidget(self.main_ui.refresh_jobs_button)

        # Add to Queue Button
        self.main_ui.add_to_queue_button = QPushButton("Add")
        self.main_ui.add_to_queue_button.clicked.connect(self.add_selected_to_queue)
        button_layout.addWidget(self.main_ui.add_to_queue_button)

        # Remove from Queue Button
        self.main_ui.remove_from_queue_button = QPushButton("Remove")
        self.main_ui.remove_from_queue_button.clicked.connect(self.remove_selected_from_queue)
        button_layout.addWidget(self.main_ui.remove_from_queue_button)

        # Move to Front of Queue Button
        self.main_ui.move_to_front_button = QPushButton("Priority Add")
        self.main_ui.move_to_front_button.clicked.connect(self.move_selected_to_front)
        button_layout.addWidget(self.main_ui.move_to_front_button)

        # ✅ Add the search bar, job list, and button row to the main layout
        layout.addWidget(self.search_bar)
        layout.addWidget(self.main_ui.job_list)
        layout.addLayout(button_layout)  # ✅ Add the button row

        container = QWidget()
        container.setLayout(layout)
        self.job_list_tab = container


    def display_jobs(self, jobs):
        self.main_ui.job_list.setRowCount(0)  # Reset the table
        for row_idx, (file_name, file_size, job_status, queue_position) in enumerate(jobs):
            self.main_ui.job_list.insertRow(row_idx)
            self.main_ui.job_list.setItem(row_idx, 0, QTableWidgetItem(file_name))
            self.main_ui.job_list.setItem(row_idx, 1, QTableWidgetItem(f"{file_size / (1024**3):.2f} GB"))  # Convert bytes to GB
            self.main_ui.job_list.setItem(row_idx, 2, QTableWidgetItem(job_status))

            queue_pos_text = str(queue_position) if queue_position is not None else "—"
            self.main_ui.job_list.setItem(row_idx, 3, QTableWidgetItem(queue_pos_text))


    def load_jobs(self):
        """Fetch jobs from the database and update the UI."""
        logging.info("Loading jobs from the database...")
        
        self.jobs = get_conversion_jobs()  # Assign the jobs to self.jobs
        logging.info(f"Retrieved {len(self.jobs)} jobs from ConversionQueue.")

        self.display_jobs(self.jobs)  # Now pass self.jobs to update the UI

        
    def filter_jobs(self):
        """Filters the displayed jobs based on search input."""
        search_text = self.search_bar.text().strip().lower()
        if not search_text:
            self.display_jobs(self.jobs)  # Reset to full job list if search is cleared
            return

        # Filter jobs in memory
        filtered_jobs = [
            job for job in self.jobs if search_text in job[0].lower() or search_text in job[2].lower()
        ]
        logging.info(f"Displaying {len(filtered_jobs)} filtered jobs for search: {search_text}")

        self.display_jobs(filtered_jobs)

    def add_selected_to_queue(self):
        """Batch update selected jobs to be added to the queue in sequential order and set status to 'queued'."""
        selected_rows = self.main_ui.job_list.selectedItems()
        if not selected_rows:
            logging.info("No jobs selected.")
            return
        # Extract unique file names from selected rows
        file_names = set()
        for item in selected_rows:
            row = item.row()
            file_name = self.main_ui.job_list.item(row, 0).text()  # File name is in the first column
            file_names.add(file_name)
        logging.info(f"Queuing {len(file_names)} jobs: {file_names}")
        # Get the next available queue position
        current_max_position = get_highest_queue_position()
        next_position = current_max_position + 1
        # Prepare batch update data for queue position and status
        job_updates = []
        for file_name in file_names:
            job_updates.append((next_position, "queued", file_name))
            next_position += 1  # Increment for each job
        # Batch update queue position and job status
        update_jobs_queue_position_and_status(job_updates)
        # Log updates
        logging.info(f"Added {len(job_updates)} jobs to the queue with 'queued' status. New max queue position: {next_position - 1}")
        # Refresh the job list
        self.load_jobs()

    def move_selected_to_front(self):
        """Moves selected jobs to the front of the queue while maintaining order."""
        selected_rows = self.main_ui.job_list.selectedItems()
        if not selected_rows:
            logging.info("No jobs selected.")
            return

        file_names = set()
        for item in selected_rows:
            row = item.row()
            file_name = self.main_ui.job_list.item(row, 0).text()  # File name is in column 0
            file_names.add(file_name)

        logging.info(f"Moving {len(file_names)} jobs to the front of the queue: {file_names}")

        # Call DB function to update queue position
        move_jobs_to_front(list(file_names))

        # Reload the job list
        self.load_jobs()

    def remove_selected_from_queue(self):
        """Removes selected jobs from the queue by calling remove_jobs_from_queue in db_handler."""
        selected_rows = self.main_ui.job_list.selectedItems()
        if not selected_rows:
            logging.info("No jobs selected.")
            return

        file_names = set()
        for item in selected_rows:
            row = item.row()
            file_name = self.main_ui.job_list.item(row, 0).text()  # File name is in column 0
            file_names.add(file_name)

        logging.info(f"Removing {len(file_names)} jobs from the queue: {file_names}")

        # Call DB function to update queue position and status
        remove_jobs_from_queue(list(file_names))

        # Reload the job list
        self.load_jobs()


