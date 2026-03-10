import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
    
    language_instructions = {
        "english": """Please explain in simple, friendly English language.""",
        
        "hindi": """Please provide TWO versions:
【हिंदी】 Full explanation in Devanagari script (medical terms in English)
【Transliteration】 Same in Latin script (Hinglish)
Example: "आपका hemoglobin..." then "Aapka hemoglobin..."
""",
        
        "malayalam": """Please provide TWO versions:
【മലയാളം】 Full explanation in Malayalam script (medical terms in English)
【Transliteration】 Same in Latin script (Manglish) - only a-z letters
Example: "നിങ്ങളുടെ hemoglobin..." then "Ningalude hemoglobin..."
""",
        
        "tamil": """Please provide TWO versions:
【தமிழ்】 Full explanation in Tamil script (medical terms in English)
【Transliteration】 Same in Latin script (Tanglish) - only a-z letters
Example: "உங்கள் hemoglobin..." then "Ungal hemoglobin..."
""",
        
        "telugu": """Please provide TWO versions:
【తెలుగు】 Full explanation in Telugu script (medical terms in English)
【Transliteration】 Same in Latin script (Tenglish) - only a-z letters
Example: "మీ hemoglobin..." then "Mee hemoglobin..."
""",
        
        "kannada": """Please provide TWO versions:
【ಕನ್ನಡ】 Full explanation in Kannada script (medical terms in English)
【Transliteration】 Same in Latin script (Kanglish) - only a-z letters
Example: "ನಿಮ್ಮ hemoglobin..." then "Nimma hemoglobin..."
""",
        
        "marathi": """Please provide TWO versions:
【मराठी】 Full explanation in Devanagari script (medical terms in English)
【Transliteration】 Same in Latin script (Marathlish) - only a-z letters
Example: "तुमचा hemoglobin..." then "Tumcha hemoglobin..."
""",
        
        "bengali": """Please provide TWO versions:
【বাংলা】 Full explanation in Bengali script (medical terms in English)
【Transliteration】 Same in Latin script (Banglish) - only a-z letters
Example: "আপনার hemoglobin..." then "Apnar hemoglobin..."
""",
        
        "gujarati": """Please provide TWO versions:
【ગુજરાતી】 Full explanation in Gujarati script (medical terms in English)
【Transliteration】 Same in Latin script (Guglish) - only a-z letters
Example: "તમારું hemoglobin..." then "Tamaru hemoglobin..."
""",
        
        "urdu": """Please provide TWO versions:
【اردو】 Full explanation in Urdu script (medical terms in English)
【Transliteration】 Same in Latin script (Roman Urdu) - only a-z letters
Example: "آپ کا hemoglobin..." then "Aap ka hemoglobin..."
""",
        
        "odia": """Please provide TWO versions:
【ଓଡ଼ିଆ】 Full explanation in Odia script (medical terms in English)
【Transliteration】 Same in Latin script (Odlish) - only a-z letters
Example: "ଆପଣଙ୍କର hemoglobin..." then "Apanankara hemoglobin..."
"""
    }
    
    lang_instruction = language_instructions.get(language.lower(), language_instructions["english"])
    
    return f"""You are a friendly medical assistant explaining lab test results to someone without medical training.

**Test Details:**
- Test: {test_name}
- Their Result: {value}
- Normal Range: {normal_range}
- Status: {status}

{lang_instruction}

Explain in 4-5 sentences:
1. What this test measures (1 sentence)
2. What {value} and {status.lower()} means (reassuring, not alarming)
3. Biological significance of the test
4. What happens biologically when the test is {status.lower()}
5. Common everyday causes (lifestyle, diet)
6. What they might feel
7. Simple next step (consult doctor)

Guidelines:
- Keep medical terms in English (hemoglobin, WBC, etc.)
- Use everyday language
- Be reassuring and calm
- 6-7 sentences total
"""

def interpret_abnormality(test_name, value, normal_range, status, language="english"):    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a compassionate medical assistant. Explain lab results in simple {language} language. For Indian languages, provide both native script and Latin transliteration."
                },
                {
                    "role": "user",
                    "content": build_prompt(test_name, value, normal_range, status, language)
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1000,  
            top_p=0.9
        )
        
        explanation = chat_completion.choices[0].message.content.strip()
        return explanation if explanation else get_fallback_explanation(test_name, value, normal_range, status, language)
    
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return get_fallback_explanation(test_name, value, normal_range, status, language)


def get_fallback_explanation(test_name, value, normal_range, status, language="english"):    
    fallback_explanations = {
        "english": {
            "Hemoglobin": {
                "LOW": f"Your hemoglobin level ({value}) is below normal. Hemoglobin carries oxygen in your blood. Low levels often come from not getting enough iron in your diet or heavy menstrual periods. You might feel tired or weak. Talk to your doctor about iron supplements.",
                "HIGH": f"Your hemoglobin level ({value}) is above normal. This can happen at high altitudes, from dehydration, or smoking. It's usually not a concern, but mention it to your doctor on your next visit."
            }
        },
        "hindi": {
            "Hemoglobin": {
                "LOW": f"""【हिंदी】
आपका hemoglobin level ({value}) सामान्य से कम है। Hemoglobin आपके खून में oxygen पहुँचाता है। यह ज़्यादातर खाने में iron की कमी या ज़्यादा periods के कारण होता है। आपको थकान और कमज़ोरी महसूस हो सकती है। Doctor से iron supplements के बारे में बात करें।

【Transliteration】
Aapka hemoglobin level ({value}) normal se kam hai. Hemoglobin aapke khoon mein oxygen carry karta hai. Yeh zyada tar iron ki kami ya heavy periods ke karan hota hai. Aapko thakaan aur kamzori mehsoos ho sakti hai. Doctor se iron supplements ke baare mein baat karein."""
            }
        },
        "malayalam": {
            "Hemoglobin": {
                "LOW": f"""【മലയാളം】
നിങ്ങളുടെ hemoglobin level ({value}) സാധാരണ പരിധിയില്‍ നിന്ന് കുറവാണ്. Hemoglobin നിങ്ങളുടെ blood-ല്‍ oxygen കൊണ്ടുപോകുന്നു. ഇത് iron ധാരാളമുള്ള ഭക്ഷണം കഴിക്കാതെ വരുന്നതാണ്, അഥവാ heavy periods കാരണം. നിങ്ങള്‍ക്ക് ക്ഷീണവും ദുര്‍ബലതയും തോന്നാം. Doctor-നെ കണ്ട് iron supplements പറ്റിയും സംസാരിക്കണം.

【Transliteration】
Ningalude hemoglobin level ({value}) normal range-il ninnu kuravanu. Hemoglobin ningalude blood-il oxygen carry cheyyunnu. Ithu iron ulla food kazhikkaathe varunnathaanu, athava heavy periods karanam. Ningalkku vishamavum durbalathayum thonnaam. Doctor-ne kandu iron supplements pattiyum samsaarikkanam."""
            }
        },
        "tamil": {
            "Hemoglobin": {
                "LOW": f"""【தமிழ்】
உங்கள் hemoglobin level ({value}) சாதாரண அளவை விட குறைவாக உள்ளது. Hemoglobin உங்கள் இரத்தத்தில் oxygen-ஐ எடுத்துச் செல்கிறது. இது பெரும்பாலும் உணவில் iron குறைவாக இருப்பதால் அல்லது அதிக periods-ஆல் ஏற்படுகிறது. உங்களுக்கு சோர்வு மற்றும் பலவீனம் ஏற்படலாம். Doctor-ஐ சந்தித்து iron supplements பற்றி பேசுங்கள்.

【Transliteration】
Ungal hemoglobin level ({value}) normal range-ah vida kuraivaaga ulladu. Hemoglobin ungal blood-il oxygen carry seyyudhu. Idhu iron kuraivaaga iruppadhaal athava heavy periods-aal varudhu. Ungalukku tiredness um weakness um thonarum. Doctor-ai santithu iron supplements pathi pesunga."""
            }
        },
        "telugu": {
            "Hemoglobin": {
                "LOW": f"""【తెలుగు】
మీ hemoglobin level ({value}) సాధారణ కంటే తక్కువగా ఉంది. Hemoglobin మీ రక్తంలో oxygen తీసుకెళ్తుంది. ఇది ఎక్కువగా ఆహారంలో iron లోపం లేదా ఎక్కువ periods వల్ల వస్తుంది. మీకు అలసట మరియు బలహీనత అనిపించవచ్చు. Doctor ని కలసి iron supplements గురించి మాట్లాడండి.

【Transliteration】
Mee hemoglobin level ({value}) normal kante thakkuvaga undi. Hemoglobin mee blood-lo oxygen carry chesthundi. Idhi iron loopam leda heavy periods valla vasthundi. Meeku alasata mariyu balaheenata anipinchavachu. Doctor ni kalasi iron supplements gurinchi matladandi."""
            }
        },
        "kannada": {
            "Hemoglobin": {
                "LOW": f"""【ಕನ್ನಡ】
ನಿಮ್ಮ hemoglobin level ({value}) ಸಾಮಾನ್ಯಕ್ಕಿಂತ ಕಡಿಮೆ ಇದೆ. Hemoglobin ನಿಮ್ಮ ರಕ್ತದಲ್ಲಿ oxygen ಅನ್ನು ಸಾಗಿಸುತ್ತದೆ. ಇದು ಹೆಚ್ಚಾಗಿ ಆಹಾರದಲ್ಲಿ iron ಕೊರತೆ ಅಥವಾ ಹೆಚ್ಚು periods ಕಾರಣ ಆಗುತ್ತದೆ. ನಿಮಗೆ ದಣಿವು ಮತ್ತು ದೌರ್ಬಲ್ಯ ಅನಿಸಬಹುದು. Doctor ಅವರನ್ನು ಭೇಟಿ ಮಾಡಿ iron supplements ಬಗ್ಗೆ ಮಾತನಾಡಿ.

【Transliteration】
Nimma hemoglobin level ({value}) normal gintha kadime ide. Hemoglobin nimma blood-alli oxygen carry madthade. Idhu iron shortage athava heavy periods inda aagthade. Nimge tiredness mathu weakness anisbahudu. Doctor avrannu meet maadi iron supplements bagge matnaadi."""
            }
        },
        "marathi": {
            "Hemoglobin": {
                "LOW": f"""【मराठी】
तुमचा hemoglobin level ({value}) सामान्यपेक्षा कमी आहे. Hemoglobin तुमच्या रक्तात oxygen वाहून नेतो. हे मुख्यत्वे अन्नात iron कमी असल्यामुळे किंवा जास्त periods मुळे होते. तुम्हाला थकवा आणि कमकुवतपणा जाणवू शकतो. Doctor ना भेटून iron supplements बद्दल बोला.

【Transliteration】
Tumcha hemoglobin level ({value}) normal peksha kami aahe. Hemoglobin tumchya blood madhe oxygen carry karto. He iron chi kami kinva jasta periods mule hote. Tumhala thakwa ani kamkuvatpana janvu shakto. Doctor na bhetun iron supplements baddal bola."""
            }
        },
        "bengali": {
            "Hemoglobin": {
                "LOW": f"""【বাংলা】
আপনার hemoglobin level ({value}) স্বাভাবিকের চেয়ে কম। Hemoglobin আপনার রক্তে oxygen বহন করে। এটি সাধারণত খাবারে iron এর অভাব বা বেশি periods এর কারণে হয়। আপনি ক্লান্তি এবং দুর্বলতা অনুভব করতে পারেন। Doctor এর সাথে দেখা করে iron supplements সম্পর্কে কথা বলুন।

【Transliteration】
Apnar hemoglobin level ({value}) normal theke kom. Hemoglobin apnar blood-e oxygen carry kore. Eta khub khaborey iron er ovab ba beshi periods er karone hoy. Apni klanti ebong durbolota onubhob korte paren. Doctor er sathe dekha kore iron supplements niye kotha bolun."""
            }
        },
        "gujarati": {
            "Hemoglobin": {
                "LOW": f"""【ગુજરાતી】
તમારું hemoglobin level ({value}) સામાન્ય કરતાં ઓછું છે. Hemoglobin તમારા લોહીમાં oxygen લઈ જાય છે. આ મોટે ભાગે ખોરાકમાં iron ની ઓછી માત્રા અથવા વધારે periods ના કારણે થાય છે. તમને થાક અને નબળાઈ લાગી શકે છે. Doctor ને મળીને iron supplements વિશે વાત કરો.

【Transliteration】
Tamaru hemoglobin level ({value}) normal karta ochhu chhe. Hemoglobin tamara blood ma oxygen lai jaay chhe. Aa iron ni kami athva vadhare periods na karane thaay chhe. Tamne thak ane nabalai lagi shake chhe. Doctor ne maleeney iron supplements vishe vat karo."""
            }
        },
        "urdu": {
            "Hemoglobin": {
                "LOW": f"""【اردو】
آپ کا hemoglobin level ({value}) معمول سے کم ہے۔ Hemoglobin آپ کے خون میں oxygen لے جاتا ہے۔ یہ زیادہ تر خوراک میں iron کی کمی یا زیادہ periods کی وجہ سے ہوتا ہے۔ آپ کو تھکاوٹ اور کمزوری محسوس ہو سکتی ہے۔ Doctor سے iron supplements کے بارے میں بات کریں۔

【Transliteration】
Aap ka hemoglobin level ({value}) normal se kam hai. Hemoglobin aap ke khoon mein oxygen le jaata hai. Yeh iron ki kami ya zyada periods ki wajah se hota hai. Aap ko thakawat aur kamzori mehsoos ho sakti hai. Doctor se iron supplements ke baare mein baat karein."""
            }
        },
        "odia": {
            "Hemoglobin": {
                "LOW": f"""【ଓଡ଼ିଆ】
ଆପଣଙ୍କର hemoglobin level ({value}) ସାଧାରଣ ଠାରୁ କମ୍ ଅଛି। Hemoglobin ଆପଣଙ୍କ ରକ୍ତରେ oxygen ବହନ କରେ। ଏହା ମୁଖ୍ୟତଃ ଖାଦ୍ୟରେ iron ଅଭାବ କିମ୍ବା ଅଧିକ periods କାରଣରୁ ହୁଏ। ଆପଣ କ୍ଲାନ୍ତି ଏବଂ ଦୁର୍ବଳତା ଅନୁଭବ କରିପାରନ୍ତି। Doctor ଙ୍କୁ ଭେଟି iron supplements ବିଷୟରେ କଥା ହୁଅନ୍ତୁ।

【Transliteration】
Apanankara hemoglobin level ({value}) normal tharu kam achhi. Hemoglobin apananka blood re oxygen carry kare. Eha khadya re iron abhab kimba adhika periods karanaru hue. Apana klanti ebam durbalata anubhaba karipaaranti. Doctor nku bhenti iron supplements bisayare katha huantu."""
            }
        }
    }
    
    lang_fallbacks = fallback_explanations.get(language.lower(), fallback_explanations["english"])
    
    if test_name in lang_fallbacks and status in lang_fallbacks[test_name]:
        return lang_fallbacks[test_name][status]
    
    fallback_messages = {
        "hindi": f"【हिंदी】\nआपका {test_name} level {status.lower()} है - {value} (सामान्य: {normal_range})। कृपया अपने doctor से इस result के बारे में बात करें।\n\n【Transliteration】\nAapka {test_name} level {status.lower()} hai - {value} (normal: {normal_range}). Kripya apne doctor se is result ke baare mein baat karein.",
        
        "malayalam": f"【മലയാളം】\nനിങ്ങളുടെ {test_name} level {status.lower()} ആണ് - {value} (സാധാരണ: {normal_range}). ദയവായി നിങ്ങളുടെ doctor-ഉമായി ഈ result പറ്റിയും സംസാരിക്കുക.\n\n【Transliteration】\nNingalude {test_name} level {status.lower()} aanu - {value} (normal: {normal_range}). Dayavayi ningalude doctor-umaayi ee result pattiyum samsaarikkuka.",
        
        "tamil": f"【தமிழ்】\nஉங்கள் {test_name} level {status.lower()} உள்ளது - {value} (சாதாரண: {normal_range}). தயவுசெய்து உங்கள் doctor-உடன் இந்த result பற்றி பேசுங்கள்.\n\n【Transliteration】\nUngal {test_name} level {status.lower()} ulladu - {value} (normal: {normal_range}). Dayavuseythu ungal doctor-udan indha result pathi pesunga.",
        
        "telugu": f"【తెలుగు】\nమీ {test_name} level {status.lower()} ఉంది - {value} (సాధారణ: {normal_range}). దయచేసి మీ doctor తో ఈ result గురించి మాట్లాడండి.\n\n【Transliteration】\nMee {test_name} level {status.lower()} undi - {value} (normal: {normal_range}). Dayachesi mee doctor tho ee result gurinchi matladandi.",
        
        "kannada": f"【ಕನ್ನಡ】\nನಿಮ್ಮ {test_name} level {status.lower()} ಇದೆ - {value} (ಸಾಮಾನ್ಯ: {normal_range}). ದಯವಿಟ್ಟು ನಿಮ್ಮ doctor ಅವರೊಂದಿಗೆ ಈ result ಬಗ್ಗೆ ಮಾತನಾಡಿ.\n\n【Transliteration】\nNimma {test_name} level {status.lower()} ide - {value} (normal: {normal_range}). Dayavittu nimma doctor avarondige ee result bagge matnaadi.",
        
        "marathi": f"【मराठी】\nतुमचा {test_name} level {status.lower()} आहे - {value} (सामान्य: {normal_range}). कृपया तुमच्या doctor शी या result बद्दल बोला.\n\n【Transliteration】\nTumcha {test_name} level {status.lower()} aahe - {value} (normal: {normal_range}). Krupaya tumchya doctor shi ya result baddal bola.",
        
        "bengali": f"【বাংলা】\nআপনার {test_name} level {status.lower()} - {value} (স্বাভাবিক: {normal_range})। দয়া করে আপনার doctor এর সাথে এই result সম্পর্কে কথা বলুন।\n\n【Transliteration】\nApnar {test_name} level {status.lower()} - {value} (normal: {normal_range}). Doya kore apnar doctor er sathe ei result somporke kotha bolun.",
        
        "gujarati": f"【ગુજરાતી】\nતમારું {test_name} level {status.lower()} છે - {value} (સામાન્ય: {normal_range}). કૃપા કરીને તમારા doctor સાથે આ result વિશે વાત કરો.\n\n【Transliteration】\nTamaru {test_name} level {status.lower()} chhe - {value} (normal: {normal_range}). Krupa kareeney tamara doctor sathe aa result vishe vat karo.",
        
        "urdu": f"【اردو】\nآپ کا {test_name} level {status.lower()} ہے - {value} (معمول: {normal_range})۔ براہ کرم اپنے doctor سے اس result کے بارے میں بات کریں۔\n\n【Transliteration】\nAap ka {test_name} level {status.lower()} hai - {value} (normal: {normal_range}). Barah-e-karam apne doctor se is result ke baare mein baat karein.",
        
        "odia": f"【ଓଡ଼ିଆ】\nଆପଣଙ୍କର {test_name} level {status.lower()} ଅଛି - {value} (ସାଧାରଣ: {normal_range})। ଦୟାକରି ଆପଣଙ୍କ doctor ସହିତ ଏହି result ବିଷୟରେ କଥା ହୁଅନ୍ତୁ।\n\n【Transliteration】\nApanankara {test_name} level {status.lower()} achhi - {value} (normal: {normal_range}). Dayakari apananka doctor sahita ehi result bisayare katha huantu."
    }
    
    return fallback_messages.get(language.lower(), f"Your {test_name} level is {status.lower()} at {value} (normal: {normal_range}). Please discuss this result with your doctor.")