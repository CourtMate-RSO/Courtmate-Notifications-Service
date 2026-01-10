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
GET /api/notifications/health
```

### Send Notification
```http
POST /api/notifications/send
```

Send an email notification (internal use). The endpoint expects a JSON body with the notification details. Example request body:

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "booking_confirmation",
  "email": "user@example.com",
  "data": {
    "reservation_id": "123e4567-e89b-12d3-a456-426614174000",
    "start_time": "2026-01-15T14:00:00Z"
  }
}
```

**Response:**
```json
{
  "message": "Notification sent"
}
```

Note: the OpenAPI specification exposes only `/api/notifications/health` and `/api/notifications/send`; previously documented v1-style endpoints (e.g. `/api/v1/notifications/send-confirmation`) have been consolidated into this single `/api/notifications/send` endpoint that accepts a `type` field to distinguish confirmation, cancellation or reminder emails. The background scheduler and any monitoring endpoints may still exist locally but are not part of the public OpenAPI contract.

# Deployment to AKS (Azure Kubernetes Service)

## Prerequisites
- AKS cluster (testCluster, resource group RSO)
- Azure Container Registry (courtmateacr.azurecr.io)
- Supabase credentials stored as Kubernetes secret `supabase-secrets`
- Helm installed locally
- Docker installed locally


## Ingress Path
- `/api/notifications(/|$)(.*)` (rewrites to service root)

## Health Endpoint
- `/health` (used for readiness/liveness probes)
