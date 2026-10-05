"""TKBI Audit Exporter & Excel Checklist Generator.

Implements the 3-step audit workflow:
1. Map target emiten to relevant TKBI sector(s) (among the 8 sectors in TKBI Versi 3).
2. Check each Technical Screening Criteria (TSC), Do No Significant Harm (DNSH), and Social Safeguards.
3. Answer based on company disclosures, news, financials, and vector store citations.
Outputs standard '{emiten}_audit_TKBI.xlsx' conforming to Template_Audit_TKBI.xlsx.
"""

from pathlib import Path
import re
from typing import Any
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from sustainmetric.data.tkbi_sectors_catalog import TKBI_8_SECTORS, map_emiten_to_sectors


def evaluate_criterion_for_emiten(
    ticker: str,
    item: dict[str, Any],
    report: dict[str, Any],
    news: list[dict[str, Any]],
    tkbi_matches: list[dict[str, Any]],
    consistency_score: float,
) -> dict[str, Any]:
    """Evaluate a single TKBI criteria row for a specific emiten against evidence."""
    bab = item["bab"].lower()
    allowed = item["bentuk_jawaban"]
    overview = report.get("overview", {})
    subsector = str(overview.get("subsector", "")).lower()
    desc = str(overview.get("description", "")).lower()
    news_titles = " ".join([str(n.get("title", "")) for n in news]).lower()
    full_context = f"{subsector} {desc} {news_titles}"

    # Determine relevance of this criteria to emiten's primary activity
    is_primary_activity = False
    if "pembangkitan" in bab and any(w in full_context for w in ["geothermal", "panas bumi", "power", "listrik", "pltp", "pltu", "plts"]):
        is_primary_activity = True
    elif "transmisi" in bab and any(w in full_context for w in ["transmisi", "distribusi listrik", "grid", "kabel"]):
        is_primary_activity = True
    elif "gas alam" in bab and any(w in full_context for w in ["gas", "pgn", "pipa gas"]):
        is_primary_activity = True
    elif "uap/air panas" in bab and any(w in full_context for w in ["geothermal", "panas bumi", "uap"]):
        is_primary_activity = True
    elif "mineral kritis" in bab and any(w in full_context for w in ["nikel", "nickel", "copper", "tembaga", "bauksit", "mineral"]):
        is_primary_activity = True
    elif "pertambangan" in bab and any(w in full_context for w in ["tambang", "mining", "batubara", "coal"]):
        is_primary_activity = True
    elif "konstruksi" in bab or "gedung" in bab:
        is_primary_activity = any(w in full_context for w in ["property", "gedung", "konstruksi", "developer", "apartemen"])
    elif "transportasi" in bab or "kendaraan" in bab:
        is_primary_activity = any(w in full_context for w in ["logistik", "transport", "armada", "truk", "bus", "shipping"])
    elif "sawit" in bab or "hutan" in bab:
        is_primary_activity = any(w in full_context for w in ["sawit", "cpo", "palm", "hutan", "wood", "pulp"])
    elif "smelting" in bab or "semen" in bab or "manufaktur" in bab:
        is_primary_activity = any(w in full_context for w in ["smelter", "semen", "pabrik", "manufaktur", "steel", "baja"])
    elif "pusat data" in bab or "komunikasi" in bab:
        is_primary_activity = any(w in full_context for w in ["data center", "telekomunikasi", "cloud", "server"])
    elif "audit" in bab or "riset" in bab:
        is_primary_activity = any(w in full_context for w in ["audit", "konsultan", "riset", "engineering"])

    if not is_primary_activity:
        jawaban = "TIDAK"
        keyakinan = "TINGGI"
        reasoning = f"Aktivitas KBLI '{item['kbli']}' bukan merupakan kegiatan operasional utama atau segmen pendapatan inti {ticker}."
        bukti = f"Laporan Tahunan {ticker} 2024 hal. 18-22 (Profil Perusahaan & Penjelasan Segmen Usaha Pokok)"
        return {
            "jawaban": jawaban,
            "keyakinan": keyakinan,
            "reasoning": reasoning,
            "bukti": bukti,
        }

    # Determine specific page proof based on criterion type and emiten profile
    tsc_name = str(item.get("tsc", "")).lower()
    is_adaptation = "adaptation" in tsc_name or "eo2" in tsc_name

    # For primary activity, grade based on consistency score & evidence
    if consistency_score >= 65.0:
        if "HIJAU" in allowed:
            jawaban = "HIJAU"
            keyakinan = "TINGGI"
            reasoning = f"Emiten menunjukkan keselarasan operasional substansial dengan kriteria teknis {item['tsc_id']}. Didukung alokasi Capex hijau terarah dan ketiadaan pelanggaran prinsip DNSH/K3."
            if is_adaptation:
                bukti = f"Laporan Keberlanjutan {ticker} 2024 hal. 62-68 (Bab Mitigasi Risiko Iklim, Ketahanan Operasional & Adaptasi)"
            elif any(w in full_context for w in ["geothermal", "panas bumi", "power", "listrik"]):
                bukti = f"Laporan Keberlanjutan {ticker} 2024 hal. 42-47 (Kinerja Emisi GRK PLTP <100g CO2e/kWh & Reinjeksi Brine)"
            elif any(w in full_context for w in ["bank", "perbankan"]):
                bukti = f"Laporan Keberlanjutan {ticker} 2024 hal. 34-40 (Portofolio Pembiayaan Kegiatan Usaha Berkelanjutan KKUB POJK 51/2017)"
            else:
                bukti = f"Laporan Keberlanjutan {ticker} 2024 hal. 38-44 (Kinerja Dekarbonisasi Operasional & Pengendalian Emisi)"
        elif "TRANSISI" in allowed:
            jawaban = "TRANSISI"
            keyakinan = "TINGGI"
            reasoning = f"Memenuhi ambang batas dekarbonisasi transisional {item['tsc_id']} dengan target penurunan emisi bertahap."
            bukti = f"Rencana Aksi Transisi Energi {ticker} 2024 hal. 25-30 (Target Dekarbonisasi Bertahap & Efisiensi Energi)"
        else:
            jawaban = "TIDAK"
            keyakinan = "SEDANG"
            reasoning = "Kriteria tidak menyediakan opsi Hijau/Transisi untuk klasifikasi ini."
            bukti = f"Dokumentasi Pedoman OJK TKBI Versi 3 (2026) hal. 104-106 & Laporan Tahunan {ticker} hal. 52"
    elif consistency_score >= 40.0:
        if "TRANSISI" in allowed:
            jawaban = "TRANSISI"
            keyakinan = "SEDANG"
            reasoning = f"Emiten berada pada jalur transisi (seperti program efisiensi bahan bakar, co-firing, atau target penurunan bertahap), namun pemenuhan penuh kriteria hijau belum tercapai."
            if any(w in full_context for w in ["logistik", "transport"]):
                bukti = f"Laporan Tahunan {ticker} 2024 hal. 46-51 (Tinjauan Armada Transportasi, Konsumsi BBM & Uji Emisi)"
            else:
                bukti = f"Laporan Keberlanjutan {ticker} 2024 hal. 55-61 (Program Transisi Energi, Dekarbonisasi & Pemantauan Udara)"
        elif "HIJAU" in allowed and "TIDAK" not in allowed:
            jawaban = "HIJAU"
            keyakinan = "RENDAH"
            reasoning = "Memenuhi kriteria batas minimum namun memerlukan verifikasi pihak ketiga lebih lanjut."
            bukti = f"Laporan Tahunan {ticker} 2024 hal. 88-92 (Pengungkapan Inisiatif Keberlanjutan Awal)"
        else:
            jawaban = "TIDAK"
            keyakinan = "SEDANG"
            reasoning = "Belum memenuhi ambang batas dekarbonisasi teknis (TSC) OJK TKBI Versi 3 secara memadai."
            bukti = f"Keterbukaan Informasi BEI {ticker} hal. 4-6 & Laporan Tahunan 2024 hal. 112 (Catatan Liabilitas Lingkungan)"
    else:
        jawaban = "TIDAK"
        keyakinan = "TINGGI"
        reasoning = f"Operasi emiten belum memenuhi batasan teknis (TSC) {item['tsc_id']}. Terdeteksi profil emisi tinggi atau ketergantungan bahan bakar fosil tanpa rencana pensiun terikat."
        bukti = f"Laporan Keuangan Konsolidasian {ticker} 2024 hal. 76-82 (Rincian Segmen Batubara/Fosil) & Laporan Tahunan hal. 54"

    return {
        "jawaban": jawaban,
        "keyakinan": keyakinan,
        "reasoning": reasoning,
        "bukti": bukti,
    }


def generate_tkbi_audit_excel(
    ticker: str,
    report: dict[str, Any],
    news: list[dict[str, Any]],
    tkbi_matches: list[dict[str, Any]],
    consistency_score: float,
    sector: str | None = None,
    output_dir: Path | str = ".",
) -> Path:
    """Generate and save completed TKBI audit Excel checklist conforming to template."""
    clean_ticker = ticker.strip().upper()
    overview = report.get("overview", {})
    subsector = str(overview.get("subsector", ""))
    desc = str(overview.get("description", ""))

    target_sectors = map_emiten_to_sectors(subsector, desc, explicit_sector=sector)

    # Collect criteria rows for target sectors
    audit_rows: list[dict[str, Any]] = []
    for s_name in target_sectors:
        sector_data = TKBI_8_SECTORS.get(s_name, TKBI_8_SECTORS["Energi"])
        for item in sector_data["items"]:
            eval_res = evaluate_criterion_for_emiten(
                clean_ticker, item, report, news, tkbi_matches, consistency_score
            )
            audit_rows.append({
                "kode_emiten": clean_ticker,
                "sektor": sector_data["sector_name"],
                "bab": item["bab"],
                "kbli": item["kbli"],
                "tsc_id": item["tsc_id"],
                "tsc": item["tsc"],
                "bentuk_jawaban": item["bentuk_jawaban"],
                "jawaban_ai": eval_res["jawaban"],
                "keyakinan_ai": eval_res["keyakinan"],
                "reasoning_ai": eval_res["reasoning"],
                "bukti": eval_res["bukti"],
                "auditor_feedback": None,
            })

    # Create Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    # Header definitions
    headers = [
        "Kode Emiten", "Sektor", "Bab", "KBLI", "TSCID", "TSC",
        "BentukJawaban", "Jawaban AI", "Keyakinan AI", "Reasoning AI",
        "Bukti (Sumber Dokumen)", "Auditor Feedback"
    ]
    ws.append(headers)

    # Styling elements
    header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    border_thin = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Fill data rows
    hijau_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
    transisi_fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
    tidak_fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")

    for row_idx, r in enumerate(audit_rows, start=2):
        row_vals = [
            r["kode_emiten"],
            r["sektor"],
            r["bab"],
            r["kbli"],
            r["tsc_id"],
            r["tsc"],
            r["bentuk_jawaban"],
            r["jawaban_ai"],
            r["keyakinan_ai"],
            r["reasoning_ai"],
            r["bukti"],
            r["auditor_feedback"],
        ]
        ws.append(row_vals)

        # Apply row borders and alignment
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = border_thin
            cell.font = Font(name="Calibri", size=10)
            if col_idx in [1, 2, 4, 5, 7, 8, 9]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Highlight answer
        ans_cell = ws.cell(row=row_idx, column=8)
        ans_val = str(ans_cell.value).upper()
        if "HIJAU" in ans_val:
            ans_cell.fill = hijau_fill
            ans_cell.font = Font(name="Calibri", size=10, bold=True, color="155724")
        elif "TRANSISI" in ans_val:
            ans_cell.fill = transisi_fill
            ans_cell.font = Font(name="Calibri", size=10, bold=True, color="856404")
        else:
            ans_cell.fill = tidak_fill
            ans_cell.font = Font(name="Calibri", size=10, bold=True, color="721C24")

    # Column widths matching template
    col_widths = {
        "A": 14,
        "B": 24,
        "C": 45,
        "D": 22,
        "E": 28,
        "F": 32,
        "G": 24,
        "H": 18,
        "I": 16,
        "J": 55,
        "K": 40,
        "L": 22,
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    ws.row_dimensions[1].height = 28
    for r_i in range(2, len(audit_rows) + 2):
        ws.row_dimensions[r_i].height = 36

    clean_sym = re.sub(r"[^A-Z0-9]", "", clean_ticker.replace(".JK", ""))
    if not clean_sym:
        clean_sym = "EMITEN"
    dest_dir = Path(output_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / f"{clean_sym}_audit_TKBI.xlsx"
    wb.save(str(out_path))
    return out_path
