import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QTabWidget
)
from PyQt6.QtCharts import QChart, QChartView, QPieSeries
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor
from ui_job_list import JobListUI
from db_handler import get_total_space_saved, get_estimated_total_savings

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Run database processing before launching UI
        self.run_database_processing()
        
        self.setWindowTitle("Plex Video Converter")
        self.setMinimumSize(1300, 600)  # Set the minimum window size
        self.initUI()

    def run_database_processing(self):
        """Runs the database processing script before launching the UI."""
        try:
            subprocess.run(["python3", "database_processing.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running database processing: {e}")

    def initUI(self):
        """Initialize the UI layout and structure"""
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left Panel (Dashboard - Pie Chart & Stats)
        left_panel = QVBoxLayout()
        self.pie_chart = self.create_pie_chart()
        left_panel.addWidget(self.pie_chart)

        # Fetch space savings values on program startup (Convert Bytes → GB)
        total_saved = get_total_space_saved() / (1024 ** 3)  # Convert bytes to GB
        estimated_savings = get_estimated_total_savings() / (1024 ** 3)  # Convert bytes to GB

        self.stats_label = QLabel(f"Space Saved So Far: {total_saved:.2f} GB\nEstimated Total Savings: {estimated_savings:.2f} GB")
        left_panel.addWidget(self.stats_label)


        # Center Panel (Job List & Logs Tab)
        center_panel = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.job_list_ui = JobListUI(self)
        self.job_list_tab = self.job_list_ui.job_list_tab  # Calls job list logic from ui_job_list.py
        self.logs_tab = self.create_logs_panel()
        self.tab_widget.addTab(self.job_list_tab, "Job List")
        self.tab_widget.addTab(self.logs_tab, "Logs / Errors")
        center_panel.addWidget(self.tab_widget)
        
        # Add "Move to Front of Queue" Button Below the Job List
        self.move_to_front_button = QPushButton("Move to Front of Queue")
        center_panel.addWidget(self.move_to_front_button)
        
        # Right Panel (Worker Management)
        right_panel = QVBoxLayout()
        self.worker_table = self.create_worker_table()
        right_panel.addWidget(self.worker_table)
        self.worker_check_button = QPushButton("Check Worker Status")
        right_panel.addWidget(self.worker_check_button)
        
        # Bottom Controls (Manual Job Management)
        controls_panel = QHBoxLayout()
        self.stop_selected_button = QPushButton("Stop Selected Scan")
        self.stop_all_button = QPushButton("Stop All Scans")
        controls_panel.addWidget(self.stop_selected_button)
        controls_panel.addWidget(self.stop_all_button)
        
        # Add Panels to Main Layout
        main_layout.addLayout(left_panel, 2)  # Assign space ratio for dashboard
        main_layout.addLayout(center_panel, 3)  # Assign space ratio for job list/logs
        main_layout.addLayout(right_panel, 3)  # Assign space ratio for worker management
        
        # Wrap everything in a vertical layout
        container = QVBoxLayout()
        container.addLayout(main_layout)
        container.addLayout(controls_panel)
        main_widget.setLayout(container)
        self.setCentralWidget(main_widget)

    def create_pie_chart(self):
        """Creates and returns a pie chart widget with job distribution."""
        series = QPieSeries()
        series.append("Converted", 50)
        series.append("Processing", 30)
        series.append("Pending", 15)
        series.append("Failed", 5)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Job Status Distribution")
        chart.legend().setVisible(False)  # Hide the default chart legend

        chartview = QChartView(chart)
        chartview.setMinimumSize(QSize(300, 300))

        # Create a custom vertical legend using QLabel
        legend_layout = QVBoxLayout()
        legend_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        legend_labels = [
            ("Converted", QColor("cyan")),
            ("Processing", QColor("blue")),
            ("Pending", QColor("darkBlue")),
            ("Failed", QColor("black")),
        ]

        for text, color in legend_labels:
            label = QLabel(f"● {text}")
            label.setStyleSheet(f"color: {color.name()}; font-size: 12px;")
            legend_layout.addWidget(label)

        # Create a container widget for the custom legend
        legend_container = QWidget()
        legend_container.setLayout(legend_layout)
        legend_container.setStyleSheet("background-color: white; padding: 5px; border-radius: 5px;")

        # Wrap the chart and legend together
        container_layout = QVBoxLayout()
        container_layout.addWidget(legend_container)  # Legend at the top
        container_layout.addWidget(chartview)  # Pie chart below

        chart_widget = QWidget()
        chart_widget.setLayout(container_layout)

        return chart_widget
    
    def create_logs_panel(self):
        """Creates a placeholder logs panel to display conversion logs/errors."""
        logs_panel = QLabel("Logs will appear here.")
        logs_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        return logs_panel

    def create_worker_table(self):
        """Creates a table for managing workers."""
        worker_table = QTableWidget()
        worker_table.setColumnCount(4)
        worker_table.setHorizontalHeaderLabels(["Worker Name", "Status", "Processing", "Enable/Disable"])
        return worker_table
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainUI()
    main_window.show()
    sys.exit(app.exec())
