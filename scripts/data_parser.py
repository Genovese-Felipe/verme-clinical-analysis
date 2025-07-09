# scripts/data_parser.py (v3.0 - Expert Analysis)

import pandas as pd
import json
import os

# --- Step 1: Ensure the data directory exists ---
output_dir = 'data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- Step 2: Define and Enrich the Exam Data ---
# This new structure adds metadata (status, significance) to each data point.

# 2.1 Enriched Biochemistry Data
biochemistry_list = [
    {
        "parameter": "Creatinine", "value": 1.18, "unit": "mg/dl",
        "reference_range": "0.6-1.8", "status": "Normal",
        "significance_pt": "Principal marcador da função de filtração renal. Valores normais sugerem que os rins ainda conseguem filtrar o sangue adequadamente.",
        "significance_en": "Primary marker of renal filtration function. Normal values suggest the kidneys can still filter blood properly."
    },
    {
        "parameter": "Urea", "value": 84.9, "unit": "mg/dl",
        "reference_range": "10-56", "status": "High",
        "significance_pt": "Produto do metabolismo de proteínas, eliminado pelos rins. A elevação (azotemia) pode indicar desidratação ou comprometimento renal.",
        "significance_en": "Product of protein metabolism, eliminated by the kidneys. Elevation (azotemia) may indicate dehydration or renal impairment."
    },
    {
        "parameter": "ALT (SGPT)", "value": 25.4, "unit": "U.I./L",
        "reference_range": "6.0-83", "status": "Normal",
        "significance_pt": "Enzima primariamente hepática. Valores normais são um forte indicativo de ausência de lesão aguda no fígado.",
        "significance_en": "Primarily a liver enzyme. Normal values are a strong indicator of no acute liver injury."
    },
    {
        "parameter": "Alkaline Phosphatase", "value": 17.9, "unit": "U.I./L",
        "reference_range": "4-81", "status": "Normal",
        "significance_pt": "Enzima presente em vários tecidos (fígado, ossos). Valores normais ajudam a descartar doenças colestáticas (fluxo biliar) e ósseas.",
        "significance_en": "Enzyme present in various tissues (liver, bones). Normal values help rule out cholestatic (bile flow) and bone diseases."
    }
]
biochemistry_df = pd.DataFrame(biochemistry_list)

# 2.2 Enriched Hematology Data
hematology_list = [
    {"parameter": "Red Blood Cells", "value": 9.18, "reference_range": "5.0-10.0", "status": "Normal"},
    {"parameter": "Hematocrit", "value": 43.0, "reference_range": "24-45", "status": "Normal"},
    {"parameter": "Hemoglobin", "value": 13.9, "reference_range": "8-15", "status": "Normal"},
    {
        "parameter": "Plasma Protein", "value": 9.2, "reference_range": "6.0-8.0", "status": "High",
        "significance_pt": "Proteínas totais no sangue. A elevação pode indicar desidratação ou inflamação crônica.",
        "significance_en": "Total proteins in the blood. Elevation may indicate dehydration or chronic inflammation."
    },
    {"parameter": "Leukocytes", "value": 7000, "reference_range": "5500-19500", "status": "Normal"},
    {"parameter": "Segmented Neutrophils", "value": 5810, "reference_range": "1925-14625", "status": "Normal"},
    {
        "parameter": "Lymphocytes", "value": 840, "reference_range": "1100-10725", "status": "Low",
        "significance_pt": "Células de defesa. A redução (linfopenia) é um achado comum em quadros de estresse ou inflamação aguda.",
        "significance_en": "Defense cells. Reduction (lymphopenia) is a common finding in stress or acute inflammation."
    },
    {"parameter": "Platelets", "value": 629000, "reference_range": "230000-680000", "status": "Normal"}
]
hematology_df = pd.DataFrame(hematology_list)

# 2.3 Enriched Ultrasound Data with Correlations
ultrasound_data = {
    "patient_name": "Verme",
    "exam_id": "66/0725",
    "exam_date": "2025-07-08",
    "pathological_findings": [
        {
            "organ": "Urinary Bladder",
            "impression": "Inflammatory Process / Cystitis",
            "report_description": "Bladder with little content, with countless suspended echogenic points and punctiform material, featuring irregular and thickened walls.",
            "key_measurements": {"wall_thickness_cm": "0.34-0.67"},
            "correlated_lab_findings": [
                {"parameter": "Lymphocytes", "status": "Low", "insight": "A linfopenia pode ser uma resposta sistêmica ao estresse e inflamação causados pela cistite."},
                {"parameter": "Plasma Protein", "status": "High", "insight": "A hiperproteinemia pode ser secundária à desidratação ou à resposta inflamatória crônica da bexiga."}
            ]
        },
        {
            "organ": "Kidneys",
            "impression": "Suspected Incipient Nephropathy / Early Stage Renal Disease",
            "report_description": "Discreetly elevated cortical echogenicity. Findings may be related to fat deposition but cannot rule out early-stage renal disease.",
            "key_measurements": {"left_kidney_cm": 3.87, "right_kidney_cm": 3.59},
            "correlated_lab_findings": [
                {"parameter": "Urea", "status": "High", "insight": "A azotemia (ureia alta) é o principal indicador laboratorial que corrobora a suspeita ultrassonográfica de disfunção renal."},
                {"parameter": "Creatinine", "status": "Normal", "insight": "A creatinina ainda normal, apesar da ureia alta, sugere um quadro inicial ou uma causa pré-renal (como desidratação)."}
            ]
        },
        {
            "organ": "Abdominal Wall",
            "impression": "Umbilical Hernia",
            "report_description": "At the umbilical scar region, a reducible volume increase is noted, containing amorphous and hypoechoic structure (omentum/mesentery), associated with a loss of continuity of the abdominal wall of approximately 0.64cm, without herniated organs.",
            "key_measurements": {"hernial_ring_cm": 0.64},
            "correlated_lab_findings": []
        }
    ],
    "normal_findings": [
        "Liver", "Gallbladder", "Spleen", "Pancreas", "Adrenal Glands", "Stomach", "Intestines"
    ]
}

# --- Step 3: Generate Correlated Insights and Metadata (The Expert Layer) ---
clinical_insights = {
    "patient_id": "Verme_66-0725",
    "assessment_date": "2025-07-09",
    "primary_hypothesis": {
        "name_pt": "Síndrome de Pandora com Cistite Idiopática Felina (CIF)",
        "name_en": "Pandora Syndrome with Feline Idiopathic Cystitis (FIC)",
        "confidence": "High",
        "evidence": [
            "Achado ultrassonográfico de cistite sem urolitíase (cálculos) visível.",
            "Linfopenia e hiperproteinemia consistentes com resposta a estresse fisiológico.",
            "Perfil epidemiológico (macho, 6 anos) é de alto risco para CIF."
        ]
    },
    "secondary_concerns": [
        {
            "name_pt": "Risco Elevado para Doença Renal Crônica (DRC)",
            "name_en": "Elevated Risk for Chronic Kidney Disease (CKD)",
            "evidence": [
                "Azotemia pré-renal (Ureia alta, Creatinina normal).",
                "Ecogenicidade cortical dos rins discretamente elevada no ultrassom.",
                "Inflamação sistêmica crônica (da cistite) é um fator de risco conhecido para progressão de DRC."
            ]
        }
    ],
    "advanced_recommendations": [
        {
            "recommendation": "Dosar o biomarcador SDMA (Dimetilarginina Simétrica).",
            "justification_pt": "SDMA é um marcador da função renal muito mais sensível e precoce que a creatinina. Um valor elevado de SDMA confirmaria o dano renal incipiente, mesmo com creatinina normal.",
            "priority": "High"
        },
        {
            "recommendation": "Realizar urinálise completa com Relação Proteína/Creatinina (RPC).",
            "justification_pt": "A RPC quantifica a perda de proteína pelos rins. Proteinúria é um fator chave no estadiamento e prognóstico da Doença Renal Crônica.",
            "priority": "High"
        },
        {
            "recommendation": "Implementar Manejo Ambiental Multimodal (MEMO).",
            "justification_pt": "Considerando a alta suspeita de Síndrome de Pandora, o manejo do estresse é tão importante quanto o tratamento médico. Isso inclui enriquecimento ambiental, múltiplas fontes de água e caixas de areia.",
            "priority": "Medium"
        }
    ]
}

# --- Step 4: Save All Files ---
biochemistry_df.to_csv(os.path.join(output_dir, 'biochemistry.csv'), index=False)
hematology_df.to_csv(os.path.join(output_dir, 'hematology.csv'), index=False)
with open(os.path.join(output_dir, 'ultrasound_findings.json'), 'w', encoding='utf-8') as f:
    json.dump(ultrasound_data, f, ensure_ascii=False, indent=4)
with open(os.path.join(output_dir, 'clinical_insights.json'), 'w', encoding='utf-8') as f:
    json.dump(clinical_insights, f, ensure_ascii=False, indent=4)

print("--- Expert Analysis & Data Enrichment Complete ---")
print("Successfully generated new enriched data files in the 'data' directory.")