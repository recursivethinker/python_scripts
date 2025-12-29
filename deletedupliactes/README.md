# Delete Duplicate Files

A Python script to recursively find and delete duplicate files within a specified directory and its subdirectories.

## Description

This script scans a target directory, calculates the MD5 hash for each file, and identifies duplicates based on these hashes. When a duplicate is found, the script keeps the first file it encountered (the "original") and deletes the subsequent identical files.

All actions, including files identified as duplicates, deletions, and any errors, are logged to a timestamped log file for review.

## Features

*   **Recursive Search**: Scans the specified directory and all its subdirectories.
*   **Accurate Identification**: Uses MD5 hashing to accurately identify files with identical content.
*   **Detailed Logging**: Creates a comprehensive log file for every run, detailing found duplicates, deleted files, and any errors.
*   **Console Summary**: Prints a summary of the total files checked, duplicates found, and duplicates deleted to the console after completion.

## Prerequisites

*   Python 3.x

## Usage

1.  Navigate to the directory containing the script.
2.  Run the script from your terminal, providing the path to the directory you want to scan as an argument.

```bash
python delete_duplicates.py /path/to/your/directory
```

### Example

```bash
# Scan a folder named "MyPhotos" located on the Desktop
python delete_duplicates.py ~/Desktop/MyPhotos
```

## How It Works

The script maintains a dictionary mapping file hashes to their file paths. As it walks through the directory tree, it computes the hash of each file.

*   If the hash is **not** in the dictionary, it's added along with the file's path. This file is considered the "original".
*   If the hash **is** already in the dictionary, the current file is considered a duplicate and is deleted.

## Logging

A log file named `delete_duplicates_YYYY_MM_DD_HH_MM_SS.log` is created in the directory where the script is executed. This log contains:
*   A list of all duplicate files found and their corresponding original file.
*   Confirmation of each file deletion.
*   Any errors encountered while reading or deleting files.
*   A final summary of the operation.

## ⚠️ Warning

**This script permanently deletes files. Deletion is irreversible.** It is strongly recommended that you **back up your data** before running this script. Use it at your own risk.