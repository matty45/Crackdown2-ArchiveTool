"""misc util functions"""
import pathlib

def get_file_name(path: str):
    """Extracts the name of a file from a full file path"""
    path = pathlib.Path(path)
    return path.stem