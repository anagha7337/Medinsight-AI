import os
import base64
from decouple import config
import google.generativeai as genai
from PIL import Image

# Initialize Gemini client
GEMINI_API_KEY = config('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

def build_scan_prompt(language="english"):
    language_instructions = {
        "english": """Please provide your analysis in simple, friendly English language.""",
        
        "hindi": """Please provide TWO versions of your analysis:

**Version 1 - Native Script (हिंदी):**
Write the FULL analysis in Devanagari (Hindi) script. Keep medical terms in English but write everything else in proper Hindi.

**Version 2 - Transliteration (Hinglish):**
Write the same analysis using Latin script (Roman Hindi) - how Indians type Hindi in English.

Format your response exactly like this:
【हिंदी】
[Your Hindi script analysis here]

【Transliteration】
[Your Hinglish analysis here]""",
        
        "malayalam": """Please provide TWO versions of your analysis:

**Version 1 - Native Script (മലയാളം):**
Write the FULL analysis in Malayalam script. Keep medical terms in English but write everything else in proper Malayalam.

**Version 2 - Transliteration (Manglish):**
Write the same analysis using ONLY Latin/English script - exactly how Malayalis type Malayalam using English keyboard.
Use simple English letters only. No special Unicode characters.

Format your response exactly like this:
【മലയാളം】
[Your Malayalam script analysis here]

【Transliteration】
[Your pure English-letter Manglish analysis here]"""
    }
    
    lang_instruction = language_instructions.get(language.lower(), language_instructions["english"])
    
    return f"""You are a compassionate medical professional analyzing a medical scan report (X-ray, CT scan, MRI, ultrasound, etc.).

Your task is to:
1. **Identify** what type of scan this is (X-ray, CT, MRI, Ultrasound, etc.)
2. **Describe** what body part/region is being scanned
3. **Explain** the key findings in simple, non-technical language
4. **Note** any abnormalities or areas of concern (if visible)
5. **Provide context** - what these findings might mean in everyday terms
6. **Suggest** general next steps (like "discuss with your doctor")

{lang_instruction}

**Important Guidelines:**
- Use simple, everyday language that non-medical people can understand
- Keep technical medical terms in English (like fracture, fluid, density, etc.)
- Be reassuring and calm in tone - don't cause unnecessary alarm
- Don't make definitive diagnoses - use phrases like "appears to show", "may indicate", "could suggest"
- Focus on education and clarity, not fear
- If the image quality is poor or unclear, mention it
- If you cannot see clear medical findings, say so honestly
- Keep the total explanation to 6-8 sentences

Remember: You're helping someone understand their medical scan, not replacing their doctor's expertise."""

def interpret_scan(image_path, language="english"):
    
    try:
        img = Image.open(image_path)
        
        model_names = [
            "models/gemini-2.5-flash",
            "models/gemini-2.5-pro",
            "models/gemini-2.0-flash"
        ]

        analysis = None
        last_error = None
        
        for model_name in model_names:
            try:
                print(f"Trying model: {model_name}")
                
                generation_config = {
                    "temperature": 0.4,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
                
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config
                )
                
                response = model.generate_content([
                    build_scan_prompt(language),
                    img
                ])
                
                analysis = response.text if hasattr(response, "text") else ""
                
                if analysis:
                    print(f"✓ Success with model: {model_name}")
                    return {
                        "success": True,
                        "analysis": analysis,
                        "language": language,
                        "model_used": model_name
                    }
            except Exception as model_error:
                last_error = str(model_error)
                print(f"  ✗ Failed with {model_name}: {last_error[:100]}")
                continue
        
        raise Exception(f"All models failed. Last error: {last_error}")
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Gemini API Error: {error_msg}")
        
        # Check for specific error types
        if "API_KEY" in error_msg.upper() or "invalid" in error_msg.lower():
            print("\n⚠️ Your API key is invalid or expired.")
            print("💡 Get a new one from: https://makersuite.google.com/app/apikey\n")
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            print("\n⚠️ API quota exceeded. Wait a bit and try again.\n")
        elif "image" in error_msg.lower():
            print("\n⚠️ Issue processing the image. Make sure it's a valid image file.\n")
        
        return get_fallback_scan_explanation(language)

def get_fallback_scan_explanation(language="english"):
    
    fallback_messages = {
        "english": """I'm unable to analyze this scan image at the moment due to a technical issue. 

For accurate interpretation of your medical scan, please:
1. Consult with your doctor or radiologist who ordered this scan
2. They have access to your full medical history and can provide proper diagnosis
3. Medical scans require professional expertise for accurate interpretation

This is a temporary technical limitation, not a reflection of your scan results.""",
        
        "hindi": """【हिंदी】
मैं अभी इस scan image को analyze नहीं कर पा रहा हूँ technical issue के कारण।

आपके medical scan की सही व्याख्या के लिए, कृपया:
1. अपने doctor या radiologist से consult करें जिन्होंने यह scan order किया था
2. उनके पास आपकी पूरी medical history है और वे proper diagnosis दे सकते हैं
3. Medical scans को सही interpretation के लिए professional expertise की ज़रूरत होती है

यह temporary technical limitation है, आपके scan results का reflection नहीं है।

【Transliteration】
Main abhi is scan image ko analyze nahi kar pa raha hoon technical issue ke karan.

Aapke medical scan ki sahi vyakhya ke liye, kripya:
1. Apne doctor ya radiologist se consult karein jinhone yeh scan order kiya tha
2. Unke paas aapki poori medical history hai aur ve proper diagnosis de sakte hain
3. Medical scans ko sahi interpretation ke liye professional expertise ki zaroorat hoti hai

Yeh temporary technical limitation hai, aapke scan results ka reflection nahi hai.""",
        
        "malayalam": """【മലയാളം】
Technical issue കാരണം ഞാന് ഈ scan image analyze ചെയ്യാന് കഴിയുന്നില്ല.

നിങ്ങളുടെ medical scan-ന്റെ ശരിയായ interpretation-നു, ദയവായി:
1. നിങ്ങളുടെ doctor അഥവാ radiologist-നെ consult ചെയ്യുക
2. അവര്ക്ക് നിങ്ങളുടെ full medical history അറിയാം, proper diagnosis നല്കാന് കഴിയും
3. Medical scans-നു professional expertise വേണം accurate interpretation-നു

ഇത് temporary technical limitation ആണ്, നിങ്ങളുടെ scan results-ന്റെ reflection അല്ല.

【Transliteration】
Technical issue kaaranam njaan ee scan image analyze cheyyaan kazhiyunnilla.

Ningalude medical scan-nte shariyaaya interpretation-nu, dayavayi:
1. Ningalude doctor athava radiologist-ne consult cheyyuka
2. Avarkku ningalude full medical history ariyaam, proper diagnosis nalkaan kazhiyum
3. Medical scans-nu professional expertise venam accurate interpretation-nu

Ithu temporary technical limitation aanu, ningalude scan results-nte reflection alla."""
    }
    
    return {
        "success": False,
        "analysis": fallback_messages.get(language.lower(), fallback_messages["english"]),
        "language": language,
        "error": "API temporarily unavailable"
    }