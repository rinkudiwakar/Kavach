# Audio Detection Door Unlock System

A sophisticated voice-based door unlock system that combines speaker recognition with intent detection for secure access control.

## Features

- **Voice Recognition**: Uses Resemblyzer for speaker embedding and verification
- **Intent Detection**: Picovoice Rhino for natural language command recognition
- **Secure Authentication**: Dual verification (voice match + correct command)
- **Cloud Storage**: Supabase integration for audio and embedding storage
- **Parallel Processing**: Concurrent voice analysis and intent detection for speed
- **Comprehensive Testing**: Full test suite included

## System Architecture

```
Audio Input → WAV Conversion → Parallel Processing
                                  ├─ Voice Embedding → Similarity Check
                                  └─ Intent Recognition
                                  ↓
                               Decision Engine → Door Action
```

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio format conversion)
- Picovoice Access Key
- Supabase Account

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg official site](https://ffmpeg.org/download.html)

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Supabase Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
AUDIO_BUCKET=audio-files
EMBEDDING_BUCKET=embeddings

# Picovoice Rhino Configuration
RHINO_ACCESS_KEY=your-picovoice-access-key
RHINO_CONTEXT_PATH=path/to/your/context.rhn

# System Configuration
SIMILARITY_THRESHOLD=0.75
```

### Rhino Context File

Create a Rhino context file for door commands. Example intents:
- `unlock_door`: "unlock the door", "open door"
- `lock_door`: "lock the door", "secure door"

Visit [Picovoice Console](https://console.picovoice.ai/) to create your context file.

## Project Structure

```
door-unlock-system/
├── db_utils.py              # Database operations
├── resemblyzer_utils.py     # Voice embedding utilities
├── rhino.py                 # Intent recognition
├── main_pipeline.py         # Main processing pipeline
├── test.py                  # Comprehensive test suite
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env                    # Configuration (create this)
└── directories/
    ├── embeddings/         # Stored voice embeddings
    ├── sample/             # Temporary audio files
    ├── sample_embedding/   # Temporary embeddings
    └── temp_audio/         # Temporary storage
```

## Usage

### 1. Initialize the System

First, process all existing audio files in your Supabase storage:

```bash
python db_utils.py
```

This will:
- Download all audio files from Supabase
- Convert them to embeddings
- Upload embeddings back to Supabase
- Store embeddings locally for quick access

### 2. Process Audio for Door Unlock

```bash
python main_pipeline.py path/to/audio/file.wav
```

### 3. Using as a Module

```python
from main_pipeline import process_audio

# Process an audio file
result = process_audio('audio.wav', threshold=0.75)

print(f"Action: {result['action']}")
print(f"Message: {result['message']}")
print(f"Similarity: {result['similarity_score']}")
print(f"Intent: {result['intent']}")
```

## API Reference

### DatabaseUtils

```python
from db_utils import DatabaseUtils

db = DatabaseUtils()

# Download audio from Supabase
db.download_audio_from_supabase('remote_file.mp3', 'local_file.mp3')

# Upload embedding
db.upload_embedding_to_supabase(embedding_array, 'user_embedding.npy')

# Process all database audios
db.process_all_database_audios()

# Initialize system
db.initialize_embeddings()
```

### ResemblyzerUtils

```python
from resemblyzer_utils import ResemblyzerUtils

resemblyzer = ResemblyzerUtils()

# Convert audio to WAV
resemblyzer.convert_to_wav('input.mp3', 'output.wav')

# Generate embedding
success, embedding = resemblyzer.generate_embedding('audio.wav')

# Calculate similarity
similarity = resemblyzer.calculate_cosine_similarity(embedding1, embedding2)

# Calculate mean similarity with stored embeddings
mean_sim, all_sims = resemblyzer.calculate_mean_similarity(sample_embedding)
```

### RhinoUtils

```python
from rhino import RhinoUtils

rhino = RhinoUtils()

# Process audio for intent
result = rhino.process_audio('command.wav')

print(result['is_understood'])  # True/False
print(result['intent'])         # 'unlock_door', 'lock_door', etc.
print(result['slots'])          # Additional parameters

rhino.cleanup()
```

### DoorUnlockPipeline

```python
from main_pipeline import DoorUnlockPipeline

pipeline = DoorUnlockPipeline(similarity_threshold=0.75)

# Execute complete pipeline
result = pipeline.execute('user_command.wav')

# Result contains:
# - action: 'open', 'locked', 'rejected', 'invalid', or 'error'
# - message: Human-readable message
# - similarity_score: Voice similarity score (0-1)
# - intent: Detected intent

pipeline.shutdown()
```

## Testing

Run the comprehensive test suite:

```bash
python test.py
```

The test suite covers:
- Resemblyzer utilities (6 tests)
- Database utilities (3 tests)
- Rhino utilities (2 tests)
- Pipeline functionality (4 tests)
- End-to-end integration (1 test)

## Decision Logic

The system makes decisions based on two factors:

1. **Voice Similarity Score** (0-1)
   - Calculated using cosine similarity of voice embeddings
   - Must exceed threshold (default: 0.75)

2. **Intent Recognition**
   - Must understand the command
   - Must be a valid intent (unlock_door or lock_door)

### Decision Table

| Similarity | Intent | Action | Message |
|------------|--------|--------|---------|
| ≥ Threshold | unlock_door | open | Door is open! |
| ≥ Threshold | lock_door | locked | Door is locked |
| < Threshold | Any | rejected | Voice does not match |
| Any | Not understood | invalid | Please say correct keyword |
| Any | Unknown | invalid | Unknown command |

## Security Considerations

1. **Threshold Tuning**: Adjust `SIMILARITY_THRESHOLD` based on your security requirements
   - Higher (0.85-0.95): More secure, may reject valid users
   - Lower (0.65-0.75): More convenient, slightly less secure

2. **Multi-Sample Training**: Store multiple voice samples per authorized user

3. **Audio Quality**: Ensure clear, noise-free recordings for best results

4. **Liveness Detection**: Consider adding liveness detection to prevent replay attacks

## Troubleshooting

### Common Issues

**Issue: "Rhino engine not initialized"**
- Solution: Check your `RHINO_ACCESS_KEY` and `RHINO_CONTEXT_PATH`

**Issue: "Supabase client not initialized"**
- Solution: Verify `SUPABASE_URL` and `SUPABASE_KEY` in environment variables

**Issue: "Audio must be 16-bit mono at 16kHz"**
- Solution: The system auto-converts, but ensure FFmpeg is installed

**Issue: "No embeddings found"**
- Solution: Run `python db_utils.py` to initialize embeddings

**Issue: Low similarity scores**
- Solution: 
  - Ensure audio quality is good (no background noise)
  - Record multiple samples of the same speaker
  - Check microphone quality

## Performance

- **Embedding Generation**: ~0.5-1 second per audio file
- **Similarity Calculation**: <0.1 seconds for 100 embeddings
- **Intent Recognition**: ~0.5-1 second
- **Total Pipeline**: ~1-2 seconds (parallel processing)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:
- Check existing issues on GitHub
- Create a new issue with detailed information
- Include logs and error messages

## Acknowledgments

- [Resemblyzer](https://github.com/resemble-ai/Resemblyzer) for voice embeddings
- [Picovoice Rhino](https://picovoice.ai/platform/rhino/) for intent recognition
- [Supabase](https://supabase.com/) for cloud storage

## Roadmap

- [ ] Add liveness detection
- [ ] Support for multiple languages
- [ ] Mobile app integration
- [ ] Real-time audio streaming
- [ ] Admin dashboard
- [ ] Activity logging and analytics