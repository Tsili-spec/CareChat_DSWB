"""
Analysis service for feedback sentiment and topic analysis
Based on Track1 implementation
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def analyze_feedback(text: str, rating: Optional[int] = None) -> Dict[str, Any]:
    """
    Analyze feedback text for sentiment, topics, and urgency
    
    Args:
        text: Feedback text to analyze
        rating: Optional rating (1-5 scale)
    
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Basic sentiment analysis based on keywords and rating
        sentiment = determine_sentiment(text, rating)
        topics = extract_topics(text, sentiment)
        urgent_flag = is_urgent(text, sentiment, rating)
        
        return {
            "sentiment": sentiment,
            "topics": topics,
            "urgent_flag": urgent_flag
        }
    except Exception as e:
        logger.error(f"Error analyzing feedback: {e}")
        return {
            "sentiment": "neutral",
            "topics": None,
            "urgent_flag": False
        }

def determine_sentiment(text: str, rating: Optional[int] = None) -> str:
    """Determine sentiment from text and rating"""
    text_lower = text.lower()
    
    # Keywords for sentiment analysis
    positive_keywords = [
        "good", "great", "excellent", "amazing", "wonderful", "satisfied",
        "happy", "pleased", "thank", "helpful", "friendly", "professional"
    ]
    
    negative_keywords = [
        "bad", "terrible", "awful", "horrible", "disappointed", "angry",
        "frustrated", "upset", "poor", "worst", "hate", "complain",
        "problem", "issue", "wrong", "error", "fail", "rude"
    ]
    
    urgent_keywords = [
        "urgent", "emergency", "immediate", "asap", "critical", "serious",
        "pain", "bleeding", "can't breathe", "chest pain", "allergic"
    ]
    
    # Check for urgent keywords first
    if any(keyword in text_lower for keyword in urgent_keywords):
        return "urgent"
    
    # Use rating if available
    if rating is not None:
        if rating <= 2:
            return "negative"
        elif rating >= 4:
            return "positive"
        else:
            return "neutral"
    
    # Count sentiment keywords
    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
    
    if negative_count > positive_count:
        return "negative"
    elif positive_count > negative_count:
        return "positive"
    else:
        return "neutral"

def extract_topics(text: str, sentiment: str) -> Optional[str]:
    """Extract main topics from negative feedback"""
    if sentiment != "negative":
        return None
    
    text_lower = text.lower()
    
    # Topic keywords
    topics_map = {
        "service": ["service", "staff", "employee", "doctor", "nurse", "reception"],
        "wait_time": ["wait", "waiting", "delayed", "slow", "time", "queue", "appointment"],
        "facility": ["facility", "building", "room", "equipment", "cleanliness", "dirty"],
        "medication": ["medication", "medicine", "prescription", "drug", "dosage"],
        "billing": ["billing", "payment", "cost", "expensive", "insurance", "charge"],
        "communication": ["communication", "explain", "information", "unclear", "confusing"]
    }
    
    for topic, keywords in topics_map.items():
        if any(keyword in text_lower for keyword in keywords):
            return topic
    
    return "general"

def is_urgent(text: str, sentiment: str, rating: Optional[int] = None) -> bool:
    """Determine if feedback indicates urgent attention needed"""
    text_lower = text.lower()
    
    urgent_keywords = [
        "urgent", "emergency", "immediate", "asap", "critical", "serious",
        "pain", "bleeding", "can't breathe", "chest pain", "allergic reaction",
        "severe", "dangerous", "life threatening", "help", "dying"
    ]
    
    # Check for urgent keywords
    if any(keyword in text_lower for keyword in urgent_keywords):
        return True
    
    # Very low rating indicates urgent attention needed
    if rating is not None and rating == 1:
        return True
    
    # Negative sentiment with complaint keywords
    if sentiment == "negative":
        complaint_keywords = ["complaint", "report", "legal", "sue", "lawsuit"]
        if any(keyword in text_lower for keyword in complaint_keywords):
            return True
    
    return False
