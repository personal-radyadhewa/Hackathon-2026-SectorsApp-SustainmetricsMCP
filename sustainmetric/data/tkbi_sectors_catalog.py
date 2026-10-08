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
        "keywords": [
            "energy", "power", "listrik", "geothermal", "panas bumi", "coal", "batubara",
            "gas", "minyak", "oil", "solar", "wind", "plts", "pltu", "pltp", "mining", "tambang",
        ],
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
        "keywords": [
            "property", "real estate", "konstruksi", "gedung", "bangunan", "developer",
            "perumahan", "residensial", "perkantoran", "apartemen", "jalan raya", "jembatan",
            "infrastruktur", "c&re", "kawasan industri",
        ],
        "items": [
            {
                "bab": "Konstruksi Gedung Hijau Baru",
                "kbli": "41011",
                "tsc_id": "CRE-KGH-011-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Gedung baru tersertifikasi BGH (Bangunan Gedung Hijau) Utama/Madya atau Greenship Gold/Platinum dengan efisiensi energi minimal 25% melampaui baseline nasional.",
            },
            {
                "bab": "Konstruksi Gedung Hijau Baru",
                "kbli": "41011",
                "tsc_id": "CRE-KGH-011-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Penerapan analisis risiko iklim fisik (CRVA), resapan air limpasan hujan terintegrasi, dan desain ketahanan bahaya bencana banjir/panas ekstrem.",
            },
            {
                "bab": "Renovasi dan Retrofit Efisiensi Energi Gedung",
                "kbli": "41012",
                "tsc_id": "CRE-RRE-012-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Renovasi gedung yang membuktikan reduksi konsumsi energi primer minimal 30% berdasarkan audit energi independen terakreditasi.",
            },
            {
                "bab": "Konstruksi Bangunan Sipil Jalan Raya dan Jembatan",
                "kbli": "42111",
                "tsc_id": "CRE-KBS-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Konstruksi jalan berperingkat Greenroads/INVEST/I-LAST, pemanfaatan aspal daur ulang (RAP) >20% atau teknologi aspal hangat (WMA).",
            },
            {
                "bab": "Pembongkaran Bangunan dan Daur Ulang Material (C&D Waste)",
                "kbli": "43110",
                "tsc_id": "CRE-PBM-110-04",
                "tsc": "EO4: Resource Resilience and Circular Economy",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Pemilahan, pemulihan, dan daur ulang limbah konstruksi & pembongkaran gedung (C&D waste) dengan recovery rate ≥70%.",
            },
            {
                "bab": "Real Estate Berkelanjutan & Akuisisi Gedung Rendah Emisi",
                "kbli": "68111",
                "tsc_id": "CRE-REB-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Kepemilikan dan pengelolaan portofolio gedung berkinerja energi tinggi dengan sertifikasi Greenship Existing Building / BGH operasional.",
            },
        ],
    },
    "Transportasi dan Pergudangan": {
        "sector_name": "Transportasi dan Pergudangan",
        "keywords": [
            "transport", "transportasi", "logistik", "logistic", "logistics", "shipping",
            "pelayaran", "kapal", "penerbangan", "pesawat", "kereta", "railway", "truk",
            "bus", "pergudangan", "warehouse", "armada", "spklu", "port", "pelabuhan", "t&s",
        ],
        "items": [
            {
                "bab": "Transportasi Darat Rendah Emisi & Kendaraan Listrik",
                "kbli": "49211",
                "tsc_id": "TS-TDRE-211-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Armada angkutan berbasis KBLBB/baterai listrik atau hidrogen emisi langsung 0g CO2/km (Hijau), atau hybrid/Euro 6/CNG dengan target penurunan emisi (Transisi).",
            },
            {
                "bab": "Transportasi Perkeretaapian Penumpang dan Barang",
                "kbli": "49111",
                "tsc_id": "TS-TPB-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Elektrifikasi jalur kereta api dengan pasokan listrik rendah karbon atau lokomotif nol emisi knalpot langsung.",
            },
            {
                "bab": "Angkutan Perairan Rendah Emisi & Pelayaran Hijau",
                "kbli": "50111",
                "tsc_id": "TS-APRE-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Kapal bertenaga listrik/biofuel/metanol hijau atau memenuhi kepatuhan IMO Carbon Intensity Indicator (CII) rating A/B dan EEXI.",
            },
            {
                "bab": "Angkutan Udara Rendah Karbon & Sustainable Aviation Fuel",
                "kbli": "51101",
                "tsc_id": "TS-AURK-101-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Penggunaan bahan bakar penerbangan berkelanjutan (SAF) bersertifikasi CORSIA dengan blending ratio minimal sesuai roadmap transisi penerbangan.",
            },
            {
                "bab": "Pergudangan Berkelanjutan & Green Logistics Hub",
                "kbli": "52101",
                "tsc_id": "TS-PBGL-101-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Fasilitas pergudangan dengan instalasi PLTS atap, forklift elektrik, sertifikasi green building, dan sistem refrigerasi ramah lingkungan (GWP rendah).",
            },
            {
                "bab": "Infrastruktur Pendukung Transportasi Hijau (SPKLU/SPBKLU)",
                "kbli": "52219",
                "tsc_id": "TS-IPTS-219-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Penyediaan fasilitas stasiun pengisian kendaraan listrik umum (SPKLU), stasiun penukaran baterai (SPBKLU), atau fasilitas shore power kapal pelabuhan.",
            },
        ],
    },
    "Pertanian, Kehutanan, dan Perikanan": {
        "sector_name": "Pertanian, Kehutanan, dan Perikanan",
        "keywords": [
            "agriculture", "pertanian", "perkebunan", "forestry", "kehutanan", "sawit",
            "cpo", "palm oil", "perikanan", "fishery", "tambak", "peternakan", "ternak",
            "kayu", "hutan", "pulp", "aff", "afolu", "padi", "unggas", "unggas",
        ],
        "items": [
            {
                "bab": "Perkebunan Kelapa Sawit Berkelanjutan",
                "kbli": "01262",
                "tsc_id": "AFF-PKS-262-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Sertifikasi 100% ISPO dan/atau RSPO, zero-deforestation sejak cutoff date nasional (NDPE), dan instalasi penangkapan gas metana POME (Methane Capture).",
            },
            {
                "bab": "Perkebunan Kelapa Sawit Berkelanjutan",
                "kbli": "01262",
                "tsc_id": "AFF-PKS-262-03",
                "tsc": "EO3: Protection of Healthy Ecosystems and Biodiversity",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Perlindungan dan pemantauan kawasan bernilai konservasi tinggi (HCV), stok karbon tinggi (HCS), serta larangan penanaman di lahan gambut.",
            },
            {
                "bab": "Pertanian Tanaman Semusim dan Tahunan Berkelanjutan",
                "kbli": "01111",
                "tsc_id": "AFF-PTST-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Penerapan pertanian presisi, pengurangan emisi pupuk nitrogen sintetis, pengelolaan air AWD padi hemat emisi, dan sertifikasi organik.",
            },
            {
                "bab": "Peternakan Berkelanjutan & Manajemen Limbah Biogas",
                "kbli": "01411",
                "tsc_id": "AFF-PBML-411-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Pemanfaatan biodigester anaerobik untuk mengolah kotoran ternak menjadi energi biogas dan mitigasi emisi metana enterik ruminansia.",
            },
            {
                "bab": "Perikanan Tangkap dan Budidaya Ramah Lingkungan",
                "kbli": "03111",
                "tsc_id": "AFF-PTB-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Elektrifikasi tambak budidaya, kapal penangkap ikan hemat energi, sertifikasi MSC/ASC/CBIB, dan pelarangan alat tangkap destruktif.",
            },
            {
                "bab": "Konservasi, Restorasi, dan Pemeliharaan Hutan Alam",
                "kbli": "02111",
                "tsc_id": "AFF-KRPHA-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Proyek restorasi ekosistem hutan gambut/mangrove dengan verifikasi penyerapan karbon berstandar SRN-PPI dan sertifikasi PHPL/FSC.",
            },
        ],
    },
    "Manufaktur": {
        "sector_name": "Manufaktur",
        "keywords": [
            "manufacturing", "manufaktur", "pabrik", "industri", "smelter", "smelting",
            "steel", "baja", "besi", "semen", "cement", "kimia", "chemical", "pupuk",
            "tekstil", "otomotif", "baterai", "solar panel", "elektronik", "keramik",
        ],
        "items": [
            {
                "bab": "Industri Logam Dasar Besi dan Baja Rendah Karbon",
                "kbli": "24101",
                "tsc_id": "MAN-IBB-101-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Produksi baja berbasis Electric Arc Furnace (EAF) daur ulang scrap atau Direct Reduced Iron (DRI) berbasis hidrogen dengan emisi <1.4 tCO2e/t baja mentah.",
            },
            {
                "bab": "Industri Pengolahan dan Pemurnian Logam Bersih (Clean Smelting)",
                "kbli": "24202",
                "tsc_id": "MAN-IPPLB-202-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Intensitas karbon peleburan nikel/aluminium di bawah ambang batas best-in-class (<12 tCO2e/t Ni), pasokan energi terbarukan/gas alam >40%, dan non-DSTP.",
            },
            {
                "bab": "Industri Semen Hijau dan Bahan Bangunan Rendah Karbon",
                "kbli": "23941",
                "tsc_id": "MAN-ISH-941-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Pengurangan clinker factor melalui material substitusi pozolan/slag dan pencapaian Thermal Substitution Rate (TSR) bahan bakar alternatif RDF/biomassa >15%.",
            },
            {
                "bab": "Industri Kimia Dasar Organik & Bio-Plastik",
                "kbli": "20114",
                "tsc_id": "MAN-IKD-114-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Pemanfaatan bahan baku nabati terbarukan terverifikasi (bio-based chemicals) atau proses sirkular daur ulang kimia dengan efisiensi energi terakreditasi ISO 50001.",
            },
            {
                "bab": "Industri Baterai dan Komponen Kendaraan Listrik",
                "kbli": "27201",
                "tsc_id": "MAN-IBEV-201-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Manufaktur sel dan modul baterai traksi KBLBB dengan rantai pasok mineral terlacak berjejak karbon rendah dan desain ramah daur ulang (closed-loop).",
            },
            {
                "bab": "Industri Teknologi Energi Terbarukan & Peralatan Efisiensi",
                "kbli": "27111",
                "tsc_id": "MAN-ITER-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Produksi panel fotovoltaik surya, turbin angin, inverter smart grid, atau motor listrik industri berefisiensi super tinggi (IE4+).",
            },
            {
                "bab": "Industri Kertas dan Pulp Berkelanjutan",
                "kbli": "17011",
                "tsc_id": "MAN-IKP-011-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Bahan baku 100% kayu dari hutan tanaman lestari bersertifikasi FSC/PEFC atau serat daur ulang, didukung kogenerasi energi biomassa mandiri.",
            },
            {
                "bab": "Industri Makanan dan Minuman Rendah Emisi",
                "kbli": "10111",
                "tsc_id": "MAN-IMMR-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Penerapan Standar Industri Hijau (SIH), pemanfaatan panas buang (waste heat recovery), dan efisiensi energi terverifikasi pada industri mamin.",
            },
        ],
    },
    "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi": {
        "sector_name": "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi",
        "keywords": [
            "water", "air", "pdam", "limbah", "air limbah", "waste", "sewerage", "sampah",
            "recycling", "daur ulang", "tpa", "rpet", "rdf", "remediasi", "sanitasi",
            "wsswmr", "lingkungan hidup",
        ],
        "items": [
            {
                "bab": "Pengelolaan dan Penyediaan Air Minum & Air Baku",
                "kbli": "36001",
                "tsc_id": "WSS-PAB-001-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Sistem penyediaan air minum dengan konsumsi energi bersih spesifik <0.5 kWh/m3 dan program pengendalian kebocoran pipa (NRW) <20%.",
            },
            {
                "bab": "Pengelolaan dan Penyediaan Air Minum & Air Baku",
                "kbli": "36001",
                "tsc_id": "WSS-PAB-001-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Rencana pengamanan air minum (RPAM), perlindungan mata air alami, serta infrastruktur pemanenan air hujan (PAH).",
            },
            {
                "bab": "Pengelolaan dan Pengolahan Air Limbah Industri & Domestik",
                "kbli": "37011",
                "tsc_id": "WSS-PAL-011-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Instalasi pengolahan air limbah (IPAL) dengan penangkapan metana (anaerobic digestion) dan pemanfaatan lumpur olahan menjadi energi/biogas.",
            },
            {
                "bab": "Pengelolaan Sampah Terpadu & Circular Waste to Energy",
                "kbli": "38211",
                "tsc_id": "WSS-PST-211-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Fasilitas Pengolahan Sampah Menjadi Energi Listrik (PSEL), pabrik Refuse Derived Fuel (RDF), kompos organik, atau penangkapan gas metana TPA >50%.",
            },
            {
                "bab": "Daur Ulang Material dan Sampah Non-B3",
                "kbli": "38301",
                "tsc_id": "WSS-DUM-301-04",
                "tsc": "EO4: Resource Resilience and Circular Economy",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Operasi daur ulang mekanik/kimia untuk plastik (rPET/rHDPE), kertas, dan logam dengan rasio perolehan material sekunder (recovery rate) >50%.",
            },
            {
                "bab": "Remediasi dan Dekontaminasi Lokasi Tercemar",
                "kbli": "39000",
                "tsc_id": "WSS-RDLT-000-03",
                "tsc": "EO3: Protection of Healthy Ecosystems and Biodiversity",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Pemulihan lahan tercemar limbah B3/bekas area pertambangan menggunakan bioremediasi/fitoremediasi bersertifikasi KLHK.",
            },
        ],
    },
    "Informasi dan Komunikasi": {
        "sector_name": "Informasi dan Komunikasi",
        "keywords": [
            "telekomunikasi", "telco", "data center", "pusat data", "cloud", "it",
            "software", "teknologi informasi", "hosting", "server", "tower", "menara",
            "komunikasi", "digital", "platform", "ic",
        ],
        "items": [
            {
                "bab": "Pusat Data Ramah Lingkungan (Green Data Center)",
                "kbli": "63111",
                "tsc_id": "IC-PDRL-111-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Power Usage Effectiveness (PUE) tahunan rata-rata ≤ 1.35 (Hijau) atau ≤ 1.50 (Transisi), kontrak energi terbarukan (PPA), dan refrigeran GWP ≤675.",
            },
            {
                "bab": "Pusat Data Ramah Lingkungan (Green Data Center)",
                "kbli": "63111",
                "tsc_id": "IC-PDRL-111-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Ketahanan fisik fasilitas server terhadap risiko iklim, redundansi pendinginan pasif, dan proteksi bahaya banjir serta cuaca ekstrem.",
            },
            {
                "bab": "Solusi Perangkat Lunak & IoT Pemantauan Karbon",
                "kbli": "62019",
                "tsc_id": "IC-SPL-019-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Pengembangan solusi perangkat lunak telemetri emisi GRK industri, sistem manajemen energi (EMS/BEMS), dan platform optimasi dekarbonisasi rantai pasok.",
            },
            {
                "bab": "Solusi Digital Ketahanan & Peringatan Dini Iklim",
                "kbli": "62019",
                "tsc_id": "IC-SDP-019-02",
                "tsc": "EO2: Climate Change Adaptation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Aplikasi peringatan dini bencana hidrometeorologi (Early Warning System / EWS) dan pemodelan ketahanan iklim berbasis AI/satelit.",
            },
            {
                "bab": "Infrastruktur Telekomunikasi Rendah Energi & Smart Towers",
                "kbli": "61100",
                "tsc_id": "IC-ITRE-100-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TRANSISI / TIDAK",
                "criteria": "Menara BTS bertenaga solar surya PV hibrid pengganti genset diesel fosil dan adopsi fitur otomatisasi hemat daya pada jaringan seluler.",
            },
        ],
    },
    "Aktivitas Profesional, Ilmiah, dan Teknis": {
        "sector_name": "Aktivitas Profesional, Ilmiah, dan Teknis",
        "keywords": [
            "konsultan", "konsuntansi", "audit", "auditor", "engineering", "rekayasa",
            "riset", "research", "laboratorium", "sertifikasi", "jasa teknis", "jasa ilmiah",
            "jasa profesional", "amdal", "pst",
        ],
        "items": [
            {
                "bab": "Jasa Audit Energi dan Manajemen Konservasi Energi",
                "kbli": "71102",
                "tsc_id": "PST-JAE-102-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Layanan audit energi perindustrian dan bangunan gedung oleh auditor energi tersertifikasi BNSP/ESDM untuk penurunan konsumsi energi signifikan.",
            },
            {
                "bab": "Jasa Verifikasi dan Validasi Inventarisasi Karbon / GRK",
                "kbli": "71203",
                "tsc_id": "PST-JVK-203-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Layanan verifikasi dan validasi emisi GRK oleh Lembaga Validasi/Verifikasi (LVV) independen terakreditasi KAN sesuai ISO 14064 / ISO 14065.",
            },
            {
                "bab": "Konsultasi Manajemen Keberlanjutan & Strategi Dekarbonisasi",
                "kbli": "70209",
                "tsc_id": "PST-KMK-209-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Jasa konsultansi penyusunan dokumen Transition Plan, target dekarbonisasi berbasis sains (SBTi), dan pelaporan keberlanjutan sesuai POJK 51/2017.",
            },
            {
                "bab": "Konsultasi Keanekaragaman Hayati & Kajian Lingkungan (AMDAL)",
                "kbli": "70209",
                "tsc_id": "PST-KKH-209-03",
                "tsc": "EO3: Protection of Healthy Ecosystems and Biodiversity",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Penyusunan kajian AMDAL, penilaian keanekaragaman hayati (IBSAP), serta kajian Stok Karbon Tinggi (HCS) dan Nilai Konservasi Tinggi (HCV).",
            },
            {
                "bab": "Riset dan Pengembangan Teknologi Dekarbonisasi (Clean Tech)",
                "kbli": "72101",
                "tsc_id": "PST-RP-101-01",
                "tsc": "EO1 – Climate Change Mitigation",
                "bentuk_jawaban": "HIJAU / TIDAK",
                "criteria": "Aktivitas litbang terapan komersialisasi teknologi penangkapan karbon di udara (Direct Air Capture), baterai padat, hidrogen, atau material ramah lingkungan.",
            },
        ],
    },
}

# Alias mapping for Indonesian and English variations
SECTOR_NAME_ALIASES: dict[str, str] = {
    "energi": "Energi",
    "energy": "Energi",
    "konstruksi dan real estat": "Konstruksi dan Real Estat",
    "construction & real estate": "Konstruksi dan Real Estat",
    "construction and real estate": "Konstruksi dan Real Estat",
    "real estate": "Konstruksi dan Real Estat",
    "property": "Konstruksi dan Real Estat",
    "transportasi dan pergudangan": "Transportasi dan Pergudangan",
    "transportation & storage": "Transportasi dan Pergudangan",
    "transportation and storage": "Transportasi dan Pergudangan",
    "logistics": "Transportasi dan Pergudangan",
    "pertanian, kehutanan, dan perikanan": "Pertanian, Kehutanan, dan Perikanan",
    "agriculture, forestry, and fishing": "Pertanian, Kehutanan, dan Perikanan",
    "aff": "Pertanian, Kehutanan, dan Perikanan",
    "plantation": "Pertanian, Kehutanan, dan Perikanan",
    "manufaktur": "Manufaktur",
    "manufacturing": "Manufaktur",
    "pengelolaan air, air limbah, sampah, dan remediasi": "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi",
    "water supply, sewerage, waste management, and remediation": "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi",
    "wsswmr": "Pengelolaan Air, Air Limbah, Sampah, dan Remediasi",
    "informasi dan komunikasi": "Informasi dan Komunikasi",
    "information and communication": "Informasi dan Komunikasi",
    "ic": "Informasi dan Komunikasi",
    "telecommunication": "Informasi dan Komunikasi",
    "aktivitas profesional, ilmiah, dan teknis": "Aktivitas Profesional, Ilmiah, dan Teknis",
    "professional, scientific and technical activities": "Aktivitas Profesional, Ilmiah, dan Teknis",
    "pst": "Aktivitas Profesional, Ilmiah, dan Teknis",
}


def map_emiten_to_sectors(subsector: str, description: str, explicit_sector: str | None = None) -> list[str]:
    """Map company subsector/description to one or more of the 8 TKBI Versi 3 sectors."""
    if explicit_sector:
        cleaned_override = explicit_sector.strip().lower()
        if explicit_sector in TKBI_8_SECTORS:
            return [explicit_sector]
        if cleaned_override in SECTOR_NAME_ALIASES:
            return [SECTOR_NAME_ALIASES[cleaned_override]]

    text_corpus = f"{subsector} {description}".lower()
    matched_sectors: list[tuple[str, int]] = []

    for sector_name, info in TKBI_8_SECTORS.items():
        score = sum(1 for kw in info["keywords"] if kw in text_corpus)
        if score > 0:
            matched_sectors.append((sector_name, score))

    if matched_sectors:
        matched_sectors.sort(key=lambda x: x[1], reverse=True)
        return [matched_sectors[0][0]]

    # Default to Energi if unmatched
    return ["Energi"]
