# ------------------------------------------------------
# This module manages CRUD operations for Vendors.
# Vendors represent companies that receive RFPs and submit proposals.
# Provides endpoints to create, list, update, and delete vendor records.
# ------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import Vendor, VendorCreate, VendorUpdate
from database import Vendor as VendorModel

router = APIRouter()


@router.post("/", response_model=Vendor)
async def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    """Create a new vendor"""

    # Create vendor record from request schema
    db_vendor = VendorModel(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)

    return db_vendor


@router.get("/", response_model=List[Vendor])
async def list_vendors(db: Session = Depends(get_db)):
    """List all vendors"""

    # Retrieve all vendors from database
    return db.query(VendorModel).all()


@router.get("/{vendor_id}", response_model=Vendor)
async def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Get a specific vendor"""

    # Find vendor by primary key
    vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor


@router.put("/{vendor_id}", response_model=Vendor)
async def update_vendor(vendor_id: int, vendor_update: VendorUpdate, db: Session = Depends(get_db)):
    """Update a vendor"""

    # Ensure vendor exists before updating
    vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Apply only fields sent by the user (partial update)
    update_data = vendor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Delete a vendor"""

    # Attempt to find vendor before deleting
    vendor = db.query(VendorModel).filter(VendorModel.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    db.delete(vendor)
    db.commit()

    return {"message": "Vendor deleted successfully"}
