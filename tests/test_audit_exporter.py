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
