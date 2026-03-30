import re

# ─────────────────────────────────────────────────────────────────────────────
#  NORMALIZATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def normalize_plain(value, unit=None):
    return float(value)

def normalize_percentage(value, unit=None):
    return float(value)

def normalize_platelets(value, unit=None):
    value = float(value)
    if unit:
        unit_lower = unit.lower()
        if "lakh" in unit_lower:
            return value * 100_000
        elif "thousand" in unit_lower or unit_lower == "k":
            return value * 1_000
    if value < 1_000:
        return value * 100_000
    return value

def normalize_wbc(value, unit=None):
    value = float(value)
    if unit:
        unit_lower = unit.lower()
        if any(x in unit_lower for x in ["10^3", "x10", "thousand", "/cumm", "cumm", "x10³", "10³"]):
            return value * 1_000 if value <= 100 else value
    return value if value >= 1_000 else value * 1_000

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
    value = float(value)
    if unit and ("mmol" in unit.lower() or "mol" in unit.lower()):
        return value * 18          # 1 mmol/L ≈ 18 mg/dL
    if value < 20:
        return value * 18
    return value


# ─────────────────────────────────────────────────────────────────────────────
#  SANITY-CHECK BOUNDS
#
#  Values outside these physical bounds almost certainly come from a parsing
#  mistake (lab codes, serial numbers, etc.).  The parser will silently drop
#  them instead of flagging them as abnormal.
# ─────────────────────────────────────────────────────────────────────────────

SANITY_BOUNDS = {
    # CBC
    "Hemoglobin":           (1,    25),
    "RBC":                  (0.5,  10),
    "WBC":                  (500,  100_000),
    "Platelets":            (5_000, 1_500_000),
    "Hematocrit":           (5,    70),
    "MCV":                  (50,   130),
    "MCH":                  (10,   50),
    "MCHC":                 (20,   40),
    "RDW":                  (5,    30),
    "MPV":                  (2,    20),
    # Differential
    "Neutrophils":          (0,    100),
    "Lymphocytes":          (0,    100),
    "Monocytes":            (0,    30),
    "Eosinophils":          (0,    60),
    "Basophils":            (0,    10),
    "ESR":                  (0,    150),
    # Glucose
    "Blood Sugar":          (20,   700),
    "Fasting Blood Sugar":  (20,   500),
    "HbA1c":                (2,    20),
    # Lipids
    "Total Cholesterol":    (50,   700),
    "Triglycerides":        (20,   2_000),
    "HDL":                  (10,   150),
    "LDL":                  (10,   500),
    "VLDL":                 (1,    200),
    # Liver
    "SGPT":                 (0,    3_000),
    "SGOT":                 (0,    3_000),
    "Total Bilirubin":      (0.1,  30),
    "Albumin":              (1,    7),
    "Total Protein":        (3,    12),
    # Kidney
    "Creatinine":           (0.1,  20),
    "Urea":                 (5,    300),
    "Uric Acid":            (0.5,  20),
    # Thyroid
    "TSH":                  (0.01, 100),
    "T3":                   (30,   500),
    "T4":                   (1,    30),
    # Vitamins
    "Vitamin D":            (1,    300),
    "Vitamin B12":          (50,   3_000),
    # Electrolytes — these are the problem children!
    "Sodium":               (100,  175),
    "Potassium":            (1.5,  10),       # K1000 → 1000 would be rejected
    "Chloride":             (70,   130),      # FGCl900 → 900 would be rejected
    "Calcium":              (4,    16),
}


def is_within_sanity_bounds(test_name, value):
    """Return True if the value is plausible for the given test."""
    if test_name not in SANITY_BOUNDS:
        return True
    lo, hi = SANITY_BOUNDS[test_name]
    return lo <= value <= hi


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PARSER
# ─────────────────────────────────────────────────────────────────────────────

def parse_report(text):
    results = {}
    text_lower = text.lower()

    print("\n" + "=" * 60)
    print("PARSING REPORT...")
    print("=" * 60)

    # ── KEY CHANGE ────────────────────────────────────────────────────────────
    #  Every numeric capture group is now preceded by  (?<![A-Za-z\d])
    #  which means "not immediately preceded by a letter or digit".
    #  This prevents  K1000 / FGCl900 / Na135ABC  etc. from matching.
    #
    #  Pattern template note:
    #    - Test keyword(s)
    #    - Optional label noise  [\s:]*(?:...)?[\s:]*
    #    - (?<![A-Za-z\d])  ← negative lookbehind  (the key guard)
    #    - ([\d\.]+)         ← value capture
    #    - optional unit capture
    # ─────────────────────────────────────────────────────────────────────────

    patterns = {

        # ── CBC ──────────────────────────────────────────────────────────────

        "Hemoglobin": {
            "regex": r"(?:hemoglobin|haemoglobin|hgb|hb|h\.b\.|hemo|haemo)"
                     r"[\s:]*(?:\(hb\))?[\s:]*(?:count)?[\s:]*(?:result)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "WBC": {
            "regex": r"(?:wbc|w\.b\.c\.|white\s+blood\s+cell|total\s+wbc"
                     r"|total\s+leuko(?:cyte)?|leuko(?:cyte)?\s+count|tlc)"
                     r"[\s:]*(?:count)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)[\s,]*"
                     r"(x10\^3|10\^3|x10³|10³|thousand|/cumm|cumm|/ul|/µl|cells/cmm)?",
            "normalizer": normalize_wbc
        },

        "RBC": {
            "regex": r"(?:rbc|r\.b\.c\.|red\s+blood\s+cell|total\s+rbc|erythrocyte)"
                     r"[\s:]*(?:count)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)[\s,]*"
                     r"(million|mill|mil|x10\^6|10\^6)?",
            "normalizer": normalize_rbc
        },

        "Platelets": {
            "regex": r"(?:platelet|plt|thrombocyte)"
                     r"[\s:]*(?:count)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)[\s,]*"
                     r"(lakh|lakhs|thousand|k|/ul|/µl|/cumm|cumm|cells)?",
            "normalizer": normalize_platelets
        },

        # ── GLUCOSE — split into two separate tests ───────────────────────────

        # Fasting Blood Sugar  (must come BEFORE the generic Blood Sugar pattern)
        "Fasting Blood Sugar": {
            "regex": r"(?:fasting\s+(?:blood\s+)?(?:glucose|sugar)|fbs"
                     r"|fasting\s+plasma\s+glucose)"
                     r"[\s:]*(?:result)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)[\s,]*"
                     r"(mg/dl|mmol/l|mmol)?",
            "normalizer": normalize_glucose
        },

        # Random / generic blood sugar (post-prandial / random / plain label)
        "Blood Sugar": {
            "regex": r"(?:(?<!fasting\s)glucose|random\s+(?:blood\s+)?(?:glucose|sugar)"
                     r"|ppbs|post\s+prandial|rbs|blood\s+sugar(?!\s+fasting))"
                     r"[\s:]*(?:result)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)[\s,]*"
                     r"(mg/dl|mmol/l|mmol)?",
            "normalizer": normalize_glucose
        },

        "HbA1c": {
            "regex": r"(?:hba1c|hb\s*a1c|glycated\s+h(?:ae)?moglobin"
                     r"|glyco(?:sylated)?\s+h(?:ae)?moglobin|a1c)"
                     r"[\s:]*(?:result)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_hba1c
        },

        # ── Differential ─────────────────────────────────────────────────────

        "Neutrophils": {
            "regex": r"(?:neutrophil|neutro|neut|polymorphs?|pmn)"
                     r"[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "Lymphocytes": {
            "regex": r"(?:lymphocyte|lympho|lymph)"
                     r"[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "Monocytes": {
            "regex": r"(?:monocyte|mono)"
                     r"[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "Eosinophils": {
            "regex": r"(?:eosinophil|eosino|eos)"
                     r"[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "Basophils": {
            "regex": r"(?:basophil|baso)"
                     r"[\s:]*(?:count)?[\s:]*(?:percent)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "ESR": {
            "regex": r"(?:esr|e\.s\.r\.|sed\s+rate|erythrocyte\s+sedimentation)"
                     r"[\s:]*(?:rate)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ── CBC indices ───────────────────────────────────────────────────────

        "Hematocrit": {
            "regex": r"(?:hematocrit|haematocrit|hct|pcv|packed\s+cell\s+volume)"
                     r"[\s:]*(?:value)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "MCV": {
            "regex": r"(?:mcv|mean\s+corp(?:uscular)?\s+vol(?:ume)?)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "MCH": {
            # Lookahead (?!c) keeps MCHC from being swallowed by this pattern
            "regex": r"(?:mch|mean\s+corp(?:uscular)?\s+h(?:ae)?moglobin)"
                     r"[\s:]*(?!c)[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "MCHC": {
            "regex": r"(?:mchc|mean\s+corp(?:uscular)?\s+h(?:ae)?moglobin\s+conc(?:entration)?)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "RDW": {
            "regex": r"(?:rdw|red\s+cell\s+dist(?:ribution)?\s+width)"
                     r"[\s:]*(?:cv)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "MPV": {
            "regex": r"(?:mpv|mean\s+platelet\s+vol(?:ume)?)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ── Kidney ────────────────────────────────────────────────────────────

        "Creatinine": {
            "regex": r"(?:creatinine|creat|crea)"
                     r"[\s:]*(?:serum)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Urea": {
            "regex": r"(?:urea|blood\s+urea|bun|blood\s+urea\s+nitrogen)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Uric Acid": {
            "regex": r"(?:uric\s+acid|urate)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ── Lipids ────────────────────────────────────────────────────────────

        "Total Cholesterol": {
            "regex": r"(?:total\s+)?cholesterol[\s:]*(?:total)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Triglycerides": {
            "regex": r"(?:triglyceride|trig|tg)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "HDL": {
            "regex": r"(?:hdl|high\s+density\s+lipoprotein)"
                     r"[\s:]*(?:cholesterol)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "LDL": {
            "regex": r"(?:ldl|low\s+density\s+lipoprotein)"
                     r"[\s:]*(?:cholesterol)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "VLDL": {
            "regex": r"(?:vldl|very\s+low\s+density\s+lipoprotein)"
                     r"[\s:]*(?:cholesterol)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ── Liver ─────────────────────────────────────────────────────────────

        "SGPT": {
            "regex": r"(?:sgpt|alt|alanine\s+(?:amino)?transaminase)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "SGOT": {
            "regex": r"(?:sgot|ast|aspartate\s+(?:amino)?transaminase)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Total Bilirubin": {
            "regex": r"(?:total\s+)?bilirubin[\s:]*(?:total)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Albumin": {
            "regex": r"(?:albumin|alb)"
                     r"[\s:]*(?:serum)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Total Protein": {
            "regex": r"(?:total\s+)?protein[\s:]*(?:serum)?[\s:]*(?:total)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ── Thyroid ───────────────────────────────────────────────────────────

        "TSH": {
            "regex": r"(?:tsh|thyroid\s+stimulating\s+hormone)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "T3": {
            "regex": r"(?:^|\s)t3[\s:]*(?:total)?[\s:]*(?:triiodothyronine)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "T4": {
            "regex": r"(?:^|\s)t4[\s:]*(?:total)?[\s:]*(?:thyroxine)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ── Vitamins ──────────────────────────────────────────────────────────

        "Vitamin D": {
            "regex": r"(?:vitamin\s+d|vit\s+d|25\s*\(?oh\)?[\s\-]*(?:vitamin\s+)?d)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Vitamin B12": {
            "regex": r"(?:vitamin\s+b12|vit\s+b12|b12|cobalamin)"
                     r"[\s:]*(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # ── Electrolytes — TIGHTEST lookbehind guards ─────────────────────────

        # Sodium:   must be preceded by whitespace / colon / start-of-line, NOT a letter/digit
        "Sodium": {
            "regex": r"(?:sodium|na\+?)"
                     r"[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # Potassium:  guards against K1000, K+1000, etc.
        "Potassium": {
            "regex": r"(?:potassium|k\+?)"
                     r"[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        # Chloride:  guards against Cl-900, FGCl900, etc.
        "Chloride": {
            "regex": r"(?:chloride|cl\-?)"
                     r"[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Calcium": {
            "regex": r"(?:calcium|ca)"
                     r"[\s:]*(?:serum)?[\s:]*(?:total)?[\s:]*"
                     r"(?<![A-Za-z\d])([\d\.]+)",
            "normalizer": normalize_plain
        },
    }

    for test, config in patterns.items():
        match = re.search(config["regex"], text_lower, re.IGNORECASE | re.MULTILINE)

        if not match:
            print(f"❌ {test}: Not found")
            continue

        raw_value = match.group(1)
        unit = match.group(2) if match.lastindex and match.lastindex >= 2 else None

        print(f"✅ {test}: Found value={raw_value}, unit={unit}")

        try:
            normalized = config["normalizer"](raw_value, unit)
        except Exception as e:
            print(f"   ⚠️ Normalization failed: {e}")
            continue

        normalized = round(normalized, 2)

        # ── Sanity-bound check ────────────────────────────────────────────────
        if not is_within_sanity_bounds(test, normalized):
            print(f"   🚫 REJECTED — {normalized} is outside sanity bounds "
                  f"{SANITY_BOUNDS.get(test)} for {test}. Likely a parsing artifact.")
            continue

        results[test] = normalized
        print(f"   → Accepted: {results[test]}")

    print("=" * 60)
    print(f"TOTAL PARSED VALUES: {len(results)}")
    print("=" * 60 + "\n")

    return results