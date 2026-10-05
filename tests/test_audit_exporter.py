"""Unit and integration tests for TKBI audit checklist generation."""

import pytest
from pathlib import Path
import openpyxl

from sustainmetric.server import generate_tkbi_audit_checklist
from sustainmetric.data.tkbi_sectors_catalog import TKBI_8_SECTORS, map_emiten_to_sectors


def test_tkbi_8_sectors_catalog_structure():
    assert len(TKBI_8_SECTORS) == 8
    required_sectors = [
        "Energi",
        "Konstruksi dan Real Estat",
        "Transportasi dan Pergudangan",
        "Pertanian, Kehutanan, dan Perikanan",
        "Manufaktur",
        "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi",
        "Informasi dan Komunikasi",
        "Aktivitas Profesional, Ilmiah, dan Teknis",
    ]
    for s in required_sectors:
        assert s in TKBI_8_SECTORS
        assert len(TKBI_8_SECTORS[s]["items"]) > 0


def test_sector_mapping():
    # Test geothermal maps to Energi
    mapped = map_emiten_to_sectors("Renewable Energy", "Geothermal power plant developer")
    assert "Energi" in mapped

    # Test coal mining maps to Energi
    mapped_coal = map_emiten_to_sectors("Coal", "Thermal coal mining operations")
    assert "Energi" in mapped_coal

    # Test property maps to Konstruksi dan Real Estat
    mapped_prop = map_emiten_to_sectors("Property", "Gedung apartemen dan real estate")
    assert "Konstruksi dan Real Estat" in mapped_prop


@pytest.mark.asyncio
async def test_generate_tkbi_audit_checklist_pgeo(tmp_path: Path):
    res = await generate_tkbi_audit_checklist(ticker="PGEO", output_dir=str(tmp_path))
    assert res["status"] == "SUCCESS"
    assert res["ticker"] == "PGEO"
    assert "PGEO_audit_TKBI.xlsx" in res["file_name"]

    file_path = Path(res["file_generated"])
    assert file_path.exists()

    # Load workbook and check sheet rows and headers
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    headers = [ws.cell(1, c).value for c in range(1, 13)]
    assert headers[0] == "Kode Emiten"
    assert headers[4] == "TSCID"
    assert headers[7] == "Jawaban AI"
    assert headers[9] == "Reasoning AI"

    # Verify rows populated
    assert ws.max_row >= 10
    first_data_row = [ws.cell(2, c).value for c in range(1, 13)]
    assert first_data_row[0] == "PGEO"
    assert first_data_row[7] in ["HIJAU", "TRANSISI", "TIDAK"]
    # Check that reasoning and feedback contain preliminary / unverified labels
    assert "[Skrining Awal Heuristik]" in str(first_data_row[9])
    assert "UNVERIFIED" in str(first_data_row[10])
    assert "PRELIMINARY_HEURISTIC" in str(first_data_row[11])


def test_evaluate_criterion_preliminary_and_unverified_labels():
    from sustainmetric.audit_exporter import evaluate_criterion_for_emiten
    mock_item = {
        "bab": "Pembangkitan Tenaga Listrik",
        "kbli": "35101",
        "tsc_id": "TSC-ENE-01",
        "tsc": "Life-cycle GHG < 100g CO2e/kWh",
        "bentuk_jawaban": ["HIJAU", "TRANSISI", "TIDAK"],
    }
    report = {
        "symbol": "PGEO",
        "overview": {"subsector": "Utilities", "description": "Geothermal power plant"},
        "financials": {},
    }
    eval_res = evaluate_criterion_for_emiten("PGEO", mock_item, report, [], [], consistency_score=75.0)

    assert eval_res["audit_tier"] == "PRELIMINARY_HEURISTIC"
    assert eval_res["verification_status"] == "UNVERIFIED"
    assert "https://sectors.app/company/PGEO" in eval_res["bukti"]
    assert "UNVERIFIED" in eval_res["bukti"]
    assert "[Skrining Awal Heuristik]" in eval_res["reasoning"]
    assert "PRELIMINARY_HEURISTIC" in eval_res["auditor_feedback"]
