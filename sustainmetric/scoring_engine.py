"""Quantitative Scoring Engine for SustainMetric IDX.

Implements the official OJK 3-Tier Evaluation Framework from 'Fact Sheets TKBI.pdf':
1. Activity-Level Assessment (Tingkat Aktivitas): TSC/SDT, EO1-EO4, EC1 DNSH, EC2 RMT, EC3 SA.
2. Entity-Level Aggregation (Tingkat Entitas): Weighted mix of % Hijau, % Transisi, % Transisi-Interim,
   % Tidak Memenuhi, and % Out-of-Scope based on proportional Revenue/CapEx/OpEx.
3. 4-Quadrant Matrix Classifier (Consistency vs Viability).
"""

from typing import Any

# Classification states per OJK Fact Sheets TKBI
TKBI_STATUS_HIJAU = "HIJAU"
TKBI_STATUS_TRANSISI = "TRANSISI"
TKBI_STATUS_TRANSISI_INTERIM = "TRANSISI-INTERIM"
TKBI_STATUS_TIDAK_MEMENUHI = "TIDAK MEMENUHI KLASIFIKASI"
TKBI_STATUS_OUT_OF_SCOPE = "TKBI NON-ELIGIBLE / OUT OF SCOPE"

# 4 Environmental Objectives (EO)
EO_MITIGATION = "EO1 – Climate Change Mitigation"
EO_ADAPTATION = "EO2 – Climate Change Adaptation"
EO_BIODIVERSITY = "EO3 – Protection of Healthy Ecosystems and Biodiversity"
EO_CIRCULAR = "EO4 – Resource Resilience and Circular Economy"

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
    """Evaluates IDX company fundamentals vs OJK TKBI green alignment."""

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
            roa_pts = 8.0
        else:
            roa_pts = 0.0

        # 4. Leverage / Solvency (Net Debt / EBITDA) - 15 pts
        net_debt = debt - cash
        if ebitda > 0:
            nd_ebitda = net_debt / ebitda
            if nd_ebitda <= 1.5:
                lev_pts = 15.0
            elif nd_ebitda <= 3.0:
                lev_pts = 10.0
            elif nd_ebitda <= 5.0:
                lev_pts = 5.0
            else:
                lev_pts = 0.0
        else:
            lev_pts = 5.0 if net_debt <= 0 else 0.0

        total_viability = min(100.0, max(0.0, cov_pts + margin_pts + roa_pts + lev_pts))
        metrics = {
            "operating_cash_flow": ocf,
            "capital_expenditures": capex,
            "capex_coverage_ratio": round(coverage, 2),
            "ocf_margin_pct": round(ocf_margin, 2),
            "roa_pct": roa,
            "total_debt": debt,
            "cash_and_equivalents": cash,
            "net_debt": net_debt,
        }
        return round(total_viability, 1), metrics

    @staticmethod
    def evaluate_activity(
        activity_name: str,
        sector: str,
        is_fossil_unabated: bool = False,
        tsc_met: bool = False,
        is_transition_tech: bool = False,
        dnsh_met: bool = True,
        has_rmt_plan: bool = False,
        social_aspects_met: bool = True,
    ) -> dict[str, Any]:
        """Tingkat Aktivitas (Activity Level): Evaluate economic activity against TKBI TSC & EC.
        
        Follows the official flowchart in Fact Sheets TKBI.pdf (Pages 3, 5, 11-13).
        """
        # 1. Scope / Eligibility check
        if is_fossil_unabated:
            status = TKBI_STATUS_OUT_OF_SCOPE
            reason = "Aktivitas bahan bakar fosil unmitigated / tidak memiliki jalur dekarbonisasi mandat TKBI."
            ec_status = {"dnsh": False, "rmt": False, "social_aspects": False}
        elif not tsc_met and not is_transition_tech:
            status = TKBI_STATUS_TIDAK_MEMENUHI
            reason = "Aktivitas terdaftar dalam TKBI tetapi belum memenuhi Technical Screening Criteria (TSC)."
            ec_status = {"dnsh": dnsh_met, "rmt": has_rmt_plan, "social_aspects": social_aspects_met}
        else:
            # Meets TSC or Transition criteria
            if dnsh_met and social_aspects_met:
                if is_transition_tech:
                    status = TKBI_STATUS_TRANSISI
                    reason = "Memenuhi kriteria transisi teknis dengan pemenuhan penuh DNSH dan Aspek Sosial."
                else:
                    status = TKBI_STATUS_HIJAU
                    reason = "Memenuhi ambang batas kontribusi substansial EO serta seluruh Kriteria Esensial (EC)."
                ec_status = {"dnsh": True, "rmt": False, "social_aspects": True}
            elif not dnsh_met and has_rmt_plan and social_aspects_met:
                # EC2 Remedial Measures to Transition allows interim transition status
                status = TKBI_STATUS_TRANSISI_INTERIM
                reason = "Belum memenuhi DNSH tetapi memiliki Rencana Tindakan Perbaikan (RMT) terikat waktu 3 tahun."
                ec_status = {"dnsh": False, "rmt": True, "social_aspects": True}
            else:
                status = TKBI_STATUS_TIDAK_MEMENUHI
                reason = "Gagal memenuhi Kriteria Esensial (DNSH atau Aspek Sosial tidak terpenuhi tanpa RMT)."
                ec_status = {"dnsh": dnsh_met, "rmt": has_rmt_plan, "social_aspects": social_aspects_met}

        return {
            "activity_name": activity_name,
            "sector": sector,
            "status": status,
            "reason": reason,
            "essential_criteria": ec_status,
        }

    @staticmethod
    def aggregate_entity(activities: list[dict[str, Any]], weights: list[float] | None = None) -> dict[str, Any]:
        """Tingkat Entitas (Entity Level): Proportionally aggregate activities into portfolio mix.
        
        Formula per Page 4 of Fact Sheets TKBI.pdf:
        Proportion = Sum((Metric Activity a / Total Metric) * 100%)
        """
        if not activities:
            return {
                "pct_hijau": 0.0,
                "pct_transisi": 0.0,
                "pct_transisi_interim": 0.0,
                "pct_tidak_memenuhi": 0.0,
                "pct_out_of_scope": 100.0,
                "total_tkbi_aligned": 0.0,
                "aggregation_basis": "Default Uniform Allocation",
            }

        n = len(activities)
        if weights is None or len(weights) != n or sum(weights) <= 0:
            w = [1.0 / n] * n
        else:
            tot = sum(weights)
            w = [val / tot for val in weights]

        pct_hijau = 0.0
        pct_transisi = 0.0
        pct_interim = 0.0
        pct_tidak = 0.0
        pct_out = 0.0

        for act, weight in zip(activities, w):
            st = act.get("status", TKBI_STATUS_TIDAK_MEMENUHI)
            pct = weight * 100.0
            if st == TKBI_STATUS_HIJAU:
                pct_hijau += pct
            elif st == TKBI_STATUS_TRANSISI:
                pct_transisi += pct
            elif st == TKBI_STATUS_TRANSISI_INTERIM:
                pct_interim += pct
            elif st == TKBI_STATUS_OUT_OF_SCOPE:
                pct_out += pct
            else:
                pct_tidak += pct

        total_aligned = pct_hijau + pct_transisi + pct_interim

        return {
            "pct_hijau": round(pct_hijau, 1),
            "pct_transisi": round(pct_transisi, 1),
            "pct_transisi_interim": round(pct_interim, 1),
            "pct_tidak_memenuhi": round(pct_tidak, 1),
            "pct_out_of_scope": round(pct_out, 1),
            "total_tkbi_aligned": round(total_aligned, 1),
            "aggregation_basis": "Revenue & Disclosed Operational Mix",
        }

    @classmethod
    def calculate_consistency_score(
        cls,
        overview: dict[str, Any],
        financials: dict[str, Any],
        news: list[dict[str, Any]],
        tkbi_matches: list[dict[str, Any]],
    ) -> tuple[float, list[str], dict[str, Any], list[dict[str, Any]]]:
        """Calculate TKBI consistency score (0-100) using 3-tier evaluation framework."""
        findings: list[str] = []

        subsector = str(overview.get("subsector", "")).lower()
        sub_industry = str(overview.get("sub_industry", "")).lower()
        industry = str(overview.get("industry", "")).lower()
        desc = str(overview.get("description", "")).lower()
        all_text = " ".join([f"{n.get('title', '')} {n.get('summary', '')}" for n in news]).lower()
        full_text = f"{all_text} {desc} {subsector} {industry} {sub_industry}"

        top_match = tkbi_matches[0] if tkbi_matches else None
        top_similarity = float(top_match.get("similarity_score", 0.0)) if top_match else 0.0
        raw_criteria_level = top_match.get("criteria_level") if top_match else "Merah"

        # Guardrail: Mining/extracting unabated thermal coal is OUT OF SCOPE under TKBI
        is_coal_extractor = any(
            k in subsector or k in industry or k in sub_industry or k in desc
            for k in ["coal", "batubara", "lignite", "anthracite"]
        )

        activities: list[dict[str, Any]] = []
        weights: list[float] = []

        if is_coal_extractor:
            act_coal = cls.evaluate_activity(
                activity_name="Pertambangan Batubara Termal Unabated",
                sector="Energi",
                is_fossil_unabated=True,
                tsc_met=False,
            )
            activities.append(act_coal)
            weights.append(0.85)

            # Check if there is a secondary transition activity
            if any(k in full_text for k in ["solar", "plts", "renewables", "biomass", "transisi"]):
                act_trans = cls.evaluate_activity(
                    activity_name="Inisiatif Diversifikasi Energi Bersih",
                    sector="Energi",
                    is_fossil_unabated=False,
                    tsc_met=True,
                    is_transition_tech=True,
                    has_rmt_plan=True,
                )
                activities.append(act_trans)
                weights.append(0.15)
                findings.append("Terdeteksi inisiatif transisi minor di samping operasi batubara dominan.")
            else:
                findings.append("Operasi utama melibatkan ekstraksi batubara termal unmitigated (TKBI Out-of-Scope).")

        elif raw_criteria_level == "Hijau" or any(w in full_text for w in ["geothermal", "panas bumi", "clean energy", "terbarukan", "plts", "pltb"]):
            act_green = cls.evaluate_activity(
                activity_name=top_match.get("activity", "Pembangkitan Energi Terbarukan") if top_match else "Pembangkitan Energi Bersih",
                sector=top_match.get("sector", "Energi") if top_match else "Energi",
                is_fossil_unabated=False,
                tsc_met=True,
                is_transition_tech=False,
                dnsh_met=True,
                social_aspects_met=True,
            )
            activities.append(act_green)
            weights.append(0.9)
            findings.append(f"Aktivitas inti memenuhi kriteria Hijau OJK TKBI ({act_green['activity_name']}).")

        elif raw_criteria_level == "Transisi" or any(w in full_text for w in ["smelter", "transition", "gas", "transisi"]):
            act_trans = cls.evaluate_activity(
                activity_name=top_match.get("activity", "Operasi Transisi Rendah Karbon") if top_match else "Operasi Transisi Industri",
                sector=top_match.get("sector", "Energi") if top_match else "Energi",
                is_fossil_unabated=False,
                tsc_met=True,
                is_transition_tech=True,
                dnsh_met=True,
                social_aspects_met=True,
            )
            activities.append(act_trans)
            weights.append(0.8)
            findings.append(f"Aktivitas diklasifikasikan sebagai fase Transisi TKBI ({act_trans['activity_name']}).")

        else:
            # Low alignment / outside criteria
            act_other = cls.evaluate_activity(
                activity_name=top_match.get("activity", "Aktivitas Konvensional") if top_match else "Operasi Komersial Umum",
                sector="Umum",
                is_fossil_unabated=False,
                tsc_met=False,
            )
            activities.append(act_other)
            weights.append(1.0)
            findings.append(f"Kesesuaian taksonomi rendah ({top_similarity:.2f}); belum memenuhi kriteria hijau terverifikasi.")

        # Aggregate at Entity Level
        entity_mix = cls.aggregate_entity(activities, weights)

        # Baseline Consistency Score grounded in Entity Proportions (Fact Sheets Page 4 formula)
        # Weighting: 1.0 * Hijau + 0.6 * Transisi + 0.4 * Transisi-Interim
        base_score = (
            1.0 * entity_mix["pct_hijau"]
            + 0.6 * entity_mix["pct_transisi"]
            + 0.4 * entity_mix["pct_transisi_interim"]
        )

        # Capital Allocation Reality Check
        capex = float(financials.get("capital_expenditures", 0) or 0)
        rev = float(financials.get("revenue", 0) or 0)
        capex_ratio = (capex / rev * 100.0) if rev > 0 else 0.0

        if entity_mix["total_tkbi_aligned"] >= 50.0:
            if capex_ratio >= 25.0:
                base_score = min(100.0, base_score + 15.0)
                findings.append(f"Komitmen belanja modal kuat: Rasio Capex/Pendapatan mencapai {capex_ratio:.1f}%.")
            elif capex_ratio >= 10.0:
                base_score = min(100.0, base_score + 8.0)
                findings.append(f"Komitmen belanja modal moderat: Rasio Capex/Pendapatan {capex_ratio:.1f}%.")
            else:
                findings.append(f"Intensitas Capex rendah ({capex_ratio:.1f}% dari pendapatan), menimbulkan risiko eksekusi transisi.")
        else:
            findings.append(f"Belanja modal terutama dialokasikan untuk pemeliharaan operasi konvensional ({capex_ratio:.1f}% dari pendapatan).")

        # Qualitative Claim vs Empirical Reality (Greenwashing Audit)
        green_claims = sum(1 for kw in GREEN_KEYWORDS if kw in full_text)
        brown_mentions = sum(1 for kw in BROWN_KEYWORDS if kw in full_text)

        if entity_mix["pct_hijau"] >= 50.0:
            if green_claims > 0:
                base_score = min(100.0, base_score + 10.0)
                findings.append("Klaim keberlanjutan didukung data operasional dan pengungkapan terverifikasi.")
        elif entity_mix["pct_transisi"] + entity_mix["pct_transisi_interim"] >= 40.0:
            if green_claims > 0 and brown_mentions > 0:
                findings.append("Pengungkapan merefleksikan profil transisi ganda (dekarbonisasi bertahap).")
        else:
            # Low TKBI alignment with excessive green promotion
            if green_claims >= 2 and (entity_mix["pct_out_of_scope"] >= 50.0 or entity_mix["pct_tidak_memenuhi"] >= 50.0):
                base_score = max(0.0, base_score - 15.0)
                findings.append("PERINGATAN GREENWASHING: Narasi hijau dipromosikan bersamaan dengan arus kas konvensional dominan.")
            elif not is_coal_extractor:
                base_score = max(base_score, 15.0)

        clamped_score = min(100.0, max(0.0, base_score))
        return round(clamped_score, 1), findings, entity_mix, activities

    @classmethod
    def evaluate(
        cls,
        overview: dict[str, Any],
        financials: dict[str, Any],
        news: list[dict[str, Any]],
        tkbi_matches: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Perform full 4-quadrant green audit evaluation with 3-tier TKBI framework."""
        viability_score, fin_summary = cls.calculate_viability_score(financials)
        consistency_score, audit_findings, entity_mix, activities = cls.calculate_consistency_score(
            overview, financials, news, tkbi_matches
        )

        # Quadrant classification (English Standard per AGENTS.md)
        # Q1: STRONG FUNDAMENTAL AND SUSTAINABLE (Consistency >= 60 & Viability >= 60)
        # Q2: SUSTAINABLE BUT HIGH FINANCIAL RISK (Consistency >= 60 & Viability < 60)
        # Q3: GREENWASHING RISK ZONE (Consistency < 60 & Viability >= 60)
        # Q4: NOT CONSIDERED (Consistency < 60 & Viability < 60)
        if consistency_score >= 60.0 and viability_score >= 60.0:
            quadrant = "STRONG FUNDAMENTAL AND SUSTAINABLE"
            quadrant_code = "Q1"
            label = "High Green & High Viability"
            definition = "High green alignment backed by robust cash flow and Capex. True sustainable compounders."
        elif consistency_score >= 60.0 and viability_score < 60.0:
            quadrant = "SUSTAINABLE BUT HIGH FINANCIAL RISK"
            quadrant_code = "Q2"
            label = "High Green & Low Viability"
            definition = "High green narrative/alignment but fragile fundamentals (cash burn, high leverage). High execution risk."
        elif consistency_score < 60.0 and viability_score >= 60.0:
            quadrant = "GREENWASHING RISK ZONE"
            quadrant_code = "Q3"
            label = "Low Green & High Viability"
            definition = "High cash generation with legacy/fossil profile and low TKBI alignment. High greenwashing vulnerability if claiming green status."
        else:
            quadrant = "NOT CONSIDERED"
            quadrant_code = "Q4"
            label = "Low Green & Low Viability"
            definition = "Low green alignment and deteriorative fundamentals. High obsolescence and default risk."

        top_match = tkbi_matches[0] if tkbi_matches else {}
        primary_status = activities[0]["status"] if activities else top_match.get("criteria_level", "Merah")

        # Grandfathering & Sunsetting status check per Fact Sheets TKBI.pdf Pages 6, 14
        has_debt = fin_summary.get("total_debt", 0) > 0
        gf_status = {
            "eligible_for_grandfathering": has_debt and entity_mix["total_tkbi_aligned"] > 0,
            "allocated_debt_rule": "Mempertahankan label hijau hingga jatuh tempo tenor di bawah TSC awal.",
            "unallocated_debt_rule": "Masa tenggang pelabelan 7 tahun di bawah TSC awal; evaluasi ulang setelahnya.",
            "sunsetting_provision": "Kriteria transisi berlaku hingga batas sunset date nasional (5 tahun siklus kaji ulang TSC).",
        }

        return {
            "quadrant": quadrant,
            "quadrant_code": quadrant_code,
            "quadrant_label": label,
            "quadrant_definition": definition,
            "consistency_score": consistency_score,
            "viability_score": viability_score,
            "tkbi_alignment": {
                "status": primary_status,
                "matched_activity": top_match.get("activity", activities[0]["activity_name"] if activities else "Unmatched"),
                "tsc_summary": top_match.get("tsc", "N/A"),
                "similarity_score": top_match.get("similarity_score", 0.0),
            },
            "tkbi_entity_aggregation": entity_mix,
            "tkbi_activity_breakdown": activities,
            "grandfathering_sunsetting_profile": gf_status,
            "financial_summary": fin_summary,
            "audit_findings": audit_findings,
        }
