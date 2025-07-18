from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from io import StringIO
import csv
from collections import defaultdict, Counter
from typing import Optional, List
from app.models.models import Feedback, Reminder
from app.db.database import get_db

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    language: Optional[List[str]] = Query(None),
    topic: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Feedback)
    if start_date:
        query = query.filter(Feedback.created_at >= start_date)
    if end_date:
        query = query.filter(Feedback.created_at <= end_date)
    if language:
        query = query.filter(Feedback.language.in_(language))
    if topic:
        query = query.filter(Feedback.topic.in_(topic))
    feedbacks = query.all()

    date_ratings = defaultdict(lambda: Counter())
    sentiment_counts = Counter()
    topic_counts = Counter()

    for fb in feedbacks:
        day = fb.created_at.date().isoformat() if fb.created_at else "Unknown"
        date_ratings[day][fb.rating] += 1
        sentiment_counts[fb.sentiment] += 1
        if fb.sentiment == "negative":
            if fb.topic:
                topic_counts[fb.topic] += 1
            else:
                topic_counts["Unidentified"] += 1

    reminder_query = db.query(Reminder)
    if start_date:
        reminder_query = reminder_query.filter(Reminder.created_at >= start_date)
    if end_date:
        reminder_query = reminder_query.filter(Reminder.created_at <= end_date)
    reminders = reminder_query.all()
    reminders_by_day = defaultdict(int)
    for r in reminders:
        day = r.created_at.date().isoformat() if r.created_at else "Unknown"
        reminders_by_day[day] += 1

    return {
        "rating_trends": {d: dict(s) for d, s in date_ratings.items()},
        "sentiment_summary": dict(sentiment_counts),
        "negative_topic_counts": dict(topic_counts),
        "reminders_by_day": reminders_by_day
    }

@router.get("/export")
def export_feedback(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    language: Optional[List[str]] = Query(None),
    topic: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Feedback)
    if start_date:
        query = query.filter(Feedback.created_at >= start_date)
    if end_date:
        query = query.filter(Feedback.created_at <= end_date)
    if language:
        query = query.filter(Feedback.language.in_(language))
    if topic:
        query = query.filter(Feedback.topic.in_(topic))
    feedbacks = query.all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Language", "Rating", "Sentiment", "Topic", "Urgency"])
    for fb in feedbacks:
        writer.writerow([
            fb.created_at.date().isoformat() if fb.created_at else "Unknown",
            fb.language,
            fb.rating,
            fb.sentiment,
            fb.topic,
            fb.urgency
        ])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=feedback_export.csv"})
