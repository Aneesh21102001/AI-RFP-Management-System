# ------------------------------------------------------
# This module initializes the database connection, ORM models,
# and session handling using SQLAlchemy. Defines Vendor, RFP,
# and Proposal tables with relationships between them.
# ------------------------------------------------------

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Load database URL (fallback to local SQLite database)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rfp_management.db")

# Create SQLAlchemy engine; special handling for SQLite threading
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory for DB operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# =======================
# Vendor Table
# =======================
class Vendor(Base):
    __tablename__ = "vendors"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic vendor information
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    contact_person = Column(String)

    # Optional notes (e.g., history, preferences)
    notes = Column(Text)

    # Timestamps for auditing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: one vendor → many proposals
    proposals = relationship("Proposal", back_populates="vendor")


# =======================
# RFP Table
# =======================
class RFP(Base):
    __tablename__ = "rfps"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Core RFP details
    title = Column(String, nullable=False)
    description = Column(Text)
    budget = Column(Float)
    delivery_days = Column(Integer)
    payment_terms = Column(String)
    warranty_required = Column(String)

    # JSON fields for item details and additional requirements
    items = Column(JSON)         # List of item objects
    requirements = Column(JSON)  # Additional constraints/conditions

    # Status of RFP: draft, sent, closed
    status = Column(String, default="draft")

    # Record timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: one RFP → many proposals
    proposals = relationship("Proposal", back_populates="rfp")


# =======================
# Proposal Table
# =======================
class Proposal(Base):
    __tablename__ = "proposals"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys linking proposal to an RFP and a Vendor
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    # Proposal details extracted from email or manually entered
    total_price = Column(Float)
    delivery_days = Column(Integer)
    payment_terms = Column(String)
    warranty = Column(String)

    # Detailed pricing breakdown and item data
    items = Column(JSON)

    # Additional content extracted from emails
    terms_conditions = Column(Text)
    raw_response = Column(Text)   # Entire email body
    extracted_data = Column(JSON) # AI-parsed structured content

    # A completeness score to evaluate how well vendor responded
    completeness_score = Column(Float)

    # Timestamps for lifecycle tracking
    received_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to RFP and Vendor
    rfp = relationship("RFP", back_populates="proposals")
    vendor = relationship("Vendor", back_populates="proposals")


# =======================
# Dependency for DB session (FastAPI-compatible)
# =======================
def get_db():
    """
    Creates a new DB session for each request and ensures it is closed afterward.
    Used as a FastAPI dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
