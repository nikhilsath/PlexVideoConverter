import sqlite3

DB_PATH = "plex_video_converter.db"

def get_conversion_jobs():
    """Fetch job records from ConversionQueue, ensuring FIFO order and displaying NULL values correctly."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT file_name, file_size, job_status, queue_position 
        FROM ConversionQueue 
        ORDER BY queue_position IS NULL, queue_position ASC;
    """)  
    jobs = cursor.fetchall()
    conn.close()
    return jobs

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
