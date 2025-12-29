import os
import hashlib
import argparse
from datetime import datetime
import sys

def get_file_hash(filepath):
    """Calculate the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as file:
        buf = file.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(65536)
    return hasher.hexdigest()

def find_and_delete_duplicates(directory, log_file):
    """Find and delete duplicate files in the given directory and its subdirectories."""
    file_hashes = {}
    duplicates_found = 0
    duplicates_deleted = 0
    total_files_checked = 0

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            total_files_checked += 1
            
            try:
                file_hash = get_file_hash(filepath)
            except IOError as e:
                log_file.write(f"Error reading file {filepath}: {str(e)}\n")
                continue

            if file_hash in file_hashes:
                duplicates_found += 1
                original_path = file_hashes[file_hash]
                log_file.write(f"Duplicate found:\n  Original: {original_path}\n  Duplicate: {filepath}\n")
                
                try:
                    os.remove(filepath)
                    log_file.write(f"Deleted: {filepath}\n")
                    duplicates_deleted += 1
                except OSError as e:
                    log_file.write(f"Error deleting file {filepath}: {str(e)}\n")
            else:
                file_hashes[file_hash] = filepath

    return total_files_checked, duplicates_found, duplicates_deleted

def main():
    parser = argparse.ArgumentParser(description="Find and delete duplicate files in a directory.")
    parser.add_argument("directory", help="The directory to search for duplicates")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_filename = f"delete_duplicates_{timestamp}.log"

    with open(log_filename, 'w') as log_file:
        print(f"Searching for duplicates in {args.directory}")
        print(f"Logging details to {log_filename}")
        
        total_files, duplicates_found, duplicates_deleted = find_and_delete_duplicates(args.directory, log_file)

        summary = f"""
Summary:
Total files checked: {total_files}
Duplicates found: {duplicates_found}
Duplicates successfully deleted: {duplicates_deleted}
        """
        log_file.write(summary)
        print(summary)
        print(f"Detailed log saved to {log_filename}")

if __name__ == "__main__":
    main()

