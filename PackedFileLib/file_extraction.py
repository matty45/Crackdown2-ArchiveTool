"""file extraction logic"""

from pathlib import Path
from util import get_file_name
from parser.toc_file import ProcessedFileEntry, WwiseEntry

def extract_file(pack_file_path: str, processed_file_entry: ProcessedFileEntry):
    """Extracts a file from the .pack."""
    # read file bytes
    with open(pack_file_path, "rb") as f:
        f.seek(processed_file_entry['File']['DataOffset'])
        file_data = f.read(processed_file_entry['File']['DataLength'])

    # build output path under a pack-specific folder
    pack_name = get_file_name(pack_file_path)
    out_path = Path(pack_name) / Path(processed_file_entry['Path'])

    # ensure parent directories exist (so the file name itself is not made a directory)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # write the bytes to the intended file path
    out_path.write_bytes(file_data)

def extract_wwise_file(pack_file_path: str, wwise_file_entry: WwiseEntry):
    """Extracts a wwise file from the .pack."""
    # read file bytes
    with open(pack_file_path, "rb") as f:
        f.seek(wwise_file_entry['DataOffset'])
        file_data = f.read(wwise_file_entry['DataLength'])

    # build output path under a pack-specific folder
    pack_name = get_file_name(pack_file_path)
    out_path = Path(pack_name) / Path("sounds") / Path(str(wwise_file_entry['FileHash']) + ".bnk")

    # ensure parent directories exist (so the file name itself is not made a directory)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # write the bytes to the intended file path
    out_path.write_bytes(file_data)

    