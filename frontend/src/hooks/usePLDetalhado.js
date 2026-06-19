import { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { fetchPLDetalhado } from '../services/api';

export function usePLDetalhado(casa, numero, ano) {
  const [pl, setPL] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { state } = useLocation();

  const carregar = useCallback(async () => {
    if (!casa || !numero || !ano) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPLDetalhado(casa, numero, ano, state);
      setPL(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [casa, numero, ano, state]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  return { pl, loading, error, recarregar: carregar };
}