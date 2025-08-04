import numpy as np
from pydub import AudioSegment
import io
import whisper
import torch

class WhisperEngine:
    def __init__(self, model_name="large"):
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
