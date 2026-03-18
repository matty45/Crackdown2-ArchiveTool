"""Toc file parsing stuff"""

from io import BufferedReader
import struct
from typing import TypedDict, Union


class TOCHeader(TypedDict):
    """Type definition for TOC header structure."""
    Signature: int
    Version: int
    Flags: int
    FileEntryCount: int
    PaddingBetweenFiles: int
    WwiseEntryCount: int
    Reserved1: int
    Reserved2: int


class FileEntry(TypedDict):
    """Type definition for TOC file entry structure."""
    PathStringOffset: int
    DataOffset: int
    DataLength: int
    PathHash: int

class ProcessedFileEntry(TypedDict):
    """Type definition for TOC file entry structure."""
    File: FileEntry
    Path: str

class WwiseEntry(TypedDict):
    """Type definition for Wwise entry structure."""
    FileHash: int
    DataOffset: int
    DataLength: int


class TOCData(TypedDict):
    """Type definition for complete TOC data structure."""
    header: TOCHeader
    file_entries: list[FileEntry]
    wwise_entries: list[WwiseEntry]
    path_string_data: bytes


def read_toc_file(file_path: str) -> TOCData:
    """Reads and parses a toc file."""

    with open(file_path, "rb") as f:
        header = read_toc_header(f)
        if header["Version"] != 2:
            raise ValueError(
                f"Invalid toc file version: expected version 2, got {header['Version']}"
            )

        file_entries = read_toc_entries(f, header)
        wwise_entries = read_wwise_entries(f, header)
        path_string_data = read_path_string_data(f, header)

        f.close()

    return {
        "header": header,
        "file_entries": file_entries,
        "wwise_entries": wwise_entries,
        "path_string_data": path_string_data
    }


def read_toc_header(reader: BufferedReader) -> TOCHeader:
    """Reads and returns the toc files header."""
    # Read exactly 32 bytes (0x20) for the header
    header_data = reader.read(32)
    if len(header_data) != 32:
        raise ValueError("File too small for header")

    # Unpack using the format string
    header = struct.unpack(">IIIIIIII", header_data)

    if header[0] != 1346454347:
        raise ValueError(
            f"Invalid signature: expected 0x{1346454347:08x} 'PACK', got 0x{header[0]:08x}"
        )

    return {
        "Signature": header[0],
        "Version": header[1],
        "Flags": header[2],
        "FileEntryCount": header[3],
        "PaddingBetweenFiles": header[4],
        "WwiseEntryCount": header[5],
        "Reserved1": header[6],
        "Reserved2": header[7],
    }


def read_toc_entries(
    reader: BufferedReader, header: TOCHeader
) -> list[FileEntry]:
    """Reads and returns the file entries from the TOC."""
    file_entry_count = header["FileEntryCount"]

    if file_entry_count == 0:
        return []

    # Each entry is 16 bytes, seek to offset 32 (after header)
    reader.seek(32)

    # Read all entries at once
    entries_data = reader.read(16 * file_entry_count)
    if len(entries_data) != 16 * file_entry_count:
        raise ValueError("File too small for entries")

    # Unpack each 16-byte entry using the correct struct format
    entries = []
    for i in range(file_entry_count):
        offset = i * 16
        entry_data = entries_data[offset : offset + 16]
        # PACKEDFILETOCENTRY has 4 unsigned integers
        path_offset, data_offset, data_length, path_hash = struct.unpack(
            ">IIII", entry_data
        )
        entries.append(
            {
                "PathStringOffset": path_offset,
                "DataOffset": data_offset,
                "DataLength": data_length,
                "PathHash": path_hash,
            }
        )

    return entries


def read_wwise_entries(
    reader: BufferedReader, header: TOCHeader
) -> list[WwiseEntry]:
    """Reads and returns the Wwise entries from the TOC."""
    wwise_entry_count = header["WwiseEntryCount"]
    file_entry_count = header["FileEntryCount"]

    if wwise_entry_count == 0:
        return []

    # Calculate offset to Wwise entries: 16 * (FileEntryCount + 2)
    wwise_offset = 16 * (file_entry_count + 2)
    reader.seek(wwise_offset)

    # Read all Wwise entries at once
    wwise_data = reader.read(12 * wwise_entry_count)
    if len(wwise_data) != 12 * wwise_entry_count:
        raise ValueError("File too small for Wwise entries")

    # Unpack each 12-byte entry
    wwise_entries = []
    for i in range(wwise_entry_count):
        offset = i * 12
        entry_data = wwise_data[offset : offset + 12]
        # PACKEDFILEWWISEENTRY has 3 unsigned integers
        file_hash, data_offset, data_length = struct.unpack(">III", entry_data)
        wwise_entries.append(
            {
                "FileHash": file_hash,
                "DataOffset": data_offset,
                "DataLength": data_length,
            }
        )

    return wwise_entries


def read_path_string_data(reader: BufferedReader, header: TOCHeader) -> bytes:
    """Reads the path string data section from the TOC."""
    file_entry_count = header["FileEntryCount"]
    wwise_entry_count = header["WwiseEntryCount"]

    # Calculate offset to path string data
    wwise_offset = 16 * (file_entry_count + 2)
    path_string_offset = 12 * wwise_entry_count + wwise_offset

    reader.seek(path_string_offset)
    return reader.read()

def extract_file_paths_from_data(path_string_data: bytes, file_entries: list[FileEntry]) -> list[ProcessedFileEntry]:
    """Extract file paths and return a list of them along with their corrosponding file entry."""
    processed_files = []

    for entry in file_entries:
        offset = entry["PathStringOffset"] * 2 # Thank you darkrk for letting me know i gotta multiply this by two.
        # Find the null terminator (double null bytes in UTF-16BE)
        null_terminator = path_string_data.find(b'\x00\x00', offset)
        if null_terminator == -1:
            # If no terminator found, take to end
            path_bytes = path_string_data[offset:]
        else:
            # Extract only up to the null terminator
            path_bytes = path_string_data[offset:null_terminator]

        # Decode using UTF-16BE for big endian byte order
        path = path_bytes.decode('utf-16be')

        processed_files.append(
            {
                "File": entry,
                "Path": path,
            }
        )

    return processed_files