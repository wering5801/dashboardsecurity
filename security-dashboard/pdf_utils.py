import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import datetime
from io import BytesIO
import base64
import tempfile
import os

def export_to_pdf(fig, title, insights):
    # Create a temporary file for the image
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        fig.savefig(tmp_file.name, format='png', bbox_inches='tight')
        tmp_filename = tmp_file.name
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, title)
    
    # Add date (hidden but keep code for future)
    # p.setFont("Helvetica", 10)
    # p.drawString(50, height - 70, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    
    # Add plot from the temp file
    p.drawImage(tmp_filename, 50, height - 350, width=500, height=250)
    
    # Add insights
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 380, "Key Insights:")
    p.setFont("Helvetica", 10)
    for i, insight in enumerate(insights):
        p.drawString(50, height - 400 - (i * 20), f"• {insight}")
    
    p.save()
    buffer.seek(0)
    
    # Clean up the temporary file
    os.unlink(tmp_filename)
    
    return buffer

def create_download_link(val, filename):
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download PDF</a>'