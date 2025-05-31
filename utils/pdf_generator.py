from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_payslip_pdf(payslip_data):
    """
    Generates a PDF in-memory bytes object for the given payslip data.
    payslip_data: dict with keys like 'employee_name', 'employee_id', 'position', etc.
    Returns: BytesIO object containing PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Employee Payslip")

    c.setFont("Helvetica", 12)
    y = height - 100
    line_height = 20

    for key, value in payslip_data.items():
        text = f"{key.replace('_', ' ').title()}: {value}"
        c.drawString(50, y, text)
        y -= line_height

    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer
