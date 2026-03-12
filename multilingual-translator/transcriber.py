"""
Transcriber Module
Uses OpenAI Whisper to convert speech to text.
"""

import whisper
from pathlib import Path
from typing import Optional, Tuple
import warnings

warnings.filterwarnings("ignore")


class WhisperTranscriber:
    """
    Wrapper class for OpenAI Whisper model.
    Handles model loading and transcription.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size: Size of Whisper model (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        
    def load_model(self) -> bool:
        """
        Load the Whisper model.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Loading Whisper model: {self.model_size}...")
            self.model = whisper.load_model(self.model_size)
            print("Whisper model loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load Whisper model: {e}")
            return False
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Tuple[bool, str, str]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (if None, auto-detects)
        
        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        # Load model if not already loaded
        if self.model is None:
            if not self.load_model():
                return False, "", "Failed to load Whisper model"
        
        try:
            # Prepare options
            options = {}
            if language:
                options["language"] = language
            
            # Transcribe
            print(f"Transcribing audio with Whisper ({self.model_size})...")
            result = self.model.transcribe(audio_path, **options)
            
            # Extract text and detected language
            text = result["text"].strip()
            detected_lang = result.get("language", "unknown")
            
            if not text:
                return False, "", "No speech detected in audio"
            
            print(f"Transcription complete! Detected language: {detected_lang}")
            return True, text, detected_lang
        
        except Exception as e:
            return False, "", f"Transcription failed: {str(e)}"
    
    def transcribe_audio_data(self, audio_data, sample_rate: int = 16000) -> Tuple[bool, str, str]:
        """
        Transcribe audio data directly (numpy array).
        
        Args:
            audio_data: Numpy array with audio samples
            sample_rate: Sample rate of audio
        
        Returns:
            Tuple of (success, transcribed_text, detected_language)
        """
        import tempfile
        from voice_recorder import save_audio
        
        # Save audio data to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            save_audio(audio_data, tmp_path, sample_rate)
        
        try:
            # Transcribe the temporary file
            success, text, lang = self.transcribe(tmp_path)
            return success, text, lang
        finally:
            # Clean up temporary file
            try:
                Path(tmp_path).unlink()
            except:
                pass


def transcribe_audio(audio_path: str, model_size: str = "base", language: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Convenience function for quick transcription.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size
        language: Optional language code for transcription
    
    Returns:
        Tuple of (success, transcribed_text, detected_language)
    """
    transcriber = WhisperTranscriber(model_size=model_size)
    return transcriber.transcribe(audio_path, language)


# Example usage
if __name__ == "__main__":
    # Test transcription
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        success, text, lang = transcribe_audio(audio_file)
        
        if success:
            print(f"\n{'='*50}")
            print(f"Transcribed Text: {text}")
            print(f"Detected Language: {lang}")
            print(f"{'='*50}")
        else:
            print(f"Error: {text}")
    else:
        print("Usage: python transcriber.py <audio_file.wav>")
