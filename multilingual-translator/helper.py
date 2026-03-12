"""
Helper Module
Utility functions for the Multilingual Voice Translator.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def create_temp_directory() -> str:
    """Create a temporary directory for audio files."""
    temp_dir = Path("temp_audio")
    temp_dir.mkdir(exist_ok=True)
    return str(temp_dir)


def generate_filename(prefix: str = "audio", extension: str = ".wav") -> str:
    """Generate a unique filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{extension}"


def cleanup_old_files(directory: str = "temp_audio", max_age_hours: int = 1) -> int:
    """
    Clean up old temporary files.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age of files to keep
    
    Returns:
        Number of files deleted
    """
    import time
    
    dir_path = Path(directory)
    if not dir_path.exists():
        return 0
    
    current_time = time.time()
    deleted_count = 0
    max_age_seconds = max_age_hours * 3600
    
    for file_path in dir_path.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
    
    return deleted_count


def format_language_code(code: str) -> str:
    """Format language code for display."""
    return code.upper()


def get_file_size(filepath: str) -> str:
    """Get human-readable file size."""
    path = Path(filepath)
    if not path.exists():
        return "0 B"
    
    size_bytes = path.stat().st_size
    
    # Convert to human-readable format
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} TB"


def save_transcript(text: str, filepath: Optional[str] = None, include_metadata: bool = True) -> str:
    """
    Save transcript to text file.
    
    Args:
        text: Transcript text
        filepath: Output file path (auto-generated if None)
        include_metadata: Whether to include timestamp and metadata
    
    Returns:
        Path to saved file
    """
    if filepath is None:
        filepath = generate_filename("transcript", ".txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        if include_metadata:
            f.write(f"Transcript generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
        
        f.write(text)
    
    return filepath


def validate_audio_file(filepath: str) -> tuple:
    """
    Validate that an audio file exists and is readable.
    
    Args:
        filepath: Path to audio file
    
    Returns:
        Tuple of (is_valid, message)
    """
    path = Path(filepath)
    
    if not path.exists():
        return False, "File does not exist"
    
    if not path.is_file():
        return False, "Path is not a file"
    
    # Check file extension
    valid_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm']
    if path.suffix.lower() not in valid_extensions:
        return False, f"Unsupported file format: {path.suffix}"
    
    # Check file size (should be > 0 and reasonable)
    file_size = path.stat().st_size
    if file_size == 0:
        return False, "File is empty"
    
    if file_size > 100 * 1024 * 1024:  # 100 MB limit
        return False, "File too large (max 100 MB)"
    
    return True, "File is valid"


def get_audio_duration(filepath: str) -> Optional[float]:
    """
    Get duration of audio file in seconds.
    
    Args:
        filepath: Path to audio file
    
    Returns:
        Duration in seconds or None if unable to determine
    """
    try:
        from scipy.io import wavfile
        
        if filepath.endswith('.wav'):
            sample_rate, data = wavfile.read(filepath)
            duration = len(data) / sample_rate
            return duration
        else:
            # For other formats, would need additional libraries
            return None
    except:
        return None


def ensure_directories():
    """Ensure all required directories exist."""
    directories = ["temp_audio", "outputs"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)


def map_whisper_lang_to_iso(whisper_lang: str) -> str:
    """
    Map Whisper language codes to ISO codes if needed.
    
    Args:
        whisper_lang: Language code from Whisper
    
    Returns:
        ISO language code
    """
    # Whisper typically uses standard ISO codes
    # This function can handle any special mappings if needed
    mapping = {
        'zh': 'zh',  # Chinese
        'no': 'no',  # Norwegian
        'da': 'da',  # Danish
    }
    
    return mapping.get(whisper_lang, whisper_lang)


# Session state helpers for Streamlit
def init_session_state(state, key: str, default_value):
    """Initialize session state if not already set."""
    if key not in state:
        state[key] = default_value


def clear_session_state(state, *keys):
    """Clear specific session state keys."""
    for key in keys:
        if key in state:
            del state[key]
