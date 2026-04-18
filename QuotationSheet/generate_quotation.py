from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


OUTPUT_FILENAME = "Delhi_PS_CRM_Quotation.xlsx"

FONT_DEFAULT = Font(name="Calibri", size=11)
FONT_TITLE = Font(name="Calibri", size=16, bold=True, color="1F3864")
FONT_SUBTITLE = Font(name="Calibri", size=12, bold=False, color="1F3864")
FONT_META = Font(name="Calibri", size=11, bold=False, color="1F3864")

FILL_SECTION = PatternFill("solid", fgColor="1F3864")  # dark navy
FILL_TABLE_HEADER = PatternFill("solid", fgColor="2E4F8A")  # dark blue
FILL_PHASE_SUBTOTAL = PatternFill("solid", fgColor="BDD7EE")  # light blue
FILL_ALT = PatternFill("solid", fgColor="EBF3FF")  # very light blue
FILL_TOTAL = PatternFill("solid", fgColor="FFD966")  # yellow

ALIGN_LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="top", wrap_text=True)
ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_CENTER_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

INDIAN_CURRENCY_FORMAT = "#,##,##0"

THIN_SIDE = Side(style="thin", color="A6A6A6")
THICK_SIDE = Side(style="thick", color="1F3864")
THIN_BORDER = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)


def _apply_font(ws) -> None:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is None:
                continue
            cell.font = FONT_DEFAULT


def _set_col_widths(ws, min_width: int = 10, max_width: int = 70) -> None:
    widths: dict[int, int] = {}
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is None:
                continue
            text = str(cell.value)
            max_line = max((len(x) for x in text.splitlines()), default=len(text))
            widths[cell.column] = max(widths.get(cell.column, 0), max_line)

    for col_idx, w in widths.items():
        adj = max(min_width, min(max_width, w + 2))
        ws.column_dimensions[get_column_letter(col_idx)].width = adj


def _fill_row(ws, row_idx: int, start_col: int, end_col: int, fill: PatternFill) -> None:
    for c in range(start_col, end_col + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = fill


def _style_section_header(ws, row_idx: int, start_col: int, end_col: int, title: str) -> None:
    ws.merge_cells(start_row=row_idx, start_column=start_col, end_row=row_idx, end_column=end_col)
    cell = ws.cell(row=row_idx, column=start_col, value=title)
    cell.fill = FILL_SECTION
    cell.font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    cell.alignment = ALIGN_CENTER_LEFT
    _fill_row(ws, row_idx, start_col, end_col, FILL_SECTION)


def _style_table_header(ws, row_idx: int, start_col: int, end_col: int) -> None:
    for c in range(start_col, end_col + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = FILL_TABLE_HEADER
        cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER


def _style_zebra_rows(
    ws,
    start_row: int,
    end_row: int,
    start_col: int,
    end_col: int,
    *,
    first_is_white: bool = True,
) -> None:
    for r in range(start_row, end_row + 1):
        is_alt = ((r - start_row) % 2 == 1) if first_is_white else ((r - start_row) % 2 == 0)
        fill = FILL_ALT if is_alt else None
        for c in range(start_col, end_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.alignment = ALIGN_LEFT
            cell.border = THIN_BORDER
            if fill:
                cell.fill = fill


def _format_currency_cell(cell, value: Optional[float]) -> None:
    if value is None:
        cell.value = ""
        cell.number_format = INDIAN_CURRENCY_FORMAT
        cell.alignment = ALIGN_RIGHT
        return
    cell.value = value
    cell.number_format = INDIAN_CURRENCY_FORMAT
    cell.alignment = ALIGN_RIGHT


def _thick_border_box(ws, start_row: int, end_row: int, start_col: int, end_col: int) -> None:
    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            cell = ws.cell(row=r, column=c)
            b = cell.border or Border()
            left = THICK_SIDE if c == start_col else b.left
            right = THICK_SIDE if c == end_col else b.right
            top = THICK_SIDE if r == start_row else b.top
            bottom = THICK_SIDE if r == end_row else b.bottom
            cell.border = Border(left=left, right=right, top=top, bottom=bottom)


def build_workbook() -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "Quotation"

    # Page setup
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.freeze_panes = "A4"  # freeze top 3 rows

    # SECTION 1 — PROJECT OVERVIEW HEADER
    # Title / subtitle / meta row (top 3 rows)
    ws.merge_cells("A1:H1")
    ws["A1"] = "Delhi PS-CRM — Project Cost Quotation"
    ws["A1"].font = FONT_TITLE
    ws["A1"].alignment = ALIGN_CENTER

    ws.merge_cells("A2:H2")
    ws["A2"] = "AI-Powered WhatsApp Civic Complaint Management System"
    ws["A2"].font = FONT_SUBTITLE
    ws["A2"].alignment = ALIGN_CENTER

    ws.merge_cells("A3:H3")
    ws["A3"] = "Team: Delhi PS-CRM | Document: Cost Quotation v1.0 | Excluding all applicable taxes"
    ws["A3"].font = FONT_META
    ws["A3"].alignment = ALIGN_CENTER

    row = 5
    section1_start = row
    _style_section_header(ws, row, 1, 8, "SECTION 1 — PROJECT OVERVIEW HEADER")
    row += 1

    info = [
        ("Target Scale", "1,00,000 complaints/month across 272 Delhi wards"),
        ("Technology Stack", "FastAPI, Gemini 2.0 Flash, Gradient Boosting ML, Azure Cloud, WhatsApp Business API, SendGrid"),
        ("Deployment Timeline", "2 months"),
        ("Languages Supported", "Hindi and English"),
    ]

    for k, v in info:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=8)
        c1 = ws.cell(row=row, column=1, value=f"{k}:")
        c2 = ws.cell(row=row, column=3, value=v)
        c1.font = Font(name="Calibri", size=11, bold=True, color="1F3864")
        c1.alignment = ALIGN_LEFT
        c2.alignment = ALIGN_LEFT
        for col in range(1, 9):
            ws.cell(row=row, column=col).border = THIN_BORDER
        row += 1

    section1_end = row - 1
    _thick_border_box(ws, section1_start, section1_end, 1, 8)

    row += 2

    # SECTION 2 — PHASE-WISE COST SUMMARY
    section2_start = row
    _style_section_header(ws, row, 1, 8, "SECTION 2 — PHASE-WISE COST SUMMARY")
    row += 1

    phase_headers = [
        "Phase",
        "Duration",
        "Description",
        "Key Activities",
        "Est. Complaints/Month",
        "Phase Cost (Rs.)",
    ]
    for i, h in enumerate(phase_headers, start=1):
        ws.cell(row=row, column=i, value=h)
    _style_table_header(ws, row, 1, 6)
    row += 1

    phases = [
        (
            "Phase 1",
            "Weeks 1-2",
            "Development and Testing",
            "Backend complete, WhatsApp bot on test numbers, ML model integrated, staging environment, internal QA",
            "0",
            115000,
        ),
        (
            "Phase 2",
            "Weeks 3-4",
            "Pilot Deployment",
            "Live in 5 Delhi wards, real citizen complaints, bug fixes, officer onboarding",
            "1,000",
            95940,
        ),
        (
            "Phase 3",
            "Weeks 5-6",
            "Partial Rollout",
            "Expand to 50 wards, department routing live, ML escalation running on real data",
            "20,000",
            55620,
        ),
        (
            "Phase 4",
            "Weeks 7-8",
            "Full Delhi Deployment",
            "All 272 wards live, 1,00,000 complaints/month, full system operational",
            "1,00,000",
            156940,
        ),
        (
            "Phase 5",
            "Month 3 onwards",
            "Steady State Operations",
            "Handed to Delhi government IT team. Maintenance only, quarterly ML retraining",
            "1,00,000",
            107250,
        ),
    ]

    phase_row_start = row
    for ph, dur, desc, acts, est, cost in phases:
        ws.cell(row=row, column=1, value=ph)
        ws.cell(row=row, column=2, value=dur)
        ws.cell(row=row, column=3, value=desc)
        ws.cell(row=row, column=4, value=acts)
        ws.cell(row=row, column=5, value=est).alignment = ALIGN_RIGHT
        _format_currency_cell(ws.cell(row=row, column=6), cost)
        row += 1
    phase_row_end = row - 1
    _style_zebra_rows(ws, phase_row_start, phase_row_end, 1, 6)

    # Totals lines (as text rows)
    total_phases_1_4 = 423500
    annual_maintenance = 1287000

    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    ws.cell(row=row, column=1, value="Total Project Cost Phases 1-4: Rs. 4,23,500").font = Font(
        name="Calibri", size=11, bold=True, color="1F3864"
    )
    ws.cell(row=row, column=1).alignment = ALIGN_LEFT
    ws.cell(row=row, column=6, value="").border = THIN_BORDER
    for c in range(1, 7):
        ws.cell(row=row, column=c).border = THIN_BORDER
    row += 1

    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    ws.cell(
        row=row,
        column=1,
        value="Annual Maintenance from Month 3: Rs. 12,87,000",
    ).font = Font(name="Calibri", size=11, bold=True, color="1F3864")
    ws.cell(row=row, column=1).alignment = ALIGN_LEFT
    for c in range(1, 7):
        ws.cell(row=row, column=c).border = THIN_BORDER
    section2_end = row
    _thick_border_box(ws, section2_start, section2_end, 1, 6)
    row += 2

    # SECTION 3 — DETAILED LINE-ITEM BREAKDOWN
    section3_start = row
    _style_section_header(ws, row, 1, 8, "SECTION 3 — DETAILED LINE-ITEM BREAKDOWN")
    row += 1

    detail_headers = [
        "Phase",
        "Category",
        "Item",
        "Specifications and Details",
        "Quantity / Duration",
        "Unit Cost (Rs.)",
        "Total Cost (Rs.)",
        "Notes",
    ]
    for i, h in enumerate(detail_headers, start=1):
        ws.cell(row=row, column=i, value=h)
    _style_table_header(ws, row, 1, 8)
    row += 1

    # Helper to write a subtotal row
    def write_phase_subtotal(label: str, amount: int) -> None:
        nonlocal row
        for c in range(1, 9):
            ws.cell(row=row, column=c).fill = FILL_PHASE_SUBTOTAL
            ws.cell(row=row, column=c).border = THIN_BORDER
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        ws.cell(row=row, column=1, value=label).font = Font(name="Calibri", size=11, bold=True)
        ws.cell(row=row, column=1).alignment = ALIGN_LEFT
        _format_currency_cell(ws.cell(row=row, column=7), amount)
        ws.cell(row=row, column=7).font = Font(name="Calibri", size=11, bold=True)
        ws.cell(row=row, column=8, value="")
        row += 1

    # Phase 1 subtotal row
    write_phase_subtotal("Phase 1 total: Rs. 1,15,000", 115000)

    # Detail line items (phases 1-4) + phase 5 recurring
    line_items = [
        # Phase 1
        ("Phase 1", "Team", "Student Developer Stipends", "5 team members: backend, ML integration, architecture, testing, DevOps", "5 x 0.5 month", "18,000/member/month", 45000, "Half month stipend weeks 1-2"),
        ("Phase 1", "Infrastructure", "Azure Container Apps Staging", "Staging FastAPI backend for internal testing", "0.5 month", "4,000", 2000, "Minimal staging instance"),
        ("Phase 1", "Infrastructure", "Azure Database for PostgreSQL Staging", "Managed database for development and testing", "0.5 month", "2,500", 1250, "Burstable B1ms tier"),
        ("Phase 1", "Testing", "WhatsApp API Sandbox", "Meta WhatsApp Business API test numbers and sandbox", "One-time", "5,000", 5000, "Test message costs"),
        ("Phase 1", "Testing", "API Integration Testing", "Gemini API test calls, SendGrid test emails, staging instance", "One-time", "4,000", 4000, "All third-party API test costs"),
        # Phase 2 subtotal row will be written separately
    ]

    def write_line_item(
        phase: str,
        category: str,
        item: str,
        specs: str,
        qty: str,
        unit_cost: str,
        total_cost: int,
        notes: str,
    ) -> None:
        nonlocal row
        ws.cell(row=row, column=1, value=phase)
        ws.cell(row=row, column=2, value=category)
        ws.cell(row=row, column=3, value=item)
        ws.cell(row=row, column=4, value=specs)
        ws.cell(row=row, column=5, value=qty)
        ws.cell(row=row, column=6, value=unit_cost).alignment = ALIGN_RIGHT
        _format_currency_cell(ws.cell(row=row, column=7), total_cost)
        ws.cell(row=row, column=8, value=notes)
        row += 1

    detail_data_start = row
    for li in line_items:
        write_line_item(*li)

    # Phase 2 subtotal
    write_phase_subtotal("Phase 2 total: Rs. 95,940", 95940)

    phase2_items = [
        ("Phase 2", "Team", "Student Developer Stipends", "5 members during pilot: monitoring, bug fixes, officer onboarding", "5 x 0.5 month", "18,000/member/month", 45000, "Half month stipend weeks 3-4"),
        ("Phase 2", "Infrastructure", "Azure Container Apps", "Live backend for 5-ward pilot", "0.5 month", "4,000", 2000, "Small instance"),
        ("Phase 2", "Infrastructure", "Azure Database for PostgreSQL", "Live database for pilot", "0.5 month", "2,500", 1250, "Burstable tier"),
        ("Phase 2", "Infrastructure", "Azure Blob Storage", "Photo evidence for pilot complaints", "0.5 month", "500", 250, "Minimal at 1K complaints"),
        ("Phase 2", "AI and ML", "Gemini 2.0 Flash API", "AI classification for 1,000 pilot complaints", "1,000 calls", "0.40/call", 400, "Per-token billing"),
        ("Phase 2", "Communication", "WhatsApp Business API", "Live messaging for 5-ward pilot", "1,000 conversations", "0.47/conversation", 470, "Per conversation"),
        ("Phase 2", "Communication", "SendGrid", "Department notification emails", "1,000 emails", "0.10/email", 100, "Free tier covers this"),
    ]
    for li in phase2_items:
        write_line_item(*li)

    # Phase 3 subtotal
    write_phase_subtotal("Phase 3 total: Rs. 55,620", 55620)
    phase3_items = [
        ("Phase 3", "Infrastructure", "Azure Container Apps", "Scaled backend for 50 wards", "0.5 month", "8,000", 4000, "Medium instance"),
        ("Phase 3", "Infrastructure", "Azure Database for PostgreSQL Flexible", "Production-grade database with backups", "0.5 month", "5,000", 2500, "General Purpose tier"),
        ("Phase 3", "Infrastructure", "Azure Blob Storage", "40GB photo storage at 20K complaints", "0.5 month", "1,500", 750, "LRS redundancy"),
        ("Phase 3", "Infrastructure", "Azure Monitor", "Observability and alerting", "0.5 month", "1,500", 750, "Required for SLA"),
        ("Phase 3", "Infrastructure", "Azure Service Bus", "Webhook event queuing at 20K/month", "0.5 month", "1,000", 500, "Standard tier"),
        ("Phase 3", "AI and ML", "Gemini 2.0 Flash API", "AI classification for 20,000 complaints", "20,000 calls", "0.40/call", 8000, "Hindi and English"),
        ("Phase 3", "AI and ML", "Azure Machine Learning", "First retraining run on real pilot data", "1 run", "8,000", 8000, "Gradient Boosting retraining"),
        ("Phase 3", "Communication", "WhatsApp Business API", "Messaging for 50-ward citizens", "20,000 conversations", "0.47/conversation", 9400, "Scaling cost"),
        ("Phase 3", "Communication", "SendGrid", "Department and HoD emails", "20,000 emails", "0.10/email", 2000, "Essentials plan"),
        ("Phase 3", "Infrastructure", "Azure Front Door CDN", "Officer dashboard CDN, domain, SSL", "0.5 month", "1,500", 750, "Dashboard goes live"),
    ]
    for li in phase3_items:
        write_line_item(*li)

    # Phase 4 subtotal
    write_phase_subtotal("Phase 4 total: Rs. 1,56,940", 156940)
    phase4_items = [
        ("Phase 4", "Infrastructure", "Azure Container Apps", "Full-scale auto-scaling for 272 wards", "0.5 month", "15,000", 7500, "Production with zone redundancy"),
        ("Phase 4", "Infrastructure", "Azure Database for PostgreSQL", "High-availability production database with geo-redundant backups and Indian data residency compliance", "0.5 month", "12,000", 6000, "Business Critical tier"),
        ("Phase 4", "Infrastructure", "Azure Blob Storage", "200GB photo storage at 1L complaints/month", "0.5 month", "4,000", 2000, "GRS geo-redundant"),
        ("Phase 4", "Infrastructure", "Azure Monitor", "Full production observability with custom dashboards", "0.5 month", "3,000", 1500, "90-day log retention"),
        ("Phase 4", "Infrastructure", "Azure Service Bus", "Premium tier guaranteed delivery at 1L/month", "0.5 month", "2,000", 1000, "Premium tier"),
        ("Phase 4", "Infrastructure", "Azure Front Door CDN", "Full production CDN with WAF and DDoS protection", "0.5 month", "3,000", 1500, "WAF enabled"),
        ("Phase 4", "AI and ML", "Gemini 2.0 Flash API", "Full-scale classification at 1,00,000 complaints/month", "1,00,000 calls", "0.40/call", 40000, "Largest AI cost"),
        ("Phase 4", "AI and ML", "Azure Machine Learning", "Second retraining on expanded real complaint dataset", "1 run", "8,000", 8000, "Accuracy improves with real data"),
        ("Phase 4", "Communication", "WhatsApp Business API", "Full Delhi citizen messaging at 1L conversations/month", "1,00,000 conversations", "0.47/conversation", 47000, "Peak communication cost"),
        ("Phase 4", "Communication", "SendGrid", "Full department and HoD email volume", "1,00,000 emails", "0.10/email", 10000, "Pro plan"),
    ]
    for li in phase4_items:
        write_line_item(*li)

    # Phase 5 recurring subtotal
    write_phase_subtotal("Phase 5 monthly recurring: Rs. 1,07,250/month", 107250)
    phase5_items = [
        ("Phase 5", "Infrastructure", "Azure Container Apps", "per month", "1 month", "15,000", 15000, "Recurring"),
        ("Phase 5", "Infrastructure", "Azure Database for PostgreSQL", "per month", "1 month", "12,000", 12000, "Recurring"),
        ("Phase 5", "Infrastructure", "Azure Blob Storage", "per month", "1 month", "4,000", 4000, "Recurring"),
        ("Phase 5", "Infrastructure", "Azure Monitor", "per month", "1 month", "3,000", 3000, "Recurring"),
        ("Phase 5", "Infrastructure", "Azure Service Bus", "per month", "1 month", "2,000", 2000, "Recurring"),
        ("Phase 5", "Infrastructure", "Azure Front Door CDN", "per month", "1 month", "3,000", 3000, "Recurring"),
        ("Phase 5", "AI and ML", "Gemini 2.0 Flash API", "per month", "1 month", "8,000", 8000, "Recurring"),
        ("Phase 5", "AI and ML", "Azure Machine Learning", "per month amortized", "1 month", "5,000", 5000, "Quarterly retraining"),
        ("Phase 5", "Communication", "WhatsApp Business API", "per month", "1 month", "47,000", 47000, "Recurring"),
        ("Phase 5", "Communication", "SendGrid", "per month", "1 month", "3,500", 3500, "Recurring"),
        ("Phase 5", "Infrastructure", "Azure backup and compliance", "per month", "1 month", "1,500", 1500, "Recurring"),
        ("Phase 5", "Infrastructure", "Azure Monitor log analytics", "per month", "1 month", "750", 750, "Recurring"),
    ]
    for li in phase5_items:
        write_line_item(*li)

    detail_data_end = row - 1
    _style_zebra_rows(ws, detail_data_start, detail_data_end, 1, 8)

    section3_end = row - 1
    _thick_border_box(ws, section3_start, section3_end, 1, 8)
    row += 2

    # SECTION 4 — UNIT ECONOMICS
    section4_start = row
    _style_section_header(ws, row, 1, 8, "SECTION 4 — UNIT ECONOMICS")
    row += 1

    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    ws.cell(row=row, column=1, value="Unit Economics and Value Justification").font = Font(
        name="Calibri", size=12, bold=True, color="1F3864"
    )
    ws.cell(row=row, column=1).alignment = ALIGN_LEFT
    for c in range(1, 9):
        ws.cell(row=row, column=c).border = THIN_BORDER
    row += 1

    ws.cell(row=row, column=1, value="Metric")
    ws.cell(row=row, column=2, value="Value")
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=8)
    _style_table_header(ws, row, 1, 8)
    row += 1

    unit_rows = [
        ("Total deployment cost Phases 1-4", 423500),
        ("Annual steady state cost Year 2", 1287000),
        ("Cost per ward per month at full scale", 393),
        ("Cost per complaint at full scale", 1.07),
        ("Citizens served estimate", 200000000),
        ("Cost per citizen per year", 0.64),
        ("Wards covered at full deployment", 272),
        ("Languages supported", "Hindi and English"),
        ("Complaints processed per year estimate", 1200000),
    ]

    unit_start = row
    for metric, value in unit_rows:
        ws.cell(row=row, column=1, value=metric)
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=8)
        c = ws.cell(row=row, column=2, value=value)
        if isinstance(value, (int, float)):
            if isinstance(value, float) and value < 10:
                c.number_format = "0.00"
            else:
                c.number_format = INDIAN_CURRENCY_FORMAT if "cost" in metric.lower() or "Rs." in str(value) else "#,##,##0"
            c.alignment = ALIGN_RIGHT
        else:
            c.alignment = ALIGN_LEFT
        for col in range(1, 9):
            ws.cell(row=row, column=col).border = THIN_BORDER
        row += 1
    unit_end = row - 1
    _style_zebra_rows(ws, unit_start, unit_end, 1, 8)

    row += 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row + 1, end_column=8)
    ws.cell(
        row=row,
        column=1,
        value=(
            "Cost per complaint of Rs. 1.07 includes AI classification, WhatsApp messaging, cloud infrastructure, "
            "email notifications, and ML-based auto-escalation -- delivered at a fraction of the cost of "
            "traditional call-centre based grievance systems."
        ),
    ).alignment = ALIGN_LEFT
    for rr in (row, row + 1):
        for c in range(1, 9):
            ws.cell(row=rr, column=c).border = THIN_BORDER
    section4_end = row + 1
    _thick_border_box(ws, section4_start, section4_end, 1, 8)

    # Apply global font and set widths
    _apply_font(ws)
    _set_col_widths(ws, min_width=12)

    # Row heights for top block
    ws.row_dimensions[1].height = 26
    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 18

    return wb


def main() -> Path:
    wb = build_workbook()
    out_path = Path(__file__).resolve().parent / OUTPUT_FILENAME
    try:
        wb.save(out_path)
        return out_path
    except PermissionError:
        # Common on Windows if the XLSX is open in Excel.
        fallback = out_path.with_name(out_path.stem + "_NEW" + out_path.suffix)
        wb.save(fallback)
        return fallback


if __name__ == "__main__":
    p = main()
    # Console totals (as required)
    phase1 = 115000
    phase2 = 95940
    phase3 = 55620
    phase4 = 156940
    grand_1_4 = phase1 + phase2 + phase3 + phase4
    print("Phase totals:")
    print(f"  Phase 1: {phase1:,}")
    print(f"  Phase 2: {phase2:,}")
    print(f"  Phase 3: {phase3:,}")
    print(f"  Phase 4: {phase4:,}")
    print(f"Grand total (Phases 1-4): {grand_1_4:,}")
    print(f"Created: {p}")

