import os
import json
import logging
from typing import List

try:
    from google import genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

# Configura a chave do Gemini se existir no ambiente
api_key = os.environ.get("GEMINI_API_KEY")

def get_dynamic_keywords(seed_topics: List[str] = None) -> List[str]:
    """
    Chama a API do Gemini (ou retorna mock) para retornar uma lista expandida
    de palavras-chave baseadas nos temas sementes.
    Em caso de falha da API, retorna a própria lista de sementes como fallback.
    """
    if not seed_topics:
        seed_topics = ["feminicídio", "violência doméstica", "direitos da mulher"]
        
    use_mock = os.environ.get("USE_MOCK_IA", "false").lower() == "true"
    if use_mock:
        logger.info("Modo MOCK_IA ativado. Retornando palavras-chave fictícias.")
        return seed_topics + ["mock_keyword_1", "mock_keyword_2"]
    
    if not genai:
        logger.error("google-generativeai não está instalado.")
        return seed_topics

    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            f"Você é um assistente especializado em legislação brasileira. "
            f"Gere até 5 palavras-chave altamente relevantes para busca legislativa sobre os temas: {', '.join(seed_topics)}. "
            f"Retorne APENAS um array JSON válido contendo palavras-chave e frases curtas como strings, sem formatação markdown."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        content = response.text
        
        # Limpa possível bloco markdown
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        keywords = json.loads(content.strip())
        if isinstance(keywords, list):
            return keywords
        return seed_topics
    except Exception as e:
        logger.error(f"Erro ao buscar palavras-chave do Gemini: {e}")
        return seed_topics
