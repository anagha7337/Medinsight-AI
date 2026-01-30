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

def build_prompt(test_name, value, normal_range, status, language="english"):
    """Build a medical explanation prompt for the AI with language support"""
    
    language_instructions = {
        "english": """Please explain in simple, friendly English language.""",
        
        "hindi": """Please explain in simple Hindi (Devanagari script). 
Keep medical/technical terms in English but explain everything else in easy-to-understand Hindi.
Example: "Aapka hemoglobin level (12.5) normal se kam hai. Hemoglobin aapke khoon mein oxygen carry karta hai..."
Write naturally mixing Hindi and English terms as Indians normally speak.""",
        
        "malayalam": """Please explain in simple Malayalam script.
Keep medical/technical terms in English but explain everything else in easy-to-understand Malayalam.
Example: "Ningalude hemoglobin level (12.5) normal range-il ninnum kuravanu. Hemoglobin ningalude blood-il oxygen carry cheyyunnu..."
Write naturally mixing Malayalam and English terms as Keralites normally speak."""
    }
    
    lang_instruction = language_instructions.get(language.lower(), language_instructions["english"])
    
    return f"""You are a friendly medical assistant explaining lab test results to someone without medical training.

**Test Details:**
- Test: {test_name}
- Their Result: {value}
- Normal Range: {normal_range}
- Status: {status}

{lang_instruction}

Explain the following in 4-5 sentences:

1. What this test measures in the body (in one sentence)
2. What it means when the value is {status.lower()} (be reassuring, not alarming)
3. Common everyday causes (lifestyle, diet, or natural factors)
4. What they might notice or feel (if anything)
5. A simple next step (like "discuss with your doctor" or "monitor it")

Important guidelines:
- Use everyday language that common people understand
- Keep medical/biological terms in English (like hemoglobin, WBC, platelets, etc.)
- Be reassuring and calm in tone
- Don't diagnose specific diseases
- Keep it concise (4-5 sentences total)
- Focus on education, not fear

Example English tone: "Your hemoglobin is a bit low, which means your blood isn't carrying as much oxygen as usual. This is often caused by not getting enough iron in your diet, like from leafy greens or red meat. You might feel a little tired or weak. It's a good idea to chat with your doctor about an iron supplement or dietary changes."
"""

def interpret_abnormality(test_name, value, normal_range, status, language="english"):
    """
    Generate AI explanation for abnormal blood test value using Groq
    
    Args:
        test_name (str): Name of the test (e.g., "Hemoglobin")
        value (float): The actual test value
        normal_range (str): Normal range string (e.g., "13.0 - 17.0")
        status (str): "HIGH" or "LOW"
        language (str): Language for explanation ("english", "hindi", "malayalam")
    
    Returns:
        str: AI-generated explanation in requested language
    """
    
    try:
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a compassionate medical assistant who explains lab results in simple, non-technical language. You educate without alarming people. Respond in {language} language as instructed."
                },
                {
                    "role": "user",
                    "content": build_prompt(test_name, value, normal_range, status, language)
                }
            ],
            model="llama-3.3-70b-versatile",  # Latest fast and accurate model
            temperature=0.3,  # Lower temperature for more consistent medical advice
            max_tokens=400,  # Increased for non-English scripts
            top_p=0.9
        )
        
        # Extract the generated text
        explanation = chat_completion.choices[0].message.content.strip()
        
        if explanation:
            return explanation
        else:
            return get_fallback_explanation(test_name, value, normal_range, status, language)
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Groq API Error: {error_msg}")
        
        # Check for specific error types
        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            print("\n⚠️ Your API key is invalid or expired.")
            print("💡 Get a new one from: https://console.groq.com/\n")
        elif "429" in error_msg or "rate_limit" in error_msg.lower():
            print("\n⚠️ Rate limit exceeded. Please wait a moment and try again.\n")
        
        # Return fallback explanation
        return get_fallback_explanation(test_name, value, normal_range, status, language)


def get_fallback_explanation(test_name, value, normal_range, status, language="english"):
    """
    Provide fallback explanations if API fails
    """
    
    fallback_explanations = {
        "english": {
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
        },
        "hindi": {
            "Hemoglobin": {
                "LOW": f"Aapka hemoglobin level ({value}) normal se kam hai. Hemoglobin aapke khoon mein oxygen carry karta hai. Yeh zyada tar iron ki kami ya heavy periods ke karan hota hai. Aapko thakaan aur kamzori mehsoos ho sakti hai. Doctor se iron supplements ke baare mein baat karein.",
                "HIGH": f"Aapka hemoglobin level ({value}) normal se zyada hai. Yeh high altitude, dehydration, ya smoking se ho sakta hai. Zyada chinta ki baat nahi hai, lekin apne doctor ko zaroor bataiye."
            },
            "WBC": {
                "LOW": f"Aapka white blood cell count ({value}) normal se kam hai. Yeh cells infections se ladti hain. Low count kuch medicines ya viral infections ke karan ho sakta hai. Safai ka khaas dhyan rakhein aur bimar logon se door rahein. Doctor se consult karein.",
                "HIGH": f"Aapka white blood cell count ({value}) badha hua hai. Iska matlab hai ki aapka body kisi infection ya inflammation se lad raha hai. Yeh aksar temporary hota hai. Doctor ko dikhana chahiye."
            },
            "Platelets": {
                "LOW": f"Aapka platelet count ({value}) normal se kam hai. Platelets blood clotting mein madad karte hain. Low count se bruising ya bleeding badh sakti hai. Contact sports avoid karein aur daant saaf karte waqt gentle rahein. Jaldi doctor se milein.",
                "HIGH": f"Aapka platelet count ({value}) badha hua hai. Yeh exercise, stress, ya inflammation ke karan ho sakta hai. Zyada serious nahi hai, lekin doctor se discuss zaroor karein."
            },
            "Blood Sugar": {
                "LOW": f"Aapka blood sugar ({value}) normal se kam hai. Isse kaanpna, pasina, ya confusion ho sakta hai. Yeh khana skip karne ya zyada insulin lene se ho sakta hai. Carbs aur protein wala snack lein. Agar yeh baar baar ho, to doctor se milein.",
                "HIGH": f"Aapka blood sugar ({value}) normal se zyada hai. Yeh prediabetes ya diabetes indicate kar sakta hai. High sugar diet, stress, ya exercise ki kami se hota hai. Doctor diet changes ya diabetes testing recommend kar sakte hain."
            },
        },
        "malayalam": {
            "Hemoglobin": {
                "LOW": f"Ningalude hemoglobin level ({value}) normal range-il ninnum kuravanu. Hemoglobin ningalude blood-il oxygen carry cheyyunnu. Ithu iron uyarnna food kazhikkaathe varunnathaanu, athava heavy periods karanam. Ningalkku vishamavum durbalathayum thonnaam. Doctor-ne kandu iron supplements pattiyum samsaarikkanam.",
                "HIGH": f"Ningalude hemoglobin level ({value}) normal-il ninnum kooduthalanu. Ithu high altitude, dehydration, athava smoking kaaranam sambhavikkaam. Valiya prashnamalla, pakshe ningalude doctor-ne ariyikkanam."
            },
            "WBC": {
                "LOW": f"Ningalude white blood cell count ({value}) normal-il ninnum kuravanu. Ee cells infections-ne ethirkkunnu. Low count chila medicines athava viral infections kaaranam aavaam. Hygiene nannaayi anusarikkanam, rogികളായ aalukaളെ avoid cheyyuka. Doctor-ne consult cheyyuka.",
                "HIGH": f"Ningalude white blood cell count ({value}) koodiyittundu. Ithu ningalude body infection athava inflammation-ne ethirkunnu ennu kaanikkunu. Ithu temporary aanu. Doctor-ne kaanikkuka."
            },
            "Platelets": {
                "LOW": f"Ningalude platelet count ({value}) normal-il ninnum kuravanu. Platelets blood clotting-nu upakaarappedunnu. Low count kaaranam bruising athava bleeding koodum. Contact sports avoid cheyyuka, teeth brush cheyyumpol gentle aayirikkuka. Vega doctor-ne kaanuka.",
                "HIGH": f"Ningalude platelet count ({value}) koodiyittundu. Ithu exercise, stress, athava inflammation kaaranam sambhavikkaam. Valya tension vendaa, pakshe doctor-umaayi samsaarikkuka."
            },
            "Blood Sugar": {
                "LOW": f"Ningalude blood sugar ({value}) normal-il ninnum kuravanu. Ithu kaaranam veppam, viyarppu, athava confusion undaavam. Food skip cheythaal athava excess insulin edukkumpol ithu sambhavikkum. Carbs-um protein-um ulla snack kazhikkuka. Ithu thadarunnu engil doctor-ne kaanuka.",
                "HIGH": f"Ningalude blood sugar ({value}) normal-il ninnum kooduthalanu. Ithu prediabetes athava diabetes indicate cheyyaam. High sugar diet, stress, athava exercise kuravaanu kaaranam. Doctor diet changes athava diabetes testing recommend cheyyum."
            },
        }
    }
    
    # Get fallback for requested language
    lang_fallbacks = fallback_explanations.get(language.lower(), fallback_explanations["english"])
    
    if test_name in lang_fallbacks and status in lang_fallbacks[test_name]:
        return lang_fallbacks[test_name][status]
    
    # Ultimate fallback
    if language.lower() == "hindi":
        return f"Aapka {test_name} level {status.lower()} hai - {value} (normal: {normal_range}). Kripya apne doctor se is result ke baare mein baat karein."
    elif language.lower() == "malayalam":
        return f"Ningalude {test_name} level {status.lower()} aanu - {value} (normal: {normal_range}). Dayavayi ningalude doctor-umaayi ee result pattiyum samsaarikkuka."
    else:
        return f"Your {test_name} level is {status.lower()} at {value} (normal: {normal_range}). Please discuss this result with your doctor for proper interpretation and next steps."