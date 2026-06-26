import { useState, useEffect } from 'react';
import { fetchGraficosResumo } from '../services/api';

export function useGraficosResumo() {
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trigger, setTrigger] = useState(0);

  useEffect(() => {
    let cancelado = false;

    async function carregar() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchGraficosResumo();
        if (!cancelado) setDados(data);
      } catch (e) {
        if (!cancelado) setError(e.message);
      } finally {
        if (!cancelado) setLoading(false);
      }
    }

    carregar();
    return () => { cancelado = true; };
  }, [trigger]);

  return { dados, loading, error, recarregar: () => setTrigger((t) => t + 1) };
}