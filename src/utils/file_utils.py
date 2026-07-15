from pathlib import Path

from fastapi import UploadFile


class FileTooLargeError(Exception):
    pass


def save_upload_file(upload: UploadFile, dest_dir: Path, max_size_mb: int) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / upload.filename

    max_bytes = max_size_mb * 1024 * 1024
    contents = upload.file.read(max_bytes + 1)
    if len(contents) > max_bytes:
        raise FileTooLargeError(f"{upload.filename} exceeds {max_size_mb}MB limit")

    dest_path.write_bytes(contents)
    return dest_path
