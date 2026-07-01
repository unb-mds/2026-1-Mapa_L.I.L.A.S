# Automação de Ingestão e NLP com IA

O projeto L.I.L.A.S. possui uma robusta pipeline para capturar os dados mais recentes do legislativo, integrando automação de DevOps através de GitHub Actions e recursos de NLP (Processamento de Linguagem Natural) para uma busca mais eficiente e semântica.

## Pipeline Automática com GitHub Actions

Configuramos um fluxo automatizado (`.github/workflows/data-ingestion.yml`) para manter nossa base de dados sempre atualizada com as proposições mais recentes da Câmara e do Senado, sem que a equipe precise interagir com os scripts manualmente.

### Funcionamento do CRON
A pipeline é ativada diariamente de segunda a sexta-feira, exatamente às **23:57 (Horário de Brasília)**. Este horário foi escolhido para capturar todo o volume de projetos pautados e lançados durante o expediente do dia no Congresso Nacional.

### Artefatos e Transparência
Ao finalizar a extração e carga no banco de dados, o próprio workflow do GitHub Actions gera e sobrescreve um artefato JSON contendo o relatório de ingestão, que pode ser acompanhado diretamente pelo site (na aba `Relatório de Ingestão`). Isso provê total transparência do que foi coletado em cada dia.

---

## Integração do Modelo de IA no Pipeline de Ingestão (Microserviço de NLP)

Este módulo de Inteligência Artificial para extração dinâmica de palavras-chave foi desenhado para melhorar o motor de busca de proposições legislativas na Câmara e no Senado, ampliando dinamicamente o escopo que antes se limitava a palavras fixas ("feminicídio", "violência doméstica").

### Arquitetura e Bibliotecas

A nova arquitetura usa a IA Generativa (Google Gemini) atuando como um *microserviço de NLP* para gerar dezenas de sinônimos e termos correlatos baseados na semântica legislativa.

Foi adotada a biblioteca oficial `google-genai` para comunicação direta com a infraestrutura da Google, rodando o modelo `gemini-2.5-flash`. A escolha se deve ao excepcional custo-benefício, à velocidade (ideal para integrações em loops de ETL) e à tolerância superior de *Rate Limits*.

### Componente Principal: `nlp_service.py`
Localizado em `backend/app/services/nlp_service.py`, este módulo abstrai o uso da API e expõe apenas a função `get_dynamic_keywords()`.

**Responsabilidades:**
1. Receber uma lista de `seed_topics` (Ex: "direitos da mulher").
2. Montar um prompt de contexto jurídico.
3. Forçar o LLM a retornar a saída estritamente em um array JSON puro.
4. Tratar sujeiras residuais no payload de resposta.
5. Interceptar qualquer falha de comunicação executando um Fallback Silencioso (retornando à lista base, garantindo resiliência total).

### O Modo "Mock" (Simulação Local)

Para otimizar o tempo de desenvolvimento da equipe e poupar cotas reais, ative o modo **Mock_IA** configurando `USE_MOCK_IA=True` no arquivo `backend/.env`. O módulo intercepta a chamada de rede antes de contactar a Google e injeta itens fictícios.

### Integração no Collector

O orquestrador `backend/app/services/collector.py` consome o `nlp_service` antes da inicialização do loop de paginação das APIs governamentais:

```python
from app.services.nlp_service import get_dynamic_keywords

def coletar_camara(...):
    palavras_chave = get_dynamic_keywords(camara_client.PALAVRAS_CHAVE)
    # Loop prossegue pelas APIs usando as palavras_chave dinâmicas ampliadas
```
