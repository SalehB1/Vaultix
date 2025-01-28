from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class EmailContent(BaseModel):
    subject: str
    recipients: List[EmailStr]
    body: Optional[str] = None
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    sender_email: Optional[EmailStr] = None  # New field for sender email
    sender_name: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[str]] = None



class EmailStatus(BaseModel):
    success: bool
    message: str
    status_code: int
    error: Optional[str] = None
