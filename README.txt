# Plex Video Converter

## Overview
Plex Video Converter is a tool designed to manage and convert video files for use in Plex. The software scans a directory, analyzes video files, and queues them for conversion based on user-defined rules.

---

## **Modular Structure**

### **Main Components**
| File                      | Purpose |
|--------------------------|-----------------------------------------------------------|
| `ui.py`                  | Main UI file, initializes and connects UI components. |
| `ui_job_list.py`         | Manages Job List UI (table, refresh, search, queueing). |
| `ui_worker_management.py` | Handles Worker Management UI (adding/removing workers). |
| `ui_controls.py`         | Handles job control buttons (start, stop, cancel jobs). |
| `db_handler.py`          | Database queries to separate UI from DB logic. |
| `event_handlers.py`      | Contains button logic and other event-based functions. |
| `database_processing.py` | Handles database updates and conversion queue logic. |

---

## **Workflow**
### **1. Initial Scan & Database Processing**
1. **Database Processing (`database_processing.py`)**:
   - Scans the directory for video files.
   - Filters out already converted files (`H.265`, `AV1`, `VP9`).
   - Inserts valid files into `ConversionQueue`.
   - Calculates estimated space savings for each file.
   - Updates the database with relevant metadata.

2. **UI Startup (`ui.py`)**:
   - Runs `database_processing.py` before launching the interface.
   - Loads saved space metrics (`get_total_space_saved()` & `get_estimated_total_savings()`).
   - Displays an interactive dashboard with a job list and worker status.

### **2. User Interaction (UI Components)**
1. **Job List (`ui_job_list.py`)**:
   - Displays all queued video files.
   - Allows searching by file name.
   - Enables selecting files to add to the conversion queue.

2. **Job Controls (`ui_controls.py`)**:
   - Users can start, stop, or cancel queued conversions.
   - Supports moving jobs to the front of the queue.

3. **Worker Management (`ui_worker_management.py`)**:
   - Displays available worker machines.
   - Allows enabling/disabling workers for processing jobs.
   - Checks worker status dynamically.

### **3. Database Logic (`db_handler.py`)**
- `get_conversion_jobs()`: Retrieves pending and active jobs.
- `update_job_status_to_queued()`: Updates selected jobs to "queued".
- `get_total_space_saved()`: Retrieves space savings from completed jobs.
- `get_estimated_total_savings()`: Estimates total savings for pending jobs.

---

## **Function Breakdown**

### **`database_processing.py`**
- **`copy_file_records_to_conversion_queue()`**:
  - Filters video files and copies them into `ConversionQueue`.
  - Prevents duplicate entries.
  - Sets `creation_date` when a file is added.

- **`process_video_files()`**:
  - Calculates `estimated_size` using a compression table.
  - Computes `space_saved = original_size - estimated_size`.
  - Updates these values in `ConversionQueue`.

### **`db_handler.py`**
- **`get_conversion_jobs()`**
  - Fetches all jobs from `ConversionQueue`.
  - Used by `ui_job_list.py` to display jobs.

- **`update_job_status_to_queued(job_ids)`**
  - Updates selected jobs to `queued`.

- **`get_total_space_saved()`**
  - Retrieves sum of `space_saved` for completed jobs.

- **`get_estimated_total_savings()`**
  - Estimates total savings for pending jobs.

### **`ui.py`**
- **`MainUI`**
  - Initializes the interface.
  - Loads space savings data on startup.

### **`ui_job_list.py`**
- **`setup_job_list()`**
  - Creates the job list table UI.

- **`load_jobs()`**
  - Loads and updates the job list from the database.

### **`ui_controls.py`**
- **`add_selected_to_queue()`**
  - Updates selected jobs to `queued` and refreshes the job list.

### **`ui_worker_management.py`**
- **`check_worker_status()`**
  - Fetches and displays active workers.

---

## **Database Tables**

### **FileRecords**
| Column              | Type      | Description |
|--------------------|----------|-------------|
| id                | INTEGER  | Primary key |
| file_name        | TEXT     | File name |
| file_path        | TEXT     | Unique path |
| file_size        | INTEGER  | File size (bytes) |
| video_codec      | TEXT     | Codec used |
| resolution       | TEXT     | Video resolution |

### **ConversionQueue**
| Column            | Type      | Description |
|------------------|----------|-------------|
| id              | INTEGER  | Primary key |
| file_name      | TEXT     | File name |
| file_size      | INTEGER  | Original file size |
| space_saved    | INTEGER  | Space saved after conversion |
| job_status     | TEXT     | Pending, queued, processing, completed |

---

## **Recent Updates**
- **Added Space Savings Calculation**
  - `get_total_space_saved()` and `get_estimated_total_savings()` added to `db_handler.py`.
  - UI now displays values in GB.
- **Implemented Search in Job List**
  - Users can filter jobs by file name.
- **Refactored UI Code into Separate Modules**
  - Improved maintainability by separating job list, worker management, and controls.

---

## **GitHub Update**
Run the following commands to update the repository:
```bash
  git add .
  git commit -m "Updated README and space savings calculation logic"
  git push origin main
```

---

## **Next Steps**
- Implement detailed job progress tracking.
- Add worker machine controls for load balancing.
- Optimize conversion queue management.
```

