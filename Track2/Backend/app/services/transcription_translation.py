from app.services.transcription import transcribe_audio

def transcribe_simple(audio_data: bytes) -> dict:
    """
    Simple transcription without translation.
    
    Args:
        audio_data: Raw audio bytes
    
    Returns:
        Dictionary containing transcription results
    """
    return transcribe_audio(audio_data)
