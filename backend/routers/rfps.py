# ------------------------------------------------------
# This module manages CRUD operations for RFPs and also
# supports generating RFPs from natural language using AI.
# It handles creating, reading, updating, deleting, and AI parsing.
# ------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import RFP, RFPCreate, RFPCreateFromText, RFPUpdate
from database import RFP as RFPModel
from ai_service import parse_natural_language_to_rfp

router = APIRouter()


@router.post("/from-text", response_model=RFP)
async def create_rfp_from_text(request: RFPCreateFromText, db: Session = Depends(get_db)):
    """Create an RFP from natural language input"""

    try:
        # Use AI to convert messy natural text into structured RFP fields
        parsed_data = parse_natural_language_to_rfp(request.text)
        
        # Convert parsed AI result into proper schema for DB insertion
        rfp_data = RFPCreate(**parsed_data)

        # Insert new RFP into database
        db_rfp = RFPModel(**rfp_data.dict())
        db.add(db_rfp)
        db.commit()
        db.refresh(db_rfp)
        return db_rfp

    except Exception as e:
        # Any parsing or validation error returns a user-friendly message
        raise HTTPException(status_code=400, detail=f"Failed to create RFP: {str(e)}")


@router.post("/", response_model=RFP)
async def create_rfp(rfp: RFPCreate, db: Session = Depends(get_db)):
    """Create an RFP manually"""

    # Directly store the provided structured RFP data
    db_rfp = RFPModel(**rfp.dict())
    db.add(db_rfp)
    db.commit()
    db.refresh(db_rfp)
    return db_rfp


@router.get("/", response_model=List[RFP])
async def list_rfps(db: Session = Depends(get_db)):
    """List all RFPs"""

    # Get all RFPs sorted by newest first
    return db.query(RFPModel).order_by(RFPModel.created_at.desc()).all()


@router.get("/{rfp_id}", response_model=RFP)
async def get_rfp(rfp_id: int, db: Session = Depends(get_db)):
    """Get a specific RFP"""

    # Fetch RFP by ID
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    return rfp


@router.put("/{rfp_id}", response_model=RFP)
async def update_rfp(rfp_id: int, rfp_update: RFPUpdate, db: Session = Depends(get_db)):
    """Update an RFP"""

    # Ensure RFP exists
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Update only fields provided in the request
    update_data = rfp_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rfp, field, value)
    
    db.commit()
    db.refresh(rfp)
    return rfp


@router.delete("/{rfp_id}")
async def delete_rfp(rfp_id: int, db: Session = Depends(get_db)):
    """Delete an RFP"""

    # Check whether RFP exists
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Remove the RFP from the database
    db.delete(rfp)
    db.commit()

    return {"message": "RFP deleted successfully"}
