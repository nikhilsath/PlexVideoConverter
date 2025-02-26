import sqlite3
import datetime
from database_processing import DB_PATH 

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
def get_worker_status(workerID):
    """
    Retrieves the current status for the given workerID from WorkerInfo.
    Returns the status string if found, or None on error.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM WorkerInfo WHERE workerID = ?", (workerID,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    except Exception as e:
        print("Error in get_worker_status:", e)
        return None

def set_worker_connected_status(workerID):
    """
    Updates the WorkerInfo table for the given workerID, setting its status to "Connected"
    and updating the last_checkin timestamp.
    
    Returns True if successful, False otherwise.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE WorkerInfo
            SET status = ?, last_checkin = ?
            WHERE workerID = ?
        """, ("Connected", current_timestamp, workerID))
        conn.commit()
        conn.close()
        print(f"Worker {workerID} status updated to Connected.")
        return True
    except Exception as e:
        print("Error in set_worker_connected_status:", e)
        return False