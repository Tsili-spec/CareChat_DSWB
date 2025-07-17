import re
from textblob import TextBlob
from typing import List, Optional

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
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

def extract_topics(text: str) -> List[str]:
    topic_keywords = {
        "wait_time": ["wait", "delay", "long queue", "waiting", "slow"],
        "staff_attitude": ["rude", "impolite", "shouted", "disrespectful", "unfriendly", "nonchalant", "care"],
        "medication": ["drug", "pill", "prescription", "medication", "dose", "tablet"],
        "cost": ["expensive", "bill", "cost", "money", "price"]
    }
    found_topics = []
    for topic, keywords in topic_keywords.items():
        for word in keywords:
            if word in text:
                found_topics.append(topic)
                break
    return found_topics

def flag_urgent(text: str) -> bool:
    urgent_keywords = [
        "wrong drug", "bleeding", "dying", "emergency",
        "critical", "injury", "pain", "severe", "unconscious", "collapsed"
    ]
    return any(word in text for word in urgent_keywords)

def analyze_feedback(text: Optional[str] = None, rating: Optional[int] = None) -> dict:
    if not text and rating is None:
        return {"error": "No input text or rating provided."}
    result = {}
    clean_text = preprocess(text) if text else ""
    if text and clean_text.strip():
        nlp_sentiment = get_sentiment_from_text(clean_text)
        result["sentiment"] = nlp_sentiment
    elif rating is not None:
        rating_sentiment = get_sentiment_from_rating(rating)
        result["sentiment"] = rating_sentiment
    if text and clean_text.strip():
        if result["sentiment"] == "negative":
            topics = extract_topics(clean_text)
            result["topics"] = topics if topics else 'Unidentified'
        result["urgent_flag"] = flag_urgent(clean_text)
    return result
