import sqlite3
import datetime
import logging

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

if __name__ == "__main__":
    copy_file_records_to_conversion_queue()
    process_video_files()
