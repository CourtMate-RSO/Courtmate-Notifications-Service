"""Background scheduler for checking upcoming reservations and sending reminders"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from app.supabase_client import admin_supabase_client
from app.email_service import send_reminder_email
from app.models import EmailReminder
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_upcoming_reservations():
    """
    Check for reservations starting in approximately 2 hours and send reminder emails.
    This function runs every 10 minutes.
    """
    try:
        logger.info("Checking for upcoming reservations...")
        
        # Get current time and time window (2 hours from now +/- 10 minutes)
        now = datetime.utcnow()
        target_time = now + timedelta(hours=2)
        window_start = target_time - timedelta(minutes=10)
        window_end = target_time + timedelta(minutes=10)
        
        # Get admin client (bypasses RLS)
        supabase = admin_supabase_client()
        
        # Query reservations starting in 2 hours
        # Only get reservations that haven't been cancelled and haven't been reminded yet
        response = supabase.table("reservations") \
            .select("*, courts(name), users:user_id(email, full_name)") \
            .gte("starts_at", window_start.isoformat()) \
            .lte("starts_at", window_end.isoformat()) \
            .is_("cancelled_at", "null") \
            .is_("reminder_sent_at", "null") \
            .execute()
        
        reservations = response.data
        
        if not reservations:
            logger.info(f"No upcoming reservations found in window {window_start} to {window_end}")
            return
        
        logger.info(f"Found {len(reservations)} upcoming reservations to remind")
        
        # Send reminder emails
        for reservation in reservations:
            try:
                # Extract user and court info
                user_email = reservation.get("users", {}).get("email")
                user_name = reservation.get("users", {}).get("full_name")
                court_name = reservation.get("courts", {}).get("name", "Court")
                
                if not user_email:
                    logger.warning(f"No email found for reservation {reservation['id']}")
                    continue
                
                # Create reminder object
                reminder = EmailReminder(
                    to_email=user_email,
                    reservation_id=reservation["id"],
                    court_name=court_name,
                    starts_at=datetime.fromisoformat(reservation["starts_at"].replace("Z", "+00:00")),
                    user_name=user_name
                )
                
                # Send reminder email
                send_reminder_email(reminder)
                
                # Update reservation to mark that reminder was sent
                supabase.table("reservations") \
                    .update({"reminder_sent_at": now.isoformat()}) \
                    .eq("id", reservation["id"]) \
                    .execute()
                
                logger.info(f"Reminder sent for reservation {reservation['id']}")
                
            except Exception as e:
                logger.error(f"Failed to send reminder for reservation {reservation['id']}: {str(e)}")
                continue
        
        logger.info(f"Completed checking upcoming reservations. Sent {len(reservations)} reminders.")
        
    except Exception as e:
        logger.error(f"Error in check_upcoming_reservations: {str(e)}")


def start_scheduler():
    """Start the background scheduler"""
    # Check for upcoming reservations every 10 minutes
    scheduler.add_job(
        check_upcoming_reservations,
        'interval',
        minutes=10,
        id='check_upcoming_reservations',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started. Will check for upcoming reservations every 10 minutes.")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown.")
