def check_abnormal_values(parsed_values):
    normal_ranges = {
        "Hemoglobin": (13.0, 17.0),        # g/dL (adjusted for both genders)
        "RBC": (4.2, 5.9),                 # million/µL
        "WBC": (4000, 11000),              # /µL
        "Platelets": (150000, 450000),     # /µL
        "Blood Sugar": (70, 140),          # mg/dL (fasting/random)
        "Neutrophils": (40, 70),           # %
        "Lymphocytes": (20, 40),           # %
        "ESR": (0, 20)                     # mm/hr
    }

    abnormal = {}

    print("\n" + "=" * 50)
    print("CHECKING ABNORMAL VALUES...")
    print("=" * 50)

    for test, value in parsed_values.items():
        if test not in normal_ranges:
            print(f"⚠️ {test}: No reference range defined")
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
                "normal_range": f"{low} - {high}"
            }
            print(f"🔻 {test}: {value} is LOW (normal: {low}-{high})")

        elif value > high:
            abnormal[test] = {
                "value": value,
                "status": "HIGH",
                "normal_range": f"{low} - {high}"
            }
            print(f"🔺 {test}: {value} is HIGH (normal: {low}-{high})")
        else:
            print(f"✅ {test}: {value} is NORMAL (normal: {low}-{high})")

    print("=" * 50)
    print(f"TOTAL ABNORMAL VALUES: {len(abnormal)}")
    print("=" * 50 + "\n")

    return abnormal