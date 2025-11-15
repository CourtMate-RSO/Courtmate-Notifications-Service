# CourtMate Notification Service

Email notification service for court reservations, handling confirmation emails and automated reminders.

## Features

- 📧 **Confirmation Emails**: Automatically send confirmation emails when a reservation is created
- ⏰ **Reminder Emails**: Send automated reminders 2 hours before a reservation starts
- 🔄 **Background Scheduler**: Continuously checks for upcoming reservations every 10 minutes
- 📊 **Monitoring Endpoints**: View upcoming reminders and service health

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
