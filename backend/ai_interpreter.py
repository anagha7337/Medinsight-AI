import os
from groq import Groq

# ⚙️ Initialize Groq client
# Get your API key from: https://console.groq.com/
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate API key exists
if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
    print("\n" + "=" * 60)
    print("❌ ERROR: GROQ_API_KEY not configured!")
    print("=" * 60)
    print("\n📋 Please follow these steps:\n")
    print("1. Get your API key from: https://console.groq.com/")
    print("2. Set it as an environment variable:\n")
    print("   Windows (CMD):")
    print("     set GROQ_API_KEY=gsk_your_key_here\n")
    print("   Windows (PowerShell):")
    print("     $env:GROQ_API_KEY='gsk_your_key_here'\n")
    print("   Mac/Linux:")
    print("     export GROQ_API_KEY=gsk_your_key_here\n")
    print("3. Run your app again: python app.py")
    print("=" * 60 + "\n")
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=GROQ_API_KEY)

def build_prompt(test_name, value, normal_range, status):
    """Build a medical explanation prompt for the AI"""
    return f"""You are a friendly medical assistant explaining lab test results to someone without medical training.

**Test Details:**
- Test: {test_name}
- Their Result: {value}
- Normal Range: {normal_range}
- Status: {status}

Please explain in simple, friendly language:

1. What this test measures in the body (in one sentence)
2. What it means when the value is {status.lower()} (be reassuring, not alarming)
3. Common everyday causes (lifestyle, diet, or natural factors)
4. What they might notice or feel (if anything)
5. A simple next step (like "discuss with your doctor" or "monitor it")

Important guidelines:
- Use everyday language, avoid medical jargon
- Be reassuring and calm in tone
- Don't diagnose specific diseases
- Keep it concise (4-5 sentences total)
- Focus on education, not fear

Example tone: "Your hemoglobin is a bit low, which means your blood isn't carrying as much oxygen as usual. This is often caused by not getting enough iron in your diet, like from leafy greens or red meat. You might feel a little tired or weak. It's a good idea to chat with your doctor about an iron supplement or dietary changes."
"""

def interpret_abnormality(test_name, value, normal_range, status):
    """
    Generate AI explanation for abnormal blood test value using Groq
    
    Args:
        test_name (str): Name of the test (e.g., "Hemoglobin")
        value (float): The actual test value
        normal_range (str): Normal range string (e.g., "13.0 - 17.0")
        status (str): "HIGH" or "LOW"
    
    Returns:
        str: AI-generated explanation in simple language
    """
    
    try:
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a compassionate medical assistant who explains lab results in simple, non-technical language. You educate without alarming people."
                },
                {
                    "role": "user",
                    "content": build_prompt(test_name, value, normal_range, status)
                }
            ],
            model="llama-3.3-70b-versatile",  # Latest fast and accurate model
            temperature=0.3,  # Lower temperature for more consistent medical advice
            max_tokens=300,  # Enough for a good explanation
            top_p=0.9
        )
        
        # Extract the generated text
        explanation = chat_completion.choices[0].message.content.strip()
        
        if explanation:
            return explanation
        else:
            return "Unable to generate explanation at this time."
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Groq API Error: {error_msg}")
        
        # Check for specific error types
        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            print("\n⚠️ Your API key is invalid or expired.")
            print("💡 Get a new one from: https://console.groq.com/\n")
        elif "429" in error_msg or "rate_limit" in error_msg.lower():
            print("\n⚠️ Rate limit exceeded. Please wait a moment and try again.\n")
        
        # Fallback explanation if API fails
        fallback_explanations = {
            "Hemoglobin": {
                "LOW": f"Your hemoglobin level ({value}) is below normal. Hemoglobin carries oxygen in your blood. Low levels often come from not getting enough iron in your diet or heavy menstrual periods. You might feel tired or weak. Talk to your doctor about iron supplements.",
                "HIGH": f"Your hemoglobin level ({value}) is above normal. This can happen at high altitudes, from dehydration, or smoking. It's usually not a concern, but mention it to your doctor on your next visit."
            },
            "WBC": {
                "LOW": f"Your white blood cell count ({value}) is below normal. These cells fight infections. Low counts can come from certain medications or viral infections. Be extra careful about hygiene and avoid sick people. Discuss this with your doctor.",
                "HIGH": f"Your white blood cell count ({value}) is elevated. This usually means your body is fighting an infection or inflammation. It's often temporary. Your doctor may want to investigate the cause."
            },
            "Platelets": {
                "LOW": f"Your platelet count ({value}) is below normal. Platelets help your blood clot. Low counts can increase bruising or bleeding. Avoid contact sports and be gentle when brushing teeth. See your doctor soon.",
                "HIGH": f"Your platelet count ({value}) is elevated. This can happen after exercise, stress, or inflammation. It's often not serious but worth discussing with your doctor to rule out other causes."
            },
            "Blood Sugar": {
                "LOW": f"Your blood sugar ({value}) is below normal. This can cause shakiness, sweating, or confusion. It may be from skipping meals or too much insulin. Have a snack with carbs and protein. If this happens often, see your doctor.",
                "HIGH": f"Your blood sugar ({value}) is above normal. This could indicate prediabetes or diabetes. High blood sugar can come from diet, stress, or lack of exercise. Your doctor may recommend dietary changes or testing for diabetes."
            },
            "Neutrophils": {
                "LOW": f"Your neutrophil percentage ({value}%) is below normal. Neutrophils fight bacterial infections. Low levels can come from viral infections or certain medications. Practice good hygiene and avoid sick people. Discuss with your doctor.",
                "HIGH": f"Your neutrophil percentage ({value}%) is elevated. This usually means your body is fighting a bacterial infection or dealing with stress. It's a normal immune response. Monitor your symptoms and consult your doctor."
            },
            "Lymphocytes": {
                "LOW": f"Your lymphocyte percentage ({value}%) is below normal. Lymphocytes are immune cells that fight viruses. Low levels can occur with stress, certain infections, or medications. Rest well and see your doctor if you feel unwell.",
                "HIGH": f"Your lymphocyte percentage ({value}%) is elevated. This often happens during viral infections like colds or flu. Your body is mounting an immune response. Rest, stay hydrated, and the levels should normalize as you recover."
            },
            "RBC": {
                "LOW": f"Your red blood cell count ({value}) is below normal. This can indicate anemia, causing fatigue and weakness. Common causes include iron deficiency or vitamin B12 deficiency. Your doctor may recommend supplements or dietary changes.",
                "HIGH": f"Your red blood cell count ({value}) is above normal. This can happen at high altitudes, from smoking, or dehydration. Drink plenty of water and mention this to your doctor at your next visit."
            },
            "ESR": {
                "HIGH": f"Your ESR ({value}) is elevated. ESR measures inflammation in your body. High levels can come from infections, autoimmune conditions, or injury. It's not specific to one condition. Your doctor will likely investigate further.",
                "LOW": f"Your ESR ({value}) is within normal range. This generally indicates no significant inflammation in your body, which is a good sign."
            }
        }
        
        # Return fallback explanation
        if test_name in fallback_explanations and status in fallback_explanations[test_name]:
            return fallback_explanations[test_name][status]
        
        return f"Your {test_name} level is {status.lower()} at {value} (normal: {normal_range}). Please discuss this result with your doctor for proper interpretation and next steps."