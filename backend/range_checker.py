def check_abnormal_values(parsed_values):
    """
    Check parsed values against normal ranges for comprehensive blood tests
    Including: CBC, Diabetes, Lipid Profile, Liver, Kidney, Thyroid, Vitamins, Electrolytes
    """
    
    normal_ranges = {
        # ========== COMPLETE BLOOD COUNT (CBC) ==========
        "Hemoglobin": (13.0, 17.0),        # g/dL (Male: 13.5-17.5, Female: 12.0-15.5)
        "RBC": (4.2, 5.9),                 # million/µL
        "WBC": (4000, 11000),              # /µL
        "Platelets": (150000, 450000),     # /µL
        "Hematocrit": (40, 50),            # % (Male: 40-54, Female: 36-48)
        "MCV": (83, 101),                  # fL (femtoliters)
        "MCH": (27, 32),                   # pg (picograms)
        "MCHC": (31.5, 34.5),              # g/dL
        "RDW": (11.6, 14.0),               # %
        "MPV": (7.5, 11.5),                # fL
        
        # Differential Count
        "Neutrophils": (40, 70),           # %
        "Lymphocytes": (20, 40),           # %
        "Monocytes": (2, 10),              # %
        "Eosinophils": (1, 6),             # %
        "Basophils": (0, 2),               # %
        
        "ESR": (0, 20),                    # mm/hr (Male: 0-15, Female: 0-20)
        
        # ========== DIABETES / GLUCOSE TESTS ==========
        "Blood Sugar": (70, 140),          # mg/dL (Fasting: 70-100, Random: <140)
        "HbA1c": (4.0, 5.6),              # % (5.7-6.4: Prediabetes, ≥6.5: Diabetes)
        
        # ========== LIPID PROFILE ==========
        "Total Cholesterol": (0, 200),     # mg/dL (Desirable: <200, Borderline: 200-239, High: ≥240)
        "Triglycerides": (0, 150),         # mg/dL (Normal: <150, Borderline: 150-199, High: ≥200)
        "HDL": (40, 200),                  # mg/dL (Low risk: >60, High risk: <40)
        "LDL": (0, 100),                   # mg/dL (Optimal: <100, High: >160)
        "VLDL": (2, 30),                   # mg/dL
        
        # ========== LIVER FUNCTION TESTS (LFT) ==========
        "SGPT": (0, 40),                   # U/L (ALT)
        "SGOT": (0, 40),                   # U/L (AST)
        "Total Bilirubin": (0.3, 1.2),     # mg/dL
        "Albumin": (3.5, 5.5),             # g/dL
        "Total Protein": (6.0, 8.3),       # g/dL
        
        # ========== KIDNEY FUNCTION TESTS (KFT) ==========
        "Creatinine": (0.6, 1.2),          # mg/dL (Male: 0.7-1.3, Female: 0.6-1.1)
        "Urea": (15, 40),                  # mg/dL
        "Uric Acid": (3.5, 7.2),           # mg/dL (Male: 3.5-7.2, Female: 2.6-6.0)
        
        # ========== THYROID FUNCTION TESTS ==========
        "TSH": (0.4, 4.5),                 # µIU/mL
        "T3": (80, 200),                   # ng/dL
        "T4": (4.5, 12.0),                 # µg/dL
        
        # ========== VITAMINS ==========
        "Vitamin D": (30, 100),            # ng/mL (Deficiency: <20, Insufficiency: 20-30)
        "Vitamin B12": (200, 900),         # pg/mL (Deficiency: <200)
        
        # ========== ELECTROLYTES ==========
        "Sodium": (135, 145),              # mEq/L
        "Potassium": (3.5, 5.0),           # mEq/L
        "Chloride": (96, 106),             # mEq/L
        "Calcium": (8.5, 10.5),            # mg/dL
    }

    abnormal = {}

    print("\n" + "=" * 50)
    print("CHECKING ABNORMAL VALUES...")
    print("=" * 50)

    for test, value in parsed_values.items():
        if test not in normal_ranges:
            print(f"⚠️ {test}: No reference range defined (skipping)")
            continue

        try:
            value = float(value)
        except:
            print(f"❌ {test}: Invalid value format")
            continue

        low, high = normal_ranges[test]

        if value < low:
            abnormal[test] = {
                "value": value,
                "status": "LOW",
                "normal_range": f"{low} - {high}",
                "category": get_test_category(test)
            }
            print(f"🔻 {test}: {value} is LOW (normal: {low}-{high})")

        elif value > high:
            abnormal[test] = {
                "value": value,
                "status": "HIGH",
                "normal_range": f"{low} - {high}",
                "category": get_test_category(test)
            }
            print(f"🔺 {test}: {value} is HIGH (normal: {low}-{high})")
        else:
            print(f"✅ {test}: {value} is NORMAL (normal: {low}-{high})")

    print("=" * 50)
    print(f"TOTAL ABNORMAL VALUES: {len(abnormal)}")
    print("=" * 50 + "\n")

    return abnormal


def get_test_category(test_name):
    """Categorize tests for better organization"""
    
    categories = {
        "Complete Blood Count": [
            "Hemoglobin", "RBC", "WBC", "Platelets", "Hematocrit", 
            "MCV", "MCH", "MCHC", "RDW", "MPV", "ESR"
        ],
        "Differential Count": [
            "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils"
        ],
        "Diabetes": [
            "Blood Sugar", "HbA1c"
        ],
        "Lipid Profile": [
            "Total Cholesterol", "Triglycerides", "HDL", "LDL", "VLDL"
        ],
        "Liver Function": [
            "SGPT", "SGOT", "Total Bilirubin", "Albumin", "Total Protein"
        ],
        "Kidney Function": [
            "Creatinine", "Urea", "Uric Acid"
        ],
        "Thyroid Function": [
            "TSH", "T3", "T4"
        ],
        "Vitamins": [
            "Vitamin D", "Vitamin B12"
        ],
        "Electrolytes": [
            "Sodium", "Potassium", "Chloride", "Calcium"
        ]
    }
    
    for category, tests in categories.items():
        if test_name in tests:
            return category
    
    return "Other Tests"