"""Unit tests for TKBIVectorStore semantic retrieval."""

import logging
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest
from sustainmetric.tkbi_vector_store import TKBIVectorStore, VECTOR_DIM

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
    assert top["similarity_score"] > 0.15


def test_tkbi_vector_store_coal_search():
    store = TKBIVectorStore(db_path=TEST_DB_PATH)
    results = store.search("coal early retirement PLTU pensiun dini", top_k=1)
    assert len(results) == 1
    assert "Coal" in results[0]["subsector"]
    assert results[0]["criteria_level"] == "Transisi"
    assert results[0]["similarity_score"] > 0.15


def test_tkbi_vector_store_banking_search():
    store = TKBIVectorStore(db_path=TEST_DB_PATH)
    results = store.search("sustainable finance green banking credit portfolio", top_k=1)
    assert len(results) == 1
    assert "Banking" in results[0]["subsector"]
    assert results[0]["similarity_score"] > 0.15


def test_tkbi_vector_store_unrelated_query_scores_low():
    store = TKBIVectorStore(db_path=TEST_DB_PATH)
    # Target query should match geothermal
    geo_res = store.search("geothermal power plant PLTP emissions", top_k=1)
    # Completely unrelated query should score much lower, near 0.0
    unrelated_res = store.search("completely unrelated chocolate ice cream dessert recipe", top_k=1)
    assert len(geo_res) == 1
    assert len(unrelated_res) == 1
    assert unrelated_res[0]["similarity_score"] < 0.10
    assert geo_res[0]["similarity_score"] > unrelated_res[0]["similarity_score"] * 2


def test_tkbi_vector_store_openai_live_mocked(caplog):
    test_key = "sk-mocked-test-key-12345"
    mock_vec = [0.1] * VECTOR_DIM

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"embedding": mock_vec}]}

    with patch("httpx.post", return_value=mock_resp) as mock_post:
        with caplog.at_level(logging.DEBUG):
            store = TKBIVectorStore(db_path=TEST_DB_PATH, openai_api_key=test_key)
            emb = store.get_embedding("test query text")

            # Check that Bearer auth was sent
            assert mock_post.called
            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["headers"]["Authorization"] == f"Bearer {test_key}"
            assert len(emb) == VECTOR_DIM

            # Invariant: Secret key must never appear in logs
            for record in caplog.records:
                assert test_key not in record.message


def test_tkbi_vector_store_openai_failure_fallback_and_no_leak(caplog):
    secret_key = "sk-super-secret-key-999"

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"

    with patch("httpx.post", return_value=mock_resp):
        with caplog.at_level(logging.DEBUG):
            store = TKBIVectorStore(db_path=TEST_DB_PATH, openai_api_key=secret_key)
            emb = store.get_embedding("fallback query")

            # Must fall back to deterministic offline embedding
            assert len(emb) == VECTOR_DIM
            assert any(val != 0.0 for val in emb)

            # Invariant: Secret key must never appear in logs
            for record in caplog.records:
                assert secret_key not in record.message
