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
    Check if the prompt is related to medical/health/greetings topics
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
        'exercise', 'fitness', 'wellness', 'healthy lifestyle',
        
        # Greetings and common phrases
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'how are you', 'how is it going', 'what\'s up', 'how can I help', 'nice to meet you',
        'thank you', 'please', 'goodbye', 'see you later', 'take care', 'have a nice day',
        'welcome', 'greetings', 'howdy', 'salutations', 'what can I do for you',
        'how can I assist', 'how may I help', 'what\'s new', 'what\'s happening',
        'how\'s it going', 'how have you been', 'long time no see', 'good to see you',
        'pleased to meet you', 'thanks for reaching out', 'appreciate your help',
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

async def get_brief_general_response(prompt: str) -> str:
    """
    Use Gemini AI to generate a brief, friendly response for non-medical questions
    """
    # Create a prompt for Gemini to give a brief, friendly response
    general_prompt = f"""You are a friendly AI assistant. The user asked: "{prompt}"

Please provide a very brief, friendly response (1-2 sentences maximum) to acknowledge their question or comment. Be conversational and natural, but keep it short since you will redirect them to medical topics afterward.

Examples:
- For greetings: "Hello! Nice to meet you."
- For weather questions: "I hope the weather is nice where you are!"
- For general topics: "That's interesting!" or "That sounds great!"

User question: {prompt}

Provide only a brief, friendly response:"""
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": general_prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,  # Higher temperature for more natural conversational responses
            "candidateCount": 1,
            "maxOutputTokens": 100  # Keep it brief
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
                    return parts[0].get("text", "That's interesting!").strip()
                else:
                    return "That's interesting!"
            else:
                return "That's interesting!"
                
    except Exception as e:
        # Fallback to simple response if Gemini call fails
        return "That's interesting!"

async def ask_gemini(prompt: str) -> str:
    """
    Process medical queries with full responses, and non-medical queries with brief responses + medical redirect.
    """
    # Check if the query is medical-related
    if not is_medical_query(prompt):
        # Get a brief response for the general question using Gemini AI
        brief_response = await get_brief_general_response(prompt)
        
        # Add medical redirect
        redirect_message = """

However, I'm specifically designed to help with medical and health-related questions. Feel free to ask me about:
• Health symptoms and conditions
• Medical treatments and medications  
• First aid and emergency care
• Preventive healthcare
• Nutrition and wellness
• Mental health topics
• General medical information

Is there anything health-related I can help you with today?"""
        
        return brief_response + redirect_message
    
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