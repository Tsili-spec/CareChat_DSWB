import asyncio
from datetime import datetime, timedelta
from typing import List
from app.services.reminder_service import ReminderService
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ReminderScheduler:
    """Scheduler for automated reminder delivery"""
    
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def start_scheduler(self):
        """Start the reminder scheduler"""
        if self.is_running:
            logger.warning("Reminder scheduler is already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting reminder scheduler...")
        
        # Start the scheduler task
        self.task = asyncio.create_task(self._scheduler_loop())
        
        return {"message": "Reminder scheduler started successfully"}
    
    def stop_scheduler(self):
        """Stop the reminder scheduler"""
        if not self.is_running:
            logger.warning("Reminder scheduler is not running")
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
        
        logger.info("🛑 Reminder scheduler stopped")
        return {"message": "Reminder scheduler stopped successfully"}
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        try:
            while self.is_running:
                logger.info("🔄 Checking for due reminders...")
                
                try:
                    await self._process_due_reminders()
                except Exception as e:
                    logger.error(f"Error processing reminders: {e}")
                
                # Wait for next check (every 5 minutes)
                await asyncio.sleep(300)  # 5 minutes
                
        except asyncio.CancelledError:
            logger.info("Reminder scheduler task cancelled")
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
            self.is_running = False
    
    async def _process_due_reminders(self):
        """Process reminders that are due for delivery"""
        try:
            # Get all active reminders
            active_reminders = await ReminderService.get_active_reminders()
            
            if not active_reminders:
                logger.debug("No active reminders found")
                return
            
            current_time = datetime.utcnow()
            due_reminders = []
            
            # Check each reminder to see if it's due
            for reminder in active_reminders:
                if self._is_reminder_due(reminder, current_time):
                    due_reminders.append(reminder)
            
            if due_reminders:
                logger.info(f"Found {len(due_reminders)} due reminders")
                
                # Send notifications for due reminders
                for reminder in due_reminders:
                    try:
                        result = await ReminderService.send_reminder_notification(reminder)
                        if result["success"]:
                            logger.info(f"✅ Reminder {reminder.reminder_id} sent successfully")
                        else:
                            logger.error(f"❌ Failed to send reminder {reminder.reminder_id}: {result['message']}")
                    
                    except Exception as e:
                        logger.error(f"Error sending reminder {reminder.reminder_id}: {e}")
            else:
                logger.debug("No due reminders found")
                
        except Exception as e:
            logger.error(f"Error in _process_due_reminders: {e}")
    
    def _is_reminder_due(self, reminder, current_time: datetime) -> bool:
        """
        Check if a reminder is due for delivery
        
        Args:
            reminder: Reminder object
            current_time: Current datetime
            
        Returns:
            True if reminder is due, False otherwise
        """
        try:
            # Check scheduled times
            for scheduled_time in reminder.scheduled_time:
                # Check if this scheduled time is due (within 5 minutes)
                time_diff = abs((current_time - scheduled_time).total_seconds())
                if time_diff <= 300:  # 5 minutes tolerance
                    return True
            
            # Check recurring reminders based on days
            if reminder.days:
                current_day = current_time.strftime("%A").lower()
                if current_day in [day.lower() for day in reminder.days]:
                    # For daily reminders, check if it's the right time
                    # This is a simplified check - you might want more sophisticated logic
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if reminder is due: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "status": "running" if self.is_running else "stopped"
        }

# Create global scheduler instance
reminder_scheduler = ReminderScheduler()
