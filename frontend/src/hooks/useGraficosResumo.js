import { useState, useEffect, useCallback } from 'react';
import { fetchGraficosResumo } from '../services/api';

export function useGraficosResumo() {
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const carregar = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchGraficosResumo();
      setDados(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  return { dados, loading, error, recarregar: carregar };
}