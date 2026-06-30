import { useState, useEffect } from 'react';

const BASE_URL = 'http://localhost:8000';

export function useStats() {
  const [stats, setStats] = useState({
    total: '--',
    emTramitacao: '--',
    aprovados: '--',
    arquivados: '--',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/api/projetos-de-lei/stats`)
      .then(r => r.json())
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