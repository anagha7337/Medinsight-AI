import requests
import os
import time

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_TOKEN = os.getenv("HF_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def build_prompt(test_name, value, normal_range, status):
    return f"""
You are a medical assistant explaining lab reports to non-medical people.

Test name: {test_name}
Result value: {value}
Normal range: {normal_range}
Status: {status}

Explain in a friendly, reassuring way:

1. What this test measures in the body
2. What it means when the value is {status.lower()}
3. Common biological or lifestyle causes
4. Possible symptoms (if any)
5. A simple follow-up suggestion

Do NOT diagnose diseases.
Do NOT alarm the user.
Use simple language.
Keep it concise but informative.
"""

def interpret_abnormality(test_name, value, normal_range, status):
    payload = {
        "inputs": build_prompt(test_name, value, normal_range, status),
        "parameters": {
            "max_new_tokens": 250,
            "temperature": 0.3
        }
    }

    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=60
        )

        data = response.json()

        # 🟡 Model loading
        if isinstance(data, dict) and "error" in data:
            return "AI model is warming up. Please try again in a few seconds."

        # 🟢 Normal response
        if isinstance(data, list) and len(data) > 0:
            text = data[0].get("generated_text", "").strip()
            if text:
                return text

        return "Unable to generate interpretation at this time."

    except Exception as e:
        print("AI ERROR:", e)
        return "Unable to generate interpretation at this time."
