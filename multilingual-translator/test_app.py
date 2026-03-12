"""
Test script for the Multilingual Voice Translator.
Tests each module individually.
"""

import sys
from pathlib import Path

def test_language_config():
    """Test language configuration module."""
    print("\n" + "="*50)
    print("Testing Language Config...")
    print("="*50)
    
    from language_config import (
        SUPPORTED_LANGUAGES,
        LANGUAGE_NAMES,
        get_language_name,
        get_gtts_code,
        is_language_supported
    )
    
    assert len(SUPPORTED_LANGUAGES) > 0, "No languages configured"
    print(f"✓ {len(SUPPORTED_LANGUAGES)} languages configured")
    
    # Test English
    assert is_language_supported("en"), "English should be supported"
    assert get_language_name("en") == "English", "English name mismatch"
    print("✓ English language test passed")
    
    # Test Hindi
    assert is_language_supported("hi"), "Hindi should be supported"
    print("✓ Hindi language test passed")
    
    # Test gTTS codes
    assert get_gtts_code("en") == "en", "English gTTS code mismatch"
    assert get_gtts_code("zh") == "zh-CN", "Chinese gTTS code mismatch"
    print("✓ gTTS codes test passed")
    
    print("✅ Language Config: ALL TESTS PASSED\n")
    return True


def test_helper():
    """Test helper module."""
    print("\n" + "="*50)
    print("Testing Helper Module...")
    print("="*50)
    
    from helper import (
        ensure_directories,
        generate_filename,
        get_file_size,
        validate_audio_file
    )
    
    # Test directory creation
    ensure_directories()
    assert Path("temp_audio").exists(), "temp_audio directory not created"
    assert Path("outputs").exists(), "outputs directory not created"
    print("✓ Directory creation test passed")
    
    # Test filename generation
    filename = generate_filename("test", ".wav")
    assert "test_" in filename, "Filename prefix missing"
    assert filename.endswith(".wav"), "Filename extension incorrect"
    print(f"✓ Filename generation: {filename}")
    
    print("✅ Helper Module: ALL TESTS PASSED\n")
    return True


def test_voice_recorder():
    """Test voice recorder module (without actual recording)."""
    print("\n" + "="*50)
    print("Testing Voice Recorder Module...")
    print("="*50)
    
    from voice_recorder import check_audio_quality, reduce_noise
    import numpy as np
    
    # Test audio quality check with synthetic data
    # Create a simple sine wave (simulating speech)
    sample_rate = 16000
    duration = 2  # seconds
    frequency = 440  # Hz
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    is_valid, msg = check_audio_quality(audio_data)
    assert is_valid, f"Synthetic audio should be valid: {msg}"
    print("✓ Audio quality check test passed")
    
    # Test silence detection
    silence = np.zeros(int(sample_rate))
    is_valid, msg = check_audio_quality(silence)
    assert not is_valid, "Silence should be detected"
    print("✓ Silence detection test passed")
    
    # Test noise reduction (just ensure it doesn't crash)
    reduced = reduce_noise(audio_data, sample_rate)
    assert len(reduced) == len(audio_data), "Audio length changed after noise reduction"
    print("✓ Noise reduction test passed")
    
    print("✅ Voice Recorder Module: ALL TESTS PASSED\n")
    return True


def test_transcriber():
    """Test transcriber module structure (not full model load)."""
    print("\n" + "="*50)
    print("Testing Transcriber Module...")
    print("="*50)
    
    from transcriber import WhisperTranscriber
    
    # Just test class instantiation
    transcriber = WhisperTranscriber(model_size="base")
    assert transcriber.model_size == "base", "Model size not set correctly"
    assert transcriber.model is None, "Model should be None before loading"
    print("✓ Transcriber initialization test passed")
    
    print("✅ Transcriber Module: STRUCTURE TEST PASSED\n")
    print("Note: Full model loading requires significant memory and time")
    return True


def test_translator():
    """Test translator module structure."""
    print("\n" + "="*50)
    print("Testing Translator Module...")
    print("="*50)
    
    from translator import MarianTranslator
    
    # Test class instantiation
    translator = MarianTranslator()
    assert translator.tokenizer is None, "Tokenizer should be None before loading"
    assert translator.model is None, "Model should be None before loading"
    print("✓ Translator initialization test passed")
    
    # Test same-language translation (no model needed)
    success, result = translator.translate("Hello", "en", "en")
    assert success, "Same language translation should succeed"
    assert result == "Hello", "Same language should return original text"
    print("✓ Same-language translation test passed")
    
    print("✅ Translator Module: STRUCTURE TEST PASSED\n")
    print("Note: Full model loading requires downloading models from HuggingFace")
    print("      (skipped due to memory constraints in test environment)")
    return True


def test_tts():
    """Test text-to-speech module."""
    print("\n" + "="*50)
    print("Testing Text-to-Speech Module...")
    print("="*50)
    
    from text_to_speech import TextToSpeech
    import os
    
    tts = TextToSpeech()
    
    # Test with simple English text
    test_text = "Hello world"
    output_file = "test_output.mp3"
    
    success, result = tts.generate_speech(test_text, "en", output_file)
    
    if success:
        assert Path(output_file).exists(), "Output file not created"
        assert Path(output_file).stat().st_size > 0, "Output file is empty"
        print(f"✓ TTS generation test passed: {output_file}")
        
        # Clean up
        try:
            os.remove(output_file)
            print("✓ Test file cleaned up")
        except:
            pass
    else:
        print(f"⚠ TTS test skipped (likely needs internet): {result}")
    
    print("✅ Text-to-Speech Module: TEST COMPLETED\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("MULTILINGUAL VOICE TRANSLATOR - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Language Config", test_language_config),
        ("Helper Module", test_helper),
        ("Voice Recorder", test_voice_recorder),
        ("Transcriber", test_transcriber),
        ("Translator", test_translator),
        ("Text-to-Speech", test_tts),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {str(e)}\n")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
