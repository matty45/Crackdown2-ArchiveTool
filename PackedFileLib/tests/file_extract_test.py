"""pack toc file extraction test"""

from file_extraction import extract_file
from parser.toc_file import read_toc_file, extract_file_paths_from_data

def file_extract_test(file_path : str) -> bool:
    """This will attempt to load a toc file then attempt to extract files from its corrosponding pack archive."""
    file = read_toc_file(file_path + ".toc")
    if file:
        # Extract file paths from the raw path string data and map them to the file entries that they belong to.
        processed_file_entries = extract_file_paths_from_data(file['path_string_data'], file['file_entries'])

        for entry in processed_file_entries:
            extract_file(file_path,entry)

        return True
    else:
        print(f"\nCould not open {file_path}")
        return False