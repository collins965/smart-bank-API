from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_statement_pdf(user, transactions, month, year):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"SmartBank360 - Transaction Statement")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"User: {user.username}")
    p.drawString(100, 765, f"Month: {month} / {year}")
    p.drawString(100, 750, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 720
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y, "Date")
    p.drawString(200, y, "Type")
    p.drawString(300, y, "Amount")
    p.drawString(400, y, "Status")
    p.line(90, y-5, 500, y-5)

    p.setFont("Helvetica", 10)
    for txn in transactions:
        y -= 20
        if y < 100:
            p.showPage()
            y = 780
        p.drawString(100, y, txn.timestamp.strftime('%Y-%m-%d'))
        p.drawString(200, y, txn.type.capitalize())
        p.drawString(300, y, f"KES {txn.amount}")
        p.drawString(400, y, txn.status.capitalize())

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
