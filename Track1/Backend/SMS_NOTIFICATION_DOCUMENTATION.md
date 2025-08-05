# SMS Notification System Documentation

## Overview

The CareChat SMS notification system provides automated reminder delivery to patients via SMS using Twilio. The system integrates with the existing reminder database to send notifications at scheduled times.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reminder      │    │   SMS Scheduler  │    │   SMS Service   │
│   Database      │───▶│   (Background)   │───▶│   (Twilio)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Patient       │    │   Delivery       │    │   Patient's     │
│   Phone Number  │    │   Tracking       │    │   Mobile Phone  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## SMS Notification Workflow

### 1. Reminder Creation
When a new reminder is created via the API:

```json
POST /api/reminder/
{
    "patient_id": "uuid",
    "title": "Take Morning Medication",
    "message": "Take your blood pressure medication with breakfast",
    "scheduled_time": ["2024-01-15T08:00:00Z"],
    "days": ["Monday", "Wednesday", "Friday"],
    "status": "active"
}
```

**What happens:**
- Reminder is stored in the database
- System logs the new reminder with scheduling details
- Background scheduler will automatically detect and send at the right time

### 2. Background Scheduler Operation

The SMS scheduler runs as a background task that:

1. **Checks every minute** for due reminders
2. **Finds active reminders** where:
   - Current day matches one of the reminder's days
   - Current time matches scheduled time (±1 minute tolerance)
   - Reminder hasn't been sent in the last hour (prevents duplicates)
3. **Triggers SMS sending** for each due reminder
4. **Records delivery status** in the database

### 3. SMS Message Formatting

For each reminder, the system:

1. **Retrieves patient information** (name, phone number)
2. **Formats a concise message**:
   ```
   Hi [FirstName], CareChat Reminder: [Title]. [Message]. Time: [CurrentTime]. Reply STOP to opt out.
   ```
3. **Keeps messages short** (under 160 characters when possible) for better delivery rates
4. **Includes opt-out instructions** for compliance

### 4. SMS Delivery Process

```
Scheduler → SMS Service → Twilio API → Carrier → Patient's Phone
    ↓           ↓            ↓          ↓           ↓
Database ←  Delivery   ←  Message  ←  Status   ←  Receipt
Recording   Tracking     SID         Update     Confirmation
```

1. **SMS Service** validates patient phone number
2. **Twilio API** queues the message for delivery
3. **Carrier networks** deliver to patient's phone
4. **Delivery status** is tracked and recorded
5. **Database logging** maintains audit trail

### 5. Delivery Status Tracking

Each SMS attempt is recorded in the `reminder_delivery` table:

```sql
reminder_delivery:
- delivery_id (UUID)
- reminder_id (FK to reminders)
- sent_at (timestamp)
- delivery_status (queued/sent/delivered/failed)
- provider_response (Twilio response details)
```

**Status meanings:**
- `queued`: Message accepted by Twilio, pending delivery
- `sent`: Message sent to carrier network
- `delivered`: Message confirmed delivered to phone
- `failed`: Delivery failed (invalid number, network error, etc.)

## API Endpoints

### Core SMS Operations

#### Send Immediate SMS
```http
POST /api/reminder/{reminder_id}/send-sms
```
Manually trigger an SMS for testing or urgent notifications.

#### Get Upcoming Reminders
```http
GET /api/reminder/upcoming?hours_ahead=24
```
View reminders scheduled for the next N hours.

#### Check SMS Service Status
```http
GET /api/reminder/sms-status
```
Verify SMS configuration and service health.

### Scheduler Management

#### Start Scheduler
```http
POST /api/reminder/start-scheduler
```
Begin automatic SMS reminder processing.

#### Stop Scheduler
```http
POST /api/reminder/stop-scheduler
```
Stop automatic SMS processing (for maintenance).

## Configuration

### Environment Variables Required

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_NUMBER=+1234567890

# For testing
MY_NUMBER=+1234567890  # Your verified number for testing
```

### Twilio Setup

1. **Create Twilio Account** at https://twilio.com
2. **Get Account SID and Auth Token** from Twilio Console
3. **Purchase a Twilio phone number** for sending SMS
4. **Verify recipient numbers** during development
5. **Add payment method** for production use

## Time Zone Handling

The system uses **UTC time** internally:

1. **Scheduled times** are stored in UTC
2. **Background checks** run on UTC time
3. **Time matching** uses UTC for consistency
4. **Display times** should be converted to local time zones in frontend

## SMS Best Practices Implemented

### Message Content
- **Keep messages concise** (under 160 characters preferred)
- **Include clear identification** ("CareChat Reminder")
- **Add current time** for context
- **Include opt-out instructions** ("Reply STOP to opt out")

### Delivery Optimization
- **Simple, plain text** messages for better delivery rates
- **Avoid special characters** that might cause encoding issues
- **Rate limiting** prevents spam detection
- **Duplicate prevention** avoids sending same reminder multiple times

### Error Handling
- **Graceful failures** don't crash the system
- **Detailed logging** for troubleshooting
- **Status tracking** monitors delivery success
- **Retry logic** for transient failures

## Monitoring and Logging

### Log Locations
- **Application logs**: `logs/carechat_api.log`
- **SMS activity**: Logged with `INFO` level
- **Errors**: Logged with `ERROR` level

### Key Log Messages
```
INFO: SMS sent successfully. SID: SM1234567890abcdef
INFO: Reminder SMS sent to John Doe (+1234567890)
INFO: Found 3 due reminders to send
ERROR: Twilio error sending SMS to +1234567890: Invalid phone number
```

### Monitoring Endpoints
- **GET /api/reminder/sms-status**: Service health check
- **GET /api/reminder/upcoming**: Preview scheduled notifications
- **Database queries**: Check `reminder_delivery` table for delivery history

## Testing

### Manual Testing
Use the provided test script:
```bash
python3 test_sms_reminder_integration.py
```

### Unit Testing
Test individual components:
```bash
python3 sms_test.py --basic
python3 sms_test.py --reminder
python3 sms_test.py --feedback
```

### Integration Testing
1. **Create test patient** with verified phone number
2. **Create reminder** for near-future time
3. **Start scheduler** to enable automatic sending
4. **Send immediate SMS** to test connectivity
5. **Monitor logs** for delivery confirmation

## Production Considerations

### Security
- **Environment variables** for sensitive credentials
- **Phone number validation** prevents abuse
- **Rate limiting** to prevent spam
- **Admin-only endpoints** for scheduler control

### Scalability
- **Background processing** doesn't block API requests
- **Database indexing** on reminder lookup fields
- **Twilio queue management** handles high volume
- **Error recovery** for failed deliveries

### Compliance
- **STOP message handling** for opt-outs
- **Delivery confirmation** for audit trails
- **Patient consent** requirements
- **HIPAA considerations** for healthcare data

## Troubleshooting

### Common Issues

#### SMS Not Configured
```json
{
  "sms_configured": false,
  "status": "not_configured"
}
```
**Solution**: Check environment variables for Twilio credentials.

#### Message Delivery Failed
```json
{
  "success": false,
  "error": "Invalid phone number"
}
```
**Solutions**:
- Verify phone number format (+1234567890)
- Check if number is verified in Twilio (development mode)
- Ensure sufficient Twilio account balance

#### Scheduler Not Running
```json
{
  "scheduler_running": false
}
```
**Solution**: Call `POST /api/reminder/start-scheduler` to start automatic processing.

#### No Reminders Being Sent
**Check**:
1. Scheduler is running
2. Reminders have status "active"
3. Current day is in reminder's days list
4. Current time matches scheduled time
5. SMS service is configured

### Debug Steps

1. **Check service status**:
   ```bash
   curl http://localhost:8000/api/reminder/sms-status
   ```

2. **View upcoming reminders**:
   ```bash
   curl http://localhost:8000/api/reminder/upcoming
   ```

3. **Send test SMS**:
   ```bash
   curl -X POST http://localhost:8000/api/reminder/{reminder_id}/send-sms
   ```

4. **Check logs**:
   ```bash
   tail -f logs/carechat_api.log
   ```

## Future Enhancements

### Planned Features
- **Multi-language SMS** using patient's preferred language
- **SMS templates** for different reminder types
- **Delivery retry logic** for failed messages
- **SMS analytics dashboard** with delivery metrics
- **Patient SMS preferences** (time zones, frequency limits)
- **Two-way SMS** for patient responses

### Integration Opportunities
- **Calendar integration** for appointment reminders
- **Medication database** for drug-specific instructions
- **Emergency alerts** for urgent health notifications
- **Family notifications** for missed reminders

This SMS notification system provides a robust foundation for automated patient communication while maintaining reliability, compliance, and ease of use.
