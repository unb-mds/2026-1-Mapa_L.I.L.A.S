import { useState, useEffect } from 'react';
import { fetchDashboard } from '../services/api';

const FILTROS_INICIAL = { estado: '', partido: '', genero: '', mes: '' };

export function useDashboard() {
  const [compararPor, setCompararPor] = useState('partido');
  const [filtros, setFiltros] = useState(FILTROS_INICIAL);
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
        const params = { comparar_por: compararPor, ...filtros };
        const data = await fetchDashboard(params);
        if (!cancelado) setDados(data);
      } catch (e) {
        if (!cancelado) setError(e.message);
      } finally {
        if (!cancelado) setLoading(false);
      }
    }

    carregar();
    return () => { cancelado = true; };
  }, [compararPor, filtros, trigger]);

  const mudarComparar = (nova) => {
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
    recarregar: () => setTrigger((t) => t + 1),
  };
}