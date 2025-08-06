"""
Transcription Service for audio processing and speech-to-text conversion
Supports multiple audio formats and languages using Whisper model
Based on Track2 implementation adapted for MongoDB system
"""
from typing import List, Dict, Any, Optional, Tuple
import os
import tempfile
import logging
import numpy as np
from pathlib import Path
import uuid
import numpy as np
from pydub import AudioSegment
import io
import whisper
import torch
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

class WhisperEngine:
    def __init__(self, model_name="small"):
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        print("✅ Whisper model loaded successfully")
    
    def transcribe(self, audio_data: bytes) -> dict:
        """Transcribe audio bytes to text and language info."""
        try:
            # Convert audio to the required format
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            audio = audio.set_frame_rate(16000).set_channels(1)
            samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        except Exception as e:
            print(f"Audio conversion error: {e}")
            return {"text": "", "language": "unknown", "confidence": 0.0, "segments": []}
        
        try:
            # Transcribe using Whisper
            result = self.model.transcribe(
                samples,
                task="transcribe",
                fp16=torch.cuda.is_available()
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(result.get("segments", []))
            
            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "en"),
                "confidence": confidence,
                "segments": result.get("segments", [])
            }
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return {"text": "", "language": "unknown", "confidence": 0.0, "segments": []}
    
    def _calculate_confidence(self, segments: list) -> float:
        """Calculate confidence score from segment probabilities."""
        if not segments:
            return 0.0
        
        confidences = []
        for segment in segments:
            if 'avg_logprob' in segment:
                # Convert log probability to linear scale
                confidence = np.exp(segment['avg_logprob'])
                confidences.append(confidence)
        
        return np.mean(confidences) if confidences else 0.0

# Global instance for reuse
whisper_engine = WhisperEngine()

def transcribe_audio(audio_data: bytes) -> dict:
    """Public function to transcribe audio data."""
    return whisper_engine.transcribe(audio_data)

def transcribe_simple(audio_data: bytes) -> dict:
    """
    Simple transcription without translation.
    
    Args:
        audio_data: Raw audio bytes
    
    Returns:
        Dictionary containing transcription results
    """
    return transcribe_audio(audio_data)

def transcribe_and_translate(audio_bytes: bytes) -> Dict[str, Any]:
    """
    Transcribe audio and translate to multiple languages
    
    Args:
        audio_bytes: Audio file content as bytes
    
    Returns:
        Dictionary with transcription and translation results
    """
    try:
        from app.services.translation import detect_language, translate_text
        
        # First transcribe the audio
        transcription_result = transcribe_simple(audio_bytes)
        
        if not transcription_result.get("text"):
            return {
                "original_text": "",
                "detected_language": "en",
                "translations": {},
                "confidence": 0.0,
                "duration": 0.0,
                "success": False,
                "error": "Transcription failed"
            }
        
        original_text = transcription_result["text"]
        detected_language = transcription_result.get("language", "en")
        
        # Translate to common languages
        translations = {}
        target_languages = ["en", "fr", "es"]
        
        for target_lang in target_languages:
            if target_lang != detected_language:
                translated = translate_text(original_text, detected_language, target_lang)
                translations[target_lang] = translated
            else:
                translations[target_lang] = original_text
        
        return {
            "original_text": original_text,
            "detected_language": detected_language,
            "translations": translations,
            "confidence": transcription_result.get("confidence", 0.0),
            "duration": len(audio_bytes) / 16000,  # Mock duration calculation
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Transcription and translation error: {e}")
        return {
            "original_text": "",
            "detected_language": "en",
            "translations": {},
            "confidence": 0.0,
            "duration": 0.0,
            "success": False,
            "error": str(e)
        }

def save_audio_file(audio_bytes: bytes, filename: str) -> str:
    """
    Save audio bytes to a temporary file
    
    Args:
        audio_bytes: Audio file content
        filename: Original filename
    
    Returns:
        Path to saved file
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = "upload"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving audio file: {e}")
        raise e
