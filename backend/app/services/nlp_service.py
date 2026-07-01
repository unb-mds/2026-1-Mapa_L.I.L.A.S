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

def classificar_projeto(ementa: str) -> bool:
    """
    Chama a API do Gemini (ou mock) para classificar se a ementa de um projeto de lei
    é focada no combate ao feminicídio ou violência doméstica contra a mulher.
    Retorna True se for relevante, False caso contrário.
    """
    if not ementa:
        return False
        
    use_mock = os.environ.get("USE_MOCK_IA", "false").lower() == "true"
    if use_mock:
        # Mock simula acerto para a palavra "feminicídio" ou "violência"
        ementa_lower = ementa.lower()
        return "feminicídio" in ementa_lower or "violência" in ementa_lower

    if not genai:
        logger.error("google-generativeai não está instalado.")
        return False

    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            f"Você é um classificador binário especializado em legislação brasileira. "
            f"Analise a seguinte ementa de projeto de lei: '{ementa}'. "
            f"Responda EXATAMENTE E APENAS com a palavra 'true' se o projeto trata diretamente "
            f"sobre feminicídio ou violência doméstica contra a mulher. "
            f"Responda 'false' caso contrário ou se for apenas tangencial. "
            f"NÃO inclua nenhuma formatação ou texto extra."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        content = response.text.strip().lower()
        return content == "true"
        
    except Exception as e:
        logger.error(f"Erro ao classificar projeto com Gemini: {e}")
        return False
