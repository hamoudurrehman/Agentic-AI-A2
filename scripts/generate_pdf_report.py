"""Generate professional PDF R&D Report from REPORT.md using ReportLab."""
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PDF = os.path.join(BASE_DIR, "docs", "GigBid_RD_Report.pdf")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header
        self.drawString(54, 750, "AI-4016 R&D Report | GigBid: Multi-Agent Freelancer Copilot")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, letter[0] - 54, 742)
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 40, page_text)
        self.drawString(54, 40, "FAST-NUCES Islamabad · Engineering Design Review")
        self.line(54, 52, letter[0] - 54, 52)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#ffffff')
    )

    elements = []

    # Title block
    elements.append(Paragraph("AI-4016 R&D Report: GigBid Multi-Agent Freelancer Copilot", title_style))
    elements.append(Paragraph("<b>LangGraph Multi-Agent Systems · Advanced RAG · Model Context Protocol (MCP) · Web App</b><br/>"
                              "Author: AI Engineering Team · Course Instructor: Muhammad Owais Idrees, FAST-NUCES Islamabad", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    # Read REPORT.md
    report_md_path = os.path.join(BASE_DIR, "docs", "REPORT.md")
    with open(report_md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_table = False
    table_data = []

    for line in lines:
        line_str = line.strip()

        # Skip main title lines already rendered
        if line_str.startswith("# AI-4016") or line_str.startswith("**Author") or line_str.startswith("**Institution"):
            continue
        if line_str.startswith("**Course") or line_str.startswith("**Date") or line_str.startswith("**Artifacts"):
            continue
        if line_str == "---":
            continue

        # Table processing
        if line_str.startswith("|"):
            in_table = True
            parts = [p.strip() for p in line_str.split("|")[1:-1]]
            if all(re.match(r"^:?-+:?$", p) for p in parts if p):
                continue # delimiter row
            table_data.append(parts)
            continue
        elif in_table:
            # Table ended
            if table_data:
                col_count = len(table_data[0])
                table_flowable_data = []
                for row_idx, row in enumerate(table_data):
                    flow_row = []
                    for c_idx, cell in enumerate(row):
                        clean_cell = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", cell)
                        clean_cell = re.sub(r"\*(.*?)\*", r"<i>\1</i>", clean_cell)
                        st = table_header if row_idx == 0 else table_cell
                        flow_row.append(Paragraph(clean_cell, st))
                    table_flowable_data.append(flow_row)

                # Responsive column width calculation
                available_width = letter[0] - 108 # 504 pt
                col_w = available_width / col_count
                t = Table(table_flowable_data, colWidths=[col_w]*col_count)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
                ]))
                elements.append(Spacer(1, 4))
                elements.append(t)
                elements.append(Spacer(1, 6))
            in_table = False
            table_data = []

        if not line_str:
            continue

        if line_str.startswith("## "):
            sec_title = line_str[3:]
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(sec_title, h1_style))
        elif line_str.startswith("### "):
            sec_title = line_str[4:]
            elements.append(Paragraph(sec_title, h2_style))
        elif line_str.startswith("- ") or line_str.startswith("* "):
            content = line_str[2:]
            clean_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            clean_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", clean_text)
            clean_text = clean_text.replace("`", "")
            elements.append(Paragraph(f"• {clean_text}", bullet_style))
        elif re.match(r"^\d+\.\s", line_str):
            num = line_str.split(".")[0]
            content = line_str[len(num)+2:]
            clean_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            clean_text = clean_text.replace("`", "")
            elements.append(Paragraph(f"{num}. {clean_text}", bullet_style))
        else:
            clean_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line_str)
            clean_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", clean_text)
            clean_text = clean_text.replace("`", "")
            elements.append(Paragraph(clean_text, body_style))

    # Build the document
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"R&D Report generated successfully: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
