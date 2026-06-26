import { useState, useEffect } from 'react';
import { fetchProjetos, fetchFiltros } from '../services/api';

const FILTROS_INICIAL = {
  keyword: '',
  partido: '',
  uf: '',
  status: '',
  ano: '',
};

export function useProjetosLei() {
  const [projetos, setProjetos] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [ordenar, setOrdenar] = useState('recentes');
  const [filtros, setFiltros] = useState(FILTROS_INICIAL);
  const [filtrosAplicados, setFiltrosAplicados] = useState(FILTROS_INICIAL);
  const [metaFiltros, setMetaFiltros] = useState({ partidos: [], ufs: [], anos: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trigger, setTrigger] = useState(0);

  // Carrega metadados dos filtros uma única vez
  useEffect(() => {
    let cancelado = false;
    async function carregarFiltros() {
      try {
        const data = await fetchFiltros();
        if (!cancelado) setMetaFiltros(data);
      } catch (e) {
        console.error('Erro ao carregar metadados dos filtros:', e);
      }
    }
    carregarFiltros();
    return () => { cancelado = true; };
  }, []);

  // Carrega projetos sempre que filtros, página, ordenação ou trigger mudam
  useEffect(() => {
    let cancelado = false;
    async function carregarProjetos() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchProjetos({
          ...filtrosAplicados,
          page,
          per_page: 6,
          ordenar,
        });
        if (!cancelado) {
          setProjetos(data.projetos);
          setTotal(data.total);
          setTotalPages(data.total_pages);
        }
      } catch (e) {
        if (!cancelado) setError(e.message);
      } finally {
        if (!cancelado) setLoading(false);
      }
    }
    carregarProjetos();
    return () => { cancelado = true; };
  }, [filtrosAplicados, page, ordenar, trigger]);

  const aplicarFiltros = () => {
    setFiltrosAplicados({ ...filtros });
    setPage(1);
  };

  const limparFiltros = () => {
    setFiltros(FILTROS_INICIAL);
    setFiltrosAplicados(FILTROS_INICIAL);
    setPage(1);
  };

  return {
    projetos,
    total,
    totalPages,
    page,
    setPage,
    ordenar,
    setOrdenar,
    filtros,
    setFiltros,
    metaFiltros,
    loading,
    error,
    aplicarFiltros,
    limparFiltros,
    recarregar: () => setTrigger((t) => t + 1),
  };
}