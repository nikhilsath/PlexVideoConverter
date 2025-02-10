#!/bin/bash

# Define the base path to test files
TEST_DIR="./test_files"

# List of video files to test
FILES=(
    "$TEST_DIR/Blade.Runner.2049.2017.2160p.4K.BluRay.x265.10bit.AAC5.1-[YTS.MX].mkv"
    "$TEST_DIR/Encanto (2021) [1080p] [WEBRip] [5.1] [YTS.MX]/Encanto.2021.1080p.WEBRip.x264.AAC5.1-[YTS.MX].mp4"
    "$TEST_DIR/Home Improvement - 4x02 - Don't Tell Momma.avi"
    "$TEST_DIR/Inception/Inception.mp4"
    "$TEST_DIR/The Social Network (2010) [1080]/The Social Network (2010) 1080p BrRip x264 - 1.2GB - YIFY.mp4"
    "$TEST_DIR/corrupt_file.mp4"  # Placeholder for failed conversion test file
)

# Loop through files and play them for 5 seconds
for FILE in "${FILES[@]}"; do
    if [[ -f "$FILE" ]]; then
        echo "Testing: $FILE"
        ffplay -t 5 -autoexit -nodisp "$FILE"
    else
        echo "File not found: $FILE"
    fi
done
