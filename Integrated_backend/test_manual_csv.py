#!/usr/bin/env python3
"""
Quick test of the CSV endpoint to verify it doesn't crash
"""
import csv
from io import StringIO

def test_manual_csv_generation():
    """Test manual CSV generation matching the endpoint logic"""
    print("Testing manual CSV generation...")
    
    # Sample data that might come from the database
    sample_feedback = [
        {
            "created_at": "2025-08-06",
            "language": "en",
            "rating": 3,
            "sentiment": "neutral",
            "topic": None,
            "urgency": "not urgent"
        },
        {
            "created_at": "2025-08-06",
            "language": "en", 
            "rating": 1,
            "sentiment": "negative",
            "topic": ["staff_attitude", "cost"],
            "urgency": "not urgent"
        },
        {
            "created_at": "2025-08-06",
            "language": "en",
            "rating": 1,
            "sentiment": "negative", 
            "topic": "{staff_attitude,cost,medication}",
            "urgency": "not urgent"
        }
    ]
    
    # Generate CSV using the same logic as the endpoint
    output = StringIO()
    writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_ALL)
    
    # Write header
    writer.writerow(['Date', 'Language', 'Rating', 'Sentiment', 'Topic', 'Urgency'])
    
    # Write data rows
    for feedback in sample_feedback:
        date_str = feedback["created_at"]
        rating_str = str(feedback["rating"]) if feedback["rating"] else ""
        sentiment_str = feedback["sentiment"] if feedback["sentiment"] else ""
        urgency_str = feedback["urgency"] if feedback["urgency"] else "not urgent"
        language_str = feedback["language"] if feedback["language"] else "en"
        
        # Handle topic
        topic_str = ""
        if feedback["topic"]:
            if isinstance(feedback["topic"], list):
                clean_topics = [str(topic).strip() for topic in feedback["topic"] if topic]
                if clean_topics:
                    topic_str = "{" + ",".join(clean_topics) + "}"
            elif isinstance(feedback["topic"], str):
                topic_clean = feedback["topic"].strip()
                if topic_clean:
                    if not (topic_clean.startswith('{') and topic_clean.endswith('}')):
                        topic_str = "{" + topic_clean + "}"
                    else:
                        topic_str = topic_clean
        
        writer.writerow([
            date_str,
            language_str,
            rating_str,
            sentiment_str,
            topic_str,
            urgency_str
        ])
    
    # Get the CSV content
    output.seek(0)
    csv_content = output.getvalue()
    output.close()
    
    print("Generated CSV content:")
    print("=" * 80)
    print(csv_content)
    print("=" * 80)
    
    # Parse it back to verify column integrity
    lines = csv_content.strip().split('\n')
    print(f"\nVerification:")
    for i, line in enumerate(lines):
        columns = line.split('\t')
        print(f"Line {i+1}: {len(columns)} columns")
        if len(columns) != 6:
            print(f"  ❌ ERROR: Expected 6 columns, got {len(columns)}")
            return False
        else:
            print(f"  ✅ OK: Correct column count")
    
    print("\n✅ CSV generation test passed!")
    return True

if __name__ == "__main__":
    success = test_manual_csv_generation()
    exit(0 if success else 1)
