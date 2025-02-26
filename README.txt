Plex Video Converter – Detailed Documentation
Overview

Plex Video Converter is a distributed video conversion system designed to optimize large video libraries by converting video files to H.265 (HEVC) while reducing file sizes and preserving quality. The project distributes video conversion work across multiple machines (workers) and offers rich UI controls for managing job queues, worker registration, and processing logs.
Project Goals

    Reduce Storage Usage: Convert videos to a more efficient codec (H.265) to save disk space.
    Distributed Processing: Use multiple worker machines to share and balance the conversion load.
    Intuitive User Interfaces: Provide separate interfaces for job management and worker management.
    Robust Error Handling: Track conversion failures, log errors, and allow for job retries.
    Real-Time Monitoring: Display live job progress, worker status, and system logs.

System Architecture

    UI Component:
        ui.py – The main conversion UI (job list, overall workflow).
        uiworker.py – The worker-specific UI (job queue display, worker control).
    Database Component:
    An SQLite database (plex_video_converter.db) that stores:
        WorkerInfo: Worker details and registration data.
        ConversionQueue: Conversion job records (file metadata, job status, queue order).
        Logs: System log entries capturing events and errors.
    Worker Component:
    Each worker machine registers itself and polls the database for jobs. The worker’s unique identifier (workerID) is embedded in the job status (e.g., processing-<workerID>) to track assignment.
    Storage Component:
    Manages file locations, conversion outputs, and file metadata.

Database Schema and Instructions
Schema Overview

The SQLite database comprises at least three key tables:

    WorkerInfo
    Tracks worker machine details.
        Columns:
            id (INTEGER, primary key)
            hostname (TEXT)
            ip_address (TEXT)
            os (TEXT)
            cpu_info (TEXT)
            ram_info (TEXT)
            last_checkin (TIMESTAMP)
            status (TEXT; e.g., "Connected", "processing-<workerID>")
            workerID (TEXT, UNIQUE)

    ConversionQueue
    Holds conversion job records.
        Columns:
            id (INTEGER, primary key)
            file_name (TEXT)
            file_path (TEXT)
            file_size (INTEGER, in bytes)
            job_status (TEXT; e.g., "Pending", "processing-<workerID>", "Completed")
            queue_position (INTEGER; if not NULL, indicates that the job is queued)
            estimated_size (INTEGER)
            space_saved (INTEGER)
            Plus additional columns for file metadata.

    Logs
    Records processing events and error messages.
        Columns:
            id (INTEGER, primary key)
            timestamp (TIMESTAMP)
            worker_id (TEXT)
            job_id (INTEGER)
            message (TEXT)

SQL Commands to Verify the Schema

After setting up the database, run these commands in your SQLite shell to confirm the schema details:

PRAGMA table_info(WorkerInfo);
PRAGMA table_info(ConversionQueue);
PRAGMA table_info(Logs);

If needed, ensure that a unique index exists on workerID:

CREATE UNIQUE INDEX IF NOT EXISTS idx_workerID ON WorkerInfo(workerID);

Detailed File Descriptions

The following sections provide a detailed breakdown of every file in the Archive.zip, including function descriptions, when each function is run, variable details, and any ordering or placement requirements.
1. ui.py

Purpose:

    This file launches the main conversion UI and handles overall job management.

Functions and Key Code:

    UI Initialization (in __init__ or main routine):
        When it runs: Immediately on executing python3 ui.py.
        Function: Initializes the main window, creates widgets (job list, worker management panels), registers callbacks (button clicks, search events).
        Variables:
            Global variables like DB_PATH are defined at the top.
            Instance variables for UI components (e.g., job list table, search bar, refresh buttons) are created in the constructor.
        Ordering:
            All UI widgets must be set up before callbacks are connected.

    Worker Registration Call:
        Calls register_local_worker() (from database_processing.py) during initialization.
        Requirement: This call must occur after the database is set up.

    Event Handlers:
        Functions that react to user actions (e.g., filtering the job list, refreshing data) are connected after the UI is built.

2. uiworker.py

Purpose:

    Provides a dedicated interface for worker tasks, including displaying the queued conversion jobs.

Widgets and Functions:

    Widgets:
        job_queue_table (QTableWidget): Displays queued jobs in a table-like format with columns for File Name, Size (GB), Status, and Order.
        worker_status_label and worker_info_label: Display current worker state.
        refresh_button: Refreshes the queue display.
    Functions:
        __init__(self):
            When it runs: On instantiation during startup.
            Purpose: Constructs the UI by creating the left panel (job queue, log tabs) and right panel (worker controls).
            Variables:
                Local variables like main_layout, left_panel, right_panel.
                Instance variables for UI widgets (e.g., self.job_queue_table, self.refresh_button).
            Ordering: Must be called before any events occur.
            Startup Call: Calls self.update_queue_table() at the end of initialization to load queue data.
        update_queue_table(self):
            When it runs: On UI load and when the refresh button is clicked.
            Purpose: Retrieves queued jobs via get_queue() from db_handler.py and populates job_queue_table accordingly.
            Local Variables:
                jobs: List of queued jobs.
                size_gb: Calculated file size in GB.
            Ordering: This function requires that the table widget is already created.

3. ui_job_list.py

Purpose:

    Handles the display and filtering of conversion jobs in the main UI.

Functions:

    setup_job_list(self):
        When it runs: During the initialization of the job list UI.
        Purpose: Sets up the job list table, search bar, and button row.
        Local Variables:
            Layout objects (e.g., layout, button_layout) and widgets (search bar, table).
    display_jobs(self, jobs):
        When it runs: After fetching jobs from the database or after filtering.
        Purpose: Populates the job list table with the job records.
        Variables:
            Uses parameter jobs to display file name, file size (converted to GB), job status, and queue order.
    filter_jobs(self):
        When it runs: Triggered by changes in the search bar.
        Purpose: Filters the jobs in memory using the search text and updates the table by calling display_jobs.
        Local Variables:
            search_text: The lowercased text from the search bar.

4. ui_worker_management.py

Purpose:

    Manages worker registration and status updates.

Functions:

    Worker Management UI Setup:
        When it runs: At startup or when the Worker Management tab is activated.
        Purpose: Displays current workers, allows enabling/disabling workers, and updates worker statuses.
        Variables:
            Local layout variables and worker detail widgets.
    Event Handlers:
        Handle actions like refreshing worker info, reordering jobs, etc.

5. db_handler.py

Purpose:

    Provides functions to interact with the SQLite database.

Key Functions:

    get_queue():
        When it runs: Called from UI update functions in ui.py and uiworker.py to load queued jobs.
        Purpose: Retrieves job records from ConversionQueue where queue_position is not NULL, ordered by queue_position ASC.
        Local Variables:
            Uses a cursor to run the SQL query; stores the result in queued.
    Other Functions:
        Additional functions for updating job order, moving jobs, and error handling are also defined here. Each function’s purpose is described in its comments.

6. database_processing.py

Purpose:

    Contains functions that process the database, update job records, and manage worker registration.

Key Functions:

    copy_file_records_to_conversion_queue():
        When it runs: Typically as a background task or on startup.
        Purpose: Copies records from FileRecords to ConversionQueue, skipping duplicates.
        Local Variables:
            current_timestamp for record insertion, local cursor variables.
    calculate_estimated_size(file_size, video_codec):
        When it runs: Called from process_video_files().
        Purpose: Calculates the estimated size after conversion using a global COMPRESSION_TABLE.
    process_video_files():
        When it runs: After copying records to the ConversionQueue.
        Purpose: Updates each job record with an estimated size and calculated space saved.
        Local Variables:
            Uses a local list updates to store SQL update tuples.
    register_local_worker():
        When it runs: Called during startup from ui.py.
        Purpose: Registers the local machine in WorkerInfo.
        Local Variables:
            Uses get_local_machine_info() to get system details.
            Generates a unique workerID using uuid.uuid4().
            Calls clear_workers() before proceeding (see below).
    clear_workers():
        When it runs: At the beginning of register_local_worker().
        Purpose: Checks for active workers (with "processing" in their status) and clears the WorkerInfo table if none are active.
        Local Variables:
            Uses processing_count to determine if clearing is allowed.
        Return Value:
            Returns True if the table was cleared; False otherwise.
        Ordering:
            Must run before register_local_worker() completes.

7. requirements.txt

Purpose:

    Lists all required Python libraries and their versions needed to run the project.
    Key Libraries:
        PyQt6, psutil, cryptography, among others.
    Usage:
        Run pip install -r requirements.txt to install dependencies.

8. Archive.zip

    Purpose:
        Contains the complete source code of the project, including all files described above.

Startup Process

There are two primary startup files in this project:
1. ui.py

    How to Run:
    Execute with python3 ui.py.
    Purpose:
    Launches the main conversion user interface.
    Startup Steps:
        Initializes global variables (e.g., DB_PATH, configuration constants).
        Sets up the main UI window, including job list, search/filter functionality, and worker management.
        Calls register_local_worker() (from database_processing.py) to register the local machine.
        Loads queued conversion jobs and other data into the UI.
    Dependencies:
    The database must be initialized and the schema set up (see Database Schema section).

2. uiworker.py

    How to Run:
    Execute with python3 uiworker.py.
    Purpose:
    Provides a dedicated interface for worker-specific tasks.
    Startup Steps:
        Sets up the WorkerUI window.
        Creates a QTableWidget (job_queue_table) to display queued jobs.
        Connects control buttons (start, stop, refresh) with corresponding event handlers.
        Immediately calls update_queue_table() during initialization to load the current job queue.
    Dependencies:
    Requires get_queue() from db_handler.py to function correctly.

Final Notes and Extensibility

    Function Placement and Ordering:
        Ensure global variables and constants are declared at the top of each file.
        UI initialization functions (e.g., __init__) must set up widgets before event handlers are connected.
        Database functions assume that the database schema is already in place.

    Extending the System:
        As new features or files are added, update this README to include detailed function descriptions and variable usage.
        Any changes to the database schema should be reflected in the SQL commands provided above.

    Usage by AI Assistants:
        This document is intended to serve as a complete guide for AI assistants and human contributors alike, ensuring that the project remains aligned and easy to work with.