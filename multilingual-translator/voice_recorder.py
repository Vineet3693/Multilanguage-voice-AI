"""
Voice Recorder Module
Records audio from microphone or loads from file.
"""

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")


def record_audio(duration: int = 5, sample_rate: int = 16000) -> np.ndarray:
    """
    Record audio from microphone for specified duration.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Audio sample rate (Whisper expects 16000 Hz)
    
    Returns:
        numpy array containing audio data
    """
    print(f"Recording for {duration} seconds...")
    
    # Record audio
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,  # Mono
        dtype=np.float32
    )
    
    # Wait for recording to complete
    sd.wait()
    
    print("Recording complete!")
    return recording.flatten()


def save_audio(audio_data: np.ndarray, filepath: str, sample_rate: int = 16000) -> str:
    """
    Save audio data to WAV file.
    
    Args:
        audio_data: Numpy array with audio samples
        filepath: Output file path
        sample_rate: Sample rate for the audio
    
    Returns:
        Path to saved file
    """
    # Normalize audio to 16-bit integer range
    audio_normalized = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    
    # Write to file
    write(filepath, sample_rate, audio_normalized)
    
    return filepath


def load_audio_file(filepath: str, target_sample_rate: int = 16000) -> np.ndarray:
    """
    Load audio from file and resample if necessary.
    
    Args:
        filepath: Path to audio file
        target_sample_rate: Target sample rate (16000 for Whisper)
    
    Returns:
        Numpy array with audio data
    """
    from scipy.io import wavfile
    from scipy import signal
    
    # Read audio file
    sample_rate, audio_data = wavfile.read(filepath)
    
    # Convert to float32
    if audio_data.dtype == np.int16:
        audio_data = audio_data.astype(np.float32) / 32767.0
    elif audio_data.dtype == np.int32:
        audio_data = audio_data.astype(np.float32) / 2147483647.0
    
    # Resample if necessary
    if sample_rate != target_sample_rate:
        num_samples = int(len(audio_data) * target_sample_rate / sample_rate)
        audio_data = signal.resample(audio_data, num_samples)
    
    # Ensure mono channel
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)
    
    return audio_data


def check_audio_quality(audio_data: np.ndarray, threshold: float = 0.01) -> tuple:
    """
    Check if audio contains speech or is just silence/noise.
    
    Args:
        audio_data: Numpy array with audio samples
        threshold: Amplitude threshold for silence detection
    
    Returns:
        Tuple of (is_valid, message)
    """
    # Calculate RMS amplitude
    rms = np.sqrt(np.mean(audio_data ** 2))
    
    # Check for silence
    if rms < threshold:
        return False, "No speech detected. Please speak louder or closer to the microphone."
    
    # Check minimum duration (at least 1 second of actual audio)
    min_samples = 16000  # 1 second at 16000 Hz
    if len(audio_data) < min_samples:
        return False, "Audio too short. Please speak for at least 1 second."
    
    return True, "Audio quality OK"


def reduce_noise(audio_data: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """
    Reduce background noise from audio.
    
    Args:
        audio_data: Numpy array with audio samples
        sample_rate: Audio sample rate
    
    Returns:
        Noise-reduced audio data
    """
    try:
        import noisereduce as nr
        
        # Apply noise reduction
        reduced_audio = nr.reduce_noise(
            y=audio_data,
            sr=sample_rate,
            prop_decrease=0.75,  # How much noise to reduce
            stationary=True  # Assume stationary noise
        )
        
        return reduced_audio
    except ImportError:
        # Return original if noisereduce not available
        return audio_data
    except Exception as e:
        print(f"Noise reduction failed: {e}")
        return audio_data


# Convenience function for complete recording workflow
def record_and_save(duration: int = 5, output_path: str = "input.wav") -> tuple:
    """
    Complete workflow: record audio, check quality, and save.
    
    Args:
        duration: Recording duration in seconds
        output_path: Output file path
    
    Returns:
        Tuple of (success, audio_data, message)
    """
    try:
        # Record audio
        audio_data = record_audio(duration=duration)
        
        # Optional: Reduce noise
        audio_data = reduce_noise(audio_data)
        
        # Check quality
        is_valid, message = check_audio_quality(audio_data)
        
        if not is_valid:
            return False, None, message
        
        # Save audio
        save_audio(audio_data, output_path)
        
        return True, audio_data, "Recording saved successfully"
    
    except Exception as e:
        return False, None, f"Recording failed: {str(e)}"
