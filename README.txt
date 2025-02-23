# Plex Video Converter - Project Documentation

## Overview
Plex Video Converter is a distributed video conversion system designed to optimize large video libraries by converting them to H.265 (HEVC) while maintaining quality and reducing file size. This system employs multiple networked machines (workers) to perform video encoding tasks efficiently.

---

## **Product Design Document (PDD)**

### **Project Goals**
1. **Reduce storage usage** by converting video files to H.265.
2. **Leverage multiple machines** to distribute the encoding workload.
3. **Provide UI controls** for managing job queues and workers.
4. **Ensure lossless audio** while maintaining high video quality.
5. **Automate job processing** using priority-based queues.

### **System Architecture**
- **UI Component**: PyQt6-based interface for managing jobs and workers.
- **Database Component**: SQLite stores job queue, worker status, and conversion metadata.
- **Worker Component**: Each worker runs an agent that retrieves and processes jobs.
- **Storage Component**: Shared storage for distributing and storing converted files.

### **Key Features**
- **Worker Registration & Management**: Workers register on startup and periodically check for jobs.
- **Conversion Queue**: Jobs are added based on file eligibility and queued for processing.
- **Job Prioritization**: Supports FIFO, manual priority overrides, and job reordering.
- **Auto-Error Handling**: Failed jobs return to the queue with logged errors.
- **Live Status Tracking**: UI displays real-time job progress and worker activity.
- **Storage Monitoring**: Prevents processing if space is insufficient.

### **Workflow**
1. **Workers Register**: Machines detect available storage and register themselves.
2. **Jobs Are Added**: The system selects videos that need conversion.
3. **Workers Poll for Jobs**: Machines fetch the next available job based on priority.
4. **Processing Begins**: The selected video is converted using `ffmpeg`.
5. **Validation & Cleanup**: Completed jobs are verified and replace original files.
6. **Logs & Status Updates**: Job statuses are logged and displayed in the UI.

---

## **Technical Design Document (TDD)**

### **Database Schema**

#### **WorkerInfo Table** (Tracks all workers)
| Column          | Type    | Description |
|---------------|--------|-------------|
| id            | INTEGER | Primary Key |
| hostname      | TEXT   | Machine name |
| ip_address    | TEXT   | Worker IP Address |
| os            | TEXT   | OS Type |
| cpu_info      | TEXT   | Processor Details |
| ram_info      | TEXT   | RAM Capacity |
| last_checkin  | TIMESTAMP | Last communication |
| status        | TEXT   | 'Connected' or 'Disabled' |

#### **ConversionQueue Table** (Tracks jobs for conversion)
| Column          | Type    | Description |
|---------------|--------|-------------|
| id            | INTEGER | Primary Key |
| file_name     | TEXT   | Video Filename |
| file_path     | TEXT   | Location of video file |
| file_size     | INTEGER | Size of the file (Bytes) |
| job_status    | TEXT   | Pending, Processing, Completed, Failed |
| queue_position | INTEGER | Job Order |
| estimated_size | INTEGER | Expected final size |
| space_saved   | INTEGER | Calculated space saved |
| assigned_worker | TEXT | Worker assigned to the job |

#### **Logs Table** (Tracks processing events)
| Column          | Type    | Description |
|---------------|--------|-------------|
| id            | INTEGER | Primary Key |
| timestamp     | TIMESTAMP | Time of log entry |
| worker_id     | TEXT   | Worker that generated the log |
| job_id        | INTEGER | Associated job (if applicable) |
| message       | TEXT   | Log content |

### **Worker Processing Flow**
1. **Worker Registers** (Inserts or updates `WorkerInfo` table).
2. **Fetches Next Job** (SELECT next job from `ConversionQueue`).
3. **Checks Storage Availability** (Ensures there is enough free space before processing).
4. **Runs FFmpeg Conversion**:
    ```sh
    ffmpeg -i "input.mp4" -c:v libx265 -preset slow -crf 18 -c:a copy -map 0 "output.mp4"
    ```
5. **Validation & Replacement**:
   - New file is verified.
   - Original file is deleted.
   - Processed file replaces it.
6. **Logs Completion & Updates Queue**.

---

## **README**

### **Installation & Setup**
1. Clone the repository:
   ```sh
   git clone https://github.com/yourrepo/plex-video-converter.git
   cd plex-video-converter
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the UI:
   ```sh
   python3 ui.py
   ```

### **Usage Guide**
- **Job Management**: Add/remove jobs, reorder priority, track progress.
- **Worker Management**: View available workers, enable/disable workers.
- **Error Handling**: Logs errors and allows re-processing failed jobs.

### **Known Issues**
- Ensure workers have sufficient RAM for encoding.
- Files requiring extreme compression may take longer.

### **Contributing**
- Fork the repo, make changes, and submit a pull request.

### **License**
- MIT License

---

This documentation provides a detailed overview of the Plex Video Converter system, ensuring clarity in implementation and further development.

