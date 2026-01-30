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
        
        "hindi": """Please provide TWO versions of the explanation:

**Version 1 - Native Script (हिंदी):**
Write the FULL explanation in Devanagari (Hindi) script. Keep medical terms in English but write everything else in proper Hindi.
Example: "आपका hemoglobin level (12.5) सामान्य से कम है। Hemoglobin आपके खून में oxygen ले जाता है..."

**Version 2 - Transliteration (Hinglish):**
Write the same explanation using Latin script (Roman Hindi) - how Indians type Hindi in English.
Example: "Aapka hemoglobin level (12.5) normal se kam hai. Hemoglobin aapke khoon mein oxygen carry karta hai..."

Format your response exactly like this:
【हिंदी】
[Your Hindi script explanation here]

【Transliteration】
[Your Hinglish explanation here]""",
        
        "malayalam": """Please provide TWO versions of the explanation:

**Version 1 - Native Script (മലയാളം):**
Write the FULL explanation in Malayalam script. Keep medical terms in English but write everything else in proper Malayalam.
Example: "നിങ്ങളുടെ hemoglobin level (12.5) സാധാരണ പരിധിയില്‍ നിന്ന് കുറവാണ്. Hemoglobin നിങ്ങളുടെ blood-ല്‍ oxygen കൊണ്ടുപോകുന്നു..."

**Version 2 - Transliteration (Manglish):**
Write the same explanation using ONLY Latin/English script - exactly how Malayalis type Malayalam using English keyboard.
Use simple English letters only. No special Unicode characters.
Example: "Ningalude hemoglobin level (12.5) normal range-il ninnu kuravanu. Hemoglobin ningalude blood-il oxygen carry cheyyunnu..."

IMPORTANT for Transliteration:
- Use only a-z, A-Z letters
- Replace ള with 'la' or 'l' 
- Replace ു with 'u'
- Replace ് with '' (remove it or use simple letter)
- Write naturally as Keralites type in WhatsApp/SMS

Format your response exactly like this:
【മലയാളം】
[Your Malayalam script explanation here]

【Transliteration】
[Your pure English-letter Manglish explanation here]"""
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
                    "content": f"You are a compassionate medical assistant who explains lab results in simple, non-technical language. You educate without alarming people. Respond in {language} language as instructed, providing both native script and transliteration for Hindi and Malayalam."
                },
                {
                    "role": "user",
                    "content": build_prompt(test_name, value, normal_range, status, language)
                }
            ],
            model="llama-3.3-70b-versatile",  # Latest fast and accurate model
            temperature=0.3,  # Lower temperature for more consistent medical advice
            max_tokens=600,  # Increased for dual format
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
                "LOW": f"""【हिंदी】
आपका hemoglobin level ({value}) सामान्य से कम है। Hemoglobin आपके खून में oxygen पहुँचाता है। यह ज़्यादातर खाने में iron की कमी या ज़्यादा periods के कारण होता है। आपको थकान और कमज़ोरी महसूस हो सकती है। Doctor से iron supplements के बारे में बात करें।

【Transliteration】
Aapka hemoglobin level ({value}) normal se kam hai. Hemoglobin aapke khoon mein oxygen carry karta hai. Yeh zyada tar iron ki kami ya heavy periods ke karan hota hai. Aapko thakaan aur kamzori mehsoos ho sakti hai. Doctor se iron supplements ke baare mein baat karein.""",
                "HIGH": f"""【हिंदी】
आपका hemoglobin level ({value}) सामान्य से ज़्यादा है। यह ऊँचाई पर, dehydration, या smoking से हो सकता है। ज़्यादा चिंता की बात नहीं है, लेकिन अपने doctor को ज़रूर बताइए।

【Transliteration】
Aapka hemoglobin level ({value}) normal se zyada hai. Yeh high altitude, dehydration, ya smoking se ho sakta hai. Zyada chinta ki baat nahi hai, lekin apne doctor ko zaroor bataiye."""
            },
            "WBC": {
                "LOW": f"""【हिंदी】
आपका white blood cell count ({value}) सामान्य से कम है। ये cells infections से लड़ती हैं। कम count कुछ medicines या viral infections के कारण हो सकता है। सफ़ाई का ख़ास ध्यान रखें और बीमार लोगों से दूर रहें। Doctor से consult करें।

【Transliteration】
Aapka white blood cell count ({value}) normal se kam hai. Yeh cells infections se ladti hain. Low count kuch medicines ya viral infections ke karan ho sakta hai. Safai ka khaas dhyan rakhein aur bimar logon se door rahein. Doctor se consult karein.""",
                "HIGH": f"""【हिंदी】
आपका white blood cell count ({value}) बढ़ा हुआ है। इसका मतलब है कि आपका body किसी infection या inflammation से लड़ रहा है। यह अक्सर temporary होता है। Doctor को दिखाना चाहिए।

【Transliteration】
Aapka white blood cell count ({value}) badha hua hai. Iska matlab hai ki aapka body kisi infection ya inflammation se lad raha hai. Yeh aksar temporary hota hai. Doctor ko dikhana chahiye."""
            },
        },
        "malayalam": {
            "Hemoglobin": {
                "LOW": f"""【മലയാളം】
നിങ്ങളുടെ hemoglobin level ({value}) സാധാരണ പരിധിയില്‍ നിന്ന് കുറവാണ്. Hemoglobin നിങ്ങളുടെ blood-ല്‍ oxygen കൊണ്ടുപോകുന്നു. ഇത് iron ധാരാളമുള്ള ഭക്ഷണം കഴിക്കാതെ വരുന്നതാണ്, അഥവാ heavy periods കാരണം. നിങ്ങള്‍ക്ക് ക്ഷീണവും ദുര്‍ബലതയും തോന്നാം. Doctor-നെ കണ്ട് iron supplements പറ്റിയും സംസാരിക്കണം.

【Transliteration】
Ningalude hemoglobin level ({value}) normal range-il ninnu kuravanu. Hemoglobin ningalude blood-il oxygen carry cheyyunnu. Ithu iron ulla food kazhikkaathe varunnathaanu, athava heavy periods karanam. Ningalkku vishamavum durbalathayum thonnaam. Doctor-ne kandu iron supplements pattiyum samsaarikkanam.""",
                "HIGH": f"""【മലയാളം】
നിങ്ങളുടെ hemoglobin level ({value}) സാധാരണയില്‍ നിന്ന് കൂടുതലാണ്. ഇത് high altitude, dehydration, അഥവാ smoking കാരണം സംഭവിക്കാം. വലിയ പ്രശ്നമല്ല, പക്ഷേ നിങ്ങളുടെ doctor-നെ അറിയിക്കണം.

【Transliteration】
Ningalude hemoglobin level ({value}) normal-il ninnu kooduthalanu. Ithu high altitude, dehydration, athava smoking kaaranam sambhavikkaam. Valiya prashnamalla, pakshe ningalude doctor-ne ariyikkanam."""
            },
            "WBC": {
                "LOW": f"""【മലയാളം】
നിങ്ങളുടെ white blood cell count ({value}) സാധാരണയില്‍ നിന്ന് കുറവാണ്. ഈ cells infections-നെ എതിര്‍ക്കുന്നു. കുറഞ്ഞ count ചില medicines അഥവാ viral infections കാരണം ആവാം. Hygiene നന്നായി അനുസരിക്കണം, രോഗികളായ ആളുകളെ avoid ചെയ്യുക. Doctor-നെ consult ചെയ്യുക.

【Transliteration】
Ningalude white blood cell count ({value}) normal-il ninnu kuravanu. Ee cells infections-ne ethirkkunnu. Low count chila medicines athava viral infections kaaranam aavaam. Hygiene nannaayi anusarikkanam, rogikalaaya aalukale avoid cheyyuka. Doctor-ne consult cheyyuka.""",
                "HIGH": f"""【മലയാളം】
നിങ്ങളുടെ white blood cell count ({value}) കൂടിയിട്ടുണ്ട്. ഇത് നിങ്ങളുടെ body infection അഥവാ inflammation-നെ എതിര്‍ക്കുന്നു എന്ന് കാണിക്കുന്നു. ഇത് temporary ആണ്. Doctor-നെ കാണിക്കുക.

【Transliteration】
Ningalude white blood cell count ({value}) koodiyittundu. Ithu ningalude body infection athava inflammation-ne ethirkunnu ennu kaanikkunu. Ithu temporary aanu. Doctor-ne kaanikkuka."""
            },
            "Platelets": {
                "LOW": f"""【മലയാളം】
നിങ്ങളുടെ platelet count ({value}) സാധാരണയില്‍ നിന്ന് കുറവാണ്. Platelets blood clotting-നു ഉപകാരപ്പെടുന്നു. Low count കാരണം bruising അഥവാ bleeding കൂടും. Contact sports avoid ചെയ്യുക, teeth brush ചെയ്യുമ്പോള്‍ gentle ആയിരിക്കുക. വേഗം doctor-നെ കാണുക.

【Transliteration】
Ningalude platelet count ({value}) normal-il ninnu kuravanu. Platelets blood clotting-nu upakaarappedunnu. Low count kaaranam bruising athava bleeding koodum. Contact sports avoid cheyyuka, teeth brush cheyyumpol gentle aayirikkuka. Vegam doctor-ne kaanuka.""",
                "HIGH": f"""【മലയാളം】
നിങ്ങളുടെ platelet count ({value}) കൂടിയിട്ടുണ്ട്. ഇത് exercise, stress, അഥവാ inflammation കാരണം സംഭവിക്കാം. വലിയ tension വേണ്ടാ, പക്ഷേ doctor-ഉമായി സംസാരിക്കുക.

【Transliteration】
Ningalude platelet count ({value}) koodiyittundu. Ithu exercise, stress, athava inflammation kaaranam sambhavikkaam. Valiya tension vendaa, pakshe doctor-umaayi samsaarikkuka."""
            },
            "Blood Sugar": {
                "LOW": f"""【മലയാളം】
നിങ്ങളുടെ blood sugar ({value}) സാധാരണയില്‍ നിന്ന് കുറവാണ്. ഇത് കാരണം വെപ്പം, വിയര്‍പ്പ്, അഥവാ confusion ഉണ്ടാവാം. Food skip ചെയ്താല്‍ അഥവാ excess insulin എടുക്കുമ്പോള്‍ ഇത് സംഭവിക്കും. Carbs-ഉം protein-ഉം ഉള്ള snack കഴിക്കുക. ഇത് തുടരുന്നു എങ്കില്‍ doctor-നെ കാണുക.

【Transliteration】
Ningalude blood sugar ({value}) normal-il ninnu kuravanu. Ithu kaaranam veppam, viyarppu, athava confusion undaavam. Food skip cheythaal athava excess insulin edukkumpol ithu sambhavikkum. Carbs-um protein-um ulla snack kazhikkuka. Ithu thadarunnu engil doctor-ne kaanuka.""",
                "HIGH": f"""【മലയാളം】
നിങ്ങളുടെ blood sugar ({value}) സാധാരണയില്‍ നിന്ന് കൂടുതലാണ്. ഇത് prediabetes അഥവാ diabetes indicate ചെയ്യാം. High sugar diet, stress, അഥവാ exercise കുറവാണ് കാരണം. Doctor diet changes അഥവാ diabetes testing recommend ചെയ്യും.

【Transliteration】
Ningalude blood sugar ({value}) normal-il ninnu kooduthalanu. Ithu prediabetes athava diabetes indicate cheyyaam. High sugar diet, stress, athava exercise kuravaanu kaaranam. Doctor diet changes athava diabetes testing recommend cheyyum."""
            },
        }
    }
    
    # Get fallback for requested language
    lang_fallbacks = fallback_explanations.get(language.lower(), fallback_explanations["english"])
    
    if test_name in lang_fallbacks and status in lang_fallbacks[test_name]:
        return lang_fallbacks[test_name][status]
    
    # Ultimate fallback
    if language.lower() == "hindi":
        return f"""【हिंदी】
आपका {test_name} level {status.lower()} है - {value} (सामान्य: {normal_range})। कृपया अपने doctor से इस result के बारे में बात करें।

【Transliteration】
Aapka {test_name} level {status.lower()} hai - {value} (normal: {normal_range}). Kripya apne doctor se is result ke baare mein baat karein."""
    elif language.lower() == "malayalam":
        return f"""【മലയാളം】
നിങ്ങളുടെ {test_name} level {status.lower()} ആണ് - {value} (സാധാരണ: {normal_range}). ദയവായി നിങ്ങളുടെ doctor-ഉമായി ഈ result പറ്റിയും സംസാരിക്കുക.

【Transliteration】
Ningalude {test_name} level {status.lower()} aanu - {value} (normal: {normal_range}). Dayavayi ningalude doctor-umaayi ee result pattiyum samsaarikkuka."""
    else:
        return f"Your {test_name} level is {status.lower()} at {value} (normal: {normal_range}). Please discuss this result with your doctor for proper interpretation and next steps."