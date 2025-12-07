# ------------------------------------------------------
# This module manages CRUD operations for proposals and
# provides AI-powered comparison of proposals for an RFP.
# Used after vendor responses are parsed or manually added.
# ------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import Proposal, ProposalCreate, ProposalUpdate, ProposalWithVendor, ComparisonResult
from database import Proposal as ProposalModel, RFP as RFPModel, Vendor as VendorModel
from ai_service import compare_proposals_and_recommend

router = APIRouter()

@router.post("/", response_model=Proposal)
async def create_proposal(proposal: ProposalCreate, db: Session = Depends(get_db)):
    """Create a proposal (usually from email parsing)"""

    # Ensure the referenced RFP exists
    rfp = db.query(RFPModel).filter(RFPModel.id == proposal.rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Ensure the vendor exists
    vendor = db.query(VendorModel).filter(VendorModel.id == proposal.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Create the proposal record
    db_proposal = ProposalModel(**proposal.dict())
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal


@router.get("/", response_model=List[ProposalWithVendor])
async def list_proposals(rfp_id: int = None, db: Session = Depends(get_db)):
    """List all proposals, optionally filtered by RFP"""

    # Begin querying proposals
    query = db.query(ProposalModel)

    # If rfp_id is provided, filter by RFP
    if rfp_id:
        query = query.filter(ProposalModel.rfp_id == rfp_id)

    return query.all()


@router.get("/{proposal_id}", response_model=ProposalWithVendor)
async def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    """Get a specific proposal"""

    # Fetch the proposal by ID
    proposal = db.query(ProposalModel).filter(ProposalModel.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    return proposal


@router.put("/{proposal_id}", response_model=Proposal)
async def update_proposal(proposal_id: int, proposal_update: ProposalUpdate, db: Session = Depends(get_db)):
    """Update a proposal"""

    # Fetch the proposal
    proposal = db.query(ProposalModel).filter(ProposalModel.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Only update fields provided by the client
    update_data = proposal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(proposal, field, value)
    
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("/rfp/{rfp_id}/compare", response_model=ComparisonResult)
async def compare_proposals(rfp_id: int, db: Session = Depends(get_db)):
    """Compare proposals for a given RFP and get AI recommendations"""

    # Validate RFP exists
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Fetch all proposals for this RFP
    proposals = db.query(ProposalModel).filter(ProposalModel.rfp_id == rfp_id).all()
    if not proposals:
        raise HTTPException(status_code=404, detail="No proposals found for this RFP")
    
    # Build structured data the AI model can compare
    proposals_data = []
    for prop in proposals:
        vendor = db.query(VendorModel).filter(VendorModel.id == prop.vendor_id).first()
        proposals_data.append({
            "vendor_name": vendor.name if vendor else "Unknown",
            "total_price": prop.total_price,
            "delivery_days": prop.delivery_days,
            "payment_terms": prop.payment_terms,
            "warranty": prop.warranty,
            "completeness_score": prop.completeness_score or 0,
            "items": prop.items or []
        })
    
    # Prepare RFP data for context
    rfp_data = {
        "title": rfp.title,
        "budget": rfp.budget,
        "delivery_days": rfp.delivery_days,
        "payment_terms": rfp.payment_terms,
        "warranty_required": rfp.warranty_required,
        "items": rfp.items or []
    }
    
    # Use AI to compare proposals and recommend the best option
    try:
        comparison_result = compare_proposals_and_recommend(rfp_data, proposals_data)
        return comparison_result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to compare proposals: {str(e)}"
        )
