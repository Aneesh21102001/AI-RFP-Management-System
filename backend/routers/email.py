# ------------------------------------------------------
# This module handles sending RFPs to vendors via email
# and receiving/parsing vendor proposal responses using AI.
# It saves proposal data into the database after processing.
# ------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import SendRFPRequest, ReceiveEmailRequest, Proposal
from database import RFP as RFPModel, Vendor as VendorModel, Proposal as ProposalModel
from email_service import send_rfp_email
from ai_service import extract_proposal_details
import re

router = APIRouter()

@router.post("/send-rfp")
async def send_rfp(request: SendRFPRequest, db: Session = Depends(get_db)):
    """Send an RFP to selected vendors via email"""

    # Fetch the RFP from database
    rfp = db.query(RFPModel).filter(RFPModel.id == request.rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Fetch all vendors based on selected vendor IDs
    vendors = db.query(VendorModel).filter(VendorModel.id.in_(request.vendor_ids)).all()
    if len(vendors) != len(request.vendor_ids):
        raise HTTPException(status_code=404, detail="One or more vendors not found")
    
    # Prepare the RFP details that will be sent via email
    rfp_data = {
        "title": rfp.title,
        "description": rfp.description,
        "budget": rfp.budget,
        "delivery_days": rfp.delivery_days,
        "payment_terms": rfp.payment_terms,
        "warranty_required": rfp.warranty_required,
        "items": rfp.items or [],
        "requirements": rfp.requirements or []
    }
    
    # Loop through vendors and try sending RFP email to each
    results = []
    for vendor in vendors:
        try:
            await send_rfp_email(vendor.email, vendor.name, rfp_data)
            results.append({
                "vendor_id": vendor.id, 
                "vendor_name": vendor.name, 
                "status": "sent"
            })
        except Exception as e:
            # Capture failures per vendor (email issues, SMTP, etc.)
            results.append({
                "vendor_id": vendor.id, 
                "vendor_name": vendor.name, 
                "status": "failed", 
                "error": str(e)
            })
    
    # Update RFP status after attempting all emails
    rfp.status = "sent"
    db.commit()
    
    return {"message": "RFP sending completed", "results": results}


@router.post("/receive", response_model=Proposal)
async def receive_vendor_email(request: ReceiveEmailRequest, db: Session = Depends(get_db)):
    """Receive and parse a vendor email response"""

    # RFP ID can come directly or extracted from subject/body
    rfp_id = request.rfp_id
    
    if not rfp_id:
        # Try to extract RFP ID from email subject (e.g., "RFP #10")
        match = re.search(r'RFP[:\s#]*(\d+)', request.subject, re.IGNORECASE)
        if match:
            rfp_id = int(match.group(1))
        else:
            # No RFP ID provided and not found in subject — stop early
            raise HTTPException(
                status_code=400, 
                detail="RFP ID not found in email. Please specify rfp_id."
            )
    
    # Validate RFP exists
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Find vendor using sender's email address
    vendor = db.query(VendorModel).filter(VendorModel.email == request.from_email).first()
    if not vendor:
        raise HTTPException(
            status_code=404, 
            detail=f"Vendor with email {request.from_email} not found"
        )
    
    # Check if vendor already sent a proposal for this RFP
    existing_proposal = db.query(ProposalModel).filter(
        ProposalModel.rfp_id == rfp_id,
        ProposalModel.vendor_id == vendor.id
    ).first()
    
    # Prepare data so the AI model knows what the original RFP asked for
    rfp_data = {
        "title": rfp.title,
        "budget": rfp.budget,
        "delivery_days": rfp.delivery_days,
        "payment_terms": rfp.payment_terms,
        "warranty_required": rfp.warranty_required,
        "items": rfp.items or []
    }
    
    try:
        # Use AI to extract structured proposal details from vendor's email body
        extracted_data = extract_proposal_details(request.body, rfp_data)
        
        # Create a dictionary with fields to store/update in DB
        proposal_data = {
            "rfp_id": rfp_id,
            "vendor_id": vendor.id,
            "total_price": extracted_data.get("total_price"),
            "delivery_days": extracted_data.get("delivery_days"),
            "payment_terms": extracted_data.get("payment_terms"),
            "warranty": extracted_data.get("warranty"),
            "items": extracted_data.get("items"),
            "terms_conditions": extracted_data.get("terms_conditions"),
            "raw_response": request.body,
            "extracted_data": extracted_data,
            "completeness_score": extracted_data.get("completeness_score", 0)
        }
        
        if existing_proposal:
            # Update existing proposal (vendor replied again)
            for field, value in proposal_data.items():
                # Avoid overwriting identifiers
                if field not in ["rfp_id", "vendor_id"]:
                    setattr(existing_proposal, field, value)
            db.commit()
            db.refresh(existing_proposal)
            return existing_proposal
        
        else:
            # Create a brand-new proposal record
            db_proposal = ProposalModel(**proposal_data)
            db.add(db_proposal)
            db.commit()
            db.refresh(db_proposal)
            return db_proposal
            
    except Exception as e:
        # Any parsing/AI error is surfaced as a 500
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse email: {str(e)}"
        )
