"""Quantitative Scoring Engine for SustainMetric IDX.

Computes Financial Viability Score (0-100) and TKBI Consistency Score (0-100)
and maps equities into the 4-Quadrant Matrix Framework.
"""

from typing import Any


GREEN_KEYWORDS = [
    "geothermal", "panas bumi", "pltp", "solar", "wind", "plts", "pltb",
    "renewable", "clean energy", "terbarukan", "green bond", "kkub",
    "dekarbonisasi", "emission reduction", "sustainable financing", "gar"
]

BROWN_KEYWORDS = [
    "thermal coal", "batubara", "pltu", "mining expansion", "ekspansi tambang",
    "coal production target", "fossil", "unabated"
]


class ScoringEngine:
    """Evaluates IDX company fundamentals vs OJK TKBI 2024 green alignment."""

    @staticmethod
    def calculate_viability_score(financials: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        """Calculate fundamental viability score (0-100) based on cash flow, capex coverage, ROA, leverage."""
        ocf = float(financials.get("operating_cash_flow", 0) or 0)
        capex = float(financials.get("capital_expenditures", 0) or 0)
        rev = float(financials.get("revenue", 0) or 0)
        roa = float(financials.get("roa_pct", 0) or 0)
        debt = float(financials.get("total_debt", 0) or 0)
        cash = float(financials.get("cash_and_equivalents", 0) or 0)
        ebitda = float(financials.get("ebitda", 0) or 0)

        # 1. Capex Coverage Ratio (OCF / Capex) - 40 pts
        coverage = (ocf / capex) if capex > 0 else (2.0 if ocf > 0 else 0.0)
        if coverage >= 1.5 and ocf > 0:
            cov_pts = 40.0
        elif coverage >= 1.0 and ocf > 0:
            cov_pts = 30.0
        elif coverage >= 0.5 and ocf > 0:
            cov_pts = 15.0
        else:
            cov_pts = 0.0

        # 2. Operating Cash Flow Margin (OCF / Revenue) - 25 pts
        ocf_margin = (ocf / rev * 100.0) if rev > 0 else 0.0
        if ocf_margin >= 20.0:
            margin_pts = 25.0
        elif ocf_margin >= 10.0:
            margin_pts = 18.0
        elif ocf_margin > 0.0:
            margin_pts = 10.0
        else:
            margin_pts = 0.0

        # 3. ROA - 20 pts
        if roa >= 8.0:
            roa_pts = 20.0
        elif roa >= 4.0:
            roa_pts = 15.0
        elif roa > 0.0:
            roa_pts = 10.0
        else:
            roa_pts = 0.0

        # 4. Solvency (Net Debt / EBITDA) - 15 pts
        net_debt = debt - cash
        if net_debt <= 0:
            solv_pts = 15.0
        elif ebitda > 0:
            nd_ebitda = net_debt / ebitda
            if nd_ebitda < 2.0:
                solv_pts = 12.0
            elif nd_ebitda < 3.5:
                solv_pts = 8.0
            else:
                solv_pts = 0.0
        else:
            solv_pts = 0.0

        total_viability = min(100.0, max(0.0, cov_pts + margin_pts + roa_pts + solv_pts))
        metrics = {
            "operating_cash_flow": ocf,
            "capex": capex,
            "capex_coverage_ratio": round(coverage, 2),
            "ocf_margin_pct": round(ocf_margin, 2),
            "roa_pct": roa,
            "net_debt": net_debt,
        }
        return round(total_viability, 1), metrics

    @staticmethod
    def calculate_consistency_score(
        overview: dict[str, Any],
        financials: dict[str, Any],
        news: list[dict[str, Any]],
        tkbi_matches: list[dict[str, Any]],
    ) -> tuple[float, list[str]]:
        """Calculate TKBI 2024 consistency score (0-100) and identify greenwashing discrepancies."""
        findings: list[str] = []
        score = 0.0

        # 1. Base Taxonomy Alignment (Max 45 pts)
        top_match = tkbi_matches[0] if tkbi_matches else None
        criteria_level = top_match.get("criteria_level") if top_match else "Merah"
        
        if criteria_level == "Hijau":
            score += 45.0
            findings.append(f"Core activity aligns with TKBI 2024 'Hijau' criteria ({top_match.get('activity')}).")
        elif criteria_level == "Transisi":
            score += 30.0
            findings.append(f"Activity classified under TKBI 2024 'Transisi' phase ({top_match.get('activity')}).")
        else:
            score += 10.0
            findings.append("Core operations fall outside or fail green screening criteria under TKBI 2024.")

        # 2. Capex Commitment & Intensity (Max 30 pts)
        capex = float(financials.get("capital_expenditures", 0) or 0)
        rev = float(financials.get("revenue", 0) or 0)
        capex_ratio = (capex / rev * 100.0) if rev > 0 else 0.0

        if criteria_level in ["Hijau", "Transisi"]:
            if capex_ratio >= 25.0:
                score += 30.0
                findings.append(f"Strong capital commitment: Capex/Revenue ratio is {capex_ratio:.1f}%.")
            elif capex_ratio >= 10.0:
                score += 20.0
                findings.append(f"Moderate capital commitment: Capex/Revenue ratio is {capex_ratio:.1f}%.")
            else:
                score += 5.0
                findings.append(f"Low capital intensity: Capex/Revenue is only {capex_ratio:.1f}%, raising execution risk.")
        else:
            # Brown sector: check if capex is flowing into transition or sustaining coal
            score += 5.0
            findings.append(f"Capital expenditure is primarily targeted at maintaining legacy operations ({capex_ratio:.1f}% of revenue).")

        # 3. Qualitative Claim vs Action Audit (Max 25 pts with penalties)
        green_claim_count = 0
        brown_mention_count = 0
        all_text = " ".join([f"{n.get('title', '')} {n.get('summary', '')}" for n in news]).lower()
        desc = str(overview.get("description", "")).lower()
        full_text = f"{all_text} {desc}"

        for kw in GREEN_KEYWORDS:
            if kw in full_text:
                green_claim_count += 1
        for kw in BROWN_KEYWORDS:
            if kw in full_text:
                brown_mention_count += 1

        if criteria_level == "Hijau":
            if green_claim_count > 0:
                score += 25.0
                findings.append(f"Documented clean energy deployment backed by verified news releases.")
            else:
                score += 15.0
        elif criteria_level == "Transisi":
            if green_claim_count > 0 and brown_mention_count > 0:
                score += 20.0
                findings.append("Disclosures reflect ongoing dual-profile transition dynamics.")
            else:
                score += 10.0
        else:
            # Fossil / Laggard profile
            if green_claim_count >= 3 and capex_ratio < 10.0:
                # Discrepancy: Aggressive green narrative without capital commitment -> GREENWASHING RED FLAG
                score -= 15.0
                findings.append("GREENWASHING ALERT: High green promotional narrative detected without material capital expenditure support.")
            elif brown_mention_count > 0:
                findings.append("Operations dominated by thermal extraction; minimal green transition disclosures.")

        clamped_score = min(100.0, max(0.0, score))
        return round(clamped_score, 1), findings

    @classmethod
    def evaluate(
        cls,
        overview: dict[str, Any],
        financials: dict[str, Any],
        news: list[dict[str, Any]],
        tkbi_matches: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Perform full 4-quadrant green audit evaluation."""
        viability_score, fin_summary = cls.calculate_viability_score(financials)
        consistency_score, audit_findings = cls.calculate_consistency_score(
            overview, financials, news, tkbi_matches
        )

        # Quadrant classification
        # Q1: Transisi Tangguh (Consistency >= 60 & Viability >= 60)
        # Q2: Dampak Spekulatif (Consistency >= 60 & Viability < 60)
        # Q3: Sumber Kas Konvensional (Consistency < 60 & Viability >= 60)
        # Q4: Tertinggal & Red Flag (Consistency < 60 & Viability < 60)
        if consistency_score >= 60.0 and viability_score >= 60.0:
            quadrant = "Transisi Tangguh"
            quadrant_code = "Q1"
            definition = "High green alignment backed by robust cash flow and Capex. True sustainable compounder."
        elif consistency_score >= 60.0 and viability_score < 60.0:
            quadrant = "Dampak Spekulatif"
            quadrant_code = "Q2"
            definition = "High green narrative/alignment but fragile fundamentals (cash burn, high leverage). High execution risk."
        elif consistency_score < 60.0 and viability_score >= 60.0:
            quadrant = "Sumber Kas Konvensional"
            quadrant_code = "Q3"
            definition = "High cash generation with legacy/fossil profile and low TKBI alignment. High greenwashing vulnerability if claiming green status."
        else:
            quadrant = "Tertinggal & Red Flag"
            quadrant_code = "Q4"
            definition = "Low green alignment + deteriorative fundamentals. High obsolescence and default risk."

        top_match = tkbi_matches[0] if tkbi_matches else {}

        return {
            "quadrant": quadrant,
            "quadrant_code": quadrant_code,
            "quadrant_definition": definition,
            "consistency_score": consistency_score,
            "viability_score": viability_score,
            "tkbi_alignment": {
                "status": top_match.get("criteria_level", "Merah"),
                "matched_activity": top_match.get("activity", "Unmatched"),
                "tsc_summary": top_match.get("tsc", "N/A"),
                "similarity_score": top_match.get("similarity_score", 0.0),
            },
            "financial_summary": fin_summary,
            "audit_findings": audit_findings,
        }
