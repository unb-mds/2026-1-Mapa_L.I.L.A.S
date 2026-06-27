import { useState, useEffect } from 'react';
import { fetchStats } from '../services/api';

export function useStats() {
  const [stats, setStats] = useState({
    total: '--',
    emTramitacao: '--',
    aprovados: '--',
    arquivados: '--',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats()
      .then((data) => {
        setStats({
          total: data.total,
          emTramitacao: data.em_tramitacao,
          aprovados: data.aprovados,
          arquivados: data.arquivados,
        });
      })
      .catch(() => {
        console.warn('Stats API indisponível.');
      })
      .finally(() => setLoading(false));
  }, []);

  return { stats, loading };
}