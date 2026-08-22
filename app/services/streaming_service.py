import os
from pathlib import Path
from typing import Generator, Tuple
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

def get_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
    """Parse HTTP Range header: e.g. 'bytes=0-1024' or 'bytes=1024-'"""
    try:
        units, range_val = range_header.strip().split("=")
        if units != "bytes":
            raise ValueError("Invalid range units")
        
        parts = range_val.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        
        if start >= file_size or end >= file_size or start > end:
            raise ValueError("Range out of bounds")
        
        return start, end
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Requested range not satisfiable for file size {file_size}"
        )

def file_iterator(file_path: Path, start: int, end: int, chunk_size: int = 1024 * 128) -> Generator[bytes, None, None]:
    """Yield file chunks between start and end byte offsets."""
    with open(file_path, "rb") as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            bytes_to_read = min(chunk_size, remaining)
            chunk = f.read(bytes_to_read)
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk

def create_streaming_response(file_path: Path, range_header: str = None, media_type: str = "audio/mpeg") -> StreamingResponse:
    """Builds a partial content streaming response or full stream response."""
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found on disk."
        )
    
    file_size = os.path.getsize(file_path)
    
    if range_header:
        start, end = get_range_header(range_header, file_size)
        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": media_type,
        }
        return StreamingResponse(
            file_iterator(file_path, start, end),
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            headers=headers
        )
    else:
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": media_type,
        }
        return StreamingResponse(
            file_iterator(file_path, 0, file_size - 1),
            status_code=status.HTTP_200_OK,
            headers=headers
        )
