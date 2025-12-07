from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rfp_management.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    contact_person = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    proposals = relationship("Proposal", back_populates="vendor")

class RFP(Base):
    __tablename__ = "rfps"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    budget = Column(Float)
    delivery_days = Column(Integer)
    payment_terms = Column(String)
    warranty_required = Column(String)
    items = Column(JSON)  # List of items with specifications
    requirements = Column(JSON)  # Additional requirements
    status = Column(String, default="draft")  # draft, sent, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    proposals = relationship("Proposal", back_populates="rfp")

class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    
    total_price = Column(Float)
    delivery_days = Column(Integer)
    payment_terms = Column(String)
    warranty = Column(String)
    items = Column(JSON)  # Extracted item prices and details
    terms_conditions = Column(Text)
    raw_response = Column(Text)  # Original email content
    extracted_data = Column(JSON)  # AI-extracted structured data
    completeness_score = Column(Float)  # 0-1 score of how complete the response is
    received_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rfp = relationship("RFP", back_populates="proposals")
    vendor = relationship("Vendor", back_populates="proposals")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
