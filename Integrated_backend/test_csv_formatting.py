#!/usr/bin/env python3
"""
Test script for CSV formatting logic
"""
import csv
import ast
from io import StringIO
from datetime import datetime

def test_topic_formatting():
    """Test the topic formatting logic"""
    print("Testing topic formatting logic...")
    
    # Sample topic data in different formats (as they might appear in the database)
    test_topics = [
        None,  # No topic
        "",    # Empty topic
        "staff_attitude",  # Simple string
        "staff_attitude,cost",  # Comma-separated string
        ["staff_attitude", "cost"],  # List
        ["staff_attitude", "cost", "medication"],  # Longer list
        "{staff_attitude,cost}",  # Already formatted
        "['staff_attitude', 'cost', 'medication']",  # String representation of list
        '"staff_attitude", "cost"',  # Quoted items
    ]
    
    def format_topic(topic):
        """Format topic using the same logic as in the endpoint"""
        topic_str = ""
        if topic:
            try:
                if isinstance(topic, list):
                    # If topic is a list, format as {topic1,topic2}
                    clean_topics = [str(t).strip() for t in topic if t]
                    if clean_topics:
                        topic_str = "{" + ",".join(clean_topics) + "}"
                elif isinstance(topic, str):
                    # If topic is a string, handle different formats
                    topic_clean = topic.strip()
                    if topic_clean:
                        # Remove any existing brackets and parse
                        topic_clean = topic_clean.strip('{}[]')
                        
                        # Try to parse if it looks like a list representation
                        if topic_clean.startswith("'") or topic_clean.startswith('"'):
                            # Handle string representations like "['topic1', 'topic2']"
                            try:
                                parsed_topics = ast.literal_eval('[' + topic_clean + ']')
                                if isinstance(parsed_topics, list):
                                    clean_topics = [str(t).strip().strip("'\"") for t in parsed_topics if t]
                                    topic_str = "{" + ",".join(clean_topics) + "}"
                                else:
                                    topic_str = "{" + topic_clean + "}"
                            except:
                                # If parsing fails, treat as comma-separated string
                                topics = [t.strip().strip("'\"") for t in topic_clean.split(',') if t.strip()]
                                topic_str = "{" + ",".join(topics) + "}"
                        else:
                            # Simple comma-separated or single topic
                            topics = [t.strip() for t in topic_clean.split(',') if t.strip()]
                            topic_str = "{" + ",".join(topics) + "}"
            except Exception as e:
                # If anything fails, just use the original topic as string
                print(f"Error processing topic: {e}")
                topic_str = "{" + str(topic).strip('{}[]') + "}"
        return topic_str
    
    # Test each topic format
    for i, topic in enumerate(test_topics):
        formatted = format_topic(topic)
        print(f"Test {i+1}: {repr(topic)} -> {repr(formatted)}")
    
    print("\nTesting CSV generation...")
    
    # Create sample data similar to what might be in the database
    sample_feedback = [
        {
            "created_at": datetime(2025, 8, 6),
            "language": "en",
            "rating": 3,
            "sentiment": "neutral",
            "topic": None,
            "urgency": "not urgent"
        },
        {
            "created_at": datetime(2025, 8, 6),
            "language": "en", 
            "rating": 1,
            "sentiment": "negative",
            "topic": ["staff_attitude", "cost"],
            "urgency": "not urgent"
        },
        {
            "created_at": datetime(2025, 8, 6),
            "language": "en",
            "rating": 1,
            "sentiment": "negative", 
            "topic": "['staff_attitude', 'cost', 'medication']",
            "urgency": "not urgent"
        }
    ]
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_ALL)  # Quote all fields
    
    # Write header
    writer.writerow(['Date', 'Language', 'Rating', 'Sentiment', 'Topic', 'Urgency'])
    
    # Write data rows using the same logic as the endpoint
    for feedback in sample_feedback:
        date_str = feedback["created_at"].strftime('%Y-%m-%d') if feedback["created_at"] else "Unknown"
        rating_str = str(feedback["rating"]) if feedback["rating"] else ""
        sentiment_str = feedback["sentiment"] if feedback["sentiment"] else ""
        topic_str = format_topic(feedback["topic"])
        urgency_str = feedback["urgency"] if feedback["urgency"] else "not urgent"
        language_str = feedback["language"] if feedback["language"] else "en"
        
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
    
    # Verify that each row has exactly 6 columns
    lines = csv_content.strip().split('\n')
    print(f"\nCSV Validation:")
    print(f"Total lines: {len(lines)}")
    
    for i, line in enumerate(lines):
        columns = line.split('\t')
        print(f"Line {i+1}: {len(columns)} columns -> {columns}")
        if len(columns) != 6:
            print(f"  ❌ ERROR: Expected 6 columns, got {len(columns)}")
        else:
            print(f"  ✅ OK: Correct number of columns")

if __name__ == "__main__":
    test_topic_formatting()
