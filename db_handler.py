import sqlite3
import logging

DB_PATH = "plex_video_converter.db"

def get_conversion_jobs():
    """Fetch job records from ConversionQueue, ensuring FIFO order and displaying NULL values correctly."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT file_name, file_size, job_status, queue_position 
        FROM ConversionQueue 
        ORDER BY queue_position IS NULL, queue_position ASC, file_size DESC 
    """)  
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def get_queue():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()  # Initialize cursor

    cursor.execute("""
        SELECT file_name, file_size, job_status, queue_position 
        FROM ConversionQueue 
        WHERE queue_position IS NOT NULL
        ORDER BY queue_position ASC;
    """)
    
    queued = cursor.fetchall()
    conn.close()
    return queued


def update_job_status_to_queued(file_names):
    """Update selected job status to 'queued' in the database and assign queue positions."""
    if not file_names:
        return  # No files selected

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get the current highest queue position
    cursor.execute("SELECT COALESCE(MAX(queue_position), 0) FROM ConversionQueue;")
    highest_position = cursor.fetchone()[0]
    
    # Assign new queue positions sequentially
    job_updates = []
    for file_name in file_names:
        highest_position += 1
        job_updates.append((highest_position, file_name))

    # Update job status and queue position in batch
    cursor.executemany("""
        UPDATE ConversionQueue 
        SET job_status = 'queued', queue_position = ? 
        WHERE file_name = ?;
    """, job_updates)

    conn.commit()
    conn.close()

def get_total_space_saved():
    """Returns the total space saved from completed conversion jobs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(space_saved), 0) 
        FROM ConversionQueue 
        WHERE job_status = 'completed';
    """)
    total_saved = cursor.fetchone()[0]
    conn.close()
    return total_saved

def get_estimated_total_savings():
    """Returns the estimated total space savings from pending jobs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(space_saved), 0) 
        FROM ConversionQueue 
        WHERE job_status = 'pending';
    """)
    estimated_savings = cursor.fetchone()[0]
    conn.close()
    return estimated_savings

def get_highest_queue_position():
    """Fetches the current highest queue position from ConversionQueue."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(queue_position), 0) FROM ConversionQueue;")
    highest_position = cursor.fetchone()[0]
    conn.close()
    return highest_position

def update_jobs_queue_position_and_status(job_updates):
    """Updates the queue position and job status for multiple jobs based on file names in ConversionQueue."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany("UPDATE ConversionQueue SET queue_position = ?, job_status = ? WHERE file_name = ?;", job_updates)
    conn.commit()
    conn.close()

def move_jobs_to_front(file_names):
    """Moves selected jobs to the front of the queue and sets status to 'queued'."""
    if not file_names:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get the lowest queue position
    cursor.execute("SELECT COALESCE(MIN(queue_position), 1) FROM ConversionQueue WHERE queue_position IS NOT NULL;")
    min_position = cursor.fetchone()[0]

    # Shift all existing queued jobs down
    num_jobs = len(file_names)
    cursor.execute(f"UPDATE ConversionQueue SET queue_position = queue_position + {num_jobs} WHERE queue_position IS NOT NULL;")

    # Assign new queue positions and update job status
    new_positions = []
    for i, file_name in enumerate(file_names):
        new_positions.append((min_position + i, "queued", file_name))

    cursor.executemany("UPDATE ConversionQueue SET queue_position = ?, job_status = ? WHERE file_name = ?;", new_positions)
    conn.commit()
    conn.close()

def remove_jobs_from_queue(file_names):
    """Removes selected jobs from the queue by setting queue_position to NULL and job_status to 'pending',
    then reorders the remaining queued jobs to remove gaps."""
    
    if not file_names:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Step 1: Remove selected jobs by setting queue_position to NULL and job_status to 'pending'
    query = f"""
        UPDATE ConversionQueue 
        SET queue_position = NULL, job_status = 'pending' 
        WHERE file_name IN ({','.join(['?'] * len(file_names))});
    """
    cursor.execute(query, file_names)

    # Step 2: Retrieve all queued jobs sorted by queue_position
    cursor.execute("SELECT id FROM ConversionQueue WHERE queue_position IS NOT NULL ORDER BY queue_position ASC;")
    queued_jobs = cursor.fetchall()

    # Step 3: If there are remaining jobs, renumber queue positions from 1 to N
    if queued_jobs:
        new_positions = [(index + 1, job_id[0]) for index, job_id in enumerate(queued_jobs)]

        # Step 4: Execute batch update to renumber the queue
        cursor.executemany("UPDATE ConversionQueue SET queue_position = ? WHERE id = ?;", new_positions)

    conn.commit()
    conn.close()

def get_registered_workers():
    """Fetches all registered workers from WorkerInfo table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hostname, ip_address, os, 'Connected' AS status, last_checkin 
        FROM WorkerInfo
        ORDER BY last_checkin DESC;
    """)  # Make sure 'status' is manually added as 'Connected'
    workers = cursor.fetchall()
    conn.close()
    return workers

def update_conversion_queue():
    """Clears the queue and updates it with new/modified records from FileRecords."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear the existing conversion queue
    cursor.execute("DELETE FROM ConversionQueue;")
    logging.info("Cleared ConversionQueue.")

    # Insert updated records from FileRecords
    cursor.execute("""
        INSERT INTO ConversionQueue (
            file_name, file_path, file_size, last_modified, scan_date, 
            storage_location, video_codec, resolution, duration, 
            bit_rate, audio_codec, audio_channels, sample_rate, 
            language, container_format, original_size, estimated_size, 
            space_saved, creation_date, modification_date
        )
        SELECT 
            file_name, file_path, file_size, file_modified AS last_modified, 
            last_scanned AS scan_date, 
            COALESCE(top_folder, 'Unknown') AS storage_location,  
            video_codec, resolution, duration, video_bitrate AS bit_rate, 
            audio_codec, audio_channels, audio_sample_rate AS sample_rate, 
            audio_languages AS language, file_format AS container_format, 
            file_size AS original_size, NULL AS estimated_size, NULL AS space_saved, 
            CURRENT_TIMESTAMP AS creation_date, NULL AS modification_date
        FROM FileRecords
        WHERE video_codec NOT IN ('hevc', 'av1', 'vp9')
        AND video_codec IS NOT NULL;
    """)

    rows_inserted = cursor.rowcount
    conn.commit()
    conn.close()

    logging.info(f"Inserted {rows_inserted} updated records into ConversionQueue.")
    return rows_inserted