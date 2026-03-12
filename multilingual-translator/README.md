# Multilingual Voice Translator

A complete voice translation application that converts speech in any language to text and audio in your target language.

## 🎯 Features

- **Speech-to-Text**: Uses OpenAI's Whisper model for accurate transcription
- **Translation**: Helsinki-NLP MarianMT for fast, offline-capable translation
- **Text-to-Speech**: Google TTS (gTTS) for natural-sounding audio output
- **Multi-language Support**: 8+ languages including English, Hindi, Spanish, French, German, Chinese, Japanese, Arabic
- **User-Friendly UI**: Built with Streamlit for an intuitive interface
- **Audio Upload**: Alternative to microphone recording
- **Download Options**: Save transcripts and audio files

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Microphone (for recording)
- Internet connection (for first-time model downloads and gTTS)
- **Minimum 1GB RAM** (2GB+ recommended for loading AI models)

### Installation

```bash
# Clone or navigate to the project directory
cd multilingual-translator

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### ⚠️ Memory Requirements

This application uses AI models that require significant memory:
- **Whisper (Speech-to-Text)**: ~150MB for base model
- **Helsinki-NLP (Translation)**: ~300-500MB per language pair
- **Recommended**: 2GB+ RAM for smooth operation

If you encounter memory issues:
1. Use the `tiny` Whisper model instead of `base`
2. Close other applications
3. Consider running on a machine with more RAM

### Usage

1. **Select Target Language**: Choose from the dropdown in the sidebar
2. **Set Recording Duration**: Adjust slider (3-15 seconds)
3. **Record Audio**: Click the record button and speak
4. **View Results**: See original text, detected language, translated text
5. **Listen**: Play the translated audio
6. **Download**: Save transcript (.txt) or audio (.mp3)

## 📁 Project Structure

```
multilingual-translator/
├── app.py              # Main Streamlit application
├── voice_recorder.py   # Audio recording functionality
├── transcriber.py      # Whisper speech-to-text
├── translator.py       # Helsinki-NLP translation
├── text_to_speech.py   # gTTS text-to-speech
├── language_config.py  # Language codes and configurations
├── helper.py           # Utility functions
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🧠 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Speech-to-Text | OpenAI Whisper | Transcribe audio to text |
| Translation | Helsinki-NLP MarianMT | Translate between languages |
| Text-to-Speech | gTTS | Generate natural audio |
| UI Framework | Streamlit | Web interface |
| Audio Processing | sounddevice, scipy | Record and process audio |

## 🌐 Supported Languages

- English (en)
- Hindi (hi)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Arabic (ar)
- Portuguese (pt)
- Russian (ru)

## ⚙️ Configuration

### Whisper Model Selection

Choose based on your hardware:
- `tiny`: Fastest, least accurate (weak computers)
- `base`: Good balance (recommended)
- `small`: Better accuracy, slower
- `medium`/`large`: Best accuracy, requires GPU

### Recording Duration

- Short (3-5s): Quick phrases
- Medium (6-10s): Full sentences
- Long (11-15s): Paragraphs

## 🛠️ Edge Cases Handled

- Background noise reduction
- Minimum audio duration validation
- Silence detection
- Same source/target language check
- Missing translation model fallback
- Offline TTS fallback

## 🚀 Deployment

### Local Development

```bash
streamlit run app.py
```

### HuggingFace Spaces

1. Create a new Space on HuggingFace
2. Upload all project files
3. Add `requirements.txt`
4. Configure Docker or Python environment
5. Deploy!

## 💼 Interview Preparation

This project demonstrates:
- Deep Learning (Whisper architecture)
- NLP & Translation (MarianMT)
- Audio Processing (spectrograms, sampling)
- API Integration (gTTS, HuggingFace)
- End-to-End System Design
- Error Handling & Edge Cases
- Clean Code Architecture

Common interview questions covered:
- How does Whisper work internally?
- Explain transformer architecture
- STT vs TTS differences
- Handling multiple language pairs
- Production scaling strategies

## 🔮 Future Enhancements

- [ ] Video input support
- [ ] Real-time streaming translation
- [ ] Multi-speaker detection
- [ ] Mobile app version
- [ ] Document translation
- [ ] LangChain integration for context-aware translation

## 📄 License

MIT License - Feel free to use for learning and projects!

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.
