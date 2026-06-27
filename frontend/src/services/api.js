import { mockProjetos, mockFiltros } from '../mocks/projetosLei';
import { mockPLsDetalhados } from '../mocks/plDetalhado';
import { mockGraficosResumo } from '../mocks/graficosResumo';
import { MOCK_POR_DIMENSAO } from '../mocks/dashboard';

const USE_MOCK = false;
const USE_MOCK_GRAFICOS = false;
const USE_MOCK_DASHBOARD = false;
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchProjetos(params = {}) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 600));
    let projetos = [...mockProjetos.projetos];
    if (params.keyword) {
      const kw = params.keyword.toLowerCase();
      projetos = projetos.filter(
        (p) => p.ementa.toLowerCase().includes(kw) || p.numero.includes(kw)
      );
    }
    if (params.partido) projetos = projetos.filter((p) => p.autor_partido === params.partido);
    if (params.uf) projetos = projetos.filter((p) => p.autor_uf === params.uf);
    if (params.status) projetos = projetos.filter((p) => p.status === params.status);
    if (params.ano) projetos = projetos.filter((p) => p.ano === Number(params.ano));
    if (params.ordenar === 'antigos') {
      projetos.sort((a, b) => new Date(a.ultima_atualizacao) - new Date(b.ultima_atualizacao));
    } else if (params.ordenar === 'numero_asc') {
      projetos.sort((a, b) => Number(a.numero) - Number(b.numero));
    } else {
      projetos.sort((a, b) => new Date(b.ultima_atualizacao) - new Date(a.ultima_atualizacao));
    }
    const per_page = params.per_page || 6;
    const page = params.page || 1;
    const total = projetos.length;
    const total_pages = Math.ceil(total / per_page) || 1;
    const start = (page - 1) * per_page;
    return { total, page, per_page, total_pages, projetos: projetos.slice(start, start + per_page) };
  }
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '' && v != null))
  ).toString();
  const response = await fetch(`${BASE_URL}/api/projetos-de-lei?${query}`);
  if (!response.ok) throw new Error('Erro ao buscar projetos');
  return response.json();
}

export async function fetchFiltros() {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    return mockFiltros;
  }
  const response = await fetch(`${BASE_URL}/api/projetos-de-lei/filtros`);
  if (!response.ok) throw new Error('Erro ao buscar filtros');
  return response.json();
}

export async function fetchPLDetalhado(casa, numero, ano) {
  const USE_MOCK_DETALHADO = false;
  if (USE_MOCK_DETALHADO) {
    await new Promise((r) => setTimeout(r, 500));
    const idMock = `pl-${numero}-${ano}`;
    const pl = mockPLsDetalhados[idMock];
    const todos = Object.values(mockPLsDetalhados);
    const hash = `${casa}${numero}${ano}`.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
    const plBase = pl ? { ...pl } : { ...todos[hash % todos.length] };
    plBase.numero = numero;
    plBase.ano = Number(ano);
    return plBase;
  }
  const response = await fetch(`${BASE_URL}/api/projetos-de-lei/${casa}/${numero}/${ano}`);
  if (response.status === 404) throw new Error('not_found');
  if (!response.ok) throw new Error('Erro ao buscar projeto de lei');
  return response.json();
}

export async function fetchGraficosResumo() {
  if (USE_MOCK_GRAFICOS) {
    await new Promise((r) => setTimeout(r, 600));
    return mockGraficosResumo;
  }
  const response = await fetch(`${BASE_URL}/api/graficos/resumo`);
  if (!response.ok) throw new Error('Erro ao buscar resumo dos gráficos');
  return response.json();
}

export async function fetchDashboard(params = {}) {
  if (USE_MOCK_DASHBOARD) {
    await new Promise((r) => setTimeout(r, 600));
    const dimensao = params.comparar_por || 'partido';
    return MOCK_POR_DIMENSAO[dimensao] || MOCK_POR_DIMENSAO.partido;
  }
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '' && v != null))
  ).toString();
  const response = await fetch(`${BASE_URL}/api/graficos/distribuicao?${query}`);
  if (!response.ok) throw new Error('Erro ao buscar dados do dashboard');
  return response.json();
}