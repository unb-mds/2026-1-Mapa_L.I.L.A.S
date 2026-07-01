# Cobertura de Testes Unitários

Para garantir a estabilidade e qualidade das entregas, o projeto conta com uma extensa bateria de testes automatizados, focados prioritariamente na API (backend) utilizando a biblioteca `pytest`.

## Escopo dos Testes

Alcançamos uma cobertura que engloba praticamente todo o código principal do backend, com baterias que garantem desde a lógica de agregação até resiliência contra falhas de comunicação externa:

* **Endpoints de Cache (`test_cache_endpoints.py`):** Validação estrita do ciclo de vida do cache (Redis/Local), certificando-se de que pesquisas idênticas repetidas ao longo do dia são respondidas instantaneamente sem bater no banco de dados Neon.
* **Agregadores de Gráficos (`test_graficos_resumo.py`):** Testes que garantem que as métricas calculadas e formatadas pela API (ex: agrupar Projetos de Lei por Tema ou por Estado do autor) estão corretas antes de serem despachadas para o ecossistema Frontend (React).
* **Módulo NLP e Ingestão:** Simulação (Mocking) das requisições ao Google Gemini e às APIs da Câmara e Senado. Isso garante que a esteira de `data-ingestion` valide suas lógicas de parsing sem precisar consumir nossa cota diária de requisições web.


