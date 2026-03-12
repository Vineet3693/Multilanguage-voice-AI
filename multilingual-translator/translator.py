"""
Translator Module
Uses Helsinki-NLP MarianMT models for translation.
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional, Tuple
import warnings

warnings.filterwarnings("ignore")


class MarianTranslator:
    """
    Wrapper class for Helsinki-NLP MarianMT translation models.
    Handles model loading and translation between language pairs.
    """
    
    def __init__(self):
        """Initialize the translator with empty model references."""
        self.tokenizer = None
        self.model = None
        self.current_pair = None
    
    def load_model(self, source_lang: str, target_lang: str) -> bool:
        """
        Load translation model for specific language pair.
        
        Args:
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'hi')
        
        Returns:
            True if successful, False otherwise
        """
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        
        try:
            # Check if we need to reload (different language pair)
            if self.current_pair == (source_lang, target_lang):
                print(f"Using cached model for {source_lang} → {target_lang}")
                return True
            
            print(f"Loading translation model: {model_name}...")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            self.current_pair = (source_lang, target_lang)
            print(f"Translation model loaded successfully!")
            return True
        
        except Exception as e:
            print(f"Failed to load translation model: {e}")
            self.current_pair = None
            return False
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Tuple of (success, translated_text)
        """
        # Handle same language case
        if source_lang == target_lang:
            return True, text
        
        # Load appropriate model
        if not self.load_model(source_lang, target_lang):
            # Try fallback: translate via English if direct pair not available
            if source_lang != "en" and target_lang != "en":
                print(f"Trying fallback translation via English...")
                success1, intermediate = self.translate(text, source_lang, "en")
                if success1:
                    return self.translate(intermediate, "en", target_lang)
            
            return False, f"Translation model not available for {source_lang} → {target_lang}"
        
        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            
            # Generate translation
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                outputs = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode output
            translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return True, translated
        
        except Exception as e:
            return False, f"Translation failed: {str(e)}"
    
    def translate_batch(self, texts: list, source_lang: str, target_lang: str) -> Tuple[bool, list]:
        """
        Translate multiple texts at once.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Tuple of (success, list of translated_texts)
        """
        if source_lang == target_lang:
            return True, texts
        
        if not self.load_model(source_lang, target_lang):
            return False, []
        
        try:
            translations = []
            for text in texts:
                success, translated = self.translate(text, source_lang, target_lang)
                if success:
                    translations.append(translated)
                else:
                    translations.append(f"[Translation failed: {text}]")
            
            return True, translations
        
        except Exception as e:
            return False, []


# Fallback translator using deep-translator if Helsinki models fail
class FallbackTranslator:
    """Simple fallback translator using deep-translator library."""
    
    def __init__(self):
        self.translator = None
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """Translate using Google Translate via deep-translator."""
        try:
            from deep_translator import GoogleTranslator
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text)
            return True, translated
        
        except ImportError:
            return False, "deep-translator not installed"
        except Exception as e:
            return False, f"Fallback translation failed: {str(e)}"


def translate_text(text: str, source_lang: str, target_lang: str, use_fallback: bool = True) -> Tuple[bool, str]:
    """
    Convenience function for quick translation.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        use_fallback: Whether to use fallback translator if primary fails
    
    Returns:
        Tuple of (success, translated_text)
    """
    # Primary translator
    translator = MarianTranslator()
    success, result = translator.translate(text, source_lang, target_lang)
    
    # Try fallback if needed
    if not success and use_fallback:
        print("Falling back to alternative translator...")
        fallback = FallbackTranslator()
        return fallback.translate(text, source_lang, target_lang)
    
    return success, result


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 4:
        text = sys.argv[1]
        src = sys.argv[2]
        tgt = sys.argv[3]
        
        success, translated = translate_text(text, src, tgt)
        
        if success:
            print(f"\n{'='*50}")
            print(f"Original ({src}): {text}")
            print(f"Translated ({tgt}): {translated}")
            print(f"{'='*50}")
        else:
            print(f"Error: {translated}")
    else:
        print("Usage: python translator.py <text> <source_lang> <target_lang>")
        print("Example: python translator.py 'Hello' en hi")
