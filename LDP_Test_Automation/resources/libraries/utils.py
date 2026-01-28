"""
Utility functions for Robot Framework tests
"""
from pathlib import Path
from datetime import datetime
import os


def get_timestamp_folder():
    """Generate timestamp folder name: YYYYMMDD-HHMMSS"""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def create_result_folder(base_dir="results"):
    """Create result folder with timestamp"""
    timestamp = get_timestamp_folder()
    folder_path = Path(base_dir) / timestamp
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (folder_path / "logs").mkdir(exist_ok=True)
    (folder_path / "reports").mkdir(exist_ok=True)
    (folder_path / "screenshots").mkdir(exist_ok=True)
    
    return str(folder_path)


def format_file_url(file_path):
    """Convert file path to file:// URL format"""
    abs_path = Path(file_path).resolve()
    return abs_path.as_uri()


def mask_sensitive_data(text, mask_char="*", visible_chars=3):
    """Mask sensitive data (e.g., phone numbers, ID cards)"""
    if not text or len(text) <= visible_chars * 2:
        return text
    
    visible_start = text[:visible_chars]
    visible_end = text[-visible_chars:]
    masked = mask_char * (len(text) - visible_chars * 2)
    return f"{visible_start}{masked}{visible_end}"






