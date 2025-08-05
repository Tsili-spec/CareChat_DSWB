import re
import spacy
import numpy as np
from textblob import TextBlob
from typing import List, Optional, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the English language model
nlp = spacy.load('en_core_web_md')

def preprocess(text: str) -> str:
    text = text.lower()                                 # Convert to lowercase
    text = re.sub(r"[^\w\s]", "", text)                 # Remove punctuation
    text = re.sub(r"\s+", " ", text)                    # remove whitespace
    return text.strip()

def get_sentiment_from_text(text: str) -> str:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def get_sentiment_from_rating(rating: int) -> str:
    if rating >= 4:
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "negative"

class TopicAnalyzer:
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
        # Create word vectors for each keyword
        self.topic_word_vectors = {}
        for topic, keywords in self.topic_keywords.items():
            self.topic_word_vectors[topic] = [nlp(word) for word in keywords]

    def _get_text_similarity(self, text: str, topic: str) -> float:
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

    def extract_topics(self, text: str, similarity_threshold: float = 0.45) -> List[str]:
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
    urgent_keywords = [
        "wrong drug", "bleeding", "dying", "emergency",
        "critical", "injury", "pain", "severe", "unconscious", "collapsed"
    ]
    return any(word in text for word in urgent_keywords)

class FeedbackAnalyzer:
    def __init__(self):
        self.topic_analyzer = TopicAnalyzer()

    def analyze_feedback(self, text: Optional[str] = None, rating: Optional[int] = None) -> dict:
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
