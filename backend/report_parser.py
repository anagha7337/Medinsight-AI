import re

#  NORMALIZATION HELPERS  #

def normalize_plain(value, unit=None):
    return float(value)

def normalize_percentage(value, unit=None):
    return float(value)

def normalize_platelets(value, unit=None):
    value = float(value)
    if unit:
        unit_lower = unit.lower()
        if "lakh" in unit_lower:
            return value * 100000
        elif "thousand" in unit_lower or "k" == unit_lower:
            return value * 1000
    if value < 1000:
        return value * 100000
    return value

def normalize_wbc(value, unit=None):
    value = float(value)
    if unit:
        unit_lower = unit.lower()
        if any(x in unit_lower for x in ["10^3", "x10", "thousand", "/cumm", "cumm", "x10³", "10³"]):
            if value > 100:
                return value
            else:
                return value * 1000
    if value >= 1000:
        return value
    return value * 1000

def normalize_rbc(value, unit=None):
    value = float(value)
    if 3 <= value <= 7:
        return value
    if value > 100:
        return value / 1_000_000
    return value

def normalize_hba1c(value, unit=None):
    return float(value)

def normalize_glucose(value, unit=None):
    """Blood glucose normalization"""
    value = float(value)
    if unit and ("mmol" in unit.lower() or "mol" in unit.lower()):
        return value * 18  # 1 mmol/L = 18 mg/dL
    if value < 20:
        return value * 18
    return value

# MAIN PARSER  #

def parse_report(text):
    results = {}
    text_original = text
    text_lower = text.lower()

    print("\n" + "=" * 50)
    print("PARSING REPORT...")
    print("=" * 50)

    patterns = {
        # HEMOGLOBIN
        "Hemoglobin": {
            "regex": r"(?:hemoglobin|haemoglobin|hgb|hb|h\.b\.|hemo|haemo)[\s:]*(?:\(hb\))?[\s:]*(?:count)?[\s:]*(?:result)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # WBC - White Blood Cells
        "WBC": {
            "regex": r"(?:wbc|w\.b\.c\.|white\s+blood\s+cell|total\s+wbc|total\s+leuko(?:cyte)?|leuko(?:cyte)?\s+count|tlc)[\s:]*(?:count)?[\s:]*([\d\.]+)[\s,]*(x10\^3|10\^3|x10³|10³|thousand|/cumm|cumm|/ul|/µl|cells/cmm)?",
            "normalizer": normalize_wbc
        },

        # RBC - Red Blood Cells
        "RBC": {
            "regex": r"(?:rbc|r\.b\.c\.|red\s+blood\s+cell|total\s+rbc|erythrocyte)[\s:]*(?:count)?[\s:]*([\d\.]+)[\s,]*(million|mill|mil|x10\^6|10\^6)?",
            "normalizer": normalize_rbc
        },

        # PLATELETS
        "Platelets": {
            "regex": r"(?:platelet|plt|thrombocyte)[\s:]*(?:count)?[\s:]*([\d\.]+)[\s,]*(lakh|lakhs|thousand|k|/ul|/µl|/cumm|cumm|cells)?",
            "normalizer": normalize_platelets
        },

        # BLOOD SUGAR / GLUCOSE
        "Blood Sugar": {
            "regex": r"(?:glucose|blood\s+sugar|fasting\s+(?:blood\s+)?(?:glucose|sugar)|random\s+(?:blood\s+)?(?:glucose|sugar)|fbs|rbs|ppbs|post\s+prandial|plasma\s+glucose)[\s:]*(?:result)?[\s:]*([\d\.]+)[\s,]*(mg/dl|mmol/l|mmol)?",
            "normalizer": normalize_glucose
        },

        # HbA1c - Glycated Hemoglobin
        "HbA1c": {
            "regex": r"(?:hba1c|hb\s*a1c|glycated\s+h(?:ae)?moglobin|glyco(?:sylated)?\s+h(?:ae)?moglobin|a1c)[\s:]*(?:result)?[\s:]*([\d\.]+)",
            "normalizer": normalize_hba1c
        },

        # NEUTROPHILS
        "Neutrophils": {
            "regex": r"(?:neutrophil|neutro|neut|polymorphs?|pmn)[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        # LYMPHOCYTES
        "Lymphocytes": {
            "regex": r"(?:lymphocyte|lympho|lymph)[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        # MONOCYTES
        "Monocytes": {
            "regex": r"(?:monocyte|mono)[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        # EOSINOPHILS
        "Eosinophils": {
            "regex": r"(?:eosinophil|eosino|eos)[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        # BASOPHILS
        "Basophils": {
            "regex": r"(?:basophil|baso)[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        # ESR - Erythrocyte Sedimentation Rate
        "ESR": {
            "regex": r"(?:esr|e\.s\.r\.|sed\s+rate|erythrocyte\s+sedimentation)[\s:]*(?:rate)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # HEMATOCRIT / PCV
        "Hematocrit": {
            "regex": r"(?:hematocrit|haematocrit|hct|pcv|packed\s+cell\s+volume)[\s:]*(?:value)?[\s:]*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        # MCV - Mean Corpuscular Volume
        "MCV": {
            "regex": r"(?:mcv|mean\s+corp(?:uscular)?\s+vol(?:ume)?)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # MCH - Mean Corpuscular Hemoglobin
        "MCH": {
            "regex": r"(?:mch|mean\s+corp(?:uscular)?\s+h(?:ae)?moglobin)[\s:]*(?!c)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # MCHC - Mean Corpuscular Hemoglobin Concentration
        "MCHC": {
            "regex": r"(?:mchc|mean\s+corp(?:uscular)?\s+h(?:ae)?moglobin\s+conc(?:entration)?)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # RDW - Red Cell Distribution Width
        "RDW": {
            "regex": r"(?:rdw|red\s+cell\s+dist(?:ribution)?\s+width)[\s:]*(?:cv)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # MPV - Mean Platelet Volume
        "MPV": {
            "regex": r"(?:mpv|mean\s+platelet\s+vol(?:ume)?)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # CREATININE
        "Creatinine": {
            "regex": r"(?:creatinine|creat|crea)[\s:]*(?:serum)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # UREA / BUN
        "Urea": {
            "regex": r"(?:urea|blood\s+urea|bun|blood\s+urea\s+nitrogen)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # URIC ACID
        "Uric Acid": {
            "regex": r"(?:uric\s+acid|urate)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # CHOLESTEROL - Total
        "Total Cholesterol": {
            "regex": r"(?:total\s+)?cholesterol[\s:]*(?:total)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # TRIGLYCERIDES
        "Triglycerides": {
            "regex": r"(?:triglyceride|trig|tg)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # HDL Cholesterol
        "HDL": {
            "regex": r"(?:hdl|high\s+density\s+lipoprotein)[\s:]*(?:cholesterol)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # LDL Cholesterol
        "LDL": {
            "regex": r"(?:ldl|low\s+density\s+lipoprotein)[\s:]*(?:cholesterol)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # VLDL Cholesterol
        "VLDL": {
            "regex": r"(?:vldl|very\s+low\s+density\s+lipoprotein)[\s:]*(?:cholesterol)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # SGPT / ALT - Liver Function
        "SGPT": {
            "regex": r"(?:sgpt|alt|alanine\s+(?:amino)?transaminase)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # SGOT / AST - Liver Function
        "SGOT": {
            "regex": r"(?:sgot|ast|aspartate\s+(?:amino)?transaminase)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # BILIRUBIN - Total
        "Total Bilirubin": {
            "regex": r"(?:total\s+)?bilirubin[\s:]*(?:total)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ALBUMIN
        "Albumin": {
            "regex": r"(?:albumin|alb)[\s:]*(?:serum)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # TOTAL PROTEIN
        "Total Protein": {
            "regex": r"(?:total\s+)?protein[\s:]*(?:serum)?[\s:]*(?:total)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # TSH - Thyroid
        "TSH": {
            "regex": r"(?:tsh|thyroid\s+stimulating\s+hormone)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # T3 - Thyroid
        "T3": {
            "regex": r"(?:^|\s)t3[\s:]*(?:total)?[\s:]*(?:triiodothyronine)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # T4 - Thyroid
        "T4": {
            "regex": r"(?:^|\s)t4[\s:]*(?:total)?[\s:]*(?:thyroxine)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # VITAMIN D
        "Vitamin D": {
            "regex": r"(?:vitamin\s+d|vit\s+d|25\s*\(?oh\)?[\s\-]*(?:vitamin\s+)?d)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # VITAMIN B12
        "Vitamin B12": {
            "regex": r"(?:vitamin\s+b12|vit\s+b12|b12|cobalamin)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # CALCIUM
        "Calcium": {
            "regex": r"(?:calcium|ca)[\s:]*(?:serum)?[\s:]*(?:total)?[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # SODIUM
        "Sodium": {
            "regex": r"(?:sodium|na\+?)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # POTASSIUM
        "Potassium": {
            "regex": r"(?:potassium|k\+?)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        },

        # CHLORIDE
        "Chloride": {
            "regex": r"(?:chloride|cl\-?)[\s:]*([\d\.]+)",
            "normalizer": normalize_plain
        }
    }

    for test, config in patterns.items():
        match = re.search(config["regex"], text_lower, re.IGNORECASE | re.MULTILINE)

        if not match:
            print(f"❌ {test}: Not found")
            continue

        raw_value = match.group(1)
        unit = match.group(2) if match.lastindex >= 2 else None

        print(f"✅ {test}: Found value={raw_value}, unit={unit}")

        try:
            normalized = config["normalizer"](raw_value, unit)
            results[test] = round(normalized, 2)
            print(f"   → Normalized to: {results[test]}")
        except Exception as e:
            print(f"   ⚠️ Normalization failed: {e}")
            continue

    print("=" * 50)
    print(f"TOTAL PARSED VALUES: {len(results)}")
    print("=" * 50 + "\n")

    return results