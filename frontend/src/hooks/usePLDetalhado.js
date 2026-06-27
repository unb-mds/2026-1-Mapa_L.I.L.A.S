import { useState, useEffect } from 'react';
import { fetchPLDetalhado } from '../services/api';

export function usePLDetalhado(casa, numero, ano) {
  const [pl, setPL] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trigger, setTrigger] = useState(0);

  useEffect(() => {
    if (!casa || !numero || !ano) return;
    let cancelado = false;

    async function carregar() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchPLDetalhado(casa, numero, ano);
        if (!cancelado) setPL(data);
      } catch (e) {
        if (!cancelado) setError(e.message);
      } finally {
        if (!cancelado) setLoading(false);
      }
    }

    carregar();
    return () => { cancelado = true; };
  }, [casa, numero, ano, trigger]);

  return { pl, loading, error, recarregar: () => setTrigger((t) => t + 1) };
}