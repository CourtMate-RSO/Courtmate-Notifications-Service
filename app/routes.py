"""API routes for the Notification Service"""
from fastapi import APIRouter, HTTPException, status, Header, Depends
from fastapi.responses import JSONResponse
from app.models import (
    NotificationRequest,
    EmailConfirmation,
    EmailReminder,
    Reservation,
)
from typing import List, Optional
from uuid import UUID
from app.supabase_client import admin_supabase_client
from app.email_service import send_confirmation_email, send_reminder_email
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notifications"])

# Service-to-service authentication
def verify_service_key(x_service_key: Optional[str] = Header(None)):
    """
    Verify that requests come from authorized services only.
    This prevents unauthorized external calls to the notification endpoints.
    """
    expected_key = os.getenv("INTERNAL_SERVICE_KEY")
    
    if not expected_key:
        logger.warning("INTERNAL_SERVICE_KEY not set - service authentication disabled")
        return True
    
    if not x_service_key or x_service_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing service authentication key"
        )
    return True

@router.post("/send-confirmation", status_code=status.HTTP_200_OK)
async def send_reservation_confirmation(
    reservation_id: UUID,
    authorized: bool = Depends(verify_service_key)
):
    """
    Send a confirmation email for a reservation.
    This endpoint should be called by the booking service after creating a reservation.
    
    Requires: X-Service-Key header for authentication
    
    Args:
        reservation_id: UUID of the reservation
        
    Returns:
        dict: Success message
    """
    try:
        # Get reservation details from database using admin client
        # This is appropriate because:
        # 1. Called by booking service (no user token)
        # 2. Needs to access reservation regardless of user
        supabase = admin_supabase_client()
        
        response = supabase.table("reservations") \
            .select("*, courts(name, location, price_per_hour), users:user_id(email, full_name)") \
            .eq("id", str(reservation_id)) \
            .execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found"
            )
        
        reservation = response.data[0]
        
        # Check if already cancelled
        if reservation.get("cancelled_at"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send confirmation for cancelled reservation"
            )
        
        # Extract details
        user_email = reservation.get("users", {}).get("email")
        user_name = reservation.get("users", {}).get("full_name")
        court_name = reservation.get("courts", {}).get("name", "Court")
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found"
            )
        
        # Create confirmation email object
        confirmation = EmailConfirmation(
            to_email=user_email,
            reservation_id=reservation["id"],
            court_name=court_name,
            starts_at=datetime.fromisoformat(reservation["starts_at"].replace("Z", "+00:00")),
            ends_at=datetime.fromisoformat(reservation["ends_at"].replace("Z", "+00:00")),
            total_price=reservation["total_price"],
            user_name=user_name
        )
        
        # Send email
        email_response = send_confirmation_email(confirmation)
        
        # Update reservation to mark confirmation sent
        supabase.table("reservations") \
            .update({"confirmation_sent_at": datetime.utcnow().isoformat()}) \
            .eq("id", str(reservation_id)) \
            .execute()
        
        logger.info(f"Confirmation email sent for reservation {reservation_id}")
        
        return {
            "message": "Confirmation email sent successfully",
            "reservation_id": reservation_id,
            "email": user_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send confirmation email: {str(e)}"
        )


@router.post("/send-reminder", status_code=status.HTTP_200_OK)
async def send_reservation_reminder(
    reservation_id: UUID,
    authorized: bool = Depends(verify_service_key)
):
    """
    Manually send a reminder email for a reservation.
    This is typically called by the scheduler, but can be triggered manually.
    
    Requires: X-Service-Key header for authentication
    
    Args:
        reservation_id: UUID of the reservation
        
    Returns:
        dict: Success message
    """
    try:
        # Using admin client is correct here - scheduler/manual trigger
        supabase = admin_supabase_client()
        
        response = supabase.table("reservations") \
            .select("*, courts(name), users:user_id(email, full_name)") \
            .eq("id", str(reservation_id)) \
            .execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found"
            )
        
        reservation = response.data[0]
        
        # Check if already cancelled
        if reservation.get("cancelled_at"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send reminder for cancelled reservation"
            )
        
        # Extract details
        user_email = reservation.get("users", {}).get("email")
        user_name = reservation.get("users", {}).get("full_name")
        court_name = reservation.get("courts", {}).get("name", "Court")
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found"
            )
        
        # Create reminder email object
        reminder = EmailReminder(
            to_email=user_email,
            reservation_id=reservation["id"],
            court_name=court_name,
            starts_at=datetime.fromisoformat(reservation["starts_at"].replace("Z", "+00:00")),
            user_name=user_name
        )
        
        # Send email
        email_response = send_reminder_email(reminder)
        
        # Update reservation to mark reminder sent
        supabase.table("reservations") \
            .update({"reminder_sent_at": datetime.utcnow().isoformat()}) \
            .eq("id", str(reservation_id)) \
            .execute()
        
        logger.info(f"Reminder email sent for reservation {reservation_id}")
        
        return {
            "message": "Reminder email sent successfully",
            "reservation_id": reservation_id,
            "email": user_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending reminder email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send reminder email: {str(e)}"
        )


@router.get("/upcoming-reminders", status_code=status.HTTP_200_OK)
async def get_upcoming_reminders(authorized: bool = Depends(verify_service_key)):
    """
    Get list of upcoming reservations that need reminders (for debugging/monitoring).
    
    Requires: X-Service-Key header for authentication
    
    Returns:
        dict: List of reservations needing reminders
    """
    try:
        from datetime import timedelta
        
        # Using admin client is correct - system monitoring endpoint
        supabase = admin_supabase_client()
        
        # Get current time and 2 hours from now
        now = datetime.utcnow()
        target_time = now + timedelta(hours=2)
        window_start = target_time - timedelta(minutes=10)
        window_end = target_time + timedelta(minutes=10)
        
        # Query reservations
        response = supabase.table("reservations") \
            .select("id, starts_at, reminder_sent_at, courts(name), users:user_id(email)") \
            .gte("starts_at", window_start.isoformat()) \
            .lte("starts_at", window_end.isoformat()) \
            .is_("cancelled_at", "null") \
            .is_("reminder_sent_at", "null") \
            .execute()
        
        reservations = response.data
        
        return {
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "count": len(reservations),
            "reservations": reservations
        }
        
    except Exception as e:
        logger.error(f"Error getting upcoming reminders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming reminders: {str(e)}"
        )