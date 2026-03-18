"""pack toc file loading test"""

from parser.toc_file import read_toc_file, extract_file_paths_from_data

def load_toc_test(file_path : str) -> bool:
    """This loads a toc file and prints out some of its info."""
    file = read_toc_file(file_path  + ".toc")
    if file:
        # Extract file paths from the raw path string data and map them to the file entries that they belong to.
        processed_file_entries = extract_file_paths_from_data(file['path_string_data'], file['file_entries'])

        for entry in processed_file_entries:
            print(entry)

        return True
    else:
        print(f"\nCould not open {file_path}")
        return False