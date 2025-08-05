"""
Reminder Scheduler Service for CareChat Backend
Handles automatic scheduling and sending of reminder SMS at appropriate times
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.database import get_db
from app.models.models import Reminder, Patient, ReminderDelivery
from app.services.sms_service import sms_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ReminderScheduler:
    """Service for scheduling and sending reminder notifications"""
    
    def __init__(self):
        """Initialize the reminder scheduler"""
        self.is_running = False
        self.check_interval = 60  # Check every minute for due reminders
    
    async def start_scheduler(self):
        """Start the reminder scheduler background task"""
        if self.is_running:
            logger.warning("Reminder scheduler is already running")
            return
        
        self.is_running = True
        logger.info("Starting reminder scheduler...")
        
        try:
            while self.is_running:
                await self._check_and_send_due_reminders()
                await asyncio.sleep(self.check_interval)
        except Exception as e:
            logger.error(f"Reminder scheduler error: {str(e)}")
        finally:
            self.is_running = False
            logger.info("Reminder scheduler stopped")
    
    def stop_scheduler(self):
        """Stop the reminder scheduler"""
        self.is_running = False
        logger.info("Stopping reminder scheduler...")
    
    async def _check_and_send_due_reminders(self):
        """Check for due reminders and send SMS notifications"""
        try:
            # Get database session
            db: Session = next(get_db())
            
            # Get current time and day
            now = datetime.utcnow()
            current_day = now.strftime("%A")  # Full day name (e.g., "Monday")
            
            # Find active reminders that are due
            due_reminders = self._get_due_reminders(db, now, current_day)
            
            if due_reminders:
                logger.info(f"Found {len(due_reminders)} due reminders to send")
                
                for reminder in due_reminders:
                    await self._send_reminder_notification(db, reminder)
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error checking due reminders: {str(e)}")
    
    def _get_due_reminders(self, db: Session, current_time: datetime, current_day: str) -> List[Reminder]:
        """
        Get reminders that are due to be sent now
        
        Logic:
        1. Reminder must be active
        2. Current day must be in the reminder's days list
        3. Current time must match one of the scheduled times (within 1 minute tolerance)
        4. Reminder should not have been sent in the last hour (to avoid duplicates)
        """
        try:
            # Get all active reminders for today
            active_reminders = db.query(Reminder).filter(
                Reminder.status == "active"
            ).all()
            
            due_reminders = []
            
            for reminder in active_reminders:
                # Check if reminder is scheduled for today
                if current_day not in reminder.days:
                    continue
                
                # Check if current time matches any scheduled time (within 1-minute window)
                for scheduled_time in reminder.scheduled_time:
                    if self._is_time_match(current_time, scheduled_time):
                        # Check if we haven't sent this reminder recently
                        if not self._was_sent_recently(db, reminder.reminder_id, hours=1):
                            due_reminders.append(reminder)
                            break  # Only add once per reminder
            
            return due_reminders
            
        except Exception as e:
            logger.error(f"Error getting due reminders: {str(e)}")
            return []
    
    def _is_time_match(self, current_time: datetime, scheduled_time: datetime, tolerance_minutes: int = 1) -> bool:
        """
        Check if current time matches scheduled time within tolerance
        
        Args:
            current_time: Current UTC time
            scheduled_time: Scheduled time from database
            tolerance_minutes: Tolerance window in minutes
        """
        try:
            # Extract time components (ignore date)
            current_hour = current_time.hour
            current_minute = current_time.minute
            
            scheduled_hour = scheduled_time.hour
            scheduled_minute = scheduled_time.minute
            
            # Calculate total minutes from midnight
            current_total_minutes = current_hour * 60 + current_minute
            scheduled_total_minutes = scheduled_hour * 60 + scheduled_minute
            
            # Check if within tolerance
            time_diff = abs(current_total_minutes - scheduled_total_minutes)
            
            return time_diff <= tolerance_minutes
            
        except Exception as e:
            logger.error(f"Error checking time match: {str(e)}")
            return False
    
    def _was_sent_recently(self, db: Session, reminder_id: str, hours: int = 1) -> bool:
        """
        Check if reminder was sent recently to avoid duplicates
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_delivery = db.query(ReminderDelivery).filter(
                and_(
                    ReminderDelivery.reminder_id == reminder_id,
                    ReminderDelivery.sent_at >= cutoff_time
                )
            ).first()
            
            return recent_delivery is not None
            
        except Exception as e:
            logger.error(f"Error checking recent delivery: {str(e)}")
            return False
    
    async def _send_reminder_notification(self, db: Session, reminder: Reminder):
        """Send SMS notification for a specific reminder"""
        try:
            # Check if SMS service is configured
            if not sms_service.is_configured():
                logger.warning(f"SMS service not configured, skipping reminder {reminder.reminder_id}")
                return
            
            # Get patient information
            patient = db.query(Patient).filter(Patient.patient_id == reminder.patient_id).first()
            if not patient:
                logger.error(f"Patient not found for reminder {reminder.reminder_id}")
                return
            
            # Send SMS
            result = sms_service.send_reminder_sms(db, str(reminder.reminder_id))
            
            if result['success']:
                logger.info(f"✅ Reminder SMS sent to {patient.full_name} for: {reminder.title}")
            else:
                logger.error(f"❌ Failed to send reminder SMS: {result['error']}")
            
        except Exception as e:
            logger.error(f"Error sending reminder notification: {str(e)}")
    
    def send_immediate_reminder(self, db: Session, reminder_id: str) -> Dict[str, Any]:
        """
        Send a reminder immediately (for testing or manual triggers)
        
        Args:
            db: Database session
            reminder_id: UUID of reminder to send
            
        Returns:
            Dict with result information
        """
        try:
            # Validate reminder exists and is active
            reminder = db.query(Reminder).filter(
                and_(
                    Reminder.reminder_id == reminder_id,
                    Reminder.status == "active"
                )
            ).first()
            
            if not reminder:
                return {
                    'success': False,
                    'error': 'Reminder not found or not active',
                    'reminder_id': reminder_id
                }
            
            # Send SMS
            result = sms_service.send_reminder_sms(db, reminder_id)
            
            return {
                **result,
                'sent_immediately': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending immediate reminder: {str(e)}")
            return {
                'success': False,
                'error': f"Service error: {str(e)}",
                'reminder_id': reminder_id
            }
    
    def get_upcoming_reminders(self, db: Session, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """
        Get reminders that are scheduled in the next specified hours
        
        Args:
            db: Database session
            hours_ahead: How many hours ahead to look
            
        Returns:
            List of upcoming reminders with timing information
        """
        try:
            current_time = datetime.utcnow()
            upcoming = []
            
            # Get all active reminders
            active_reminders = db.query(Reminder).filter(
                Reminder.status == "active"
            ).all()
            
            for reminder in active_reminders:
                # Get patient info
                patient = db.query(Patient).filter(
                    Patient.patient_id == reminder.patient_id
                ).first()
                
                if not patient:
                    continue
                
                # Check each scheduled time
                for scheduled_time in reminder.scheduled_time:
                    # Calculate next occurrence
                    next_occurrence = self._get_next_occurrence(
                        current_time, scheduled_time, reminder.days
                    )
                    
                    if next_occurrence and next_occurrence <= current_time + timedelta(hours=hours_ahead):
                        upcoming.append({
                            'reminder_id': str(reminder.reminder_id),
                            'patient_name': patient.full_name,
                            'patient_phone': patient.phone_number,
                            'title': reminder.title,
                            'message': reminder.message,
                            'next_occurrence': next_occurrence.isoformat(),
                            'days': reminder.days,
                            'scheduled_time': scheduled_time.isoformat()
                        })
            
            # Sort by next occurrence
            upcoming.sort(key=lambda x: x['next_occurrence'])
            
            return upcoming
            
        except Exception as e:
            logger.error(f"Error getting upcoming reminders: {str(e)}")
            return []
    
    def _get_next_occurrence(self, current_time: datetime, scheduled_time: datetime, days: List[str]) -> datetime:
        """Calculate the next occurrence of a reminder"""
        try:
            # Map day names to weekday numbers (Monday=0, Sunday=6)
            day_mapping = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            
            # Get scheduled weekdays
            scheduled_weekdays = [day_mapping.get(day) for day in days if day in day_mapping]
            
            if not scheduled_weekdays:
                return None
            
            # Start from today
            search_date = current_time.date()
            
            # Look for next occurrence within next 7 days
            for i in range(8):  # Check today + next 7 days
                check_date = search_date + timedelta(days=i)
                
                if check_date.weekday() in scheduled_weekdays:
                    # Create datetime with scheduled time
                    next_occurrence = datetime.combine(
                        check_date,
                        scheduled_time.time()
                    )
                    
                    # If it's today, make sure it's in the future
                    if next_occurrence > current_time:
                        return next_occurrence
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating next occurrence: {str(e)}")
            return None


# Global scheduler instance
reminder_scheduler = ReminderScheduler()
