"""
SMS Service for CareChat Backend
Handles SMS notifications for reminders and feedback alerts using Twilio
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from app.models.models import Patient, Reminder, ReminderDelivery
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SMSService:
    """Service for sending SMS notifications via Twilio"""
    
    def __init__(self):
        """Initialize SMS service with Twilio credentials from environment"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_NUMBER')
        
        # Validate configuration
        if not all([self.account_sid, self.auth_token, self.twilio_number]):
            logger.error("Missing Twilio configuration. Check environment variables.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("SMS Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if SMS service is properly configured"""
        return self.client is not None
    
    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send an SMS message via Twilio
        
        Args:
            to_number: Recipient phone number (with country code)
            message: Message content to send
            
        Returns:
            Dict with delivery status, message SID, and error info if any
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMS service not configured',
                'message_sid': None,
                'status': 'failed'
            }
        
        try:
            # Send the message
            message_instance = self.client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully. SID: {message_instance.sid}")
            
            return {
                'success': True,
                'message_sid': message_instance.sid,
                'status': message_instance.status,
                'error': None
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {str(e)}")
            return {
                'success': False,
                'error': f"Twilio error: {str(e)}",
                'message_sid': None,
                'status': 'failed'
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_number}: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'message_sid': None,
                'status': 'failed'
            }
    
    def send_reminder_sms(self, db: Session, reminder_id: str, patient_phone: str = None) -> Dict[str, Any]:
        """
        Send a reminder SMS to a patient
        
        Args:
            db: Database session
            reminder_id: UUID of the reminder to send
            patient_phone: Optional phone number override
            
        Returns:
            Dict with delivery status and tracking information
        """
        try:
            # Get reminder and patient details
            reminder = db.query(Reminder).filter(Reminder.reminder_id == reminder_id).first()
            if not reminder:
                return {
                    'success': False,
                    'error': 'Reminder not found',
                    'reminder_id': reminder_id
                }
            
            patient = db.query(Patient).filter(Patient.patient_id == reminder.patient_id).first()
            if not patient:
                return {
                    'success': False,
                    'error': 'Patient not found',
                    'reminder_id': reminder_id
                }
            
            # Use provided phone or patient's phone
            phone_number = patient_phone or patient.phone_number
            if not phone_number:
                return {
                    'success': False,
                    'error': 'No phone number available',
                    'reminder_id': reminder_id
                }
            
            # Create SMS message
            message = self._format_reminder_message(reminder, patient)
            
            # Send SMS
            result = self.send_sms(phone_number, message)
            
            # Record delivery attempt in database
            delivery_record = ReminderDelivery(
                reminder_id=reminder.reminder_id,
                sent_at=datetime.utcnow(),
                delivery_status=result['status'],
                provider_response=str(result)
            )
            db.add(delivery_record)
            db.commit()
            
            logger.info(f"Reminder SMS sent to {patient.full_name} ({phone_number})")
            
            return {
                **result,
                'reminder_id': reminder_id,
                'patient_name': patient.full_name,
                'phone_number': phone_number,
                'delivery_id': delivery_record.delivery_id
            }
            
        except Exception as e:
            logger.error(f"Error sending reminder SMS: {str(e)}")
            return {
                'success': False,
                'error': f"Service error: {str(e)}",
                'reminder_id': reminder_id
            }
    
    def _format_reminder_message(self, reminder: Reminder, patient: Patient) -> str:
        """
        Format a reminder message for SMS
        Keep it concise for better delivery rates
        """
        # Get current time for personalization
        current_time = datetime.now().strftime("%H:%M")
        
        # Create a concise, friendly message
        message = f"Hi {patient.full_name.split()[0]}, "
        message += f"CareChat Reminder: {reminder.title}. "
        message += f"{reminder.message[:100]}{'...' if len(reminder.message) > 100 else ''} "
        message += f"Time: {current_time}. Reply STOP to opt out."
        
        return message
    
    def send_feedback_alert_sms(self, admin_phone: str, feedback_summary: str) -> Dict[str, Any]:
        """
        Send a feedback alert SMS to healthcare admin
        
        Args:
            admin_phone: Administrator phone number
            feedback_summary: Summary of the feedback received
            
        Returns:
            Dict with delivery status
        """
        try:
            timestamp = datetime.now().strftime("%H:%M")
            message = f"CareChat Alert: New patient feedback at {timestamp}. {feedback_summary[:120]}{'...' if len(feedback_summary) > 120 else ''} Check dashboard for details."
            
            result = self.send_sms(admin_phone, message)
            
            logger.info(f"Feedback alert SMS sent to admin: {admin_phone}")
            return result
            
        except Exception as e:
            logger.error(f"Error sending feedback alert SMS: {str(e)}")
            return {
                'success': False,
                'error': f"Service error: {str(e)}"
            }
    
    def check_delivery_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Check the delivery status of a sent message
        
        Args:
            message_sid: Twilio message SID to check
            
        Returns:
            Dict with current delivery status
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMS service not configured'
            }
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'success': True,
                'message_sid': message_sid,
                'status': message.status,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'price': message.price,
                'price_unit': message.price_unit
            }
            
        except TwilioException as e:
            logger.error(f"Error checking message status {message_sid}: {str(e)}")
            return {
                'success': False,
                'error': f"Twilio error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error checking message status {message_sid}: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }


# Global SMS service instance
sms_service = SMSService()
