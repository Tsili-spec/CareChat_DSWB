import re
import spacy
import numpy as np
from textblob import TextBlob
from typing import List, Optional, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Load the English language model (will be downloaded via spacy download command)
try:
    nlp = spacy.load('en_core_web_md')
    logger.info("Spacy English model loaded successfully")
except OSError:
    logger.warning("Spacy English model not found. Run: python -m spacy download en_core_web_md")
    nlp = None

def preprocess(text: str) -> str:
    """Preprocess text for analysis"""
    text = text.lower()                                 # Convert to lowercase
    text = re.sub(r"[^\w\s]", "", text)                 # Remove punctuation
    text = re.sub(r"\s+", " ", text)                    # remove whitespace
    return text.strip()

def get_sentiment_from_text(text: str) -> str:
    """Analyze sentiment from text using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def get_sentiment_from_rating(rating: int) -> str:
    """Determine sentiment from rating"""
    if rating >= 4:
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "negative"

class TopicAnalyzer:
    """Topic analysis using keyword matching and semantic similarity"""
    
    def __init__(self):
        self.topic_keywords = {
            "wait_time": ["wait", "delay", "queue", "slow", "time"],
            "staff_attitude": ["rude", "impolite", "shout", "disrespect", "unfriendly", "care", 
                             "attitude", "behavior", "manner", "treatment", "service", "doctor", "nurse"],
            "medication": ["drug", "pill", "prescription", "medication", "dose", "tablet", "medicine", 
                         "treatment", "pharmacy", "prescribe"],
            "cost": ["expensive", "bill", "cost", "money", "price", "payment", "charge", "fee", "afford", 
                    "insurance", "financial"]
        }
        
        # Create word vectors for each keyword if spacy is available
        self.topic_word_vectors = {}
        if nlp:
            for topic, keywords in self.topic_keywords.items():
                self.topic_word_vectors[topic] = [nlp(word) for word in keywords]
    
    def _get_text_similarity(self, text: str, topic: str) -> float:
        """Calculate semantic similarity between text and topic keywords"""
        if not nlp:
            # Fallback to simple keyword matching
            return self._simple_keyword_match(text, topic)
        
        # Process the input text
        doc = nlp(text.lower())
        
        # Calculate similarity between each word in text and topic keywords
        max_similarities = []
        for token in doc:
            if not token.is_stop and not token.is_punct:
                similarities = [token.similarity(keyword) for keyword in self.topic_word_vectors[topic]]
                if similarities:
                    max_similarities.append(max(similarities))
        
        # Return average of top similarities if any found
        return sum(max_similarities) / len(max_similarities) if max_similarities else 0.0
    
    def _simple_keyword_match(self, text: str, topic: str) -> float:
        """Simple keyword matching fallback"""
        text_words = set(text.lower().split())
        topic_words = set(self.topic_keywords[topic])
        matches = len(text_words.intersection(topic_words))
        return matches / len(topic_words) if topic_words else 0.0
    
    def extract_topics(self, text: str, similarity_threshold: float = 0.45) -> List[str]:
        """Extract topics from text"""
        found_topics = []
        text = text.lower()
        
        # Calculate similarity scores for each topic
        topic_similarities = {}
        for topic in self.topic_keywords.keys():
            similarity = self._get_text_similarity(text, topic)
            if similarity > similarity_threshold:
                topic_similarities[topic] = similarity
        
        # Sort topics by similarity score
        sorted_topics = sorted(topic_similarities.items(), key=lambda x: x[1], reverse=True)
        found_topics = [topic for topic, score in sorted_topics]
        
        return found_topics

def flag_urgent(text: str) -> bool:
    """Flag urgent feedback based on keywords"""
    urgent_keywords = [
        "wrong drug", "bleeding", "dying", "emergency",
        "critical", "injury", "pain", "severe", "unconscious", "collapsed"
    ]
    text_lower = text.lower()
    return any(word in text_lower for word in urgent_keywords)

class FeedbackAnalyzer:
    """Main feedback analyzer combining sentiment, topic, and urgency analysis"""
    
    def __init__(self):
        self.topic_analyzer = TopicAnalyzer()
    
    def analyze_feedback(self, text: Optional[str] = None, rating: Optional[int] = None) -> dict:
        """
        Analyze feedback for sentiment, topics, and urgency
        
        Args:
            text: Feedback text (optional)
            rating: Feedback rating 1-5 (optional)
            
        Returns:
            Dictionary containing analysis results
        """
        # Case 1: No input at all
        if not text and rating is None:
            return {"error": "No input text or rating provided."}

        result = {}
        clean_text = preprocess(text) if text else ""

        # Case 2: Use NLP sentiment if text is given (regardless of rating)
        if text and clean_text.strip():  # ensure text is not just spaces
            nlp_sentiment = get_sentiment_from_text(clean_text)
            result["sentiment"] = nlp_sentiment
            
        # Case 3: If no text (or just empty spaces), fallback to rating sentiment
        elif rating is not None:
            rating_sentiment = get_sentiment_from_rating(rating)
            result["sentiment"] = rating_sentiment
        
        # Case 4: Topics are analyzed for all text feedback, with confidence scores
        if text and clean_text.strip():
            topics = self.topic_analyzer.extract_topics(clean_text)
            result["topics"] = topics if topics else 'Unidentified'
            result["urgent_flag"] = flag_urgent(clean_text)

        return result

# Create a global instance for backward compatibility
feedback_analyzer = FeedbackAnalyzer()

def analyze_feedback(text: Optional[str] = None, rating: Optional[int] = None) -> dict:
    """
    Backward compatibility function that maintains the original API
    """
    return feedback_analyzer.analyze_feedback(text=text, rating=rating)
