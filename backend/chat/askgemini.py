import os
import httpx
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not found in environment")

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

def is_medical_query(prompt: str) -> bool:
    """
    Check if the prompt is related to medical/health topics
    """
    prompt_lower = prompt.lower()
    
    # Medical keywords and phrases
    medical_keywords = [
        # General medical terms
        'health', 'medical', 'medicine', 'doctor', 'hospital', 'clinic', 'patient',
        'diagnosis', 'treatment', 'therapy', 'prescription', 'medication', 'drug',
        'surgery', 'operation', 'procedure', 'examination', 'test', 'screening',
        
        # Symptoms and conditions
        'symptom', 'pain', 'ache', 'fever', 'headache', 'nausea', 'vomit', 'diarrhea',
        'cough', 'cold', 'flu', 'infection', 'virus', 'bacteria', 'disease', 'illness',
        'sick', 'injury', 'wound', 'cut', 'burn', 'bruise', 'swelling', 'rash',
        'allergy', 'asthma', 'diabetes', 'cancer', 'heart', 'blood', 'pressure',
        'cholesterol', 'stroke', 'seizure', 'depression', 'anxiety', 'stress',
        
        # Body parts and systems
        'brain', 'lung', 'liver', 'kidney', 'stomach', 'intestine', 'bone', 'muscle',
        'skin', 'eye', 'ear', 'nose', 'throat', 'chest', 'abdomen', 'back', 'neck',
        'arm', 'leg', 'hand', 'foot', 'joint', 'spine', 'nerve', 'blood vessel',
        
        # Medical professionals
        'physician', 'surgeon', 'nurse', 'pharmacist', 'therapist', 'specialist',
        'cardiologist', 'neurologist', 'dermatologist', 'psychiatrist', 'pediatrician',
        
        # Medical questions/phrases
        'what is', 'how to treat', 'how to cure', 'side effects', 'dosage',
        'first aid', 'emergency', 'urgent care', 'when to see doctor',
        'is it normal', 'should i worry', 'what causes', 'how to prevent',
        
        # Common medical abbreviations
        'covid', 'hiv', 'aids', 'std', 'uti', 'bmi', 'bp', 'hr', 'temp',
        
        # Pregnancy and reproductive health
        'pregnancy', 'pregnant', 'birth', 'labor', 'delivery', 'contraception',
        'fertility', 'menstruation', 'period', 'ovulation',
        
        # Mental health
        'mental health', 'psychological', 'psychiatric', 'therapy', 'counseling',
        'bipolar', 'schizophrenia', 'ptsd', 'adhd', 'autism', 'ocd',
        
        # Nutrition and wellness
        'nutrition', 'vitamin', 'mineral', 'diet', 'weight loss', 'weight gain',
        'exercise', 'fitness', 'wellness', 'healthy lifestyle'
    ]
    
    # Check for medical keywords
    for keyword in medical_keywords:
        if keyword in prompt_lower:
            return True
    
    # Check for medical question patterns
    medical_patterns = [
        r'\b(what|how|why|when|where|can|should|is|are|do|does|will|would)\b.*\b(health|medical|medicine|doctor|hospital|treatment|symptom|disease|illness|pain|sick|injury|medication|drug)\b',
        r'\bi (have|feel|am|got|experience|suffer)\b.*(pain|ache|symptom|sick|ill|infection|fever|headache|nausea|dizzy)',
        r'\bmy (head|chest|stomach|back|neck|arm|leg|hand|foot|eye|ear|nose|throat|skin|heart|lung|liver|kidney)\b.*(hurt|pain|ache|sore|problem|issue)',
        r'\b(diagnose|treatment|cure|heal|recover|medicine|medication|prescription|dosage|side effect)\b',
        r'\bfirst aid\b|\bemergency\b|\burgent care\b',
        r'\b(normal|abnormal|healthy|unhealthy|risk|danger|safe|unsafe)\b.*\b(health|medical|body|condition)\b'
    ]
    
    for pattern in medical_patterns:
        if re.search(pattern, prompt_lower):
            return True
    
    return False

async def ask_gemini(prompt: str) -> str:
    """
    Process medical queries only. Non-medical queries are declined.
    """
    # Check if the query is medical-related
    if not is_medical_query(prompt):
        return """I'm sorry, but I can only assist with medical and health-related questions. 
        
Please ask me about:
• Health symptoms and conditions
• Medical treatments and medications
• First aid and emergency care
• Preventive healthcare
• Nutrition and wellness
• Mental health topics
• General medical information

For non-medical questions, please consult other resources or services."""
    
    # Add medical context to the prompt for better responses
    medical_prompt = f"""You are a helpful medical AI assistant. Please provide accurate, evidence-based medical information while emphasizing that this is for educational purposes only and not a substitute for professional medical advice. Always recommend consulting healthcare professionals for proper diagnosis and treatment.

User question: {prompt}

Please provide a helpful, informative response while including appropriate medical disclaimers."""
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # Correct payload structure for Gemini API
    payload = {
        "contents": [{
            "parts": [{
                "text": medical_prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.3,  # Lower temperature for more factual medical responses
            "candidateCount": 1,
            "maxOutputTokens": 1024
        }
    }
    
    url = f"{BASE_URL}?key={API_KEY}"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Parse the response correctly
            candidates = data.get("candidates", [])
            if candidates and len(candidates) > 0:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts and len(parts) > 0:
                    medical_response = parts[0].get("text", "No text found in response")
                    
                    # Add standard medical disclaimer
                    disclaimer = "\n\n⚠️ **Medical Disclaimer**: This information is for educational purposes only and should not replace professional medical advice. Always consult with a qualified healthcare provider for proper diagnosis and treatment."
                    
                    return medical_response + disclaimer
                else:
                    return "No content parts found in response"
            else:
                return "No candidates found in response"
                
    except httpx.TimeoutException:
        return "Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"An error occurred: {str(e)}"