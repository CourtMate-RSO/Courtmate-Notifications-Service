"""Email service for sending notifications using Brevo (formerly Sendinblue)"""
import brevo_python
from brevo_python.api.transactional_emails_api import TransactionalEmailsApi
from brevo_python.models.send_smtp_email import SendSmtpEmail
from brevo_python.rest import ApiException
from app.config import get_settings
from app.models import EmailConfirmation, EmailReminder
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Brevo API
configuration = brevo_python.Configuration()
configuration.api_key['api-key'] = settings.brevo_api_key
api_instance = TransactionalEmailsApi(brevo_python.ApiClient(configuration))


def format_datetime(dt: datetime) -> str:
    """Format datetime for display in emails"""
    return dt.strftime("%A, %B %d, %Y at %I:%M %p")


def format_time(dt: datetime) -> str:
    """Format time for display in emails"""
    return dt.strftime("%I:%M %p")


def send_confirmation_email(confirmation: EmailConfirmation) -> dict:
    """
    Send a reservation confirmation email
    
    Args:
        confirmation: EmailConfirmation object with reservation details
        
    Returns:
        dict: Response from Resend API
    """
    user_name = confirmation.user_name or "Valued Customer"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .detail-row {{
                margin: 15px 0;
                padding: 10px;
                background-color: white;
                border-left: 4px solid #4CAF50;
            }}
            .detail-label {{
                font-weight: bold;
                color: #555;
            }}
            .detail-value {{
                color: #333;
                margin-top: 5px;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                color: #777;
                font-size: 12px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                margin: 20px 0;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Reservation Confirmed!</h1>
            </div>
            <div class="content">
                <p>Dear {user_name},</p>
                <p>Your court reservation has been successfully confirmed. Here are your booking details:</p>
                
                <div class="detail-row">
                    <div class="detail-label">🏟️ Court</div>
                    <div class="detail-value">{confirmation.court_name}</div>
                </div>
                
                <div class="detail-row">
                    <div class="detail-label">📅 Date & Time</div>
                    <div class="detail-value">
                        {format_datetime(confirmation.starts_at)}<br>
                        to {format_time(confirmation.ends_at)}
                    </div>
                </div>
                
                <div class="detail-row">
                    <div class="detail-label">💰 Total Price</div>
                    <div class="detail-value">${confirmation.total_price:.2f}</div>
                </div>
                
                <div class="detail-row">
                    <div class="detail-label">🔖 Reservation ID</div>
                    <div class="detail-value">{confirmation.reservation_id}</div>
                </div>
                
                <p style="margin-top: 30px;">
                    <strong>Important:</strong> You will receive a reminder email 2 hours before your reservation time.
                </p>
                
                <p>If you need to cancel or modify your reservation, please contact us as soon as possible.</p>
                
                <p>We look forward to seeing you!</p>
            </div>
            <div class="footer">
                <p>This is an automated message from CourtMate. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        # Create Brevo email object
        send_smtp_email = SendSmtpEmail(
            to=[{"email": confirmation.to_email, "name": user_name}],
            sender={"email": settings.from_email, "name": settings.from_name},
            subject=f"Reservation Confirmed - {confirmation.court_name}",
            html_content=html_content
        )
        
        # Send email via Brevo
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Confirmation email sent to {confirmation.to_email} for reservation {confirmation.reservation_id}")
        logger.debug(f"Brevo response: {api_response}")
        
        return {"success": True, "message_id": api_response.message_id}
        
    except ApiException as e:
        logger.error(f"Brevo API error sending confirmation email: {e}")
        raise Exception(f"Failed to send confirmation email: {e}")
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        raise


def send_reminder_email(reminder: EmailReminder) -> dict:
    """
    Send a reservation reminder email
    
    Args:
        reminder: EmailReminder object with reservation details
        
    Returns:
        dict: Response from Resend API
    """
    user_name = reminder.user_name or "Valued Customer"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #FF9800;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .detail-row {{
                margin: 15px 0;
                padding: 10px;
                background-color: white;
                border-left: 4px solid #FF9800;
            }}
            .detail-label {{
                font-weight: bold;
                color: #555;
            }}
            .detail-value {{
                color: #333;
                margin-top: 5px;
            }}
            .warning-box {{
                background-color: #FFF3CD;
                border: 1px solid #FFE69C;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                color: #777;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⏰ Reminder: Your Reservation is Soon!</h1>
            </div>
            <div class="content">
                <p>Dear {user_name},</p>
                
                <div class="warning-box">
                    <strong>⚠️ Your court reservation is starting in 2 hours!</strong>
                </div>
                
                <p>Here are your booking details:</p>
                
                <div class="detail-row">
                    <div class="detail-label">🏟️ Court</div>
                    <div class="detail-value">{reminder.court_name}</div>
                </div>
                
                <div class="detail-row">
                    <div class="detail-label">📅 Date & Time</div>
                    <div class="detail-value">{format_datetime(reminder.starts_at)}</div>
                </div>
                
                <div class="detail-row">
                    <div class="detail-label">🔖 Reservation ID</div>
                    <div class="detail-value">{reminder.reservation_id}</div>
                </div>
                
                <p style="margin-top: 30px;">
                    <strong>Tips:</strong>
                </p>
                <ul>
                    <li>Please arrive at least 10 minutes early</li>
                    <li>Bring your reservation confirmation</li>
                    <li>Check weather conditions if playing outdoors</li>
                </ul>
                
                <p>See you soon!</p>
            </div>
            <div class="footer">
                <p>This is an automated reminder from CourtMate. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        # Create Brevo email object
        send_smtp_email = SendSmtpEmail(
            to=[{"email": reminder.to_email, "name": user_name}],
            sender={"email": settings.from_email, "name": settings.from_name},
            subject=f"Reminder: Your Court Reservation at {reminder.court_name} is in 2 Hours",
            html_content=html_content
        )
        
        # Send email via Brevo
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Reminder email sent to {reminder.to_email} for reservation {reminder.reservation_id}")
        logger.debug(f"Brevo response: {api_response}")
        
        return {"success": True, "message_id": api_response.message_id}
        
    except ApiException as e:
        logger.error(f"Brevo API error sending reminder email: {e}")
        raise Exception(f"Failed to send reminder email: {e}")
    except Exception as e:
        logger.error(f"Failed to send reminder email: {str(e)}")
        raise
