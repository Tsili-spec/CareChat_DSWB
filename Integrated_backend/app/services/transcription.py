import whisper
import tempfile
import os
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Load Whisper model (will be downloaded automatically on first use)
try:
    model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    model = None

def transcribe_audio(audio_data: bytes) -> dict:
    """
    Transcribe audio data to text using OpenAI Whisper
    
    Args:
        audio_data: Audio file data as bytes
        
    Returns:
        Dictionary containing transcribed text, detected language, and confidence
    """
    if not model:
        logger.error("Whisper model not available")
        return {
            "text": "",
            "language": "unknown",
            "confidence": 0.0
        }
    
    try:
        # Create temporary file for audio data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio
            result = model.transcribe(temp_file_path)
            
            transcribed_text = result["text"]
            detected_language = result.get("language", "unknown")
            
            # Whisper doesn't provide confidence in the same way, so we'll estimate it
            # based on the length and content of the transcription
            confidence = min(1.0, len(transcribed_text) / 100) if transcribed_text else 0.0
            
            logger.info(f"Successfully transcribed audio, detected language: {detected_language}")
            
            return {
                "text": transcribed_text,
                "language": detected_language,
                "confidence": confidence
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        return {
            "text": "",
            "language": "unknown",
            "confidence": 0.0
        }
