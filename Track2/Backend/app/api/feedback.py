# Export chat data for feedback analysis
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from app.db.database import get_db
from app.models.conversation import ChatMessage, Conversation
from app.models.user import User
import csv
import os
from datetime import datetime, date
from typing import Optional
import tempfile

router = APIRouter(tags=["Feedback"])

@router.get('/export-chat-data')
def export_chat_data(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None, description="Filter by year (e.g., 2025)"),
    month: Optional[int] = Query(None, description="Filter by month (1-12)"),
    day: Optional[int] = Query(None, description="Filter by day (1-31)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Export chat conversations as CSV file with optional filtering.
    
    Parameters:
    - year: Filter by specific year
    - month: Filter by specific month (requires year)
    - day: Filter by specific day (requires year and month)
    - start_date: Start date for range filtering (YYYY-MM-DD)
    - end_date: End date for range filtering (YYYY-MM-DD)
    
    If no parameters provided, exports current day's data.
    """
    try:
        # Build query for chat messages with user info
        query = db.query(
            ChatMessage.role,
            ChatMessage.content,
            ChatMessage.timestamp,
            ChatMessage.model_used,
            ChatMessage.conversation_id,
            User.full_name.label("user_name")
        ).join(
            Conversation, ChatMessage.conversation_id == Conversation.conversation_id
        ).join(
            User, Conversation.patient_id == User.patient_id
        )
        
        # Apply date filters
        today = date.today()
        
        if start_date and end_date:
            # Date range filtering
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(
                and_(
                    ChatMessage.timestamp >= start_dt,
                    ChatMessage.timestamp <= end_dt
                )
            )
            filename_suffix = f"{start_date}_to_{end_date}"
        elif year:
            query = query.filter(extract('year', ChatMessage.timestamp) == year)
            if month:
                query = query.filter(extract('month', ChatMessage.timestamp) == month)
                if day:
                    query = query.filter(extract('day', ChatMessage.timestamp) == day)
                    filename_suffix = f"{year}-{month:02d}-{day:02d}"
                else:
                    filename_suffix = f"{year}-{month:02d}"
            else:
                filename_suffix = f"{year}"
        else:
            # Default: current day
            query = query.filter(
                and_(
                    extract('year', ChatMessage.timestamp) == today.year,
                    extract('month', ChatMessage.timestamp) == today.month,
                    extract('day', ChatMessage.timestamp) == today.day
                )
            )
            filename_suffix = today.strftime("%Y-%m-%d")
        
        # Order by timestamp
        query = query.order_by(ChatMessage.timestamp)
        
        # Execute query
        messages = query.all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="No chat data found for the specified criteria")
        
        # Create temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        csv_filename = f"chat_export_{filename_suffix}.csv"
        
        try:
            writer = csv.writer(temp_file)
            
            # Write headers
            writer.writerow([
                'User Name',
                'Type',
                'Message Content', 
                'Timestamp',
                'Model/Source'
            ])
            
            # Group messages by conversation to pair questions and responses
            conversations = {}
            for msg in messages:
                conv_id = str(msg.conversation_id)
                if conv_id not in conversations:
                    conversations[conv_id] = []
                conversations[conv_id].append(msg)
            
            # Write data rows
            for conv_id, conv_messages in conversations.items():
                for msg in conv_messages:
                    # Determine message type
                    message_type = "Prompt" if msg.role == "user" else "Response"
                    
                    # Determine model/source
                    if msg.role == "user":
                        model_source = msg.user_name
                    else:
                        model_source = msg.model_used or "gemma2-9b-it"  # Default current model
                    
                    writer.writerow([
                        msg.user_name,
                        message_type,
                        msg.content,
                        msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        model_source
                    ])
            
            temp_file.close()
            
            # Return file response
            return FileResponse(
                path=temp_file.name,
                filename=csv_filename,
                media_type='text/csv',
                headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
            )
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise HTTPException(status_code=500, detail=f"Error creating CSV file: {str(e)}")
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
