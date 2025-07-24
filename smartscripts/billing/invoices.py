# billing/invoices.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_invoice_pdf(invoice_data: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.drawString(100, 750, "SmartScripts - Invoice")
    c.drawString(100, 730, f"Invoice ID: {invoice_data.get('invoice_id')}")
    c.drawString(100, 710, f"Customer ID: {invoice_data.get('customer_id')}")
    c.drawString(100, 690, f"Plan: {invoice_data.get('plan_name')}")
    c.drawString(100, 670, f"Amount Paid: ${invoice_data.get('amount')}")
    c.drawString(100, 650, f"Date: {invoice_data.get('date')}")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()
