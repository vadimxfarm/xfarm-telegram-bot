from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
from database import get_farmer
from work_plan import get_work_plan

# Реєструємо шрифт з підтримкою кирилиці
try:
    # Спробуємо знайти стандартний шрифт Windows
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    DEFAULT_FONT = 'DejaVuSans'
except:
    # Якщо немає — використовуємо вбудований (можливо, з квадратами)
    DEFAULT_FONT = 'Helvetica'

def generate_pdf_report(user_id, output_path):
    farmer = get_farmer(user_id)
    if not farmer or not farmer[0] or not farmer[1]:
        return False

    city, crops = farmer
    tasks = get_work_plan(crops)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Створюємо стиль з підтримкою кирилиці
    custom_style = ParagraphStyle(
        'Custom',
        parent=styles['Normal'],
        fontName=DEFAULT_FONT,
        fontSize=12,
        leading=14
    )
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName=DEFAULT_FONT,
        fontSize=18,
        leading=22
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontName=DEFAULT_FONT,
        fontSize=14,
        leading=16
    )

    story = []
    story.append(Paragraph("Агрономічний звіт", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Регіон:</b> {city}", custom_style))
    story.append(Paragraph(f"<b>Культури:</b> {crops}", custom_style))
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>План робіт на цей місяць:</b>", heading_style))
    story.append(Spacer(1, 12))
    
    if tasks and tasks[0] != "Немає запланованих робіт у цьому місяці.":
        for task in tasks:
            story.append(Paragraph(task, custom_style))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("Немає запланованих робіт у цьому місяці.", custom_style))

    doc.build(story)
    return True