import { useState, useEffect, useCallback } from 'react';
import { fetchDashboard } from '../services/api';

const FILTROS_INICIAL = { estado: '', partido: '', genero: '', mes: '' };

export function useDashboard() {
  const [compararPor, setCompararPor] = useState('partido');
  const [filtros, setFiltros] = useState(FILTROS_INICIAL);
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const carregar = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { comparar_por: compararPor, ...filtros };
      const data = await fetchDashboard(params);
      setDados(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [compararPor, filtros]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const mudarComparar = (nova) => {
    // Reseta o filtro da dimensão anterior ao trocar
    setFiltros((prev) => ({ ...prev, [compararPor]: '' }));
    setCompararPor(nova);
  };

  const mudarFiltro = (campo, valor) => {
    setFiltros((prev) => ({ ...prev, [campo]: valor }));
  };

  return {
    compararPor,
    mudarComparar,
    filtros,
    mudarFiltro,
    dados,
    loading,
    error,
    recarregar: carregar,
  };
}
