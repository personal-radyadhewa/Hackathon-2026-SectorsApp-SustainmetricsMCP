"""Unit tests for TKBIVectorStore semantic retrieval."""

import pytest
import shutil
from pathlib import Path
from sustainmetric.tkbi_vector_store import TKBIVectorStore

TEST_DB_PATH = Path(".cache/test_tkbi_vectors.db")

@pytest.fixture(autouse=True)
def clean_test_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_tkbi_vector_store_seeding_and_search():
    store = TKBIVectorStore(db_path=TEST_DB_PATH)
    results = store.search("geothermal power plant PLTP emissions", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "Geothermal" in top["subsector"]
    assert top["criteria_level"] == "Hijau"
    assert top["similarity_score"] > 0.5

def test_tkbi_vector_store_coal_search():
    store = TKBIVectorStore(db_path=TEST_DB_PATH)
    results = store.search("coal early retirement PLTU pensiun dini", top_k=1)
    assert len(results) == 1
    assert "Coal" in results[0]["subsector"]
    assert results[0]["criteria_level"] == "Transisi"

def test_tkbi_vector_store_banking_search():
    store = TKBIVectorStore(db_path=TEST_DB_PATH)
    results = store.search("sustainable finance green banking credit portfolio", top_k=1)
    assert len(results) == 1
    assert "Banking" in results[0]["subsector"]
