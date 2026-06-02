import ollama
import json
from app.schemas import OllamaResponse


def extract_spaced_concept(term: str, context: str) -> OllamaResponse:
    # Prompt para o modelo de IA
    prompt = f"""
    Given the term "{term}" and its context "{context}", provide the following information in a JSON format:
    1. A concise translation of the term in Portuguese.
    2. A list of synonyms for the term in English.
    3. A brief explanation of the context in which the term is used.

    The response should be in the following JSON format:
    {{
        "translation": "Portuguese translation here",
        "synonyms": "Comma-separated synonyms here",
        "context_explanation": "Brief explanation of the context here"
    }}
    """

    # Chamada ao modelo de IA
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "user", "content": prompt}
        ],
        format="json"
    )

    raw_content = response['message']['content']

    try:
        parsed_json = json.loads(raw_content)
        return OllamaResponse(**parsed_json)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"Failed to parse Ollama response: {e}. Raw content: {raw_content}")