import { useState, useRef } from 'react';
import { useDashboard } from '../../hooks/useDashboard';
import NavBar from '../../components/NavBar';
import Footer from '../../components/Footer';
import BreadcrumbDashboard from '../../components/Dashboard/BreadcrumbDashboard';
import SeletorComparar from '../../components/Dashboard/SeletorComparar';
import FiltrosDashboard from '../../components/Dashboard/FiltrosDashboard';
import CardIndicadores from '../../components/Dashboard/CardIndicadores';
import GraficoColunas from '../../components/Dashboard/GraficoColunas';
import GraficoPizza from '../../components/Dashboard/GraficoPizza';
import BotaoExportar from '../../components/Dashboard/BotaoExportar';

const LABELS_DIMENSAO = {
  partido: 'Partido',
  estado: 'Estado',
  genero: 'Gênero do Autor',
  mes: 'Mês',
};

function SkeletonGrafico() {
  return (
    <div className="animate-pulse">
      <div className="h-[350px] bg-gray-100 rounded-xl" />
    </div>
  );
}

export default function Dashboard() {
  const [abaAtiva, setAbaAtiva] = useState('colunas');
  const chartRef = useRef(null);

  const {
    compararPor,
    mudarComparar,
    filtros,
    mudarFiltro,
    dados,
    loading,
    error,
    recarregar,
  } = useDashboard();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <NavBar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-10">
        <BreadcrumbDashboard />

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 uppercase mb-1">
            Painel de Dados Legislativos
          </h1>
          <p className="text-sm text-gray-500 leading-relaxed max-w-2xl">
            Análise visual e monitoramento avançado da tramitação de projetos de lei,
            filtrados por recortes demográficos e regionais.
          </p>
        </div>

        {/* Seletor Comparar por */}
        <SeletorComparar ativo={compararPor} onChange={mudarComparar} />

        {/* Filtros */}
        <FiltrosDashboard
          compararPor={compararPor}
          filtros={filtros}
          onChange={mudarFiltro}
        />

        {/* Cards de indicadores */}
        <CardIndicadores indicadores={dados?.indicadores} loading={loading} />

        {/* Área do gráfico */}
        {error ? (
          <div className="flex flex-col items-center justify-center py-16 gap-4">
            <p className="text-gray-500 text-center text-sm">
              Não foi possível carregar os dados. Tente novamente.
            </p>
            <button
              onClick={recarregar}
              className="px-5 py-2 text-sm font-semibold bg-[#5B4FCF] text-white rounded-lg hover:bg-[#4338CA] transition-colors"
            >
              Tentar novamente
            </button>
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            {/* Cabeçalho da área do gráfico */}
            <div className="flex items-center justify-between mb-5">
              <div className="flex gap-1">
                {['colunas', 'pizza'].map((aba) => (
                  <button
                    key={aba}
                    onClick={() => setAbaAtiva(aba)}
                    className={`px-4 py-1.5 text-sm font-semibold rounded-lg transition-colors ${
                      abaAtiva === aba
                        ? 'text-[#5B4FCF] border-b-2 border-[#5B4FCF]'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {aba.toUpperCase()}
                  </button>
                ))}
              </div>
              <BotaoExportar
                chartRef={chartRef}
                nomeArquivo={`lilas-${compararPor}-${abaAtiva}`}
              />
            </div>

            {/* Título e data */}
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-base font-semibold text-gray-800">
                Distribuição de PLs por {LABELS_DIMENSAO[compararPor]}
              </h2>
              {dados?.data_atualizacao && (
                <span className="text-xs text-gray-400 flex-shrink-0">
                  Atualizado em {dados.data_atualizacao}
                </span>
              )}
            </div>

            {/* Gráfico */}
            {loading ? (
              <SkeletonGrafico />
            ) : !dados?.dados?.length ? (
              <div className="flex items-center justify-center h-[350px]">
                <p className="text-gray-400 text-sm">
                  Nenhum dado encontrado para os filtros selecionados.
                </p>
              </div>
            ) : abaAtiva === 'colunas' ? (
              <GraficoColunas dados={dados.dados} chartRef={chartRef} />
            ) : (
              <GraficoPizza dados={dados.dados} chartRef={chartRef} />
            )}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}