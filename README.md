# CourtMate Notification Service

Email notification service for court reservations, handling confirmation emails and automated reminders.

## Features

- 📧 **Confirmation Emails**: Automatically send confirmation emails when a reservation is created
- ⏰ **Reminder Emails**: Send automated reminders 2 hours before a reservation starts
- 🔄 **Background Scheduler**: Continuously checks for upcoming reservations every 10 minutes
- 📊 **Monitoring Endpoints**: View upcoming reminders and service health

## Architecture

The service consists of:
- **FastAPI Application**: RESTful API for sending notifications
- **Background Scheduler**: APScheduler for checking upcoming reservations
- **Email Service**: Resend integration for sending beautifully formatted emails
- **Supabase Integration**: Database access for reservation and user data

## Setup

### 1. Environment Variables

Copy `.example.env` to `.env` and fill in the required values:

```bash
cp .example.env .env
```

Required environment variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# Email Configuration (Resend)
RESEND_API_KEY=re_your_resend_api_key
FROM_EMAIL=notifications@yourdomain.com

# Service Configuration
ENV=dev
API_TITLE=Courtmate Notifications Service
API_VERSION=v1
```

### 2. Get Resend API Key

1. Sign up at [Resend.com](https://resend.com)
2. Verify your domain (or use the test domain for development)
3. Generate an API key from the dashboard
4. Add the API key to your `.env` file

### 3. Database Migration

Run the migration to add notification tracking fields to the reservations table:

```bash
cd ../Courtmate-Database
# Apply the migration using your Supabase CLI or dashboard
supabase db push
```

This adds:
- `confirmation_sent_at`: Tracks when confirmation email was sent
- `reminder_sent_at`: Tracks when reminder email was sent

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Service

#### Development
```bash
uvicorn app.main:app --reload --port 8003
```

#### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

#### Docker
```bash
docker-compose up --build
```

## API Endpoints

### Health Check
```http
GET /health
```

### Send Confirmation Email
```http
POST /api/v1/notifications/send-confirmation?reservation_id={uuid}
```

Send a confirmation email for a reservation. This should be called by the Booking Service immediately after creating a reservation.

**Response:**
```json
{
  "message": "Confirmation email sent successfully",
  "reservation_id": "uuid",
  "email": "user@example.com"
}
```

### Send Reminder Email
```http
POST /api/v1/notifications/send-reminder?reservation_id={uuid}
```

Manually send a reminder email for a reservation. (Normally handled automatically by the scheduler)

**Response:**
```json
{
  "message": "Reminder email sent successfully",
  "reservation_id": "uuid",
  "email": "user@example.com"
}
```

### Get Upcoming Reminders
```http
GET /api/v1/notifications/upcoming-reminders
```

View upcoming reservations that need reminders (for monitoring/debugging).

**Response:**
```json
{
  "window_start": "2025-11-15T10:00:00Z",
  "window_end": "2025-11-15T10:20:00Z",
  "count": 2,
  "reservations": [...]
}
```

## Integration with Booking Service

To integrate with the Booking Service, add this code after successfully creating a reservation:

```python
import httpx

async def create_reservation(...):
    # ... create reservation code ...
    
    # Send confirmation email
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://notification-service:8003/api/v1/notifications/send-confirmation",
                params={"reservation_id": str(reservation.id)}
            )
            response.raise_for_status()
            logger.info(f"Confirmation email sent for reservation {reservation.id}")
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        # Don't fail the reservation if email fails
    
    return reservation
```

## Email Templates

### Confirmation Email
- ✅ Reservation confirmation
- 📅 Date and time details
- 🏟️ Court information
- 💰 Total price
- 🔖 Reservation ID

### Reminder Email
- ⏰ 2-hour advance notice
- 📅 Reservation details
- 💡 Tips for arrival
- 🏟️ Court location

## Background Scheduler

The service automatically runs a background scheduler that:
- Checks for upcoming reservations every 10 minutes
- Sends reminder emails for reservations starting in 2 hours (±10 minutes)
- Only sends reminders for non-cancelled reservations
- Tracks which reservations have already received reminders

## Development

### Project Structure
```
app/
├── __init__.py
├── main.py              # FastAPI application
├── routes.py            # API endpoints
├── models.py            # Pydantic models
├── config.py            # Configuration
├── supabase_client.py   # Database client
├── email_service.py     # Email sending logic
└── scheduler.py         # Background job scheduler
```

### Testing

Test the endpoints using the Swagger UI:
```
http://localhost:8003/api/v1/notifications/docs
```

## Monitoring

- Check `/health` endpoint for service status
- Use `/api/v1/notifications/upcoming-reminders` to see pending reminders
- Monitor logs for email sending activity

## Error Handling

The service handles various error cases:
- Missing reservation
- Cancelled reservations
- Missing user email
- Email sending failures
- Database connection issues

All errors are logged and appropriate HTTP status codes are returned.

## Notes

- Reminder emails are only sent once per reservation
- The scheduler runs continuously while the service is running
- Email sending failures don't crash the service
- Uses UTC timestamps for all scheduling

## License

This service is part of the CourtMate application ecosystem.
