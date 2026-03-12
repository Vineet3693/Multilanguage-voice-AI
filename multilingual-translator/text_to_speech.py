"""
Text-to-Speech Module
Uses Google TTS (gTTS) to convert text to speech.
"""

from gtts import gTTS
from pathlib import Path
from typing import Tuple, Optional
import warnings

warnings.filterwarnings("ignore")


class TextToSpeech:
    """
    Wrapper class for Google Text-to-Speech.
    Handles text-to-audio conversion.
    """
    
    def __init__(self):
        """Initialize TTS engine."""
        self.last_lang = None
    
    def generate_speech(self, text: str, language: str, output_path: str = "output.mp3", slow: bool = False) -> Tuple[bool, str]:
        """
        Convert text to speech and save as MP3 file.
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'en', 'hi', 'es')
            output_path: Output file path
            slow: Whether to speak slowly
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate text
            if not text or not text.strip():
                return False, "No text provided for TTS"
            
            # Create gTTS object
            print(f"Generating speech in {language}...")
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to file
            tts.save(output_path)
            
            print(f"Speech saved to {output_path}")
            return True, output_path
        
        except Exception as e:
            error_msg = str(e)
            
            # Handle common gTTS errors
            if "Could not translate" in error_msg:
                return False, f"gTTS error: Language '{language}' may not be supported"
            elif "Connection" in error_msg or "HTTP" in error_msg:
                return False, "gTTS requires internet connection. Please check your connection."
            else:
                return False, f"TTS failed: {error_msg}"
    
    def generate_speech_bytes(self, text: str, language: str, slow: bool = False) -> Tuple[bool, bytes]:
        """
        Convert text to speech and return as bytes (for streaming).
        
        Args:
            text: Text to convert to speech
            language: Language code
            slow: Whether to speak slowly
        
        Returns:
            Tuple of (success, audio_bytes)
        """
        try:
            if not text or not text.strip():
                return False, b""
            
            print(f"Generating speech bytes in {language}...")
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to bytes buffer
            from io import BytesIO
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return True, audio_buffer.read()
        
        except Exception as e:
            return False, b""


# Offline fallback using pyttsx3
class OfflineTTS:
    """Fallback TTS that works offline (robotic voice)."""
    
    def __init__(self):
        self.engine = None
    
    def generate_speech(self, text: str, language: str, output_path: str = "output_offline.mp3") -> Tuple[bool, str]:
        """Generate speech using offline TTS."""
        try:
            import pyttsx3
            
            if self.engine is None:
                self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Note: pyttsx3 doesn't support all languages well
            # It uses system voices which vary by OS
            
            # Save to file (pyttsx3 doesn't directly save to MP3)
            self.engine.save_to_file(text, output_path.replace('.mp3', '.wav'))
            self.engine.runAndWait()
            
            # Try to convert WAV to MP3 if needed
            if output_path.endswith('.mp3'):
                wav_path = output_path.replace('.mp3', '.wav')
                if Path(wav_path).exists():
                    try:
                        from pydub import AudioSegment
                        sound = AudioSegment.from_wav(wav_path)
                        sound.export(output_path, format="mp3")
                        Path(wav_path).unlink()  # Remove WAV file
                    except:
                        # Keep WAV if conversion fails
                        Path(wav_path).rename(output_path)
            
            return True, output_path
        
        except ImportError:
            return False, "pyttsx3 not installed for offline TTS"
        except Exception as e:
            return False, f"Offline TTS failed: {str(e)}"


def text_to_speech(text: str, language: str, output_path: str = "output.mp3", use_fallback: bool = True) -> Tuple[bool, str]:
    """
    Convenience function for quick text-to-speech conversion.
    
    Args:
        text: Text to convert
        language: Language code
        output_path: Output file path
        use_fallback: Whether to try offline fallback if gTTS fails
    
    Returns:
        Tuple of (success, message)
    """
    # Primary: gTTS
    tts = TextToSpeech()
    success, result = tts.generate_speech(text, language, output_path)
    
    # Fallback to offline if needed
    if not success and use_fallback:
        print("Falling back to offline TTS...")
        offline_tts = OfflineTTS()
        return offline_tts.generate_speech(text, language, output_path)
    
    return success, result


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 3:
        text = sys.argv[1]
        lang = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else "output.mp3"
        
        success, result = text_to_speech(text, lang, output)
        
        if success:
            print(f"\n{'='*50}")
            print(f"Text: {text}")
            print(f"Language: {lang}")
            print(f"Audio saved to: {result}")
            print(f"{'='*50}")
        else:
            print(f"Error: {result}")
    else:
        print("Usage: python text_to_speech.py <text> <language_code> [output_file]")
        print("Example: python text_to_speech.py 'Hello world' en hello.mp3")
