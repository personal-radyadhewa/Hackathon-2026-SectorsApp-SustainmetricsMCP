"""TKBI Versi 3 (2026) 8-Sector Master Taxonomy Catalog.

Defines all 8 Focus & Enabling Sectors established by OJK:
1. Energi (Energy)
2. Konstruksi dan Real Estat (Construction & Real Estate)
3. Transportasi dan Pergudangan (Transportation & Storage)
4. Pertanian, Kehutanan, dan Perikanan (Agriculture, Forestry, & Fishing)
5. Manufaktur (Manufacturing)
6. Pengelolaan Air, Air Limbah, Sampah, dan Remediasi (WSSWMR)
7. Informasi dan Komunikasi (Information & Communication - Enabling)
8. Aktivitas Profesional, Ilmiah, dan Teknis (PST - Enabling)
"""

from typing import Any

TKBI_8_SECTORS: dict[str, dict[str, Any]] = {
    "Energi": {
        "sector_name": "Energi",
        "keywords": ["energy", "power", "listrik", "geothermal", "panas bumi", "coal", "batubara", "gas", "minyak", "oil", "solar", "wind", "plts", "pltu", "pltp", "mining"],
        "items": [
            {
                "bab": "Aktivitas Pembangkitan Tenaga Listrik",
                "kbli": "35101",
                "tsc_id": "E-APTL-101-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Intensitas emisi GRK daur hidup < 100g CO2e/kWh (Hijau) atau pensiun dini PLTU batubara terikat sebelum 2040 dengan co-firing biomassa berkelanjutan (Transisi).",
            },
            {
                "bab": "Aktivitas Pembangkitan Tenaga Listrik",
                "kbli": "35101",
                "tsc_id": "E-APTL-101-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Penilaian risiko iklim fisik komprehensif dan implementasi rencana adaptasi ketahanan infrastruktur ketenagalistrikan.",
            },
            {
                "bab": "Aktivitas Transmisi dan Distribusi Tenaga Listrik",
                "kbli": "[35102, 35103]",
                "tsc_id": "E-ATDTL-102103-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Jaringan transmisi/distribusi mengalirkan listrik terbarukan terhubung grid (>67% bauran terbarukan atau smart grid terkontrol).",
            },
            {
                "bab": "Aktivitas Transmisi dan Distribusi Tenaga Listrik",
                "kbli": "[35102, 35103]",
                "tsc_id": "E-ATDTL-102103-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Perlindungan aset transmisi dari bahaya kenaikan muka air laut, tanah longsor, dan banjir ekstrem.",
            },
            {
                "bab": "Aktivitas Penunjang Kelistrikan",
                "kbli": "35104",
                "tsc_id": "E-APK-104-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Layanan pemeliharaan dan efisiensi sistem pembangkit serta jaringan energi bersih terbarukan.",
            },
            {
                "bab": "Distribusi Gas Alam dan Buatan",
                "kbli": "35202",
                "tsc_id": "E-DGAB-202-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Infrastruktur pipa gas mendukung integrasi hidrogen hijau atau biometana, dengan deteksi & eliminasi kebocoran metana (<0.1%).",
            },
            {
                "bab": "Distribusi Gas Alam dan Buatan",
                "kbli": "35202",
                "tsc_id": "E-DGAB-202-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Ketahanan fasilitas kompresi dan pipa gas terhadap pergeseran tektonik dan cuaca ekstrem.",
            },
            {
                "bab": "Pengadaan Uap/Air Panas dan Dingin",
                "kbli": "35301",
                "tsc_id": "E-PUAPD-301-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Pemanfaatan fluida panas bumi langsung atau pendinginan distrik efisiensi tinggi berbasis energi bersih.",
            },
            {
                "bab": "Pengadaan Uap/Air Panas dan Dingin",
                "kbli": "35301",
                "tsc_id": "E-PUAPD-301-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Pengelolaan siklus air tertutup dan perlindungan kelangkaan air tanah permukaan.",
            },
            {
                "bab": "Aktivitas Pertambangan dan Penggalian Mineral Kritis",
                "kbli": "[07292 , 07293 , 07294 , 07295, 07296, 07299]",
                "tsc_id": "E-APPMK-292293294295296299-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "TRANSISI / TIDAK",
                "criteria": "Penambangan mineral transisi (nikel, tembaga, bauksit, litium) dengan rencana dekarbonisasi operasi tambang dan non-DSTP.",
            },
            {
                "bab": "Aktivitas Pertambangan dan Penggalian Kuarsa/Pasir Kuarsa",
                "kbli": "08995",
                "tsc_id": "E-APPKPK-995-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Produksi pasir kuarsa/silika untuk bahan baku sel surya PV nasional dengan pemulihan lahan pascatambang berstandar tinggi.",
            },
            {
                "bab": "Pertambangan dan Penggalian Lainnya YTDL",
                "kbli": "08999",
                "tsc_id": "E-PPLYTDL-999-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Ekstraksi bahan galian pendukung komponen dekarbonisasi tanpa merusak kawasan hutan lindung.",
            },
            {
                "bab": "Aktivitas Penunjang Pertambangan dan Penggalian Lainnya",
                "kbli": "09900",
                "tsc_id": "E-APPPL-900-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "TRANSISI / TIDAK",
                "criteria": "Penyediaan jasa penunjang pertambangan yang menggunakan armada elektrifikasi atau efisiensi bahan bakar bersertifikasi.",
            },
            {
                "bab": "Carbon Capture and Storage (CCS) dan Carbon Capture, Utilization, and Storage (CCUS)",
                "kbli": "[39001, 39002]",
                "tsc_id": "E-CCSCCUS-001002-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Injeksi karbon permanen pada reservoir migas habis/saline aquifer dengan monitoring kebocoran berintegritas tinggi >99% retensi.",
            },
        ],
    },
    "Konstruksi dan Real Estat": {
        "sector_name": "Konstruksi dan Real Estat",
        "keywords": ["property", "real estate", "konstruksi", "gedung", "bangunan", "developer", "perumahan", "infrastruktur", "semen"],
        "items": [
            {
                "bab": "Konstruksi Gedung Hijau Baru",
                "kbli": "41011",
                "tsc_id": "CRE-KGH-011-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Gedung baru tersertifikasi BGH (Bangunan Gedung Hijau) Utama/Madya atau Greenship Gold/Platinum dengan penghematan energi minimal 25% dari standar nasional.",
            },
            {
                "bab": "Renovasi dan Retrofit Efisiensi Energi Gedung",
                "kbli": "41012",
                "tsc_id": "CRE-RRE-012-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Renovasi terbukti menurunkan konsumsi energi primer minimal 30% berdasarkan audit energi terakreditasi.",
            },
            {
                "bab": "Ketahanan Bangunan Terhadap Bencana Iklim",
                "kbli": "41011",
                "tsc_id": "CRE-KBI-011-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Desain drainase resapan air permukaan terintegrasi, ketahanan gempa & gelombang panas ekstrem.",
            },
        ],
    },
    "Transportasi dan Pergudangan": {
        "sector_name": "Transportasi dan Pergudangan",
        "keywords": ["transport", "logistik", "logistic", "shipping", "kapal", "penerbangan", "kereta", "truk", "bus", "pergudangan", "warehouse"],
        "items": [
            {
                "bab": "Transportasi Darat Rendah Emisi & Kendaraan Listrik",
                "kbli": "49211",
                "tsc_id": "TS-TDRE-211-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Operasi armada berbasis Kendaraan Bermotor Listrik Berbasis Baterai (KBLBB) atau emisi langsung 0g CO2/km (Hijau), atau hybrid/Euro 6 (Transisi).",
            },
            {
                "bab": "Transportasi Perkeretaapian Penumpang dan Barang",
                "kbli": "49111",
                "tsc_id": "TS-TPB-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Elektrifikasi jalur rel kereta api atau lokomotif bertenaga baterai / hidrogen bersih.",
            },
            {
                "bab": "Pergudangan Berkelanjutan & Green Logistics Hub",
                "kbli": "52101",
                "tsc_id": "TS-PBGL-101-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Gudang beratap solar panel terintegrasi dan sistem pencahayaan/refrigerasi efisiensi tinggi nol gas ODS.",
            },
        ],
    },
    "Pertanian, Kehutanan, dan Perikanan": {
        "sector_name": "Pertanian, Kehutanan, dan Perikanan",
        "keywords": ["agriculture", "forestry", "sawit", "palm oil", "kehutanan", "perikanan", "fishery", "tambak", "kayu", "pulp", "paper", "tanaman"],
        "items": [
            {
                "bab": "Perkebunan Kelapa Sawit Berkelanjutan",
                "kbli": "01262",
                "tsc_id": "AFF-PKS-262-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Sertifikasi 100% ISPO dan/atau RSPO, zero-deforestation sejak cutoff date nasional, dan penangkapan gas metana dari POME (Methane Capture).",
            },
            {
                "bab": "Konservasi, Restorasi, dan Pemeliharaan Hutan Alam",
                "kbli": "02111",
                "tsc_id": "AFF-KRPHA-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Proyek restorasi ekosistem hutan gambut/mangrove dengan verifikasi penyerapan karbon berstandar SRN-PPI.",
            },
            {
                "bab": "Perikanan Tangkap dan Budidaya Ramah Lingkungan",
                "kbli": "03111",
                "tsc_id": "AFF-PTB-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Alat tangkap selektif bebas pukat harimau, sertifikasi perikanan berkelanjutan, dan elektrifikasi tambang/tambak.",
            },
        ],
    },
    "Manufaktur": {
        "sector_name": "Manufaktur",
        "keywords": ["manufacturing", "manufaktur", "pabrik", "smelter", "steel", "baja", "semen", "cement", "kimia", "chemical", "tekstil", "otomotif"],
        "items": [
            {
                "bab": "Industri Pengolahan dan Pemurnian Logam Bersih (Clean Smelting)",
                "kbli": "24202",
                "tsc_id": "MAN-IPPLB-202-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Intensitas karbon peleburan nikel/aluminium di bawah ambang batas best-in-class (<12 tCO2e/t Ni) dengan pasokan energi terbarukan minimal 40%.",
            },
            {
                "bab": "Industri Semen Hijau dan Bahan Bangunan Rendah Karbon",
                "kbli": "23941",
                "tsc_id": "MAN-ISH-941-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Pengurangan rasio klinker menggunakan material substitusi pozolan/slag dan pemanfaatan bahan bakar alternatif (RDF/biomassa) >15%.",
            },
            {
                "bab": "Industri Kimia Dasar Organik & Bio-Plastik",
                "kbli": "20114",
                "tsc_id": "MAN-IKD-114-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Bahan baku nabati terbarukan terverifikasi (bio-based chemicals) atau proses sirkular daur ulang kimia.",
            },
        ],
    },
    "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi": {
        "sector_name": "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi",
        "keywords": ["water", "limbah", "waste", "sewerage", "sampah", "recycling", "daur ulang", "tpa", "remediasi", "sanitasi"],
        "items": [
            {
                "bab": "Pengelolaan dan Pengolahan Air Limbah Industri & Domestik",
                "kbli": "37011",
                "tsc_id": "WSS-PAL-011-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Fasilitas pengolahan limbah cair dengan penangkapan metana dan pemanfaatan lumpur tinja menjadi biogas energi.",
            },
            {
                "bab": "Pengelolaan Sampah Terpadu & Circular Waste to Energy",
                "kbli": "38211",
                "tsc_id": "WSS-PST-211-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Fasilitas daur ulang material plastik/kertas tingkat recovery >50% atau konversi sampah menjadi Refuse Derived Fuel (RDF).",
            },
        ],
    },
    "Informasi dan Komunikasi": {
        "sector_name": "Informasi dan Komunikasi",
        "keywords": ["telekomunikasi", "telco", "data center", "cloud", "it", "software", "informasi", "komunikasi", "tower"],
        "items": [
            {
                "bab": "Pusat Data Ramah Lingkungan (Green Data Center)",
                "kbli": "63111",
                "tsc_id": "IC-PDRL-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Efisiensi Daya Fasilitas Pusat Data (PUE - Power Usage Effectiveness) tahunan rata-rata < 1.35 didukung kontrak energi terbarukan (PPA). (Exempt dari EC-DNSH menurut TKBI Versi 3).",
            },
            {
                "bab": "Solusi Perangkat Lunak & IoT Pemantauan Karbon",
                "kbli": "62019",
                "tsc_id": "IC-SPL-019-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Pengembangan solusi digital telemetri penghematan energi atau pelaporan jejak emisi GRK industri terakreditasi.",
            },
        ],
    },
    "Aktivitas Profesional, Ilmiah, dan Teknis": {
        "sector_name": "Aktivitas Profesional, Ilmiah, dan Teknis",
        "keywords": ["konsultan", "audit", "engineering", "riset", "research", "laboratorium", "sertifikasi", "jasa teknis"],
        "items": [
            {
                "bab": "Jasa Audit Energi dan Sertifikasi Karbon",
                "kbli": "71102",
                "tsc_id": "PST-JAE-102-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Layanan inspeksi dan verifikasi independen inventarisasi emisi GRK sesuai ISO 14064 atau regulasi OJK/KLHK. (Exempt dari EC-DNSH menurut TKBI Versi 3).",
            },
            {
                "bab": "Riset dan Pengembangan Teknologi Dekarbonisasi",
                "kbli": "72101",
                "tsc_id": "PST-RP-101-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Aktivitas riset terapan komersialisasi teknologi penangkapan karbon, baterai padat, atau biomassa non-pangan.",
            },
        ],
    },
}


def map_emiten_to_sectors(subsector: str, description: str, explicit_sector: str | None = None) -> list[str]:
    """Map company subsector/description to one or more of the 8 TKBI Versi 3 sectors."""
    if explicit_sector and explicit_sector in TKBI_8_SECTORS:
        return [explicit_sector]

    matched_sectors: list[tuple[str, int]] = []
    text_corpus = f"{subsector} {description}".lower()

    for sector_name, info in TKBI_8_SECTORS.items():
        score = 0
        for kw in info["keywords"]:
            if kw in text_corpus:
                score += 1
        if score > 0:
            matched_sectors.append((sector_name, score))

    if matched_sectors:
        matched_sectors.sort(key=lambda x: x[1], reverse=True)
        return [matched_sectors[0][0]]

    # Default to Energi if unknown
    return ["Energi"]
