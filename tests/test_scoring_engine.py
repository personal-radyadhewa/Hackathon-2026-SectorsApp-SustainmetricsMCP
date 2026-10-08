"""Unit tests for ScoringEngine 4-Quadrant math invariants."""

from sustainmetric.scoring_engine import ScoringEngine

def test_pgeo_evaluation_strong_fundamental_sustainable():
    # Green geothermal profile with solid cash flow
    overview = {"description": "Pertamina Geothermal Energy operates clean PLTP geothermal plants."}
    financials = {
        "operating_cash_flow": 3850000000000,
        "capital_expenditures": 2200000000000,
        "revenue": 6200000000000,
        "roa_pct": 5.33,
        "total_debt": 14000000000000,
        "cash_and_equivalents": 8500000000000,
        "ebitda": 4900000000000,
    }
    news = [{"title": "PGEO expands Lumut Balai PLTP", "summary": "Adding clean geothermal capacity."}]
    tkbi_matches = [{"activity": "Electricity Generation from Geothermal", "criteria_level": "Hijau", "similarity_score": 0.88}]

    eval_result = ScoringEngine.evaluate(overview, financials, news, tkbi_matches)
    assert eval_result["quadrant_code"] == "Q1"
    assert eval_result["quadrant"] == "STRONG FUNDAMENTAL AND SUSTAINABLE"
    assert eval_result["quadrant_label"] == "High Green & High Viability"
    assert eval_result["consistency_score"] >= 60.0
    assert eval_result["viability_score"] >= 60.0

def test_adro_evaluation_greenwashing_risk_zone():
    # High cash generation, but thermal coal operations
    overview = {"description": "Adaro is an integrated coal mining and thermal coal logistics operator."}
    financials = {
        "operating_cash_flow": 28500000000000,
        "capital_expenditures": 9800000000000,
        "revenue": 98000000000000,
        "roa_pct": 15.6,
        "total_debt": 22000000000000,
        "cash_and_equivalents": 48000000000000,
        "ebitda": 38000000000000,
    }
    news = [{"title": "Adaro posts record coal shipments", "summary": "Thermal coal demand remains elevated."}]
    tkbi_matches = [{"activity": "Coal Extraction", "criteria_level": "Merah", "similarity_score": 0.35}]

    eval_result = ScoringEngine.evaluate(overview, financials, news, tkbi_matches)
    assert eval_result["quadrant_code"] == "Q3"
    assert eval_result["quadrant"] == "GREENWASHING RISK ZONE"
    assert eval_result["quadrant_label"] == "Low Green & High Viability"
    assert eval_result["consistency_score"] < 60.0
    assert eval_result["viability_score"] >= 60.0

def test_bren_evaluation_sustainable_high_financial_risk():
    # Green profile but heavy debt / lower capex coverage
    overview = {"description": "Barito Renewables Energy develops wind and geothermal assets."}
    financials = {
        "operating_cash_flow": 3200000000000,
        "capital_expenditures": 4800000000000, # OCF < Capex -> coverage < 1.0
        "revenue": 9100000000000,
        "roa_pct": 2.91,
        "total_debt": 42000000000000,
        "cash_and_equivalents": 3800000000000,
        "ebitda": 4500000000000,
    }
    news = [{"title": "BREN acquires Sidrap wind farm", "summary": "Expanding clean energy footprint."}]
    tkbi_matches = [{"activity": "Electricity Generation from Wind", "criteria_level": "Hijau", "similarity_score": 0.85}]

    eval_result = ScoringEngine.evaluate(overview, financials, news, tkbi_matches)
    assert eval_result["quadrant_code"] == "Q2"
    assert eval_result["quadrant"] == "SUSTAINABLE BUT HIGH FINANCIAL RISK"
    assert eval_result["quadrant_label"] == "High Green & Low Viability"
    assert eval_result["consistency_score"] >= 60.0
    assert eval_result["viability_score"] < 60.0

def test_bumi_evaluation_not_considered():
    # Distressed coal operator with negative ROA / low cash flow
    overview = {"description": "Bumi Resources is engaged in thermal coal extraction."}
    financials = {
        "operating_cash_flow": 1100000000000,
        "capital_expenditures": 1900000000000,
        "revenue": 21000000000000,
        "roa_pct": -0.69,
        "total_debt": 28000000000000,
        "cash_and_equivalents": 1200000000000,
        "ebitda": 2300000000000,
    }
    news = [{"title": "Bumi Resources faces margin pressure", "summary": "Lower coal prices impact cash flow."}]
    tkbi_matches = [{"activity": "Coal Extraction", "criteria_level": "Merah", "similarity_score": 0.20}]

    eval_result = ScoringEngine.evaluate(overview, financials, news, tkbi_matches)
    assert eval_result["quadrant_code"] == "Q4"
    assert eval_result["quadrant"] == "NOT CONSIDERED"
    assert eval_result["quadrant_label"] == "Low Green & Low Viability"
    assert eval_result["consistency_score"] < 60.0
    assert eval_result["viability_score"] < 60.0


def test_evaluate_activity_3_tier_states():
    # 1. Fossil unabated -> OUT OF SCOPE
    act_coal = ScoringEngine.evaluate_activity(
        activity_name="Pertambangan Batubara Termal",
        sector="Energi",
        is_fossil_unabated=True,
    )
    assert act_coal["status"] == "TKBI NON-ELIGIBLE / OUT OF SCOPE"
    assert act_coal["essential_criteria"]["dnsh"] is False

    # 2. Transition tech with RMT remedial measure -> TRANSISI-INTERIM
    act_interim = ScoringEngine.evaluate_activity(
        activity_name="Smelter Nikel Transisi",
        sector="Manufaktur",
        is_fossil_unabated=False,
        tsc_met=True,
        is_transition_tech=True,
        dnsh_met=False,
        has_rmt_plan=True,
        social_aspects_met=True,
    )
    assert act_interim["status"] == "TRANSISI-INTERIM"
    assert act_interim["essential_criteria"]["rmt"] is True

    # 3. Clean tech meeting all EC -> HIJAU
    act_green = ScoringEngine.evaluate_activity(
        activity_name="PLTP Geothermal",
        sector="Energi",
        is_fossil_unabated=False,
        tsc_met=True,
        dnsh_met=True,
        social_aspects_met=True,
    )
    assert act_green["status"] == "HIJAU"


def test_aggregate_entity_proportional_formula():
    activities = [
        {"activity_name": "Geothermal", "status": "HIJAU"},
        {"activity_name": "Transisi Grid", "status": "TRANSISI"},
        {"activity_name": "Proyek RMT", "status": "TRANSISI-INTERIM"},
        {"activity_name": "Thermal Coal", "status": "TKBI NON-ELIGIBLE / OUT OF SCOPE"},
    ]
    # Weights by revenue share: 40% Hijau, 20% Transisi, 10% Interim, 30% Coal
    weights = [40.0, 20.0, 10.0, 30.0]
    agg = ScoringEngine.aggregate_entity(activities, weights)

    assert agg["pct_hijau"] == 40.0
    assert agg["pct_transisi"] == 20.0
    assert agg["pct_transisi_interim"] == 10.0
    assert agg["pct_out_of_scope"] == 30.0
    assert agg["total_tkbi_aligned"] == 70.0
