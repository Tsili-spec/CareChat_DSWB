# Patient Feedback Analysis Module
This branch contains the core logic for analyzing patient feedback using a combination of NLP (Natural Language Processing) and star ratings. 

🔍 What This Module Does
Sentiment Analysis

Uses NLP to classify feedback as positive, neutral, or negative.

Falls back to star rating when no text is provided.

Prioritizes text sentiment when both are available.

Topic Detection

Identifies key topics in feedback: wait_time, staff_attitude, medication, cost.

Urgency Flagging

Detects critical feedback using urgent keywords like "emergency", "bleeding", "wrong drug", etc.

