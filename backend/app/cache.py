"""
Módulo centralizado de cache para todos os endpoints da API.

Todas as instâncias de TTLCache são definidas aqui para facilitar
manutenção, testes e limpeza global.
"""
from cachetools import TTLCache

TTL_12H = 43200  # 12 horas em segundos

# Gráficos
cache_resumo = TTLCache(maxsize=2, ttl=TTL_12H)
cache_distribuicao = TTLCache(maxsize=100, ttl=TTL_12H)

# Projetos de Lei
cache_stats = TTLCache(maxsize=2, ttl=TTL_12H)
cache_filtros = TTLCache(maxsize=2, ttl=TTL_12H)
cache_projetos = TTLCache(maxsize=15, ttl=TTL_12H)  # 3 ordenações × 4 status + margem
