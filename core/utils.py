import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def generate_statement_pdf(user, transactions):
    """
    Generates a PDF account statement for the given user and list of transactions.

    Args:
        user (User): The user for whom the statement is being generated.
        transactions (QuerySet): List of TransactionHistory objects.

    Returns:
        BytesIO: A BytesIO stream of the generated PDF.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - inch, "SmartBank360 Account Statement")

    # User Info
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, height - 1.5 * inch, f"Username: {user.username}")
    p.drawString(1 * inch, height - 1.75 * inch, f"Email: {user.email}")

    # Table Headers
    y = height - 2.25 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, y, "Date")
    p.drawString(2.5 * inch, y, "Type")
    p.drawString(4 * inch, y, "Amount")
    p.drawString(5.5 * inch, y, "Status")

    # Draw transaction rows
    y -= 0.3 * inch
    p.setFont("Helvetica", 11)

    for txn in transactions:
        if y < 1 * inch:  # New page if nearing bottom
            p.showPage()
            y = height - 1 * inch
            p.setFont("Helvetica-Bold", 12)
            p.drawString(1 * inch, y, "Date")
            p.drawString(2.5 * inch, y, "Type")
            p.drawString(4 * inch, y, "Amount")
            p.drawString(5.5 * inch, y, "Status")
            y -= 0.3 * inch
            p.setFont("Helvetica", 11)

        p.drawString(1 * inch, y, txn.timestamp.strftime("%Y-%m-%d %H:%M"))
        p.drawString(2.5 * inch, y, txn.type.capitalize())
        p.drawString(4 * inch, y, f"{txn.amount} KES")
        p.drawString(5.5 * inch, y, txn.status.capitalize())
        y -= 0.25 * inch

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
