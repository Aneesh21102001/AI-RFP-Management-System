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
        # Use AI to parse natural language into structured RFP
        parsed_data = parse_natural_language_to_rfp(request.text)
        
        # Create RFP from parsed data
        rfp_data = RFPCreate(**parsed_data)
        db_rfp = RFPModel(**rfp_data.dict())
        db.add(db_rfp)
        db.commit()
        db.refresh(db_rfp)
        return db_rfp
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create RFP: {str(e)}")

@router.post("/", response_model=RFP)
async def create_rfp(rfp: RFPCreate, db: Session = Depends(get_db)):
    """Create an RFP manually"""
    db_rfp = RFPModel(**rfp.dict())
    db.add(db_rfp)
    db.commit()
    db.refresh(db_rfp)
    return db_rfp

@router.get("/", response_model=List[RFP])
async def list_rfps(db: Session = Depends(get_db)):
    """List all RFPs"""
    return db.query(RFPModel).order_by(RFPModel.created_at.desc()).all()

@router.get("/{rfp_id}", response_model=RFP)
async def get_rfp(rfp_id: int, db: Session = Depends(get_db)):
    """Get a specific RFP"""
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return rfp

@router.put("/{rfp_id}", response_model=RFP)
async def update_rfp(rfp_id: int, rfp_update: RFPUpdate, db: Session = Depends(get_db)):
    """Update an RFP"""
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    update_data = rfp_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rfp, field, value)
    
    db.commit()
    db.refresh(rfp)
    return rfp

@router.delete("/{rfp_id}")
async def delete_rfp(rfp_id: int, db: Session = Depends(get_db)):
    """Delete an RFP"""
    rfp = db.query(RFPModel).filter(RFPModel.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    db.delete(rfp)
    db.commit()
    return {"message": "RFP deleted successfully"}
