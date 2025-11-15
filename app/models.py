from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class NotificationRequest(BaseModel):
    """Request to send a notification"""
    reservation_id: UUID
    user_email: EmailStr
    notification_type: str  # "confirmation" or "reminder"

class Reservation(BaseModel):
    """Reservation model from database"""
    id: UUID
    court_id: UUID
    user_id: UUID
    starts_at: datetime
    ends_at: datetime
    total_price: float
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None

class Court(BaseModel):
    """Court model from database"""
    id: UUID
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    price_per_hour: float
    
class User(BaseModel):
    """User model from database"""
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None

class EmailConfirmation(BaseModel):
    """Confirmation email details"""
    to_email: EmailStr
    reservation_id: UUID
    court_name: str
    starts_at: datetime
    ends_at: datetime
    total_price: float
    user_name: Optional[str] = None

class EmailReminder(BaseModel):
    """Reminder email details"""
    to_email: EmailStr
    reservation_id: UUID
    court_name: str
    starts_at: datetime
    user_name: Optional[str] = None