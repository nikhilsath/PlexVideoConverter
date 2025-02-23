import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database file paths
PQC_DB_PATH = os.path.join("..", "PlexQualityCrawler", "plex_quality_crawler.db")  # Ensure correct path
PVC_DB_PATH = "plex_video_converter.db"

def fetch_file_records(db_path):
    """Fetches file records from the given database and returns them as a dictionary."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, file_modified FROM FileRecords")
    records = {row[0]: row[1] for row in cursor.fetchall()}  # Store file_path as key, file_modified as value
    conn.close()
    return records

def compare_file_records():
    """Compares FileRecords between plex_quality_crawler.db and plex_video_converter.db."""
    pqc_records = fetch_file_records(PQC_DB_PATH)
    pvc_records = fetch_file_records(PVC_DB_PATH)

    # Identify new and updated files
    new_files = {k: v for k, v in pqc_records.items() if k not in pvc_records}
    updated_files = {
        k: v for k, v in pqc_records.items() if k in pvc_records and v != pvc_records[k]
    }

    total_changes = len(new_files) + len(updated_files)

    # Log total differences
    logging.info(f"Total updated/new files: {total_changes}")

    return total_changes
