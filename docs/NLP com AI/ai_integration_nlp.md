# Integração do Modelo de IA no Pipeline de Ingestão (Microserviço de NLP)

Este documento descreve a implementação do módulo de Inteligência Artificial para extração dinâmica de palavras-chave, desenhado para melhorar o motor de busca de proposições legislativas na Câmara e no Senado no escopo do projeto L.I.L.A.S.

## Objetivo
Anteriormente, o processo de ingestão (`collector.py`) baseava-se em uma lista de strings estáticas (hardcoded) para fazer o filtro de matérias ("feminicídio", "violência doméstica").
O objetivo da nova arquitetura é usar a IA Generativa (Google Gemini) atuando como um *microserviço de NLP* para, a partir de temas-semente, gerar dezenas de sinônimos e termos correlatos baseados na semântica legislativa atual.

## Arquitetura e Bibliotecas

Foi adotada a biblioteca oficial `google-genai` para comunicação direta com a infraestrutura da Google, rodando o modelo `gemini-2.5-flash`.
A escolha se deve ao excepcional custo-benefício, à velocidade do modelo (ideal para integrações em loops de ETL) e à tolerância superior de *Rate Limits* (evitando erros 429 frequentes de outras provedoras).

### Componente Principal: `nlp_service.py`
Localizado em `backend/app/services/nlp_service.py`, este módulo abstrai o uso da API e expõe apenas a função `get_dynamic_keywords()`.

**Responsabilidades:**
1. Receber uma lista de `seed_topics` (Ex: "direitos da mulher").
2. Montar um prompt de contexto jurídico informando ao modelo seu papel ("Você é um assistente especializado em legislação brasileira...").
3. Forçar o LLM a retornar a saída estritamente em um array JSON puro.
4. Tratar sujeiras residuais no payload de resposta (ex: remoção de blocos *markdown* ` ```json `).
5. Interceptar qualquer falha de comunicação ou ausência de cota, executando um Fallback Silencioso.

## O Modo "Mock" (Simulação Local)

Para otimizar o tempo de desenvolvimento da equipe e garantir execução das suítes de testes automatizados sem esgotar as cotas reais da API, foi construído um modo **Mock_IA**.

*   **Como ativar:** No arquivo `backend/.env`, configure `USE_MOCK_IA=True`.
*   **Comportamento:** O módulo intercepta a chamada de rede antes de contactar a Google e injeta as sementes originais acrescidas de itens fictícios (`mock_keyword_1`). A integração flui sem bloqueios e de modo determinístico.

## Resiliência e Fallback

A infraestrutura foi pensada seguindo premissas de TDD e fail-safe:
Se a rede cair, se as credenciais expirarem, se houver timeout, ou se faltar a biblioteca na máquina do dev, o bloco `try/except` aborta a requisição NLP e **retorna a matriz de temas base imediatamente**.
Isso garante que o *Data Pipeline* (a rotina de ingestão de dados diários do Banco) jamais pare de funcionar por causa de um serviço terceiro.

## Integração no Collector

O orquestrador `backend/app/services/collector.py` consome o `nlp_service`.
Tanto em `coletar_camara()` quanto em `coletar_senado()`, as palavras-chave agora são puxadas antes da inicialização do loop de paginação das APIs governamentais:

```python
from app.services.nlp_service import get_dynamic_keywords

def coletar_camara(...):
    palavras_chave = get_dynamic_keywords(camara_client.PALAVRAS_CHAVE)
    for sigla in camara_client.SIGLAS_TIPO:
        for kw in palavras_chave:
            # Requisita a API da Câmara usando o "kw" gerado pela IA
```

## Configuração do Ambiente Local

Para que o script rode perfeitamente na sua máquina usando a API real:

1. Atualize o `backend/requirements.txt` (`pip install -r requirements.txt`).
2. Adicione ao `backend/.env`:
```env
GEMINI_API_KEY="Sua_Chave_De_Acesso_Aqui"
USE_MOCK_IA=False
```
3. Rode `python popular_banco.py --mode incremental`. O módulo `dotenv` inicializado no topo carregará as variáveis e o loop trará PLs usando as chaves dinâmicas (ex: *'Proteção à Mulher', 'Lei Maria da Penha'*).
