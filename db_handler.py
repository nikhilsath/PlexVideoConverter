import sqlite3

DB_PATH = "plex_video_converter.db"

def get_conversion_jobs():
    """Fetch job records from ConversionQueue."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_name, file_size, job_status FROM ConversionQueue ORDER BY id DESC;")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def update_job_status_to_queued(file_names):
    """Update selected job status to 'queued' in the database."""
    if not file_names:
        return  # No files selected

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Use placeholders for SQL security
    query = f"""
        UPDATE ConversionQueue 
        SET job_status = 'queued' 
        WHERE file_name IN ({','.join(['?'] * len(file_names))});
    """
    
    cursor.execute(query, file_names)
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