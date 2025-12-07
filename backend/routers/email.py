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
    rfp = db.query(RFPModel).filter(RFPModel.id == request.rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Get vendors
    vendors = db.query(VendorModel).filter(VendorModel.id.in_(request.vendor_ids)).all()
    if len(vendors) != len(request.vendor_ids):
        raise HTTPException(status_code=404, detail="One or more vendors not found")
    
    # Prepare RFP data
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
    
    # Send emails
    results = []
    for vendor in vendors:
        try:
            await send_rfp_email(vendor.email, vendor.name, rfp_data)
            results.append({"vendor_id": vendor.id, "vendor_name": vendor.name, "status": "sent"})
        except Exception as e:
            results.append({"vendor_id": vendor.id, "vendor_name": vendor.name, "status": "failed", "error": str(e)})
    
    # Update RFP status
    rfp.status = "sent"
    db.commit()
    
    return {"message": "RFP sending completed", "results": results}

@router.post("/receive", response_model=Proposal)
async def receive_vendor_email(request: ReceiveEmailRequest, db: Session = Depends(get_db)):
    """Receive and parse a vendor email response"""
    # Try to find RFP ID from subject or body if not provided
    rfp_id = request.rfp_id
    
    if not rfp_id:
        # Try to extract RFP ID from subject (e.g., "Re: Request for Proposal: RFP #123")
        match = re.search(r'RFP[:\s#]*(\d+)', request.subject, re.IGNORECASE)
        if match:
            rfp_id = int(match.group(1))
        else:
            # Try to find by matching vendor email to recent RFPs
            # This is a simplified approach - in production, you'd want better matching
            raise HTTPException(status_code=400, detail="RFP ID not found in email. Please specify rfp_id.")
    
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Find vendor by email
    vendor = db.query(VendorModel).filter(VendorModel.email == request.from_email).first()
    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor with email {request.from_email} not found")
    
    # Check if proposal already exists
    existing_proposal = db.query(ProposalModel).filter(
        ProposalModel.rfp_id == rfp_id,
        ProposalModel.vendor_id == vendor.id
    ).first()
    
    # Prepare RFP data for AI extraction
    rfp_data = {
        "title": rfp.title,
        "budget": rfp.budget,
        "delivery_days": rfp.delivery_days,
        "payment_terms": rfp.payment_terms,
        "warranty_required": rfp.warranty_required,
        "items": rfp.items or []
    }
    
    # Use AI to extract proposal details
    try:
        extracted_data = extract_proposal_details(request.body, rfp_data)
        
        # Create or update proposal
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
            # Update existing proposal
            for field, value in proposal_data.items():
                if field not in ["rfp_id", "vendor_id"]:
                    setattr(existing_proposal, field, value)
            db.commit()
            db.refresh(existing_proposal)
            return existing_proposal
        else:
            # Create new proposal
            db_proposal = ProposalModel(**proposal_data)
            db.add(db_proposal)
            db.commit()
            db.refresh(db_proposal)
            return db_proposal
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse email: {str(e)}")
