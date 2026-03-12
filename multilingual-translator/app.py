"""
Multilingual Voice Translator - Main Application
Built with Streamlit
"""

import streamlit as st
from pathlib import Path
import os

# Import custom modules
from language_config import (
    get_language_options_for_dropdown,
    get_language_name,
    get_gtts_code,
    SUPPORTED_LANGUAGES
)
from voice_recorder import (
    record_audio,
    save_audio,
    load_audio_file,
    check_audio_quality,
    reduce_noise
)
from transcriber import WhisperTranscriber
from translator import MarianTranslator
from text_to_speech import TextToSpeech
from helper import (
    ensure_directories,
    generate_filename,
    save_transcript,
    validate_audio_file,
    cleanup_old_files,
    init_session_state
)

# Page configuration
st.set_page_config(
    page_title="Multilingual Voice Translator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1E88E5;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left-color: #4CAF50;
    }
    .error-box {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .record-button {
        background-color: #f44336;
        color: white;
        font-size: 1.5rem;
        padding: 1rem 3rem;
        border-radius: 50px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)


def initialize_app():
    """Initialize application state and directories."""
    ensure_directories()
    
    # Initialize session state variables
    init_session_state(st.session_state, 'original_text', '')
    init_session_state(st.session_state, 'translated_text', '')
    init_session_state(st.session_state, 'detected_language', '')
    init_session_state(st.session_state, 'audio_file', None)
    init_session_state(st.session_state, 'output_audio', None)
    init_session_state(st.session_state, 'processing', False)
    init_session_state(st.session_state, 'error_message', '')


def main():
    """Main application function."""
    
    # Initialize
    initialize_app()
    
    # Header
    st.markdown('<p class="main-header">🎙️ Multilingual Voice Translator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Speak in any language → Get instant translation in text & audio</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Target language selection
        target_lang = st.selectbox(
            "🎯 Target Language",
            options=get_language_options_for_dropdown(),
            format_func=lambda x: x[1],
            help="Select the language you want to translate to"
        )
        target_lang_code = target_lang[0]
        
        # Recording duration
        duration = st.slider(
            "⏱️ Recording Duration (seconds)",
            min_value=3,
            max_value=15,
            value=5,
            step=1,
            help="How long to record audio"
        )
        
        # Whisper model selection
        whisper_model = st.selectbox(
            "🤖 Whisper Model",
            options=["tiny", "base", "small"],
            index=1,  # Default to base
            help="Choose model based on your hardware. Base is recommended."
        )
        
        st.divider()
        
        # Info box
        st.info("""
        **How to use:**
        1. Select your target language
        2. Set recording duration
        3. Click 'Record' and speak
        4. Get instant translation!
        """)
        
        # Cleanup button
        if st.button("🧹 Clean Up Temp Files"):
            deleted = cleanup_old_files()
            st.success(f"Cleaned up {deleted} old files")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Input Audio")
        
        # Option 1: Record audio
        st.markdown("**Option 1: Record from Microphone**")
        
        if st.button("🎤 Start Recording", use_container_width=True, type="primary"):
            with st.spinner("Recording... Please speak now!"):
                try:
                    # Record audio
                    audio_data = record_audio(duration=duration)
                    
                    # Apply noise reduction
                    audio_data = reduce_noise(audio_data)
                    
                    # Check quality
                    is_valid, quality_msg = check_audio_quality(audio_data)
                    
                    if not is_valid:
                        st.error(f"❌ {quality_msg}")
                        st.session_state['error_message'] = quality_msg
                    else:
                        # Save audio
                        audio_filename = generate_filename("input", ".wav")
                        save_audio(audio_data, audio_filename)
                        
                        st.session_state['audio_file'] = audio_filename
                        st.session_state['audio_data'] = audio_data
                        st.success(f"✅ Recording complete! ({duration}s)")
                        
                        # Auto-process
                        st.rerun()
                
                except Exception as e:
                    error_msg = f"Recording failed: {str(e)}"
                    st.error(error_msg)
                    st.session_state['error_message'] = error_msg
        
        st.divider()
        
        # Option 2: Upload audio file
        st.markdown("**Option 2: Upload Audio File**")
        
        uploaded_file = st.file_uploader(
            "Choose audio file",
            type=['wav', 'mp3', 'm4a', 'flac'],
            help="Supported formats: WAV, MP3, M4A, FLAC"
        )
        
        if uploaded_file is not None:
            # Save uploaded file
            upload_filename = generate_filename("upload", ".wav")
            
            with open(upload_filename, "wb") as f:
                f.write(uploaded_file.read())
            
            # Validate
            is_valid, msg = validate_audio_file(upload_filename)
            
            if is_valid:
                st.session_state['audio_file'] = upload_filename
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Load audio data
                audio_data = load_audio_file(upload_filename)
                st.session_state['audio_data'] = audio_data
                
                st.rerun()
            else:
                st.error(f"❌ {msg}")
    
    with col2:
        st.subheader("📊 Results")
        
        # Process if audio file exists
        if st.session_state.get('audio_file'):
            audio_path = st.session_state['audio_file']
            
            # Show processing status
            if st.session_state.get('processing', False):
                with st.spinner("Processing..."):
                    pass
            
            # Step 1: Transcription
            with st.expander("📝 Step 1: Speech-to-Text", expanded=True):
                if st.button("Transcribe Audio", key="transcribe_btn"):
                    with st.spinner("Transcribing with Whisper..."):
                        transcriber = WhisperTranscriber(model_size=whisper_model)
                        success, text, detected_lang = transcriber.transcribe(audio_path)
                        
                        if success:
                            st.session_state['original_text'] = text
                            st.session_state['detected_language'] = detected_lang
                            st.success("✅ Transcription complete!")
                            st.rerun()
                        else:
                            st.error(f"❌ {text}")
            
            # Display transcription results
            if st.session_state['original_text']:
                st.markdown("#### Original Text:")
                st.info(f"**Detected Language:** {st.session_state['detected_language'].upper()}")
                st.markdown(f'<div class="result-box">{st.session_state["original_text"]}</div>', unsafe_allow_html=True)
            
            # Step 2: Translation
            if st.session_state['original_text']:
                with st.expander("🌐 Step 2: Translation", expanded=True):
                    source_lang = st.session_state['detected_language']
                    
                    # Check if same language
                    if source_lang == target_lang_code:
                        st.warning("⚠️ Source and target languages are the same. No translation needed.")
                        st.session_state['translated_text'] = st.session_state['original_text']
                    elif st.button("Translate Text", key="translate_btn"):
                        with st.spinner(f"Translating from {source_lang.upper()} to {target_lang_code.upper()}..."):
                            translator = MarianTranslator()
                            success, translated = translator.translate(
                                st.session_state['original_text'],
                                source_lang,
                                target_lang_code
                            )
                            
                            if success:
                                st.session_state['translated_text'] = translated
                                st.success("✅ Translation complete!")
                                st.rerun()
                            else:
                                st.error(f"❌ {translated}")
                                # Try fallback
                                st.info("Trying alternative translation method...")
            
            # Display translation results
            if st.session_state['translated_text']:
                st.markdown("#### Translated Text:")
                target_lang_name = get_language_name(target_lang_code)
                st.markdown(f'<div class="result-box success-box"><strong>{target_lang_name}:</strong><br>{st.session_state["translated_text"]}</div>', unsafe_allow_html=True)
                
                # Step 3: Text-to-Speech
                with st.expander("🔊 Step 3: Text-to-Speech", expanded=True):
                    if st.button("Generate Speech", key="tts_btn"):
                        with st.spinner("Generating audio with Google TTS..."):
                            tts = TextToSpeech()
                            gtts_lang = get_gtts_code(target_lang_code)
                            output_filename = generate_filename("output", ".mp3")
                            
                            success, result = tts.generate_speech(
                                st.session_state['translated_text'],
                                gtts_lang,
                                output_filename
                            )
                            
                            if success:
                                st.session_state['output_audio'] = output_filename
                                st.success("✅ Audio generated!")
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")
            
            # Display audio player
            if st.session_state.get('output_audio'):
                st.markdown("#### 🔊 Translated Audio:")
                audio_path = st.session_state['output_audio']
                
                if Path(audio_path).exists():
                    audio_file = open(audio_path, "rb")
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # Download buttons
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        # Download transcript
                        transcript_text = f"Original ({st.session_state['detected_language'].upper()}):\n{st.session_state['original_text']}\n\n---\n\nTranslated ({target_lang_code.upper()}):\n{st.session_state['translated_text']}"
                        st.download_button(
                            label="📥 Download Transcript",
                            data=transcript_text,
                            file_name="transcript.txt",
                            mime="text/plain"
                        )
                    
                    with col_dl2:
                        # Download audio
                        st.download_button(
                            label="📥 Download Audio",
                            data=audio_bytes,
                            file_name="translation.mp3",
                            mime="audio/mp3"
                        )
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><strong>Powered by:</strong> OpenAI Whisper • Helsinki-NLP MarianMT • Google TTS</p>
        <p>Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Error display
    if st.session_state.get('error_message'):
        st.error(f"⚠️ {st.session_state['error_message']}")


if __name__ == "__main__":
    main()
