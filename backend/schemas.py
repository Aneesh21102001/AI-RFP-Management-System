from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Vendor Schemas
class VendorBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    notes: Optional[str] = None

class Vendor(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# RFP Schemas
class RFPBase(BaseModel):
    title: str
    description: Optional[str] = None
    budget: Optional[float] = None
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty_required: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    requirements: Optional[List[str]] = None

class RFPCreate(RFPBase):
    pass

class RFPCreateFromText(BaseModel):
    text: str  # Natural language input

class RFPUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty_required: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    requirements: Optional[List[str]] = None
    status: Optional[str] = None

class RFP(RFPBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Proposal Schemas
class ProposalBase(BaseModel):
    rfp_id: int
    vendor_id: int
    total_price: Optional[float] = None
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    terms_conditions: Optional[str] = None

class ProposalCreate(ProposalBase):
    raw_response: Optional[str] = None

class ProposalUpdate(BaseModel):
    total_price: Optional[float] = None
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    terms_conditions: Optional[str] = None

class Proposal(ProposalBase):
    id: int
    raw_response: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    completeness_score: Optional[float] = None
    received_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProposalWithVendor(Proposal):
    vendor: Vendor
    
    class Config:
        from_attributes = True

# Email Schemas
class SendRFPRequest(BaseModel):
    rfp_id: int
    vendor_ids: List[int]

class ReceiveEmailRequest(BaseModel):
    from_email: str
    subject: str
    body: str
    rfp_id: Optional[int] = None  # If known from subject/body

# Comparison Schemas
class VendorComparison(BaseModel):
    vendor_name: str
    score: float
    strengths: List[str]
    weaknesses: List[str]
    price_rank: int
    delivery_rank: int

class Recommendation(BaseModel):
    recommended_vendor: str
    reason: str
    summary: str

class ComparisonResult(BaseModel):
    comparison: List[VendorComparison]
    recommendation: Recommendation
