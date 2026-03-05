import re

# ---------------- NORMALIZATION HELPERS ---------------- #

def normalize_plain(value, unit=None):
    return float(value)


def normalize_percentage(value, unit=None):
    return float(value)


def normalize_platelets(value, unit=None):
    value = float(value)

    if unit and unit in ["lakh", "lakhs"]:
        return value * 100000  # lakh → /µL

    return value  # already /µL


def normalize_wbc(value, unit=None):
    value = float(value)

    if unit and ("10^3" in unit or "x10" in unit or "thousand" in unit.lower()):
        return value * 1000  # x10^3 → /µL

    return value


def normalize_rbc(value, unit=None):
    value = float(value)

    # OCR sometimes gives absolute counts
    if value > 100:
        return value / 1_000_000  # convert to million/µL

    return value


# ---------------- MAIN PARSER ---------------- #

def parse_report(text):
    results = {}
    text_lower = text.lower()

    print("\n" + "=" * 50)
    print("PARSING REPORT...")
    print("=" * 50)

    patterns = {
        "Hemoglobin": {
            "regex": r"(hemoglobin|haemoglobin|hb|hgb)\s*[:\-]?\s*([\d\.]+)",
            "normalizer": normalize_plain
        },

        "WBC": {
            "regex": r"(wbc|total\s+wbc\s+count|wbc\s+count|white\s+blood\s+cell)\s*[:\-]?\s*([\d\.]+)\s*(x10\^3|10\^3|thousand|/ul|/µl)?",
            "normalizer": normalize_wbc
        },

        "RBC": {
            "regex": r"(rbc|total\s+rbc\s+count|rbc\s+count|red\s+blood\s+cell)\s*[:\-]?\s*([\d\.]+)\s*(million|mill)?",
            "normalizer": normalize_rbc
        },

        "Platelets": {
            "regex": r"(platelet\s+count|platelets?)\s*[:\-]?\s*([\d\.]+)\s*(lakh|lakhs|/ul|/µl|/cumm)?",
            "normalizer": normalize_platelets
        },

        "Blood Sugar": {
            "regex": r"(glucose|blood\s+sugar|fasting\s+glucose|random\s+glucose)\s*[:\-]?\s*([\d\.]+)",
            "normalizer": normalize_plain
        },

        "Neutrophils": {
            "regex": r"(neutrophils?)\s*[:\-]?\s*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "Lymphocytes": {
            "regex": r"(lymphocytes?)\s*[:\-]?\s*([\d\.]+)",
            "normalizer": normalize_percentage
        },

        "PCV": {
            "regex": r"(pcv|packed\s+cell\s+volume|hematocrit|haematocrit)\s*[:\-]?\s*([\d\.]+)\s*(%)?",
            "normalizer": normalize_percentage
        },

        "ESR": {
            "regex": r"(esr|erythrocyte\s+sedimentation)\s*[:\-]?\s*([\d\.]+)",
            "normalizer": normalize_plain
        }
    }

    for test, config in patterns.items():
        match = re.search(config["regex"], text_lower, re.IGNORECASE)

        if not match:
            print(f"❌ {test}: Not found")
            continue

        raw_value = match.group(2)
        unit = match.group(3) if match.lastindex >= 3 else None

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