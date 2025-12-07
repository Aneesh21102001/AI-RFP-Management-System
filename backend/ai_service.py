# ------------------------------------------------------
# This module handles all AI-related logic for the system.
# It uses OpenAI models to parse natural text into RFPs,
# extract structured proposal data, and compare proposals.
# ------------------------------------------------------

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client using API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def parse_natural_language_to_rfp(user_input: str) -> dict:
    """
    Convert a natural language RFP description into a fully structured RFP.
    Used when users describe their requirements in plain English.
    """

    # Prompt instructs model to extract all RFP fields in strict JSON format
    prompt = f"""You are an AI assistant that helps convert procurement requests into structured RFPs.

User request: {user_input}

Extract the following information and return it as a JSON object:
- title
- description
- budget
- delivery_days
- payment_terms
- warranty_required
- items (array with name, quantity, specifications)
- requirements (array)

Return ONLY valid JSON, no additional text."""

    try:
        # Send structured extraction request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract structured data and always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Get raw content returned by the model
        content = response.choices[0].message.content.strip()

        # Clean possible JSON code block wrappers
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        # Convert clean JSON string to Python dict
        return json.loads(content)

    except Exception as e:
        # Wrap any failure as a readable exception
        raise Exception(f"Failed to parse RFP: {str(e)}")


def extract_proposal_details(email_content: str, rfp_data: dict) -> dict:
    """
    Extract structured proposal information from a vendor's email.
    Uses AI to understand pricing, delivery, warranty, item details, etc.
    """

    # Build a summary of RFP requirements to give AI context
    rfp_summary = f"""
RFP Title: {rfp_data.get('title', 'N/A')}
Budget: {rfp_data.get('budget', 'N/A')}
Delivery Required: {rfp_data.get('delivery_days', 'N/A')} days
Payment Terms Required: {rfp_data.get('payment_terms', 'N/A')}
Warranty Required: {rfp_data.get('warranty_required', 'N/A')}
Items: {json.dumps(rfp_data.get('items', []), indent=2)}
"""

    # AI extraction prompt to interpret vendor email into structured fields
    prompt = f"""You are an AI assistant that extracts proposal details from vendor email responses.

RFP Requirements:
{rfp_summary}

Vendor Email Response:
{email_content}

Extract the following information and return it as JSON:
- total_price
- delivery_days
- payment_terms
- warranty
- items (with name, quantity, unit_price, total_price, specifications)
- terms_conditions
- completeness_score (0 to 1)

Return ONLY valid JSON, no additional text."""

    try:
        # Call OpenAI for extraction
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract structured data and return JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        # Clean returned content
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content)

    except Exception as e:
        raise Exception(f"Failed to extract proposal details: {str(e)}")


def compare_proposals_and_recommend(rfp_data: dict, proposals: list) -> dict:
    """
    Analyze all proposals for an RFP and generate:
    - vendor comparison scores
    - strengths/weaknesses
    - rankings
    - recommended vendor with reasoning
    """

    # Convert proposals to simplified summaries for the AI
    proposals_summary = []
    for prop in proposals:
        proposals_summary.append({
            "vendor_name": prop.get("vendor_name", "Unknown"),
            "total_price": prop.get("total_price"),
            "delivery_days": prop.get("delivery_days"),
            "payment_terms": prop.get("payment_terms"),
            "warranty": prop.get("warranty"),
            "completeness_score": prop.get("completeness_score", 0),
            "items": prop.get("items", [])
        })

    # Prompt instructing AI to compare proposals and output detailed JSON
    prompt = f"""You are an AI assistant that helps procurement managers compare vendor proposals.

RFP Requirements:
Title: {rfp_data.get('title', 'N/A')}
Budget: {rfp_data.get('budget', 'N/A')}
Delivery Required: {rfp_data.get('delivery_days', 'N/A')} days
Payment Terms Required: {rfp_data.get('payment_terms', 'N/A')}
Warranty Required: {rfp_data.get('warranty_required', 'N/A')}

Proposals:
{json.dumps(proposals_summary, indent=2)}

Return a JSON object with:
- comparison (scores, strengths, weaknesses, ranks)
- recommendation (best vendor and explanation)

Return JSON ONLY."""

    try:
        # Call OpenAI to perform comparison
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Compare proposals and output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        # Clean JSON result
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content)

    except Exception as e:
        raise Exception(f"Failed to compare proposals: {str(e)}")
