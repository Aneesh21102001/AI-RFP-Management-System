import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_natural_language_to_rfp(user_input: str) -> dict:
    """
    Convert natural language description to structured RFP format.
    """
    prompt = f"""You are an AI assistant that helps convert procurement requests into structured RFPs.

User request: {user_input}

Extract the following information and return it as a JSON object:
- title: A concise title for the RFP
- description: The full description of what needs to be procured
- budget: Total budget amount (as a number, or null if not specified)
- delivery_days: Required delivery time in days (as a number, or null if not specified)
- payment_terms: Payment terms (e.g., "net 30", "net 60", etc., or null if not specified)
- warranty_required: Warranty requirements (e.g., "1 year", "2 years", etc., or null if not specified)
- items: Array of items with their specifications. Each item should have:
  - name: Item name
  - quantity: Quantity needed
  - specifications: Object with key-value pairs of specifications (e.g., {{"RAM": "16GB", "size": "27-inch"}})
- requirements: Array of any additional requirements or conditions

Return ONLY valid JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from natural language. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        raise Exception(f"Failed to parse RFP: {str(e)}")

def extract_proposal_details(email_content: str, rfp_data: dict) -> dict:
    """
    Extract structured proposal details from vendor email response.
    """
    rfp_summary = f"""
RFP Title: {rfp_data.get('title', 'N/A')}
Budget: {rfp_data.get('budget', 'N/A')}
Delivery Required: {rfp_data.get('delivery_days', 'N/A')} days
Payment Terms Required: {rfp_data.get('payment_terms', 'N/A')}
Warranty Required: {rfp_data.get('warranty_required', 'N/A')}
Items: {json.dumps(rfp_data.get('items', []), indent=2)}
"""

    prompt = f"""You are an AI assistant that extracts proposal details from vendor email responses.

RFP Requirements:
{rfp_summary}

Vendor Email Response:
{email_content}

Extract the following information and return it as a JSON object:
- total_price: Total price quoted (as a number, or null if not found)
- delivery_days: Delivery time in days (as a number, or null if not found)
- payment_terms: Payment terms offered (string, or null if not found)
- warranty: Warranty offered (string, or null if not found)
- items: Array of items with prices. Each item should have:
  - name: Item name (match to RFP items if possible)
  - quantity: Quantity (if specified)
  - unit_price: Price per unit (as a number, or null)
  - total_price: Total price for this item (as a number, or null)
  - specifications: Any specifications mentioned
- terms_conditions: Any important terms and conditions mentioned
- completeness_score: A score from 0 to 1 indicating how complete the response is (considering if all RFP requirements are addressed)

Return ONLY valid JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from vendor emails. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        raise Exception(f"Failed to extract proposal details: {str(e)}")

def compare_proposals_and_recommend(rfp_data: dict, proposals: list) -> dict:
    """
    Compare multiple proposals and provide recommendations.
    """
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
    
    prompt = f"""You are an AI assistant that helps procurement managers compare vendor proposals.

RFP Requirements:
Title: {rfp_data.get('title', 'N/A')}
Budget: {rfp_data.get('budget', 'N/A')}
Delivery Required: {rfp_data.get('delivery_days', 'N/A')} days
Payment Terms Required: {rfp_data.get('payment_terms', 'N/A')}
Warranty Required: {rfp_data.get('warranty_required', 'N/A')}

Proposals:
{json.dumps(proposals_summary, indent=2)}

Analyze these proposals and return a JSON object with:
- comparison: Array of vendor comparisons, each with:
  - vendor_name: Name of the vendor
  - score: Overall score from 0-100 (considering price, delivery, terms, completeness, and alignment with requirements)
  - strengths: Array of strengths
  - weaknesses: Array of weaknesses
  - price_rank: Ranking by price (1 = cheapest)
  - delivery_rank: Ranking by delivery speed (1 = fastest)
- recommendation: Object with:
  - recommended_vendor: Name of the recommended vendor
  - reason: Detailed explanation of why this vendor is recommended
  - summary: Brief summary of the comparison

Return ONLY valid JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that compares vendor proposals. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        raise Exception(f"Failed to compare proposals: {str(e)}")
