"""
Open Broker LOS - PDF Generator
Generates Loan Summary PDF.
"""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .models import LoanApplication

class PDFGeneratorService:
    @staticmethod
    def generate_pdf(app: LoanApplication) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = styles['Heading1']
        elements.append(Paragraph(f"Loan Application Summary", title_style))
        elements.append(Spacer(1, 12))
        
        # Loan Details
        elements.append(Paragraph(f"<b>Loan ID:</b> {app.floify_loan_id}", styles['Normal']))
        elements.append(Paragraph(f"<b>Amount:</b> ${app.loan_amount:,.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Property:</b> {app.property_address}, {app.property_state}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Borrowers
        elements.append(Paragraph(f"<b>Borrowers</b>", styles['Heading2']))
        
        data = [['Name', 'Email', 'Role']]
        for borrower in app.borrowers.all():
            role = "Primary" if borrower.is_primary else "Co-Borrower"
            data.append([
                f"{borrower.first_name} {borrower.last_name}",
                borrower.email,
                role
            ])
            
        t = Table(data, colWidths=[200, 200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        # Build
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
