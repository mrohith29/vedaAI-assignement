from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
QUESTION_PDF = OUTPUT / "sample-biology-question-paper.pdf"
ANSWER_PDF = OUTPUT / "sample-handwritten-answer-sheet.pdf"
PAGE_WIDTH, PAGE_HEIGHT = A4


def build_question_paper() -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#24201f"),
        spaceAfter=5 * mm,
    )
    subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#675f5b"),
        spaceAfter=6 * mm,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#292524"),
    )
    number = ParagraphStyle(
        "Number",
        parent=body,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#d85d48"),
    )
    instructions = ParagraphStyle(
        "Instructions",
        parent=body,
        fontSize=9,
        leading=13,
        leftIndent=4 * mm,
        rightIndent=4 * mm,
        textColor=colors.HexColor("#625956"),
    )

    doc = SimpleDocTemplate(
        str(QUESTION_PDF),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="Sample Biology Question Paper",
        author="VedaAI sample data generator",
    )
    story = [
        Paragraph("GREENFIELD SENIOR SCHOOL", title),
        Paragraph("BIOLOGY - UNIT ASSESSMENT", ParagraphStyle("Exam", parent=title, fontSize=14, textColor=colors.HexColor("#e46550"))),
        Paragraph("Class IX &nbsp;&nbsp;|&nbsp;&nbsp; Time: 45 minutes &nbsp;&nbsp;|&nbsp;&nbsp; Maximum marks: 20", subtitle),
        Table(
            [[Paragraph("Instructions: Answer all questions. Show working for numerical questions. Label diagrams clearly.", instructions)]],
            colWidths=[170 * mm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f6f1ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#ddd3cc")),
                ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]),
        ),
        Spacer(1, 8 * mm),
    ]

    questions = [
        ("1 (a)", "Define photosynthesis.", "[2]"),
        ("1 (b)", "Write the word equation for photosynthesis.", "[2]"),
        ("2", "Explain how stomata help a leaf exchange gases. Include the role of guard cells in your answer.", "[4]"),
        ("3", "A plant cell is 0.08 mm wide. In a drawing it is 40 mm wide. Calculate the magnification of the drawing and show your working.", "[3]"),
        ("4", "The table shows the rate of photosynthesis at different light intensities. Plot a line graph and describe the trend.", "[4]"),
        ("5", "State two differences between aerobic and anaerobic respiration in human muscle cells.", "[5]"),
    ]

    data = []
    for label, text, marks in questions:
        data.append([Paragraph(label, number), Paragraph(text, body), Paragraph(marks, body)])
        if label == "4":
            graph_data = Table(
                [
                    ["Light intensity (a.u.)", "10", "20", "30", "40", "50"],
                    ["Rate (bubbles/min)", "4", "8", "13", "16", "17"],
                ],
                colWidths=[42 * mm] + [16 * mm] * 5,
                style=TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdb3ad")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f6f1ed")),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]),
            )
            data.append(["", graph_data, ""])

    question_table = Table(data, colWidths=[18 * mm, 139 * mm, 13 * mm], repeatRows=0)
    question_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.45, colors.HexColor("#e6ddd8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
    ]))
    story.append(question_table)
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph("END OF QUESTION PAPER", subtitle))
    doc.build(story, onFirstPage=question_footer, onLaterPages=question_footer)


def question_footer(pdf: canvas.Canvas, doc) -> None:
    pdf.saveState()
    pdf.setStrokeColor(colors.HexColor("#ddd3cc"))
    pdf.line(20 * mm, 13 * mm, PAGE_WIDTH - 20 * mm, 13 * mm)
    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#837975"))
    pdf.drawString(20 * mm, 8.5 * mm, "Sample data for VedaAI Assessment Mapper")
    pdf.drawRightString(PAGE_WIDTH - 20 * mm, 8.5 * mm, f"Page {doc.page}")
    pdf.restoreState()


def register_handwriting_font() -> str:
    candidates = [
        Path("C:/Windows/Fonts/comic.ttf"),
        Path("C:/Windows/Fonts/segoepr.ttf"),
    ]
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont("Handwriting", str(path)))
            return "Handwriting"
    return "Times-Italic"


def build_answer_sheet() -> None:
    font = register_handwriting_font()
    pdf = canvas.Canvas(str(ANSWER_PDF), pagesize=A4, pageCompression=1)
    pdf.setTitle("Sample Handwritten Biology Answer Sheet")
    pdf.setAuthor("VedaAI sample data generator")

    draw_answer_page(pdf, font, 1)
    write_lines(pdf, font, [
        ("Q3", 45, True),
        ("Magnification = image size / actual size", 40, False),
        ("= 40 mm / 0.08 mm", 36, False),
        ("= 500 times", 34, False),
        ("Q1 (a)", 43, True),
        ("Photosynthesis is the process by which green plants make", 39, False),
        ("glucose from carbon dioxide and water using light energy.", 37, False),
        ("Q1 (b)", 43, True),
        ("carbon dioxide + water  ->  glucose + oxygen", 39, False),
        ("Q5", 43, True),
        ("Aerobic respiration uses oxygen and releases much more energy.", 38, False),
        ("Anaerobic respiration does not use oxygen and releases less", 37, False),
        ("energy. In muscles it produces lactic acid, not carbon dioxide.", 36, False),
        ("Q2", 43, True),
        ("Stomata are tiny pores, mostly on the lower leaf surface.", 38, False),
        ("Carbon dioxide diffuses into the leaf through them, while oxygen", 36, False),
        ("and water vapour diffuse out. Guard cells change shape to", 34, False),
        ("open or close each pore depending on water and light conditions...", 32, False),
    ], start_y=247 * mm)
    pdf.setFont(font, 9)
    pdf.setFillColor(colors.HexColor("#36568e"))
    pdf.drawRightString(PAGE_WIDTH - 23 * mm, 17 * mm, "Q2 continued on next page ->")
    pdf.showPage()

    draw_answer_page(pdf, font, 2)
    write_lines(pdf, font, [
        ("Q2 continued", 43, True),
        ("When guard cells take in water they become turgid and curve", 38, False),
        ("apart, opening the stoma. When they lose water they become", 37, False),
        ("flaccid and the pore closes. This controls gas exchange and", 35, False),
        ("also limits water loss by transpiration.", 34, False),
        ("Q6", 43, True),
        ("Mitosis produces two genetically identical daughter cells.", 38, False),
        ("It is used for growth and repair of tissues.", 37, False),
    ], start_y=247 * mm)
    pdf.setFont(font, 10)
    pdf.setFillColor(colors.HexColor("#36568e"))
    pdf.drawString(24 * mm, 91 * mm, "I did not answer the graph question.")
    pdf.save()


def draw_answer_page(pdf: canvas.Canvas, font: str, page_number: int) -> None:
    pdf.setFillColor(colors.HexColor("#fffefa"))
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    pdf.setStrokeColor(colors.HexColor("#ccdfed"))
    pdf.setLineWidth(0.35)
    y = 263 * mm
    while y > 20 * mm:
        pdf.line(18 * mm, y, PAGE_WIDTH - 15 * mm, y)
        y -= 8.4 * mm
    pdf.setStrokeColor(colors.HexColor("#e7a9a8"))
    pdf.line(28 * mm, 18 * mm, 28 * mm, PAGE_HEIGHT - 17 * mm)
    pdf.setFillColor(colors.HexColor("#3b598e"))
    pdf.setFont(font, 11)
    pdf.drawString(34 * mm, PAGE_HEIGHT - 18 * mm, "Name: Aarav Sharma")
    pdf.drawRightString(PAGE_WIDTH - 18 * mm, PAGE_HEIGHT - 18 * mm, f"Biology - Page {page_number}")
    pdf.setStrokeColor(colors.HexColor("#3b598e"))
    pdf.line(33 * mm, PAGE_HEIGHT - 20 * mm, 90 * mm, PAGE_HEIGHT - 20 * mm)


def write_lines(
    pdf: canvas.Canvas,
    font: str,
    lines: list[tuple[str, int, bool]],
    start_y: float,
) -> None:
    y = start_y
    for index, (text, indent, is_heading) in enumerate(lines):
        pdf.saveState()
        pdf.translate(indent * mm, y)
        pdf.rotate((-0.35, 0.2, -0.1, 0.35)[index % 4])
        pdf.setFillColor(colors.HexColor("#304f8d"))
        pdf.setFont(font, 11 if is_heading else 10.2)
        pdf.drawString(0, 0, text)
        if is_heading:
            pdf.setLineWidth(0.7)
            pdf.line(0, -1.5, pdf.stringWidth(text, font, 11), -1.5)
        pdf.restoreState()
        y -= (9.7 if is_heading else 8.4) * mm


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_question_paper()
    build_answer_sheet()
    print(QUESTION_PDF)
    print(ANSWER_PDF)


if __name__ == "__main__":
    main()
