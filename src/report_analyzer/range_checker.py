def check_abnormal_values(parsed_values):

    normal_ranges = {
        # ── COMPLETE BLOOD COUNT (CBC) ────────────────────────────────────────
        "Hemoglobin":      (13.0, 17.0),   # g/dL
        "RBC":             (4.2,  5.9),    # million/µL
        "WBC":             (4000, 11000),  # /µL
        "Platelets":       (150000, 450000),
        "Hematocrit":      (40,   50),     # %
        "MCV":             (83,   101),    # fL
        "MCH":             (27,   32),     # pg
        "MCHC":            (31.5, 34.5),   # g/dL
        "RDW":             (11.6, 14.0),   # %
        "MPV":             (7.5,  11.5),   # fL

        # ── DIFFERENTIAL COUNT ────────────────────────────────────────────────
        "Neutrophils":     (40,   70),     # %
        "Lymphocytes":     (20,   40),     # %
        "Monocytes":       (2,    10),     # %
        "Eosinophils":     (1,    6),      # %
        "Basophils":       (0,    2),      # %
        "ESR":             (0,    20),     # mm/hr

        # ── DIABETES / GLUCOSE ────────────────────────────────────────────────
        # Random blood sugar: normal <140 mg/dL
        "Blood Sugar":          (70,  140),
        # Fasting blood sugar: normal <126 mg/dL  (ADA: <100 optimal, <126 pre-diabetic threshold)
        "Fasting Blood Sugar":  (70,  126),
        "HbA1c":                (4.0, 5.6),  # % (5.7–6.4 pre-diabetes, ≥6.5 diabetes)

        # ── LIPID PROFILE ─────────────────────────────────────────────────────
        "Total Cholesterol":    (0,   200),
        "Triglycerides":        (0,   150),
        "HDL":                  (40,  200),
        "LDL":                  (0,   100),
        "VLDL":                 (2,   30),

        # ── LIVER FUNCTION TESTS (LFT) ────────────────────────────────────────
        "SGPT":                 (0,   40),
        "SGOT":                 (0,   40),
        "Total Bilirubin":      (0.3, 1.2),
        "Albumin":              (3.5, 5.5),
        "Total Protein":        (6.0, 8.3),

        # ── KIDNEY FUNCTION TESTS (KFT) ───────────────────────────────────────
        "Creatinine":           (0.6, 1.2),
        "Urea":                 (15,  40),
        "Uric Acid":            (3.5, 7.2),

        # ── THYROID FUNCTION TESTS ────────────────────────────────────────────
        "TSH":                  (0.4, 4.5),
        "T3":                   (80,  200),
        "T4":                   (4.5, 12.0),

        # ── VITAMINS ──────────────────────────────────────────────────────────
        "Vitamin D":            (30,  100),
        "Vitamin B12":          (200, 900),

        # ── ELECTROLYTES ──────────────────────────────────────────────────────
        "Sodium":               (135, 145),
        "Potassium":            (3.5, 5.0),
        "Chloride":             (96,  106),
        "Calcium":              (8.5, 10.5),
    }

    # ── EXTREME-VALUE THRESHOLDS ──────────────────────────────────────────────
    #
    #  If a value is more than this multiple above the high end of the normal
    #  range, it is almost certainly a parsing artifact even after the sanity
    #  bounds pass.  The AI explanation will be suppressed (skip_ai = True).
    #
    #  Rule-of-thumb: 5× the upper normal limit is almost always impossible.
    #  For a handful of tests (e.g. Vitamin B12 supplementation can genuinely
    #  reach 2 000+) we use a looser multiplier.
    # ─────────────────────────────────────────────────────────────────────────
    EXTREME_MULTIPLIER_DEFAULT = 5.0

    EXTREME_MULTIPLIER_OVERRIDE = {
        "SGPT":        10.0,   # acute hepatitis can push ALT >2 000 U/L
        "SGOT":        10.0,
        "Triglycerides": 8.0,  # severe hypertriglyceridemia can reach 1 000+
        "Vitamin B12": 10.0,   # supplementation / injection
        "WBC":          4.0,   # leukaemia can push above 100 000
        "Platelets":    3.0,   # reactive thrombocytosis
        "ESR":          6.0,   # severe inflammation
    }

    abnormal = {}

    print("\n" + "=" * 60)
    print("CHECKING ABNORMAL VALUES...")
    print("=" * 60)

    for test, value in parsed_values.items():
        if test not in normal_ranges:
            print(f"⚠️  {test}: No reference range defined (skipping)")
            continue

        try:
            value = float(value)
        except Exception:
            print(f"❌  {test}: Invalid value format")
            continue

        low, high = normal_ranges[test]

        if low <= value <= high:
            print(f"✅  {test}: {value} is NORMAL ({low}–{high})")
            continue

        status = "LOW" if value < low else "HIGH"

        # ── Extreme-value check ───────────────────────────────────────────────
        multiplier = EXTREME_MULTIPLIER_OVERRIDE.get(test, EXTREME_MULTIPLIER_DEFAULT)
        extreme_threshold = high * multiplier
        skip_ai = (status == "HIGH" and value > extreme_threshold)

        if skip_ai:
            print(f"🚨  {test}: {value} is EXTREMELY HIGH "
                  f"(threshold {extreme_threshold:.0f}) — AI explanation suppressed "
                  f"(likely a parsing artifact that slipped past sanity bounds)")
        else:
            print(f"{'🔻' if status == 'LOW' else '🔺'}  "
                  f"{test}: {value} is {status} (normal: {low}–{high})")

        abnormal[test] = {
            "value":        value,
            "status":       status,
            "normal_range": f"{low} - {high}",
            "category":     get_test_category(test),
            "skip_ai":      skip_ai,    # ← consumed by ai_interpreter.py
        }

    print("=" * 60)
    print(f"TOTAL ABNORMAL VALUES: {len(abnormal)}")
    print("=" * 60 + "\n")

    return abnormal


# ─────────────────────────────────────────────────────────────────────────────

def get_test_category(test_name):
    categories = {
        "Complete Blood Count": [
            "Hemoglobin", "RBC", "WBC", "Platelets", "Hematocrit",
            "MCV", "MCH", "MCHC", "RDW", "MPV", "ESR",
        ],
        "Differential Count": [
            "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils",
        ],
        "Diabetes": [
            "Blood Sugar", "Fasting Blood Sugar", "HbA1c",
        ],
        "Lipid Profile": [
            "Total Cholesterol", "Triglycerides", "HDL", "LDL", "VLDL",
        ],
        "Liver Function": [
            "SGPT", "SGOT", "Total Bilirubin", "Albumin", "Total Protein",
        ],
        "Kidney Function": [
            "Creatinine", "Urea", "Uric Acid",
        ],
        "Thyroid Function": [
            "TSH", "T3", "T4",
        ],
        "Vitamins": [
            "Vitamin D", "Vitamin B12",
        ],
        "Electrolytes": [
            "Sodium", "Potassium", "Chloride", "Calcium",
        ],
    }
    for category, tests in categories.items():
        if test_name in tests:
            return category
    return "Other Tests"