from twilio.rest import Client
from app.core.config import settings
from app.core.logging_config import get_logger
from typing import Optional

logger = get_logger(__name__)

class SMSService:
    """SMS service using Twilio"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.twilio_number = settings.TWILIO_NUMBER
        self.my_number = settings.MY_NUMBER
        
        if self.is_configured():
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio SMS service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("Twilio SMS service not configured - missing environment variables")
    
    def is_configured(self) -> bool:
        """Check if SMS service is properly configured"""
        return all([
            self.account_sid,
            self.auth_token,
            self.twilio_number,
            self.my_number
        ])
    
    async def send_sms(self, to_number: str, message: str) -> dict:
        """
        Send SMS message
        
        Args:
            to_number: Recipient phone number
            message: Message content
            
        Returns:
            Dictionary with delivery status and details
        """
        if not self.client:
            logger.error("SMS service not configured or client initialization failed")
            return {
                "success": False,
                "message": "SMS service not configured",
                "delivery_status": "failed"
            }
        
        try:
            message_instance = self.client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully to {to_number}, SID: {message_instance.sid}")
            
            return {
                "success": True,
                "message": "SMS sent successfully",
                "delivery_status": "sent",
                "message_sid": message_instance.sid,
                "provider_response": str(message_instance.status)
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            return {
                "success": False,
                "message": f"Failed to send SMS: {str(e)}",
                "delivery_status": "failed",
                "provider_response": str(e)
            }
    
    async def send_reminder_sms(self, patient_phone: str, reminder_title: str, reminder_message: str) -> dict:
        """
        Send reminder SMS to patient
        
        Args:
            patient_phone: Patient's phone number
            reminder_title: Reminder title
            reminder_message: Reminder message content
            
        Returns:
            Dictionary with delivery status and details
        """
        formatted_message = f"🏥 CareChat Reminder\n\n📋 {reminder_title}\n\n{reminder_message}\n\nTake care! 💊"
        
        return await self.send_sms(patient_phone, formatted_message)

# Create global SMS service instance
sms_service = SMSService()
