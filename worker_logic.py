import sqlite3
import datetime

# Make sure DB_PATH is defined here or imported from your configuration
from database_processing import DB_PATH  # Or define DB_PATH = "plex_video_converter.db" if not imported

def set_worker_processing_status(workerID):
    """
    Connects to the database and updates the WorkerInfo table for the worker with the given workerID,
    setting the status to "Processing" and updating last_checkin timestamp.
    
    Returns:
        True if the update was successful, False otherwise.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE WorkerInfo
            SET status = ?, last_checkin = ?
            WHERE workerID = ?
        """, ("Processing", current_timestamp, workerID))
        conn.commit()
        conn.close()
        print(f"Worker {workerID} status updated to Processing.")
        return True
    except Exception as e:
        print(f"Error updating worker status: {e}")
        return False
