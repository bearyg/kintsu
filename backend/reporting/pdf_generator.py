from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class PdfGenerator:
    @staticmethod
    def generate(data, filename_base: str) -> str:
        filepath = f"/tmp/{filename_base}.pdf"
        c = canvas.Canvas(filepath, pagesize=letter)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, data.get("title", "Inventory Report"))
        
        c.setFont("Helvetica", 12)
        y = 700
        for item in data.get("items", []):
            text = f"{item['name']} - ${item['value']}"
            c.drawString(100, y, text)
            y -= 20
            
        c.save()
        return filepath
