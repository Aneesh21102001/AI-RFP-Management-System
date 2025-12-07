# ------------------------------------------------------
# This module handles sending RFP emails to vendors using SMTP.
# It builds both plain-text and HTML email versions and sends
# them asynchronously using aiosmtplib.
# ------------------------------------------------------

import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# SMTP configuration loaded from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


async def send_rfp_email(to_email: str, vendor_name: str, rfp_data: dict) -> bool:
    """
    Send a structured RFP email to a vendor.
    Builds both plain-text and HTML formats and sends securely via SMTP.
    """

    # Ensure SMTP is configured before sending
    if not SMTP_USER or not SMTP_PASSWORD:
        raise Exception("SMTP credentials not configured")
    
    # Create an email container capable of holding multiple formats
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Request for Proposal: {rfp_data.get('title', 'RFP')}"
    message["From"] = SMTP_USER
    message["To"] = to_email
    
    # -----------------------------
    # Build PLAIN TEXT email body
    # -----------------------------

    text_body = f"""
Dear {vendor_name},

We are requesting a proposal for the following procurement:

Title: {rfp_data.get('title', 'N/A')}
Description: {rfp_data.get('description', 'N/A')}
"""

    # Add optional RFP fields only if present
    if rfp_data.get('budget'):
        text_body += f"Budget: ${rfp_data.get('budget'):,.2f}\n"
    
    if rfp_data.get('delivery_days'):
        text_body += f"Delivery Required: {rfp_data.get('delivery_days')} days\n"
    
    if rfp_data.get('payment_terms'):
        text_body += f"Payment Terms Required: {rfp_data.get('payment_terms')}\n"
    
    if rfp_data.get('warranty_required'):
        text_body += f"Warranty Required: {rfp_data.get('warranty_required')}\n"
    
    # List items included in the RFP
    if rfp_data.get('items'):
        text_body += "\nItems Required:\n"
        for item in rfp_data.get('items', []):
            text_body += f"- {item.get('name', 'N/A')}"
            if item.get('quantity'):
                text_body += f" (Quantity: {item.get('quantity')})"
            if item.get('specifications'):
                # Convert specifications dict to "key: value" string
                specs = ", ".join([f"{k}: {v}" for k, v in item.get('specifications', {}).items()])
                text_body += f" - {specs}"
            text_body += "\n"
    
    # Additional requirements list
    if rfp_data.get('requirements'):
        text_body += "\nAdditional Requirements:\n"
        for req in rfp_data.get('requirements', []):
            text_body += f"- {req}\n"
    
    # Closing instructions for vendor
    text_body += "\n\nPlease reply to this email with your proposal including:\n"
    text_body += "- Total price\n"
    text_body += "- Delivery timeline\n"
    text_body += "- Payment terms\n"
    text_body += "- Warranty information\n"
    text_body += "- Itemized pricing (if applicable)\n"
    text_body += "- Any terms and conditions\n\n"
    text_body += "Thank you for your interest.\n\nBest regards,\nProcurement Team"
    

    # -----------------------------
    # Build HTML email body
    # -----------------------------

    html_body = f"""
    <html>
      <body>
        <h2>Request for Proposal: {rfp_data.get('title', 'RFP')}</h2>
        <p>Dear {vendor_name},</p>
        <p>We are requesting a proposal for the following procurement:</p>

        <h3>Details:</h3>
        <ul>
          <li><strong>Title:</strong> {rfp_data.get('title', 'N/A')}</li>
          <li><strong>Description:</strong> {rfp_data.get('description', 'N/A')}</li>
    """

    # Add optional fields if present
    if rfp_data.get('budget'):
        html_body += f"<li><strong>Budget:</strong> ${rfp_data.get('budget'):,.2f}</li>"
    
    if rfp_data.get('delivery_days'):
        html_body += f"<li><strong>Delivery Required:</strong> {rfp_data.get('delivery_days')} days</li>"
    
    if rfp_data.get('payment_terms'):
        html_body += f"<li><strong>Payment Terms Required:</strong> {rfp_data.get('payment_terms')}</li>"
    
    if rfp_data.get('warranty_required'):
        html_body += f"<li><strong>Warranty Required:</strong> {rfp_data.get('warranty_required')}</li>"
    
    html_body += "</ul>"

    # List items in HTML format
    if rfp_data.get('items'):
        html_body += "<h3>Items Required:</h3><ul>"
        for item in rfp_data.get('items', []):
            item_text = f"<li><strong>{item.get('name', 'N/A')}</strong>"
            if item.get('quantity'):
                item_text += f" (Quantity: {item.get('quantity')})"
            if item.get('specifications'):
                specs = ", ".join([f"{k}: {v}" for k, v in item.get('specifications', {}).items()])
                item_text += f" - {specs}"
            item_text += "</li>"
            html_body += item_text
        html_body += "</ul>"
    
    # List additional requirements
    if rfp_data.get('requirements'):
        html_body += "<h3>Additional Requirements:</h3><ul>"
        for req in rfp_data.get('requirements', []):
            html_body += f"<li>{req}</li>"
        html_body += "</ul>"
    

    # Closing instructions
    html_body += """
        <h3>Please reply to this email with your proposal including:</h3>
        <ul>
          <li>Total price</li>
          <li>Delivery timeline</li>
          <li>Payment terms</li>
          <li>Warranty information</li>
          <li>Itemized pricing (if applicable)</li>
          <li>Any terms and conditions</li>
        </ul>
        <p>Thank you for your interest.</p>
        <p>Best regards,<br>Procurement Team</p>
      </body>
    </html>
    """
    
    # Attach both plain-text and HTML versions
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))
    

    # -----------------------------
    # Send email via SMTP
    # -----------------------------
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=True,  # Secure TLS connection
        )
        return True

    except Exception as e:
        # Provide clear exception message if sending fails
        raise Exception(f"Failed to send email: {str(e)}")
