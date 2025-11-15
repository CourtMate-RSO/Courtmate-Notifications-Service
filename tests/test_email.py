#!/usr/bin/env python3
"""
Test script for Brevo email configuration
Run this to verify your email setup is working before testing the full service
"""
import os
from dotenv import load_dotenv
import brevo_python
from brevo_python.api.transactional_emails_api import TransactionalEmailsApi
from brevo_python.models.send_smtp_email import SendSmtpEmail
from brevo_python.rest import ApiException

# Load environment variables
load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@courtmate.com")
FROM_NAME = os.getenv("FROM_NAME", "CourtMate")

def test_brevo_connection():
    """Test Brevo API connection and send a test email"""
    
    if not BREVO_API_KEY:
        print("❌ ERROR: BREVO_API_KEY not found in .env file")
        print("Please add your Brevo API key to the .env file")
        return False
    
    print("=" * 60)
    print("🧪 Testing Brevo Email Configuration")
    print("=" * 60)
    print(f"API Key: {BREVO_API_KEY[:20]}..." if len(BREVO_API_KEY) > 20 else "Invalid API Key")
    print(f"From Email: {FROM_EMAIL}")
    print(f"From Name: {FROM_NAME}")
    print()
    
    # Get test recipient email
    to_email = input("Enter your email address to receive test email: ").strip()
    
    if not to_email or "@" not in to_email:
        print("❌ Invalid email address")
        return False
    
    try:
        # Configure Brevo API
        configuration = brevo_python.Configuration()
        configuration.api_key['api-key'] = BREVO_API_KEY
        api_instance = TransactionalEmailsApi(brevo_python.ApiClient(configuration))
        
        # Create test email (using f-string instead of .format() to avoid CSS conflicts)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .success {{ color: #4CAF50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Test Email</h1>
                </div>
                <div class="content">
                    <h2 class="success">Brevo Integration Working!</h2>
                    <p>If you're reading this, your CourtMate Notification Service is correctly configured with Brevo.</p>
                    <p><strong>Configuration Details:</strong></p>
                    <ul>
                        <li>From: {FROM_NAME} &lt;{FROM_EMAIL}&gt;</li>
                        <li>API: Brevo (formerly Sendinblue)</li>
                        <li>Status: ✅ Active</li>
                    </ul>
                    <p>You're now ready to send confirmation and reminder emails!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_smtp_email = SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"email": FROM_EMAIL, "name": FROM_NAME},
            subject="🧪 CourtMate Test Email - Brevo Integration",
            html_content=html_content
        )
        
        print(f"📧 Sending test email to {to_email}...")
        print()
        
        # Send email
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        print("=" * 60)
        print("✅ SUCCESS! Email sent successfully!")
        print("=" * 60)
        print(f"Message ID: {api_response.message_id}")
        print()
        print("📬 Check your inbox (and spam folder) for the test email")
        print()
        print("Next steps:")
        print("1. ✅ Email configuration working")
        print("2. Start the notification service: uvicorn app.main:app --reload --port 8003")
        print("3. Test with a real reservation")
        print("=" * 60)
        
        return True
        
    except ApiException as e:
        print("=" * 60)
        print("❌ ERROR: Brevo API Error")
        print("=" * 60)
        print(f"Status: {e.status}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.body}")
        print()
        print("Common issues:")
        print("1. Invalid API key - Check your BREVO_API_KEY in .env")
        print("2. Sender not verified - Verify FROM_EMAIL in Brevo dashboard")
        print("3. Daily limit reached - Free tier has 300 emails/day limit")
        print()
        return False
        
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR: Unexpected Error")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        return False


if __name__ == "__main__":
    success = test_brevo_connection()
    exit(0 if success else 1)
