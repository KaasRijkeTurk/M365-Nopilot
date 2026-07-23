import requests
import re

MODEL = "llama3.2" 
OLLAMA_URL = "http://localhost:11434/api/generate"

def classify_text(text: str, categories=None) -> str:
    """
    Classifies text into one of the provided categories.
    
    Args:
        text (str): The text to classify.
        categories (dict, optional): A dictionary mapping category codes to descriptions.
                                     Example: {"1": "Basics", "2": "Intermediate", "3": "Advanced"}
                                     If None, uses default L1/L2/L3 logic.
    
    Returns:
        str: The category code (e.g., "1", "2", or "3").
    """
    
    # Default categories if none provided
    if categories is None:
        categories = {
            "1": "basics (introductory concepts, definitions)",
            "2": "explanations (detailed understanding, context)",
            "3": "debates (controversial topics, arguments, apologetics)"
        }

    # Build the prompt dynamically based on categories
    cat_instructions = "\n".join([f"{code} = {desc}" for code, desc in categories.items()])
    
    prompt = f"""You are a strict text classification automation.
Classify the given text into exactly one of these categories:
{cat_instructions}

Rules:
- Respond with ONLY the single digit corresponding to the category.
- Do not include explanation, punctuation, or extra words.

Text: {text}
Result:"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            },
            timeout=60
        )
        
        if r.status_code != 200:
            print(f"[AI ERROR] Ollama returned status code {r.status_code}")
            return list(categories.keys()) # Fallback to first category

        response_text = r.json().get("response", "").strip()
        
        # Extract the first valid digit from the defined categories
        valid_digits = list(categories.keys())
        match = re.search(r"|".join(valid_digits), response_text)
        
        if match:
            return match.group(0)
            
        print(f"[AI WARNING] Unexpected AI response: '{response_text}'")
        return list(categories.keys()) # Fallback

    except requests.exceptions.RequestException as e:
        print(f"[AI ERROR] Could not connect to Ollama: {e}")
        return list(categories.keys()) # Fallback
