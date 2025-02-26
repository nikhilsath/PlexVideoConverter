import sqlite3
import datetime
import logging
import socket
import platform
import psutil
import uuid

# Logging configuration
LOG_FILE = "database_processing.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Compression efficiency table (values are reduction percentages relative to H.265)
COMPRESSION_TABLE = {
    "h264": 0.45, 
    "mpeg4": 0.55, 
    "msmpeg4v3": 0.60, 
    "msmpeg4v2": 0.60,
    "vp6f": 0.50, 
    "vc1": 0.45, 
    "mpeg2video": 0.65, 
    "realvideo": 0.60,
    "dv": 0.60, 
    "prores": 0.80, 
    "theora": 0.55, 
    "cinepak": 0.65
}

EXCLUDED_IPS = {
    "0.0.0.0",          # Default route
    "255.255.255.255",  # Broadcast address
    "224.0.0.251",      # mDNS multicast
    "239.255.255.250"   # SSDP multicast
}

SKIP_CODECS = {"H.265", "HEVC", "AV1", "VP9"}  # Video codecs to be skipped

DB_PATH = "plex_video_converter.db"

def copy_file_records_to_conversion_queue():
    """Copy data from FileRecords to ConversionQueue, skipping files already in ConversionQueue."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Ensure only required rows are copied
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
        AND video_codec IS NOT NULL
        AND file_path NOT IN (SELECT file_path FROM ConversionQueue);
     """)
    
    rows_inserted = cursor.rowcount
    conn.commit()
    conn.close()
    logging.info(f"Inserted {rows_inserted} new records into ConversionQueue.")


def calculate_estimated_size(file_size, video_codec):
    """Calculate estimated size based on compression table."""
    reduction_factor = COMPRESSION_TABLE.get(video_codec, 0.0)  # Default to no reduction if unknown
    return int(file_size * (1 - reduction_factor))

def process_video_files():
    """Update estimated_size and space_saved for all video files that require conversion."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch required columns for processing, skipping already converted formats
    cursor.execute("""
        SELECT id, file_size, video_codec 
        FROM ConversionQueue 
        WHERE estimated_size IS NULL
        AND video_codec IS NOT NULL 
        AND video_codec != ''
        AND video_codec NOT IN ('hevc', 'av1', 'vp9');
    """)
    records = cursor.fetchall()

    updates = []
    for record in records:
        file_id, original_size, video_codec = record
        estimated_size = calculate_estimated_size(original_size, video_codec)
        space_saved = original_size - estimated_size
        updates.append((estimated_size, space_saved, file_id))

    # Bulk update in a single query
    cursor.executemany("UPDATE ConversionQueue SET estimated_size=?, space_saved=? WHERE id=?", updates)

    conn.commit()
    conn.close()
    logging.info(f"Updated {len(updates)} records with estimated size and space saved.")

def clear_workers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Count the number of workers with "processing" in the status column
    cursor.execute("""
        SELECT COUNT(*) 
        FROM WorkerInfo 
        WHERE status LIKE '%processing%'
    """)
    processing_count = cursor.fetchone()[0]

    if processing_count == 0:
        # No workers are processing, so clear the table
        cursor.execute("DELETE FROM WorkerInfo")
        conn.commit()
        print("Worker table cleared.")
        conn.close()
    else:
        print(f"Cannot clear worker table. {processing_count} workers are still processing.")
        conn.close()

def get_local_machine_info():
    """Fetch system information for worker registration."""
    hostname = socket.gethostname()
    
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "Unknown"

    os_type = platform.system()
    cpu_info = platform.processor()
    ram_info = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"

    return hostname, ip_address, os_type, cpu_info, ram_info

def register_local_worker():
    """Registers or updates the local machine as a worker in WorkerInfo.
    
    Checks if a worker record already exists for the local machine based on hostname and ip_address.
    If it exists, updates the record and returns the existing workerID.
    Otherwise, creates a new record and returns the new workerID.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get system details
    hostname, ip_address, os_type, cpu_info, ram_info = get_local_machine_info()

    # Skip registering if the IP is in the excluded list
    if ip_address in EXCLUDED_IPS:
        print(f"Skipping registration: {hostname} ({ip_address}) is in the excluded IP list.")
        conn.close()
        return None

    # Check if a record already exists for this worker using hostname and ip_address
    cursor.execute("SELECT workerID FROM WorkerInfo WHERE hostname = ? AND ip_address = ?", (hostname, ip_address))
    result = cursor.fetchone()
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if result is not None:
        # Existing record found; update it.
        workerID = result[0]
        cursor.execute("""
            UPDATE WorkerInfo 
            SET os = ?, cpu_info = ?, ram_info = ?, last_checkin = ?, status = 'Connected'
            WHERE workerID = ?
        """, (os_type, cpu_info, ram_info, current_timestamp, workerID))
        print(f"Updated existing worker record for {hostname} ({ip_address}) with workerID {workerID}")
    else:
        # No record exists; create a new one.
        workerID = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO WorkerInfo (hostname, ip_address, os, cpu_info, ram_info, last_checkin, status, workerID)
            VALUES (?, ?, ?, ?, ?, ?, 'Connected', ?)
        """, (hostname, ip_address, os_type, cpu_info, ram_info, current_timestamp, workerID))
        print(f"Created new worker record for {hostname} ({ip_address}) with workerID {workerID}")
    
    conn.commit()
    conn.close()
    return workerID

if __name__ == "__main__":
    copy_file_records_to_conversion_queue()
    process_video_files()
    register_local_worker()

