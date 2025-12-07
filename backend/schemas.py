# ------------------------------------------------------
# This module defines all Pydantic schemas used for validation,
# serialization, and responses in the RFP Management API.
# Includes Vendor, RFP, Proposal, Email, and AI comparison schemas.
# ------------------------------------------------------

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ======================================================
# Vendor Schemas
# ======================================================

class VendorBase(BaseModel):
    """
    Base vendor attributes shared across create, update, and response schemas.
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    notes: Optional[str] = None


class VendorCreate(VendorBase):
    """
    Schema for creating a vendor.
    Inherits all required fields from VendorBase.
    """
    pass


class VendorUpdate(BaseModel):
    """
    Schema for updating vendor details.
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    notes: Optional[str] = None


class Vendor(VendorBase):
    """
    Schema returned in GET responses for Vendor.
    Includes database-generated fields.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows reading ORM models


# ======================================================
# RFP Schemas
# ======================================================

class RFPBase(BaseModel):
    """
    Base schema for all RFP operations.
    Defines core fields used in creation, update, and responses.
    """
    title: str
    description: Optional[str] = None
    budget: Optional[float] = None
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty_required: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    requirements: Optional[List[str]] = None


class RFPCreate(RFPBase):
    """
    Schema for manually creating an RFP.
    """
    pass


class RFPCreateFromText(BaseModel):
    """
    Schema used when creating an RFP from natural-language input.
    This is sent to the AI service.
    """
    text: str


class RFPUpdate(BaseModel):
    """
    Schema for updating RFP details.
    All fields optional for partial updates.
    """
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
    """
    Schema used for returning full RFP details from API.
    Includes timestamps and status.
    """
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======================================================
# Proposal Schemas
# ======================================================

class ProposalBase(BaseModel):
    """
    Shared fields for proposal creation and response models.
    Includes pricing, terms, and item details.
    """
    rfp_id: int
    vendor_id: int
    total_price: Optional[float] = None
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    terms_conditions: Optional[str] = None


class ProposalCreate(ProposalBase):
    """
    Used when creating a proposal, usually after parsing an email.
    raw_response stores full email body.
    """
    raw_response: Optional[str] = None


class ProposalUpdate(BaseModel):
    """
    Schema for updating proposal data.
    Allows partial updates.
    """
    total_price: Optional[float] = None
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    warranty: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    terms_conditions: Optional[str] = None


class Proposal(ProposalBase):
    """
    Full proposal returned by the API, includes:
    - AI extracted data
    - completeness score
    - timestamps
    """
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
    """
    Proposal response with vendor details embedded.
    Useful when listing proposals for comparison.
    """
    vendor: Vendor

    class Config:
        from_attributes = True


# ======================================================
# Email Request Schemas
# ======================================================

class SendRFPRequest(BaseModel):
    """
    Schema used when sending an RFP to selected vendors.
    """
    rfp_id: int
    vendor_ids: List[int]


class ReceiveEmailRequest(BaseModel):
    """
    Schema used when receiving a vendor's proposal email.
    rfp_id is optional and can be extracted from subject/body.
    """
    from_email: str
    subject: str
    body: str
    rfp_id: Optional[int] = None


# ======================================================
# AI Comparison Schemas
# ======================================================

class VendorComparison(BaseModel):
    """
    Represents per-vendor comparison metrics generated by AI.
    Includes ranking and strengths/weaknesses.
    """
    vendor_name: str
    score: float
    strengths: List[str]
    weaknesses: List[str]
    price_rank: int
    delivery_rank: int


class Recommendation(BaseModel):
    """
    AI-generated supplier recommendation with reasoning.
    """
    recommended_vendor: str
    reason: str
    summary: str


class ComparisonResult(BaseModel):
    """
    Full result of comparing proposals, including:
    - detailed vendor comparisons
    - final recommendation object
    """
    comparison: List[VendorComparison]
    recommendation: Recommendation
